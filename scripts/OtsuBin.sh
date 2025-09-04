#!/bin/bash

# OtsuBin script
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state True \
        --binarization_method OtsuBin \
        --output_path outputs/binarization \
        --cropping_state True \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state True \
        --eval_output_path outputs/evaluation 

# OtsuBin only binarization
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state True \
        --binarization_method OtsuBin \
        --output_path outputs/binarization \
        --cropping_state False \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state False \
        --eval_output_path outputs/evaluation 

# OtsuBin only cropping
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state False \
        --binarization_method OtsuBin \
        --output_path outputs/binarization \
        --cropping_state True \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state False \
        --eval_output_path outputs/evaluation 

# OtsuBin only evaluation
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state False \
        --binarization_method OtsuBin \
        --output_path outputs/binarization \
        --cropping_state False \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state True \
        --eval_output_path outputs/evaluation 