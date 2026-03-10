import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from object_detection import ObjectDetector
from depth_estimation import DepthEstimator
from navigation_logic import NavigationSystem

st.set_page_config(page_title="AI Navigation System", layout="wide")

st.title("AI Indoor Navigation System")
st.write("Live AI obstacle detection with navigation guidance")

# Load AI models once
@st.cache_resource
def load_models():
    detector = ObjectDetector()
    depth_estimator = DepthEstimator()
    nav = NavigationSystem()
    return detector, depth_estimator, nav

detector, depth_estimator, nav_system = load_models()


def estimate_distance(depth_map, x_center, y_center):
    try:
        depth_val = depth_map[int(y_center), int(x_center)]
        return min(1000/(depth_val+1e-6),10)
    except:
        return -1


class VideoProcessor(VideoProcessorBase):

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        h, w = img.shape[:2]

        objects = detector.detect(img)

        depth_map = depth_estimator.estimate_depth(img)

        for obj in objects:

            x1,y1,x2,y2 = obj["bounding_box"]

            cx = (x1+x2)/2
            cy = (y1+y2)/2

            distance = estimate_distance(depth_map,cx,cy)

            direction = nav_system.determine_direction(cx,w)

            label = obj["label"]

            text = f"{label} {direction} {distance:.2f}m"

            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)

            cv2.putText(img,text,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,(0,255,0),2)

        return img


webrtc_streamer(
    key="navigation-camera",
    video_processor_factory=VideoProcessor
)
