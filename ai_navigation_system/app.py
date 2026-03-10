import streamlit as st
import cv2
import numpy as np

from object_detection import ObjectDetector
from depth_estimation import DepthEstimator
from navigation_logic import NavigationSystem

st.title("AI Indoor Navigation System")

@st.cache_resource
def load_models():
    detector = ObjectDetector()
    depth = DepthEstimator()
    nav = NavigationSystem()
    return detector, depth, nav

detector, depth_estimator, nav = load_models()

img_file = st.camera_input("Capture Image")

def estimate_distance(depth_map, x, y):
    try:
        d = depth_map[int(y), int(x)]
        return min(1000/(d+1e-6),10)
    except:
        return -1

if img_file:

    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes,1)

    h,w = frame.shape[:2]

    objects = detector.detect(frame)

    depth_map = depth_estimator.estimate_depth(frame)

    for obj in objects:

        x1,y1,x2,y2 = obj["bounding_box"]

        cx = (x1+x2)/2
        cy = (y1+y2)/2

        dist = estimate_distance(depth_map,cx,cy)

        direction = nav.determine_direction(cx,w)

        label = obj["label"]

        text = f"{label} {direction} {dist:.2f}m"

        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

        cv2.putText(frame,text,(x1,y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,(0,255,0),2)

    instruction = nav.get_instruction(objects,w)

    st.image(frame,channels="BGR")

    st.success(f"Navigation: {instruction}")
