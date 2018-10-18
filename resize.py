from PIL import Image
import os

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


image_file_paths = get_file_paths('/home/vagrant/src/my-project/train')

i = 0
for image_path in image_file_paths:
    resize_and_align(image_path, '/home/vagrant/src/my-project/result', i)
    i+=1
