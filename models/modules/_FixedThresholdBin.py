import cv2
import numpy as np
from tqdm import tqdm


class FixedThresholdBin:
    def __init__(self, anomaly_map_path_list, threshold):
        '''
        Get the anomaly maps and the fixed threshold.
        
        Args:
            anomaly_map_path_list: The paths of the anomaly score images to be binarized.
            threshold: The fixed threshold for binarization.
        '''
        self.anomaly_map_path_list = anomaly_map_path_list
        self.anomaly_map_list = [cv2.imread(x, cv2.IMREAD_GRAYSCALE) for x in self.anomaly_map_path_list]
        self.threshold = threshold
            

    def binarize_anomaly_maps(self):
        '''
        Binarize all images using the fixed threshold.
        
        Returns:
            binarized_images (list): a list of binarized images
            thresholds (list): a list of thresholds used for binarization
        '''
        binarized_maps = []
        thresholds = []
        for i, anomaly_map in enumerate(tqdm(self.anomaly_map_list)):
            bin_result = np.where(anomaly_map >= self.threshold*255, 255, 0).astype(np.uint8)
            binarized_maps.append(bin_result)
            thresholds.append(int(self.threshold*255))
            
        return binarized_maps, thresholds