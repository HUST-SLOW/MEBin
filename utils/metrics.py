import os
import sys
sys.path.append(os.getcwd())


def calculate_iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Args:
        box1 (list): Coordinates of the first bounding box in the format [xmin, ymin, xmax, ymax].
        box2 (list): Coordinates of the second bounding box in the format [xmin, ymin, xmax, ymax].
    Returns:
        float: The IoU value between the two boxes.
    """
    # Calculate the coordinates of the intersection area
    inter_xmin = max(box1[0], box2[0])
    inter_ymin = max(box1[1], box2[1])
    inter_xmax = min(box1[2], box2[2])
    inter_ymax = min(box1[3], box2[3])
    
    # Calculate the area of the intersection, ensuring it is non-negative
    inter_area = max(0, inter_xmax - inter_xmin) * max(0, inter_ymax - inter_ymin)
    
    # Calculate the areas of the two boxes
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    # Calculate the union area (total area minus the intersection area)
    union_area = box1_area + box2_area - inter_area
    
    # Calculate the IoU
    iou = inter_area / union_area if union_area > 0 else 0
    return iou


def compute_tp_fp_fn(gt_boxes, pred_boxes, iou_threshold=0.1):
    """
    Compute True Positives (TP), False Positives (FP), and False Negatives (FN) 
    based on the IoU threshold between ground truth boxes and predicted boxes.

    Args:
        gt_boxes (list): List of ground truth bounding boxes in the format [xmin, ymin, xmax, ymax].
        pred_boxes (list): List of predicted bounding boxes in the format [xmin, ymin, xmax, ymax].
        iou_threshold (float): The minimum IoU required to consider a match.
    Returns:
        tuple: (TP, FP, FN) counts.
    """
    TP, FP, FN = 0, 0, 0
    # Iterate through each predicted box to check for matches with ground truth boxes
    for pred_box in pred_boxes:
        matched = False
        for gt_box in gt_boxes:
            iou = calculate_iou(pred_box, gt_box)
            if iou >= iou_threshold:
                matched = True
                break
        if matched:
            TP += 1
        else:
            FP += 1
    
    # Iterate through each ground truth box to check for unmatched boxes (False Negatives)
    for gt_box in gt_boxes:
        matched = False
        for pred_box in pred_boxes:
            iou = calculate_iou(pred_box, gt_box)
            if iou >= iou_threshold:
                matched = True
                break
        if not matched:
            FN += 1
    
    return TP, FP, FN



def evaluate_region_level(pred_boxes, gt_boxes, ano_type):
    """
    Evaluate the region-level performance by calculating TP, FP, and FN 
    for a set of predicted boxes against ground truth boxes.

    Parameters:
        pred_boxes (dict): Dictionary of predicted boxes with image names as keys.
        gt_boxes (dict): Dictionary of ground truth boxes with image names as keys.
        ano_type (str): Type of anomaly ('good' or other).
    Returns:
        tuple: (TP_all, FP_all, FN_all) total counts for all images.
    """
    img_names = gt_boxes.keys()
    
    TP_all, FP_all, FN_all = 0, 0, 0
    # Iterate through each image
    for img_name in img_names:
        pred_boxes_ls = pred_boxes[img_name]
        gt_boxes_ls = gt_boxes[img_name]
        if ano_type == 'good':
            TP, FP, FN = 0, 0, 0
            gt_box = gt_boxes_ls[0]
            for pred_box in pred_boxes_ls:
                if pred_box != gt_box:
                    FP += 1
                else:
                    TP += 1       
        else: 
            TP, FP, FN = compute_tp_fp_fn(gt_boxes_ls, pred_boxes_ls, 0.1)
        TP_all += TP
        FP_all += FP
        FN_all += FN
        
    return TP_all, FP_all, FN_all


