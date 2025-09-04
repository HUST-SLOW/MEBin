import os
import json
from tqdm import tqdm
import sys
sys.path.append(os.getcwd())

from models.modules._crop import crop_sub_image_mask

mvtec_class_names = ["bottle", "cable", "capsule", "carpet", "grid",
                    "hazelnut", "leather", "metal_nut", "pill", "screw",
                    "tile", "toothbrush", "transistor", "wood", "zipper"]

def mvtec_crop(args):
    '''
    Crop images and their corresponding masks for the MVTec dataset and save the results.
    
    Args:
        args (dict): Configuration arguments
    Returns:
        None
    '''
    
    dataset_path = args['dataset']['dataset_path']
    
    if not args['cropping']['gt_crop']:
        bin_method = args['binarization']['binarization_method']
        if bin_method == 'FixedThresholdBin':
            bin_result_path = os.path.join(args['binarization']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method+'_'+f"{int(args['binarization']['fixed_threshold']*10)}")
            crop_output_path = os.path.join(args['cropping']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method+'_'+f"{int(args['binarization']['fixed_threshold']*10)}")
        else:
            bin_result_path = os.path.join(args['binarization']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method)
            crop_output_path = os.path.join(args['cropping']['output_path'], args['dataset']['dataset_name'], args['dataset']['ad_method'], bin_method)
            
    else:
        crop_output_path = os.path.join(args['cropping']['output_path'], args['dataset']['dataset_name'], 'GT_crop')
    
    # Iterate through each class in the MVTec dataset
    for class_name in mvtec_class_names:
        print(f'Cropping {class_name}...')
        class_output_path = os.path.join(crop_output_path, class_name)
        os.makedirs(class_output_path, exist_ok=True)
        
        # Collect image-mask paths
        image_path_list = []
        mask_path_list = []
        anomaly_num_list = []
        anomaly_types = sorted(os.listdir(os.path.join(dataset_path, class_name, 'test')))
        for anomaly_type in anomaly_types:
            anomaly_type_image_paths = sorted(os.listdir(os.path.join(dataset_path, class_name, 'test', anomaly_type)))
            image_path_list.extend([os.path.join(dataset_path, class_name, 'test', anomaly_type, path) for path in anomaly_type_image_paths])
            if args['cropping']['gt_crop']:
                if anomaly_type != 'good':
                    anomaly_type_mask_paths = sorted(os.listdir(os.path.join(dataset_path, class_name, 'ground_truth', anomaly_type)))
                    mask_path_list.extend([os.path.join(dataset_path, class_name, 'ground_truth', anomaly_type, path) for path in anomaly_type_mask_paths])
                else:
                    anomaly_type_mask_paths = [None]*len(anomaly_type_image_paths)
                    mask_path_list.extend([None]*len(anomaly_type_image_paths))
            else:
                anomaly_type_mask_paths = sorted(os.listdir(os.path.join(bin_result_path, class_name, anomaly_type)))
                mask_path_list.extend([os.path.join(bin_result_path, class_name, anomaly_type, path) for path in anomaly_type_mask_paths])
            assert len(anomaly_type_image_paths) == len(anomaly_type_mask_paths), f'Image and mask count mismatch in {class_name}/{anomaly_type}'
            anomaly_num = len(anomaly_type_image_paths)
            anomaly_num_list.append(anomaly_num)

        # Initialize a nested dictionary to store crop box information for the current class
        class_crop_boxes_dict = {}

        # Crop the images and masks
        start = 0
        for i, anomaly_type in enumerate(tqdm(anomaly_types)):
            anomaly_type_out_path = os.path.join(class_output_path, anomaly_type)
            os.makedirs(anomaly_type_out_path, exist_ok=True)
            os.makedirs(os.path.join(anomaly_type_out_path, 'image'), exist_ok=True)
            os.makedirs(os.path.join(anomaly_type_out_path, 'mask'), exist_ok=True)
            end = start + anomaly_num_list[i]
            anomaly_type_image_paths = image_path_list[start:end]
            anomaly_type_mask_paths = mask_path_list[start:end]
            
            # Initialize a dictionary to store crop box information for the current anomaly type
            class_crop_boxes_dict[anomaly_type] = {}
            
            for j, (image_path, mask_path) in enumerate(zip(anomaly_type_image_paths, anomaly_type_mask_paths)):
                cropped_images, cropped_masks, crop_boxes = crop_sub_image_mask(image_path, mask_path)
                image_name = os.path.basename(image_path)
                
                # Store crop box information for the current image
                class_crop_boxes_dict[anomaly_type][image_name] = crop_boxes
                
                for k, (cropped_image, cropped_mask) in enumerate(zip(cropped_images, cropped_masks)):
                    cropped_name = f"{image_name}_{k}.png"
                    cropped_image.save(os.path.join(anomaly_type_out_path, 'image', cropped_name))
                    cropped_mask.save(os.path.join(anomaly_type_out_path, 'mask', cropped_name))
            start = end
        
        # Save the crop box information for the current class to a JSON file
        with open(os.path.join(class_output_path, 'crop_boxes.json'), 'w') as f:
            json.dump(class_crop_boxes_dict, f, indent=4)
            
    return
            