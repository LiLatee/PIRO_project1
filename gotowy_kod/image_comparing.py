from scipy import interpolate
from scipy.interpolate import interp1d
import statistics 
import numpy as np
from random import randrange

def get_line_length(point1, point2):
    return math.pow((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 , 0.5)

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

def get_base(img):
    bottom = img.shape[0]-1
    width  = img.shape[1]-1
    base_coords = []
    for w in range(0,width):
        if img[bottom-25,w] == 255:
            base_coords.append(np.array([bottom-10,w]))
    return np.array(base_coords)

def get_middle(img):
    bottom = img.shape[0]-1
    width  = img.shape[1]-1
    middle = bottom - int((bottom)*2/5)
    middle_coords = []
    for w in range(0,width):
        if img[middle,w] == 255:
            middle_coords.append(np.array([middle,w]))
    return np.array(middle_coords)

def generate_points(line,num_p=50):
    points = np.linspace(line[0],line[-1],num=num_p)
    return points[1:-1]

def generate_function(line1, line2):
    functions = []
    for i in range(0,len(line1)):
        lineX = [line1[i,0],line2[i,0]]
        lineY = [line1[i,1],line2[i,1]]
        functions.append(interpolate.interp1d(lineX, lineY, fill_value="extrapolate"))
    return functions

def find_border(lineX,lineY,img):
    for i in range(0,len(lineX)):
        if img[int(lineX[i]),int(lineY[i])] == 255:
            return np.array(list(zip(lineX[0:i],lineY[0:i]))),np.array(list(zip(lineX[i:],lineY[i:]))),[lineX[i],lineY[i]]
    return [],[]

def get_highest_and_lowest(lines_black,lines_white):
    highest = 10000
    lowest = 0
    for l in lines_black:
        for element in l:
            if element[0]>lowest:
                lowest = element[0]
    for l in lines_white:
        for element in l:
            if element[0]<highest:
                highest = element[0]
    return highest,lowest

def get_features(functions, peaks, highest, lowest):
    feature_to_lowest = []
    feature_to_highest = []
    for i,f in enumerate(functions):
        h_w = f(highest)
        l_w = f(lowest)
        h = [highest,h_w]
        l = [lowest,l_w]
        peak_for_line = peaks[i]
        
        len_to_lowest = get_line_length(peak_for_line,l)
        len_to_highest = get_line_length(peak_for_line,h)
        feature_to_lowest.append(len_to_lowest)
        feature_to_highest.append(len_to_highest)

    return feature_to_lowest,np.array(feature_to_highest)[::-1]

def calculate_dev_for_lists(l1,l2):
    return statistics.stdev(np.subtract(l1,l2))
    
    
def compare_images(img_features):
    deviation_matrix = []
    for i1,img_f1 in enumerate(img_features):
        scores_for_img = []
        for i2,img_f2 in enumerate(img_features): 
            if i1 == i2:
                scores_for_img.append(200000)
            else:
                dev = calculate_dev_for_lists(img_f1[0],img_f2[1])
                scores_for_img.append(dev)
        deviation_matrix.append(scores_for_img)
    return deviation_matrix

def analyze_image(img,num_of_points=50):
    hight = img.shape[0]
    width = img.shape[1]

    base = get_base(img)
    middle = get_middle(img)
    print(img.shape)
    print(base)
    print(middle)
    base = generate_points(base,num_of_points)
    middle = generate_points(middle,num_of_points)

    functions = generate_function(base,middle)

    lines = []
    for f in functions:
        xnew = np.arange(0, hight, 1)
        ynew = f(xnew)
        lines.append(np.array([xnew,ynew]))

    lines_black = []
    lines_white = []
    lines_peaks = []
    
    for l in lines:
        black,white,peak = find_border(l[0],l[1],img)
        lines_black.append(black)
        lines_white.append(white)
        lines_peaks.append(peak)

    highest, lowest = get_highest_and_lowest(lines_black,lines_white)

    features = get_features(functions, lines_peaks, highest, lowest)
    return features

def print_out(out):
    out_with_id = []
    
    for o_r in out:
        row = []
        
        for i,o in enumerate(o_r):
            row.append([int(i),o])
            
        row = np.array(row)
        sort_order = sorted(row[:,1])
        row = [tuple for x in sort_order for tuple in row if tuple[1] == x]
        
        out_with_id.append(row)        
    out_with_id = np.array(out_with_id)  
    for r in out_with_id:
        string = ''
        for p in range(0,len(r)-1) :
            string +=" "+str(int(r[p][0]))
        print(string)
        
def get_output_based_on_path(path):
    path = os.path.join(path, '')
    images_paths = glob.glob(os.path.join(path, '*.png'))
    images_paths = get_ordered_images_paths(images_paths)
    images = [io.imread(image_path) for image_path in images_paths]
    get_output_list_of_images(images)

    
def get_output_list_of_images(images):
    data_f = []
    for img in images:
        data_f.append(analyze_image(img,50))
    out = compare_images(data_f)
    print_out(out)

# def get_output_list_of_images(images):
#     data_f = []
#     for img in images:
#         try:
#             data_f.append(analyze_image(img,50))
#         except:
#             print(randrange(len(images)))
#     out = compare_images(data_f)
#     print_out(out)

# get_output_list_of_images(images) #--przykład wywołania