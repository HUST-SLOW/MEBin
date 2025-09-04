import os
import json
import csv
import sys
sys.path.append(os.getcwd())

from utils.metrics import evaluate_region_level
from models.mebin_crop import mvtec_crop

mvtec_class_names = ["bottle", "cable", "capsule", "carpet", "grid",
                    "hazelnut", "leather", "metal_nut", "pill", "screw",
                    "tile", "toothbrush", "transistor", "wood", "zipper"]

def mvtec_eval(args):
    '''
    Evaluate the binarization results for the MVTec dataset and compute metrics such as True Positives (TP), 
    False Positives (FP), False Negatives (FN), False Positive Rate (FPR), and False Negative Rate (FNR).
    
    Args:
        args (dict): Configuration arguments
    Returns:
        None
    '''
    # Determine the binarization method and construct the output paths for cropping and evaluation
    bin_method = args['binarization']['binarization_method']
    if bin_method == 'FixedThresholdBin':
        crop_output_path = os.path.join(args['cropping']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method+'_'+f"{int(args['binarization']['fixed_threshold']*10)}")
        eval_output_path = os.path.join(args['evaluation']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method+'_'+f"{int(args['binarization']['fixed_threshold']*10)}")
    else:
        crop_output_path = os.path.join(args['cropping']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method)
        eval_output_path = os.path.join(args['evaluation']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method)
    
    os.makedirs(eval_output_path, exist_ok=True)
    
    # Define the paths for predicted and ground truth JSON files
    pred_json_path = os.path.join(crop_output_path)
    gt_json_path = os.path.join(args['cropping']['output_path'], args['dataset']['dataset_name'], 'GT_crop')

    # Check if the ground truth JSON path exists; if not, perform cropping with ground truth
    if not os.path.exists(gt_json_path):
        args['cropping']['gt_crop'] = True
        mvtec_crop(args)
    
    TP_list, FP_list, FN_list = [], [], []
    FPR_list, FNR_list = [], []

    # Iterate through each class in the MVTec dataset
    for class_name in mvtec_class_names:
        class_TP, class_FP, class_FN = 0, 0, 0
        
        # Load the predicted and ground truth bounding boxes for the current class
        pred_dir = os.path.join(pred_json_path, class_name, 'crop_boxes.json')
        with open(pred_dir, 'r') as f:
            pred_boxes_dict = json.load(f)
        gt_dir = os.path.join(gt_json_path, class_name, 'crop_boxes.json')
        with open(gt_dir, 'r') as f:
            gt_boxes_dict = json.load(f)
        
        # Get the list of anomaly types for the current class
        ano_type_list = os.listdir(os.path.join(pred_json_path, class_name))
        ano_type_list = [ano_type for ano_type in ano_type_list if 'json' not in ano_type]
        
        if 'combined' in ano_type_list:
            ano_type_list.remove('combined')
        
        # Iterate through each anomaly type for the current class
        for ano_type in ano_type_list:
            # Get the predicted and ground truth boxes for the current anomaly type
            ano_type_pred_boxes = pred_boxes_dict[ano_type]
            ano_type_gt_boxes = gt_boxes_dict[ano_type]
            
            # Evaluate the region-level performance for the current anomaly type
            ano_type_TP, ano_type_FP, ano_type_FN = evaluate_region_level(ano_type_pred_boxes, ano_type_gt_boxes, ano_type)

            # Accumulate TP, FP, and FN for the current class
            class_TP += ano_type_TP
            class_FP += ano_type_FP
            class_FN += ano_type_FN
            
        class_FPR = class_FP / (class_TP + class_FP) if class_TP + class_FP > 0 else 0
        class_FNR = class_FN / (class_TP + class_FN) if class_TP + class_FN > 0 else 0
            
        TP_list.append(class_TP)
        FP_list.append(class_FP)
        FN_list.append(class_FN)
        FPR_list.append(class_FPR)
        FNR_list.append(class_FNR)
        
    TP_avg = sum(TP_list)/len(TP_list)
    FP_avg = sum(FP_list)/len(FP_list)
    FN_avg = sum(FN_list)/len(FN_list)
    FPR_avg = sum(FPR_list)/len(FPR_list)
    FNR_avg = sum(FNR_list)/len(FNR_list)
    
    # Save the evaluation results to a CSV file
    csv_file_path = os.path.join(eval_output_path, 'results.csv')
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['class_name', 'TP', 'FP', 'FN', 'FPR', 'FNR'])
        for i, class_name in enumerate(mvtec_class_names):
            writer.writerow([class_name, TP_list[i], FP_list[i], FN_list[i], round(FPR_list[i], 3), round(FNR_list[i], 3)]) 
        writer.writerow(['Average', round(TP_avg, 3), round(FP_avg, 3), round(FN_avg, 3), round(FPR_avg, 3), round(FNR_avg, 3)])
    