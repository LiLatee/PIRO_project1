import sys
import os
import glob
from skimage import io
from matplotlib import pyplot as plt

if __name__ == '__main__':
    n_of_args =  len(sys.argv)
    args = sys.argv
    path = os.path.join(os.path.split(args[1])[0], os.path.split(args[1])[1])
    n_of_cases = args[2]

    images_paths = glob.glob(os.path.join(path, '*.png'))
    img = io.imread(images_paths[0])
    io.imshow(img)
    plt.show()
