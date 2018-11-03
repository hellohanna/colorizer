from PIL import Image
import os
import shutil
import zipfile


PIX2PIX_PATH = os.environ.get('PIX2PIX_PATH', 'pix2pix')

def resize_img(file_path):
    """Resize image to max side: 512px"""

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

    img.save(file_path) 


def align_images(a_file_paths, b_file_paths, target_path):
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    for i in range(len(a_file_paths)):
        img_a = Image.open(a_file_paths[i])
        img_b = Image.open(b_file_paths[i])
        assert(img_a.size == img_b.size)

        aligned_image = Image.new("RGB", (img_a.size[0] * 2, img_a.size[1]))
        aligned_image.paste(img_a, (0, 0))
        aligned_image.paste(img_b, (img_a.size[0], 0))
        aligned_image.save(os.path.join(target_path, '{:04d}.jpg'.format(i)))


def resize_and_align(file_path, target_path, i):
    """Resize image, monochromize and align two images"""

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
    aligned_image.save(os.path.join(target_path, '{:04d}.jpg'.format(i)))


def unzip_and_prepare(path_to_zip_file, dataset_id):
    """Unzipping dataset and creating a training set of images"""
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    directory_to_extract_to = 'train/unzipped'
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()
    os.remove(path_to_zip_file)
    image_file_paths = get_file_paths(directory_to_extract_to)

    train_number = int(len(image_file_paths)*0.8)
    dataset_path = '{}/datasets/dataset_{}'.format(PIX2PIX_PATH, dataset_id)
    i = 0
    for image_path in image_file_paths:
        if i < train_number:
            resize_and_align(image_path, os.path.join(dataset_path, 'train'), i)
        else:
            resize_and_align(image_path, os.path.join(dataset_path, 'test'), i)
        i+=1
    shutil.rmtree(directory_to_extract_to)


def get_file_paths(folder):
    """Create a list of filepaths to all images in the folder"""

    image_file_paths = []
    for root, dirs, filenames in os.walk(folder):
        filenames = sorted(filenames)
        for filename in filenames:
            input_path = os.path.abspath(root)
            file_path = os.path.join(input_path, filename)
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.JPG'):
                image_file_paths.append(file_path)

        break  # prevent descending into subfolders
    return image_file_paths


