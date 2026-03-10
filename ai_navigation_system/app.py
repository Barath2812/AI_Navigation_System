import streamlit as st
import cv2
import numpy as np

from object_detection import ObjectDetector
from depth_estimation import DepthEstimator
from navigation_logic import NavigationSystem

st.set_page_config(page_title="AI Navigation System", layout="wide")

st.title("AI Indoor Navigation System")
st.write("Upload an image or capture from webcam to detect obstacles and navigation instructions.")

# Initialize AI components
@st.cache_resource
def load_models():
    detector = ObjectDetector()
    depth_estimator = DepthEstimator()
    nav_system = NavigationSystem()
    return detector, depth_estimator, nav_system

detector, depth_estimator, nav_system = load_models()


def estimate_distance(depth_map, x_center, y_center):
    try:
        depth_val = depth_map[int(y_center), int(x_center)]
        if depth_val <= 0:
            return -1
        distance = 1000.0 / (depth_val + 1e-6)
        return min(distance, 10.0)
    except:
        return -1


# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    frame_height, frame_width = frame.shape[:2]

    st.subheader("Original Image")
    st.image(frame, channels="BGR")

    with st.spinner("Running AI navigation..."):

        # Detect objects
        objects = detector.detect(frame)

        # Estimate depth
        depth_map = depth_estimator.estimate_depth(frame)

        detected_info = []

        for obj in objects:

            x1, y1, x2, y2 = obj["bounding_box"]

            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2

            distance = estimate_distance(depth_map, x_center, y_center)

            direction = nav_system.determine_direction(x_center, frame_width)

            label = obj["label"]

            detected_info.append({
                "label": label,
                "distance": distance,
                "direction": direction
            })

            text = f"{label} {direction} {distance:.2f}m"

            cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame, text, (x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,(0,255,0),2)

        instruction = nav_system.get_instruction(objects, frame_width)

    st.subheader("Detection Result")
    st.image(frame, channels="BGR")

    st.subheader("Navigation Instruction")
    st.success(instruction)

    st.subheader("Detected Objects")

    if detected_info:
        for obj in detected_info:
            st.write(
                f"**{obj['label']}** → {obj['direction']} | {obj['distance']:.2f} meters"
            )
    else:
        st.write("No obstacles detected.")
