import math
import numpy as np

def get_line_length(point1, point2):
    return math.pow((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 , 0.5)

def get_angle_of_line(line):
    (point1, point2) = line
    angle = math.atan2(point2[1] - point1[1], point2[0] - point1[0]) * 180 / np.pi
    return angle #if angle >= 0 else 180+angle

def compare_2_numbers_with_range(n1, n2, range=3):
    difference = abs(n1-n2)
    return difference <= range

def compare_2_points_with_range(point1, point2, range=3):
    x1, y1 = point1
    x2, y2 = point2
    return compare_2_numbers_with_range(x1, x2, range) and compare_2_numbers_with_range(y1, y2, range)

def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))

def get_white_to_black_ratio_in_array(pixels_array):
    white_pixel_count = 0
    black_pixel_count = 0
    
    unique_values, counts = np.unique(pixels_array, return_counts=True)
    unique_counts_dict = dict(zip(unique_values, counts))
    
    if False in unique_counts_dict:
        black_pixel_count = unique_counts_dict[False]
    if True in unique_counts_dict:
        white_pixel_count = unique_counts_dict[True]
    

    ratio = white_pixel_count/(white_pixel_count + black_pixel_count)
    return ratio
