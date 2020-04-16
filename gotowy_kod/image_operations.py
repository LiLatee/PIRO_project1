import numpy as np
from skimage import io
from skimage.transform import resize, rotate
from skimage import color
from skimage.morphology import closing, opening, disk, square
from skimage.util import img_as_bool, img_as_ubyte
from skimage.measure import regionprops, label
from skimage.filters import threshold_otsu

from util import clamp, get_white_to_black_ratio_in_array


LEFT_RIGHT_SPACE = 0
def slice_image_in_radius(image, point, radius):
    (height, width) = point
    height = int(height)
    width = int(width)
    (image_height, image_width) = image.shape
    

    point_height_in_sliced_image = radius+1
    point_width_in_sliced_image = radius+1
    if height-radius < 0 :
        point_height_in_sliced_image = radius - (radius-height)
    if width-radius < 0:
        point_width_in_sliced_image = radius - (radius-width)
    middle_point = (point_height_in_sliced_image, point_width_in_sliced_image)

    right_width_min = clamp(width-radius-1, 0, image_width)
    right_width_max = clamp(width+radius+1, 0, image_width)
    right_height_min = clamp(height-radius-1, 0, image_height)
    right_height_max = clamp(height+radius+1, 0, image_height)
    slice_of_image = image[right_height_min:right_height_max, right_width_min:right_width_max]
    return slice_of_image, middle_point

def rotate_image(image, angle, baseline):
    baseline = [(el[1],el[0]) for el in baseline]
    is_baseline_top = True
    is_baseline_left = True
    
    (image_height, image_width) = image.shape
    (base_point1, base_point2) = baseline
    
    baseline_avg_height = (base_point1[0]+base_point2[0])/2
    baseline_avg_width = (base_point1[1]+base_point2[1])/2
    if baseline_avg_height <= image_height/2:
        is_baseline_top = True
    else:
        is_baseline_top = False
        
    if baseline_avg_width <= image_width/2:
        is_baseline_left = True
    else:
        is_baseline_left = False
        
    if angle >= 0:
        if not is_baseline_left:
            return img_as_bool(rotate(image, 180+angle, resize=True))
        else:
            return img_as_bool(rotate(image, angle, resize=True))

    if angle < 0:
        if is_baseline_left:
            return img_as_bool(rotate(image, 180+angle, resize=True))
        else:
            return img_as_bool(rotate(image, angle, resize=True))
    

def max_height_and_width_from_images(images):
    max_height, max_width = images[0].shape
    for image in images:
        if image.shape[0] > max_height:
            max_height = image.shape[0]
        if image.shape[1] > max_width:
            max_width = image.shape[1]
    return max_height, max_width

def min_height_and_width_from_images(images):
    min_height, min_width = images[0].shape
    for image in images:
        if image.shape[0] < min_height:
            min_height = image.shape[0]
        if image.shape[1] < min_width:
            min_width = image.shape[1]
    return min_height, min_width

def resize_image(image, max_height, max_width):  
    scale = max_width/image.shape[1]
    new_shape = (int(image.shape[0]*scale), int(image.shape[1]*scale))
    image_resized = (resize(img_as_ubyte(image), new_shape))
    image_resized = threshold_image(image_resized)
    
    return image_resized


def cut_image_sides(image):
    label_img, num = label(image, connectivity=2, return_num=True, background=0)
    region_props = regionprops(label_img)
    biggest_region = region_props[0]
    for region in region_props:
        if region.area > biggest_region.area:
            biggest_region = region
    
    image_cut = image[biggest_region.bbox[0]:biggest_region.bbox[2],biggest_region.bbox[1]-LEFT_RIGHT_SPACE:biggest_region.bbox[3]+LEFT_RIGHT_SPACE]
    return image_cut

def threshold_image(image):
    thresh = threshold_otsu(image)
    thresholded = image > thresh
    return thresholded

def open_close_image(image):
    image = opening(closing(image, disk(5)), disk(5))
    return image

def add_black_border_to_image(image, width_of_border=30):
    (h, w) = image.shape
    new_image_left_border = np.zeros((h,w+width_of_border))
    new_image_left_border[:,width_of_border:] = image
    image = new_image_left_border
    
    (h, w) = image.shape
    new_image_right_border = np.zeros((h,w+width_of_border))
    new_image_right_border[:,:-width_of_border] = image
    image = new_image_right_border
    
    (h, w) = image.shape
    new_image_bot_border = np.zeros((h+width_of_border,w))
    new_image_bot_border[:-width_of_border,:] = image
    image = new_image_bot_border
    
    (h, w) = image.shape
    new_image_top_border = np.zeros((h+width_of_border,w))
    new_image_top_border[width_of_border:,:] = image
    image = new_image_top_border
    return image

def rotate_image_if_wrong_orientation(image):
    # dodatkowe sprawdzenie czy nie jest do góry nogami
    n_of_pixels_top_bot = int(image.shape[0]*0.1)
    n_of_pixels_left_right = int(image.shape[1]*0.1)
    white_black_ratio_first_row = get_white_to_black_ratio_in_array(image[:n_of_pixels_top_bot, :])
    
    if white_black_ratio_first_row > 0.8:
        image = img_as_bool(rotate(image, 180, resize=True))
    
    # sprawdzenie czy nie wykryło podstawy jako lewego boku, czyli czy nie leży na lewym boku 
    white_black_ratio_left_column = get_white_to_black_ratio_in_array(image[:, :n_of_pixels_left_right])
    white_black_ratio_right_column = get_white_to_black_ratio_in_array(image[:, -n_of_pixels_left_right:]) 

    if (white_black_ratio_right_column > 0.85 and white_black_ratio_left_column < 0.2):
        image = img_as_bool(rotate(image, -90, resize=True))
        image = add_black_border_to_image(image, width_of_border=30)
        image = cut_image_sides(image)
    
    # sprawdzenie czy nie wykryło podstawy jako prawego boku, czyli czy nie leży na prawym boku 
    white_black_ratio_left_column = get_white_to_black_ratio_in_array(image[:, :n_of_pixels_left_right])
    white_black_ratio_right_column = get_white_to_black_ratio_in_array(image[:, -n_of_pixels_left_right:]) 
    
    if (white_black_ratio_right_column < 0.2 and white_black_ratio_left_column > 0.85) :
        image = img_as_bool(rotate(image, 90, resize=True))     
        image = add_black_border_to_image(image, width_of_border=30)
        image = cut_image_sides(image)
        
    return image

    
