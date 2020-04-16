import sys
import os
import glob
from skimage import io
from matplotlib import pyplot as plt
import numpy as np
from image_preprocessing import rotate_scale_and_cut_image_v6

from pathlib import Path
from image_operations import *
from image_comparing import get_output_list_of_images

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
    n_images = int(args[2])
    
    images_paths = glob.glob(os.path.join(path, '*.png'))
    images_paths = get_ordered_images_paths(images_paths)
    images = [io.imread(image_path) for image_path in images_paths[:n_images]]
    max_height, max_width = max_height_and_width_from_images(images)
    processed_images = [rotate_scale_and_cut_image_v6(image, max_height, max_width) for image in images]

    get_output_list_of_images(processed_images)








    ############## testowanko ##############
    # max_height, max_width = max_height_and_width_from_images(images)
    # result_path = Path("./../data/proj1_daneB_wyniki/set8")
    # processed_images = list()
    # for i, image in enumerate(images):
    #     _, filename = os.path.split(images_paths[i])
        
    #     processed_image = rotate_scale_and_cut_image_v6(image, max_height, max_width, images_paths[i])

    #     save_path = os.path.join(os.path.join(result_path, filename))
    #     io.imsave(save_path, arr=img_as_ubyte(processed_image))


