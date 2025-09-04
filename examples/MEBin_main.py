import argparse
import os
import sys
sys.path.append(os.getcwd())

from models.mebin_bin import mvtec_bin
from models.mebin_crop import mvtec_crop  
from utils.mebin_eval import mvtec_eval


def get_args():
    """
    Parse command line arguments and return configuration dictionary.
    
    Returns:
        dict: Configuration arguments organized by category
    """
    parser = argparse.ArgumentParser(description='MEBin configuration')
    parser.add_argument('--config', type=str, default='./configs/MEBin.yaml', help='config file path')
    parser.add_argument('--dataset_path', type=str, default='data/mvtec_anomaly_detection', help='data path')
    parser.add_argument('--dataset_name', type=str, default='mvtec_ad', help='dataset name')
    parser.add_argument('--ad_method', type=str, default='MuSc', help='ad method')
    parser.add_argument('--anomaly_map_path', type=str, default='data/mvtec_ad/MuSc', help='anomaly map path')
    parser.add_argument('--state', type=str, default='True', help='binarization state')
    parser.add_argument('--binarization_method', type=str, default='MEBin', help='binarization method')
    parser.add_argument('--sample_rate', type=int, default=1, help='sample rate')
    parser.add_argument('--min_interval_len', type=int, default=16, help='min interval length')
    parser.add_argument('--erode', type=str, default='False', help='False')
    parser.add_argument('--fixed_threshold', type=float, default=0.5, help='fixed threshold')
    parser.add_argument('--output_path', type=str, default='outputs/binarization', help='binarization output path')
    parser.add_argument('--cropping_state', type=str, default='True', help='cropping state')
    parser.add_argument('--gt_crop', type=str, default='False', help='gt crop')
    parser.add_argument('--crop_output_path', type=str, default='outputs/cropping', help='cropping output path')
    parser.add_argument('--evaluation_state', type=str, default='True', help='evaluation state')
    parser.add_argument('--eval_output_path', type=str, default='outputs/evaluation', help='evaluation output path')
    cmd_args = parser.parse_args()
    
    config_args = {
        'dataset': {
            'dataset_name': cmd_args.dataset_name,
            'dataset_path': cmd_args.dataset_path,
            'ad_method': cmd_args.ad_method,
            'anomaly_map_path': cmd_args.anomaly_map_path
        },
        'binarization': {
            'state': cmd_args.state.lower() == 'true',
            'binarization_method': cmd_args.binarization_method,
            'sample_rate': cmd_args.sample_rate,
            'min_interval_len': cmd_args.min_interval_len,
            'erode': cmd_args.erode.lower() == 'true',
            'fixed_threshold': cmd_args.fixed_threshold,
            'output_path': cmd_args.output_path
        },
        'cropping': {
            'state': cmd_args.cropping_state.lower() == 'true',
            'gt_crop': cmd_args.gt_crop.lower() == 'true',
            'output_path': cmd_args.crop_output_path
        },
        'evaluation': {
            'state': cmd_args.evaluation_state.lower() == 'true',
            'output_path': cmd_args.eval_output_path
        }
    }
    
    return config_args

if __name__ == "__main__":
    
    args = get_args()
    print(args)
    
    dataset_name = args['dataset']['dataset_name']
    
    if args['binarization']['state']:
        if dataset_name == 'mvtec_ad':
            mvtec_bin(args)

    if args['cropping']['state']:
        if dataset_name == 'mvtec_ad':
            mvtec_crop(args)
          
    
    if args['evaluation']['state']:
        if dataset_name == 'mvtec_ad':
            mvtec_eval(args)



        