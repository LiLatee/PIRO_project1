import sys
import os
import glob
from skimage import io
from matplotlib import pyplot as plt
import numpy as np

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(os.path.basename(sys.argv[0]) + " <sciezka_do_katalogu_z_plikami> <liczba_obrazkow_do_wczytania> <>")
        exit(1)
    args = sys.argv
    path = os.path.join(os.path.split(args[1])[0], os.path.split(args[1])[1])
    n_images = args[2]

    images_paths = glob.glob(os.path.join(path, '*.png'))
    # print(images_paths)

    # print(path)
    print(5)
    print(2)
    print(1)
    print(4)
    print(3)
    print(0)
    for i in range(len(images_paths) - 6):
        print(6)
    
    # img = io.imread(images_paths[0])
    # io.imshow(img)
    # plt.show()
