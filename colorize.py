import os
from PIL import Image
import s3

from werkzeug.utils import secure_filename

import shutil
import subprocess


"""
take image from the database, resize and alighn it and store it 
 in the  --dataroot ./datasets/portraits
call test.py with image name.jpg :
 python test.py --dataroot ./datasets/portraits --direction=AtoB --model pix2pix 
--name portraits_pix2pix --gpu_ids -1 --norm instance  --image name.jpg
"""

PIX2PIX_PATH = os.environ.get('PIX2PIX_PATH', 'pix2pix')
RESULTS_FOLDER = \
    os.path.abspath('results/portraits_pix2pix/test_latest/images')

def resize_and_align(src_path, dest_path):
    """Resize and double the picture"""
    basewidth = 512
    baseheight = 512
    img = Image.open(src_path)
    width, height = img.size

    if width >= height:
        wpercent = (basewidth/float(width))
        hsize = int((float(height)*float(wpercent))) 
        hsize = hsize - hsize % 4
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    else:
        wpercent = (baseheight/float(height))
        wsize = int((float(width)*float(wpercent)))
        wsize = wsize - wsize % 4
        img = img.resize((wsize,baseheight), Image.ANTIALIAS)

    img_bw= img.convert('L')  #monochromize

    aligned_image = Image.new("RGB", (img.size[0] * 2, img.size[1]))
    aligned_image.paste(img_bw, (0, 0))
    aligned_image.paste(img, (img.size[0], 0))
    aligned_image.save(dest_path)


def colorize_photo(filename):
    completed = subprocess.run([
        'python', os.path.join(PIX2PIX_PATH, 'test.py'),
        '--checkpoints_dir', os.path.join(PIX2PIX_PATH, 'checkpoints'),
        '--dataroot', os.path.abspath('uploads'),
        '--direction=AtoB',
        '--model', 'pix2pix',
        '--name', 'portraits_pix2pix',
        '--gpu_ids', '-1',
        '--norm', 'instance',
        '--image', filename,
    ], stdout=subprocess.PIPE, check=True)


def resize_back(original_path, processed_path):
    img_bw = Image.open(original_path)
    img = Image.open(processed_path)
    width, height = img_bw.size
    img = img.resize((width,height), Image.ANTIALIAS)
    img.save(processed_path)

def transfer_color(original_path, colorized_path, processed_path):
    subprocess.run([
        'convert', colorized_path, original_path,
        '-colorspace', 'HSL',
        '-compose', 'CopyBlue', '-composite',
        '-colorspace', 'sRGB',
        processed_path,
    ], stdout=subprocess.PIPE, check=True)


def process(upload_folder, original_filename):
    """Returns filename of the processed photo in the uploads folder."""


    original_path = os.path.abspath(os.path.join(
        upload_folder, original_filename))
   
    test_dir = os.path.abspath(os.path.join(
        upload_folder, 'test'))
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    aligned_path = os.path.join(test_dir, original_filename)

    resize_and_align(original_path, aligned_path)
    colorize_photo(original_filename)

    basename = original_filename.rsplit('.', 1)[0]
    processed_filename = '{}_fake_B.png'.format(basename)
    colorized_path = os.path.join(
        RESULTS_FOLDER, processed_filename)

    processed_path = os.path.join(upload_folder, processed_filename)
    resize_back(original_path, colorized_path)
    transfer_color(original_path, colorized_path, processed_path)
    return processed_filename

    """resize_and_align(
        os.path.abspath(original_path), 
        os.path.abspath(target_path), 
        processed_photo
    )
    colorize_photo(processed_photo)

    shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
    
    resize_back(os.path.abspath(original_path), os.path.abspath(processed_photo)
    """




