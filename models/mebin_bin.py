import os
import json
import shutil
import cv2
import sys
sys.path.append(os.getcwd())

from models.modules._MEBin import MEBin
from models.modules._FixedThresholdBin import FixedThresholdBin
from models.modules._OtsuBin import OtsuBin

mvtec_class_names = ["bottle", "cable", "capsule", "carpet", "grid",
                    "hazelnut", "leather", "metal_nut", "pill", "screw",
                    "tile", "toothbrush", "transistor", "wood", "zipper"]

def mvtec_bin(args):
    '''
    Binarize anomaly maps for the MVTec dataset and save the results.
    This function processes each class in the MVTec dataset, binarizes the anomaly maps using the MEBin algorithm,
    and saves the binarized maps to the specified output path.
    
    Args:
        args (dict): Configuration arguments
    Returns:
        None
    '''
    
    bin_method = args['binarization']['binarization_method']
    anomaly_map_path = args['dataset']['anomaly_map_path']
    
    if bin_method == 'FixedThresholdBin':
        output_path = os.path.join(args['binarization']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method+'_'+f"{int(args['binarization']['fixed_threshold']*10)}")
    else:
        output_path = os.path.join(args['binarization']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method)
    
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)
    

    for class_name in mvtec_class_names:
        print(f'Binarizing {class_name}...')
        class_output_path = os.path.join(output_path, class_name)
        os.makedirs(class_output_path, exist_ok=True)
        
        # Collect anomaly map paths
        anomaly_map_path_list = []
        anomaly_num_list = []
        anomaly_types = sorted(os.listdir(os.path.join(anomaly_map_path, class_name)))
        
        for anomaly_type in anomaly_types:
            anomaly_type_anomaly_map_paths = sorted(os.listdir(os.path.join(anomaly_map_path, class_name, anomaly_type)))
            anomaly_map_path_list.extend([os.path.join(anomaly_map_path, class_name, anomaly_type, path) for path in anomaly_type_anomaly_map_paths])
            anomaly_num = len(anomaly_type_anomaly_map_paths)
            anomaly_num_list.append(anomaly_num)
        
        # instantiate the binarization method
        if bin_method == 'MEBin':
            bin = MEBin(anomaly_map_path_list, args['binarization']['sample_rate'], args['binarization']['min_interval_len'], args['binarization']['erode'])
        elif bin_method == 'FixedThresholdBin':
            bin = FixedThresholdBin(anomaly_map_path_list, args['binarization']['fixed_threshold'])
        elif bin_method == 'OtsuBin':
            bin = OtsuBin(anomaly_map_path_list)
        else:
            raise ValueError(f'The given binary method "{bin_method}" is not implemented, choose from ["MEBin","FixedThresholdBin","OtsuBin"]')

        # Use the selected binarization method to binarize the anomaly maps
        binarized_maps, threshold_list = bin.binarize_anomaly_maps()
        
        # Save the binarization result
        start = 0
        class_threshold_dict = {}
        for i, anomaly_type in enumerate(anomaly_types):
            anomaly_type_out_path = os.path.join(class_output_path, anomaly_type)
            os.makedirs(anomaly_type_out_path, exist_ok=True)
            end = start + anomaly_num_list[i]
            anomaly_type_binarized_maps = binarized_maps[start:end]
            anomaly_type_thresholds = threshold_list[start:end]
            
            # Iterate over the binarized maps and thresholds for the current anomaly type
            class_threshold_dict[anomaly_type] = {}
            for j, threshold in enumerate(anomaly_type_thresholds):
                map_name = os.path.basename(anomaly_map_path_list[start + j])
                class_threshold_dict[anomaly_type][map_name] = threshold
            
            # Save the binarized maps for the current anomaly type
            for j, binarized_map in enumerate(anomaly_type_binarized_maps):
                map_path = os.path.join(anomaly_type_out_path, os.path.basename(anomaly_map_path_list[start + j]))
                cv2.imwrite(map_path, binarized_map)
            
            start = end
        
        # Save the threshold information for the current class to a JSON file
        with open(os.path.join(class_output_path, 'threshold.json'), 'w') as f:
            json.dump(class_threshold_dict, f, indent=4)

    return
          
