import numpy as np
from skimage import io
from skimage.feature import canny, corner_subpix
from skimage.morphology import opening, square
from skimage.transform import probabilistic_hough_line
from skimage.measure import find_contours, approximate_polygon

from image_operations import *
from util import *


# v6
# sprawdza wykryte po kolei kąty w wielokącie i szuka dwóch dających sumę 180 lub o równych kątach, ale z przedziału 70-110
def rotate_scale_and_cut_image_v6(image, max_height, max_width, image_path=None):
    image = add_black_border_to_image(image, width_of_border=30)
    counter_of_tries = 0
    baselines = list()
    while counter_of_tries < 5:
        possible_baseline_points, angles_of_points = get_points_and_angles_in_image(image)
        baseline = get_points_at_the_base_multi(possible_baseline_points, angles_of_points) # todo, zwróci NONE
        counter_of_tries += 1
        if baseline is not None:
            baselines.append(baseline)
    

    if len(baselines) != 0:
        longest_line_index = np.argmax([get_line_length(line[0], line[1]) for line in baselines]) 
        baseline = baselines[longest_line_index]
    else:
        baseline = None

    min_length = image.shape[0] if image.shape[0] >= image.shape[1] else image.shape[1]
    if baseline is None or get_line_length(baseline[0], baseline[1]) < min_length/5:
        if image_path is not None:
            print('Nie znaleziono podstawy dla obrazka z użyciem v6: {0}'.format(image_path))
        image = threshold_image(image)
        angle, baseline = get_angle_to_rotate_image_based_on_longest_line(image)
        baseline = [(el[1],el[0]) for el in baseline]
#         return rotate_scale_and_cut_image_v1(image, image_path, max_height, max_width) #todo

    baseline = [(el[1],el[0]) for el in baseline]

    angle = get_angle_of_line(baseline)
    image = rotate_image(image, angle, baseline) 
    image = cut_image_sides(image)
    image = resize_image(image, max_height, max_width)
    image = open_close_image(image)
    image = rotate_image_if_wrong_orientation(image)
    return image

def get_points_and_angles_in_image(image):
    possible_baseline_points = find_corners(image)

    angles_of_points = list()
    for point in possible_baseline_points:
        angle = get_angle_of_point_using_hough(image, point)
        angles_of_points.append(angle)

    return possible_baseline_points, angles_of_points

def find_corners(image):
    contour = find_contours(image, level=10)[0]
    appr_pol = list(approximate_polygon(contour, tolerance=10)[:-1]) 
    appr_pol = np.around(np.array(appr_pol))
    appr_pol = corner_subpix(image, appr_pol, window_size=50)
    appr_pol = appr_pol[~np.isnan(appr_pol).any(axis=1)]
    appr_pol = list(appr_pol)
    appr_pol = appr_pol+appr_pol[:1]
    return appr_pol

def get_angle_of_point_using_hough(image, point):
    slice_of_image, _ = slice_image_in_radius(image, point, radius=20)
    slice_of_image = opening(slice_of_image, square(1))
    list_of_angles = get_list_of_different_angles_in_image_using_hough(image=slice_of_image)
#     points = corner_peaks(corner_harris(slice_of_image), min_distance=10)
#     if len(points) > 0:
#         point = points[0]
    if len(list_of_angles) == 2:
        angle_between_lines = abs(list_of_angles[0]-list_of_angles[1])
        return  angle_between_lines
    
    return None

def get_list_of_different_angles_in_image_using_hough(image):
    edges = canny(image)
    lines = probabilistic_hough_line(edges, 
                                     threshold=10, 
                                     line_length=10,
                                     line_gap=1)
    list_of_angles = [get_angle_of_line(line) for line in lines]
    list_of_angles_no_duplicates = list()
