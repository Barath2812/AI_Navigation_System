import cv2
import config
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self):
        # Load the YOLO model (pre-trained)
        self.model = YOLO(config.YOLO_MODEL_NAME)
        self.confidence_threshold = config.OBJECT_CONFIDENCE_THRESHOLD

    def detect(self, frame):
        """
        Run detection on a frame and return list of objects with label, confidence, and bounding box.
        """
        results = self.model(frame, verbose=False)
        detected_objects = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = float(box.conf[0])
                if confidence >= self.confidence_threshold:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]

                    detected_objects.append({
                        'label': label,
                        'confidence': confidence,
                        'bounding_box': [x1, y1, x2, y2]
                    })
        
        return detected_objects
