import sys
import os
import glob
from skimage import io
from matplotlib import pyplot as plt
import numpy as np
from image_preprocessing import rotate_scale_and_cut_image_v6

from pathlib import Path
from image_operations import *

def get_ordered_images_paths(images_paths):
    path, filename = os.path.split(images_paths[0])
    paths_and_filenames = [os.path.split(image_path) for image_path in images_paths]
    filenames = list(zip(*paths_and_filenames))[1]

    images_order = [int(filename[:-4]) for filename in filenames]
    res = [image_path for i, image_path in enumerate(images_paths) for x in images_order if i == x] 
    order_path_pairs = list(zip(images_order, images_paths))
    order_path_pairs.sort()
    images_paths_sorted = [x[1] for x in order_path_pairs]
    
    return images_paths_sorted



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(os.path.basename(sys.argv[0]) + " <sciezka_do_katalogu_z_plikami> <liczba_obrazkow_do_wczytania>")
        exit(1)
    args = sys.argv
    path = os.path.join(os.path.split(args[1])[0], os.path.split(args[1])[1])
    n_images = args[2]

    images_paths = glob.glob(os.path.join(path, '*.png'))
    images_paths = get_ordered_images_paths(images_paths)
    images = [io.imread(image_path) for image_path in images_paths]
    # processed_images = [rotate_scale_and_cut_image_v6(image) for image in images]

    max_height, max_width = max_height_and_width_from_images(images)
    result_path = Path("./../data/proj1_daneB_wyniki/set8")
    processed_images = list()
    for i, image in enumerate(images):
        _, filename = os.path.split(images_paths[i])
        
        processed_image = rotate_scale_and_cut_image_v6(image, images_paths[i], max_height, max_width)

        save_path = os.path.join(os.path.join(result_path, filename))
        io.imsave(save_path, arr=img_as_ubyte(processed_image))


