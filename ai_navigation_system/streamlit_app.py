import streamlit as st
import cv2
import numpy as np

from object_detection import ObjectDetector
from depth_estimation import DepthEstimator
from navigation_logic import NavigationSystem
import config

st.title("AI Indoor Navigation System")

detector = ObjectDetector()
depth_estimator = DepthEstimator()
nav_system = NavigationSystem()

frame_placeholder = st.empty()
text_placeholder = st.empty()

camera = cv2.VideoCapture(0)

def estimate_distance(depth_map, x_center, y_center):
    try:
        depth_val = depth_map[int(y_center), int(x_center)]
        if depth_val <= 0:
            return -1
        distance = 1000.0 / (depth_val + 1e-6)
        return min(distance, 10.0)
    except:
        return -1

run = st.checkbox("Start Camera")

while run:
    
    ret, frame = camera.read()
    if not ret:
        st.error("Camera not working")
        break

    frame_height, frame_width = frame.shape[:2]

    objects = detector.detect(frame)

    depth_map = depth_estimator.estimate_depth(frame)

    for obj in objects:
        x1,y1,x2,y2 = obj['bounding_box']

        x_center = (x1+x2)/2
        y_center = (y1+y2)/2

        distance = estimate_distance(depth_map,x_center,y_center)

        direction = nav_system.determine_direction(x_center,frame_width)

        label = obj['label']

        text = f"{label} {direction} {distance:.2f}m"

        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

        cv2.putText(frame,text,(x1,y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,(0,255,0),2)

    instruction = nav_system.get_instruction(objects,frame_width)

    text_placeholder.write(f"Navigation: {instruction}")

    frame_placeholder.image(frame,channels="BGR")

camera.release()
