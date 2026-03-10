import cv2
import numpy as np

def draw_bounding_boxes(frame, objects, depth_map=None):

    #Draw bounding boxes, labels, direction, and distance for detected objects.
    #Optionally display depth heatmap overlay or separately if needed.
    
    for obj in objects:
        x1, y1, x2, y2 = obj['bounding_box']
        label = obj['label']
        confidence = obj['confidence']
        distance = obj.get('distance', -1)
        direction = obj.get('direction', 'unknown')

        # Draw bounding box
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw label, direction, and distance
        text = f"{label} {confidence:.2f} | {direction}"
        if distance != -1:
            text += f" | {distance:.2f}m"
            
        cv2.putText(frame, text, (x1, max(y1 - 10, 0)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return frame
