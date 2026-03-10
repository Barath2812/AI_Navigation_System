import cv2
import torch
import numpy as np

class DepthEstimator:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load MiDaS Small model for real-time performance
        self.model_type = "MiDaS_small"  
        self.midas = torch.hub.load("intel-isl/MiDaS", self.model_type)
        self.midas.to(self.device)
        self.midas.eval()
        
        # Load transforms to resize and normalize the image
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        if self.model_type == "DPT_Large" or self.model_type == "DPT_Hybrid":
            self.transform = midas_transforms.dpt_transform
        else:
            self.transform = midas_transforms.small_transform

    def estimate_depth(self, frame):
        #Estimate depth for a given frame and return it as a numpy array.
        
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        input_batch = self.transform(img).to(self.device)
        
        with torch.no_grad():
            prediction = self.midas(input_batch)
            
            # Resize the prediction to match the original image resolution
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        # Convert to numpy array
        depth_map = prediction.cpu().numpy()
        return depth_map
