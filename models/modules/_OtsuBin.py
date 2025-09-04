import cv2
import numpy as np
from tqdm import tqdm


class OtsuBin:
    def __init__(self, anomaly_map_path_list):
        '''
        Get the anomaly maps and the fixed threshold.
        
        Args:
            anomaly_map_path_list: The paths of the anomaly score images to be binarized.
        '''
        self.anomaly_map_path_list = anomaly_map_path_list
        self.anomaly_map_list = [cv2.imread(x, cv2.IMREAD_GRAYSCALE) for x in self.anomaly_map_path_list]

    def binarize_anomaly_maps(self):
        '''
        Binarize all images using Otsu's method.
        
        Returns:
            binarized_maps (list): a list of binarized images
            thresholds (list): a list of thresholds used for binarization
        '''
        binarized_maps = []
        thresholds = []
        for i, anomaly_map in enumerate(tqdm(self.anomaly_map_list)):
            _, bin_result = cv2.threshold(anomaly_map, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            binarized_maps.append(bin_result)
            thresholds.append(int(_))
            
        return binarized_maps, thresholds