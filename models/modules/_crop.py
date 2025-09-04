from PIL import Image
import numpy as np
import cv2
import math

class rect:
    def __init__(self, x, y, width, height):
        '''
        Initialize a rectangle with the given parameters.
        Args:
            x (float): x-coordinate of the rectangle's top-left corner.
            y (float): y-coordinate of the rectangle's top-left corner.
            width (float): Width of the rectangle.
            height (float): Height of the rectangle.
        '''
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.area = width * height
        self.center = [x + (width / 2), y + (height / 2)]
        
        
def min_distance_of_rectangles(rect1, rect2):
    '''
    Calculate the minimum distance between two rectangles.
    Args:
        rect1 (rect): The first rectangle.
        rect2 (rect): The second rectangle.
    Returns:
        min_dist (float): The minimum distance between the two rectangles.
    '''
    min_dist = 0
    Dx = abs(rect1.center[0] - rect2.center[0])
    Dy = abs(rect1.center[1] - rect2.center[1])
    if (Dx < ((rect1.width + rect2.width)/ 2)) and (Dy >= ((rect1.height + rect2.height) / 2)):
        min_dist = Dy - ((rect1.height + rect2.height) / 2)
    elif (Dx >= ((rect1.width + rect2.width)/ 2)) and (Dy < ((rect1.height + rect2.height) / 2)):
        min_dist = Dx - ((rect1.width + rect2.width)/ 2)
    elif (Dx >= ((rect1.width + rect2.width)/ 2)) and (Dy >= ((rect1.height + rect2.height) / 2)):
        delta_x = Dx - ((rect1.width + rect2.width)/ 2)
        delta_y = Dy - ((rect1.height + rect2.height)/ 2)
        min_dist = math.sqrt(delta_x * delta_x  + delta_y * delta_y)
    else:
        min_dist = -1
    return min_dist

def merge_crop_boxes(crop_box_list, image_shape, max_merge_dist):
    '''
    Merge the crop boxes that are close to each other.
    
    Args:
        crop_box_list: The list of crop boxes to be merged. Each crop box is represented as a tuple (left, up, right, bottom).
        image_shape: The shape of the image.
        max_merge_dist: The maximum distance threshold for merging.
    '''

    # set the distance threshold for merging, which is 1% of the maximum image size
    distance_threshold = int(max(image_shape) * max_merge_dist)
    merge_dict = {box: [] for box in crop_box_list}

    # calculate the other crop boxes that need to be merged for each crop box
    for box1 in crop_box_list:
        merge_dict[box1] = [box2 for box2 in crop_box_list if min_distance_of_rectangles(rect(box1[0], box1[1], box1[2] - box1[0], box1[3] - box1[1]),
                                rect(box2[0], box2[1], box2[2] - box2[0], box2[3] - box2[1])) < distance_threshold]

    # generate the merge list
    merge_list = []
    
    for merge_group in merge_dict.values():
        if merge_group and sorted(merge_group) not in merge_list:
            merge_list.append(sorted(merge_group))


    # temporary storage for the merge groups that need to be removed
    temp_merge_list = []

    # find the merge groups that are subsets of other merge groups
    for group1 in merge_list:
        for group2 in merge_list:
            if group1 != group2 and set(group1).issubset(set(group2)):
                temp_merge_list.append(group1)        

    # remove the subset merge groups from the merge list
    for group_to_remove in temp_merge_list:
        if group_to_remove in merge_list:
            merge_list.remove(group_to_remove)

    # traverse each merge group and merge the bounding boxes
    for merge_group in merge_list:
        # remove the first bounding box in the merge group
        if merge_group[0] in crop_box_list:
            crop_box_list.remove(merge_group[0])

        # remove the other bounding boxes in the merge group
        for other_box in merge_group[1:]:
            if other_box in crop_box_list:
                crop_box_list.remove(other_box)

        new_merged_box = merge_group[0]

        # update the coordinates of the new bounding box
        for other_box in merge_group[1:]:
            new_merged_box = (
                min(new_merged_box[0], other_box[0]),
                min(new_merged_box[1], other_box[1]),
                max(new_merged_box[2], other_box[2]),
                max(new_merged_box[3], other_box[3])
            )

            # adjust the merged box to a square
            width = new_merged_box[2] - new_merged_box[0]
            height = new_merged_box[3] - new_merged_box[1]
            if width > height:
                difference = (width - height) / 2
                new_merged_box = (
                    new_merged_box[0],
                    new_merged_box[1] - difference,
                    new_merged_box[2],
                    new_merged_box[3] + difference
                )
            elif width < height:
                difference = (height - width) / 2
                new_merged_box = (
                    new_merged_box[0] - difference,
                    new_merged_box[1],
                    new_merged_box[2] + difference,
                    new_merged_box[3]
                )

        crop_box_list.append(new_merged_box) 
    
    merged_box_list = sorted(crop_box_list, key=lambda x: (x[2]-x[0])*(x[3]-x[1]), reverse=True)
    return merged_box_list
     
    
def crop_sub_image_mask(image_path, mask_path, padding=0.1, max_merge_dist=0.01, min_crop_size=0.1):
    '''
    Crop the sub-images based on the mask
    
    Args:
        image_path: The path of the original image.
        mask: The path of the corresponding mask.
        padding: The padding ratio of the crop box.
        max_merge_dist: The maximum distance threshold for merging.
        min_crop_size: The minimum size ratio of the crop box.
    '''
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    if mask_path is None:
        mask = np.zeros_like(image[:, :, 0])
    else:
        mask = cv2.imread(mask_path)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    image_shape = image.shape
    # resize the mask to the same size as the image
    mask = cv2.resize(mask, (image_shape[1], image_shape[0]), interpolation=cv2.INTER_NEAREST)

    # get the coordinates of the bounding box
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_list = []
    point_list = []
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)  
        area_list.append(h*w)
        point_list.append([x, y, w, h])

    # get the crop box
    if len(area_list) == 0:
        crop_box_list = [(0, 0, image_shape[1], image_shape[0])]
    else:
        area_list, sort_p_list = zip(*sorted(list(zip(area_list, point_list))))
        crop_box_list = []

        for i, point in enumerate(sort_p_list):
            x, y, width, height = point[0], point[1], point[2], point[3]
            p1, p2 = [y, x], [y+height, x+width]   
            center = [int((i+j)*0.5) for i, j in zip(p1, p2)]
            radius = max( int(max(height, width) * (1+padding) * 0.5), int(max(image_shape) * min_crop_size))   # the crop box's "radius" should be at least "min_crop_size" of the image size
            radius = min(radius, int(max(image_shape) * 0.5)) # the crop box should be within the image
            left, up, right, bottom = center[1]-radius, center[0]-radius, center[1]+radius, center[0]+radius

            # the crop box should be within the image
            if left<0:
                left, right = 0, 2*radius
            elif right>image_shape[1]:
                left, right = image_shape[1]-2*radius, image_shape[1]
            if up<0:
                up, bottom = 0, 2*radius
            elif bottom>image_shape[0]:
                up, bottom = image_shape[0]-2*radius, image_shape[0]
            crop_box_list.append((left, up, right, bottom))

    # merge the crop boxes
    merged_box_list = merge_crop_boxes(crop_box_list, image_shape, max_merge_dist)

    image = Image.fromarray(image).convert("RGB")
    mask = Image.fromarray(mask).convert("L")
    image_crop_result = [image.crop(crop_box) for crop_box in merged_box_list]
    mask_crop_result = [mask.crop(crop_box) for crop_box in merged_box_list]
    return image_crop_result, mask_crop_result, merged_box_list


