import numpy as np
import cv2 
import matplotlib.pyplot as plt

np.random.seed(1)

"""
What type of data we need

rbg image
depth image
segmentation 

Record this into ROS bag for each timestamp


object detection output
"""

"""
Approach:

Drivable Space Estimation Using Semantic Segmentation Output
1.1 Estimating  x y z coord in scence of each pixel


1.2 - Estimating The Ground Plane Using RANSAC to outplay outliers
"""