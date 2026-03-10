import cv2
import numpy as np
import config

from object_detection import ObjectDetector
from depth_estimation import DepthEstimator
from mapping import IndoorMap
from path_planning import AStarPlanner
from navigation_logic import NavigationSystem
from voice_system import VoiceSystem
from utils.visualization import draw_bounding_boxes

def estimate_distance(depth_map, x_center, y_center):
    """
    Estimate valid distance based on the depth map value at the center of the object.
    Note: MiDaS provides inverse depth. This is a rough approximation for demonstration.
    """
    try:
        depth_val = depth_map[int(y_center), int(x_center)]
        if depth_val <= 0:
            return -1
        # Example conversion from relative disparity to approximate distance (meters)
        # Tuning this constant based on practical testing is required
        distance = 1000.0 / (depth_val + 1e-6)
        # Cap distance at a reasonable value like 10 meters
        return min(distance, 10.0)
    except IndexError:
        return -1

def main():
    print("Initializing AI Navigation System...")
    
    # Initialize components
    detector = ObjectDetector()
    depth_estimator = DepthEstimator()
    indoor_map = IndoorMap()
    planner = AStarPlanner(indoor_map)
    nav_system = NavigationSystem()
    voice = VoiceSystem()
    
    # Start webcam
    cap = cv2.VideoCapture(config.CAMERA_ID)
    if not cap.isOpened():
        print(f"Error: Could not open camera {config.CAMERA_ID}")
        return

    print("Starting navigation loop. Press ESC to exit.")
    voice.speak("System initialized. Starting navigation.")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error] Failed to read from camera.")
            break
            
        frame_count += 1
        frame_height, frame_width = frame.shape[:2]

        # 1. Detect Objects
        objects = detector.detect(frame)
        
        # 2. Compute Depth Map (run every few frames or resize to optimize if needed)
        depth_map = depth_estimator.estimate_depth(frame)
        
        # Clear map for moving obstacles (or implement specific decay logic)
        indoor_map.clear_map()

        # Process each detected obstacle
        for obj in objects:
            x1, y1, x2, y2 = obj['bounding_box']
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            
            # 3. Estimate Distance
            distance = estimate_distance(depth_map, x_center, y_center)
            obj['distance'] = distance
            
            # Additional detail for display
            obj['direction'] = nav_system.determine_direction(x_center, frame_width)

            # 4. Update Occupancy Grid
            # Map image coordinates to grid coordinates (simple scaling)
            grid_x = int((x_center / frame_width) * config.MAP_WIDTH)
            grid_y = int((y_center / frame_height) * config.MAP_HEIGHT)
            indoor_map.mark_obstacle(grid_x, grid_y)

        # 5. Compute Navigation Path
        # Example start (bottom center) and goal (top center)
        start_node = (config.MAP_WIDTH // 2, config.MAP_HEIGHT - 1)
        goal_node = (config.MAP_WIDTH // 2, 0)
        
        # Only compute A* path periodically to save CPU, or when obstacles change significantly
        if frame_count % 5 == 0:
            path = planner.search(start_node, goal_node)
            # You could visualize the path on a separate mini-map if needed

        # 6. Generate Navigation Instruction & 7. Trigger Voice
        instruction = nav_system.get_instruction(objects, frame_width)
        
        if instruction != "Move forward.":
             print(f"Navigation: {instruction}")
             
             # Optionally print detections to console
             for obj in objects:
                 if obj.get('distance', -1) > 0:
                     print(f"Detected: {obj['label']} {obj['direction']} {obj['distance']:.1f} meters")
                     
             voice.speak(instruction)

        # 8. Draw Bounding Boxes
        display_frame = draw_bounding_boxes(frame.copy(), objects, depth_map)

        # 9. Display
        cv2.imshow("AI Indoor Navigation System", display_frame)

        # Exit on ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("System shut down.")

if __name__ == "__main__":
    main()
