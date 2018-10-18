import os
from PIL import Image

from werkzeug.utils import secure_filename

import subprocess

"""
take image from the database, resize and alighn it and store it 
 in the  --dataroot ./datasets/portraits
call test.py with image name.jpg :
 python test.py --dataroot ./datasets/portraits --direction=AtoB --model pix2pix 
--name portraits_pix2pix --gpu_ids -1 --norm instance  --image name.jpg
"""


def resize_and_align(image_path, target_path):
    """Resize and double the picture"""
    basewidth = 512
    baseheight = 512
    img = Image.open(file_path)
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

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    aligned_image = Image.new("RGB", (img.size[0] * 2, img.size[1]))
    aligned_image.paste(img_bw, (0, 0))
    aligned_image.paste(img, (img.size[0], 0))
    aligned_image.save(os.path.join(target_path, new.jpg))



completed = subprocess.run([
        'convert', original_path, '-set', 'colorspace', 'Gray', processed_path
    ], stdout=subprocess.PIPE, check=True)