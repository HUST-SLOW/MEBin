#!/bin/bash

# MEBin script
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state True \
        --binarization_method MEBin \
        --sample_rate 4 \
        --min_interval_len 4 \
        --erode True \
        --cropping_state True \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state True \
        --eval_output_path outputs/evaluation 

# MEBin only binarization
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state True \
        --binarization_method MEBin \
        --sample_rate 4 \
        --min_interval_len 4 \
        --erode True \
        --output_path outputs/binarization \
        --cropping_state False \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state False \
        --eval_output_path outputs/evaluation 

# MEBin only cropping
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state False \
        --binarization_method MEBin \
        --sample_rate 4 \
        --min_interval_len 4 \
        --erode True \
        --output_path outputs/binarization \
        --cropping_state True \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state False \
        --eval_output_path outputs/evaluation 

#MEBin only evaluation
python examples/MEBin_main.py \
        --dataset_path data/mvtec_anomaly_detection \
        --dataset_name mvtec_ad \
        --ad_method MuSc \
        --anomaly_map_path data/mvtec_ad/MuSc \
        --state False \
        --binarization_method MEBin \
        --sample_rate 4 \
        --min_interval_len 4 \
        --erode True \
        --output_path outputs/binarization \
        --cropping_state False \
        --gt_crop False \
        --crop_output_path outputs/cropping \
        --evaluation_state True \
        --eval_output_path outputs/evaluation 