#     print(len(lines))
    
    for angle in list_of_angles:
        add = True
        for added_angle in list_of_angles_no_duplicates:
            if compare_2_numbers_with_range(added_angle, angle, 5):
                add = False
        if add:
            list_of_angles_no_duplicates.append(angle)
                
    # np. kąty -176 i 180 są obok siebie, zależą od zwrotu, to samo z kątem 90
    # tutaj usuwamy takie przypadki, żeby mieć na penwo różne kąty
    exists_90 = False
    exists_180 = False
    modified_list_of_angles = list()
    for angle in list_of_angles_no_duplicates:
        if compare_2_numbers_with_range(90, abs(angle), 10):
            if exists_90 == False:
                exists_90 = True
                modified_list_of_angles.append(angle)
        elif compare_2_numbers_with_range(180, abs(angle), 10):
            if exists_180 == False:
                exists_180 = True
                modified_list_of_angles.append(angle)
        else:
            modified_list_of_angles.append(angle)
    
    return modified_list_of_angles

def get_points_at_the_base(list_of_points, angles_of_points):
#     print("list_of_points: ", np.array(list_of_points))
#     print("angles_of_points: ", np.array(angles_of_points))
    last_angle = None
    for i, angle in enumerate(angles_of_points):
        if last_angle is None:
            last_angle = angle
            continue
        if angle is None:
            last_angle = None
            continue
#         print((list_of_points[i-1], list_of_points[i]))
#         print(last_angle, angle)
        is_sum_180 = compare_2_numbers_with_range(last_angle + angle, 180, range=5)
        same_angles = compare_2_numbers_with_range(last_angle, angle, range=5)
        if is_sum_180 or (same_angles and angle > 60 and angle < 120):
#             print("tak")
            return (list_of_points[i-1], list_of_points[i])
        last_angle = angle
    return None

def get_points_at_the_base_multi(list_of_points, angles_of_points):
    result = list()
#     print("list_of_points: ", np.array(list_of_points))
#     print("angles_of_points: ", np.array(angles_of_points))
    last_angle = None
    for i, angle in enumerate(angles_of_points):
        if last_angle is None:
            last_angle = angle
            continue
        if angle is None:
            last_angle = None
            continue
#         print((list_of_points[i-1], list_of_points[i]))
#         print(last_angle, angle)
        is_sum_180 = compare_2_numbers_with_range(last_angle + angle, 180, range=20)
        same_angles = compare_2_numbers_with_range(last_angle, angle, range=10)
        if is_sum_180 or (same_angles and angle > 70 and angle < 110):
#             print("tak")
            result.append((list_of_points[i-1], list_of_points[i]))
        last_angle = angle
        
#     print("result")
#     print(result)
#     print("================")
    if len(result) ==0:
        return None
    # szukanie najdłuższej linii jako podstawy
    max_length = get_line_length(result[0][0], result[0][1])
    result_line = result[0]
    for line in result:
        temp_length = get_line_length(line[0], line[1])
        if temp_length > max_length:
            max_length = temp_length
            result_line = line

    return result_line

def get_angle_to_rotate_image_based_on_longest_line(image):
    thresh = threshold_otsu(image)
    image_binary = image > thresh
    label_img, num = label(image_binary, connectivity=2, return_num=True, background=0)
    region_props = regionprops(label_img)
    biggest_region = region_props[0]
    perimeter = biggest_region.perimeter
    
    edges = canny(image_binary, sigma=1, low_threshold=False, high_threshold=True)
    all_detected_lines = list()
    lines = probabilistic_hough_line(edges, threshold=10, line_length=10, line_gap=20)
    all_detected_lines += lines
    counter_of_tries = 0
    while counter_of_tries < 5:
        edges = canny(image_binary, sigma=1, low_threshold=False, high_threshold=True)
        min_length = image.shape[0] if image.shape[0] >= image.shape[1] else image.shape[1]
        lines = probabilistic_hough_line(edges, threshold=10, line_length=30,line_gap=10)
        all_detected_lines += lines
        counter_of_tries += 1

    longest_line = (lines[0],  get_line_length(lines[0][0], lines[0][1]))
    for line in lines:
        temp_lenght = get_line_length(line[0], line[1])
        if temp_lenght > longest_line[1]:
            longest_line = (line, temp_lenght)

    angle = get_angle_of_line(longest_line[0])
    baseline = longest_line[0]
    return angle, baseline