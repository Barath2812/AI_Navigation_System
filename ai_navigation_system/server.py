import cv2
import numpy as np
import base64
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

import config
from object_detection import ObjectDetector
from depth_estimation import DepthEstimator
from mapping import IndoorMap
from path_planning import AStarPlanner
from navigation_logic import NavigationSystem

app = FastAPI()

# Initialize components once
print("Loading AI Models...")
detector = ObjectDetector()
depth_estimator = DepthEstimator()
indoor_map = IndoorMap()
planner = AStarPlanner(indoor_map)
nav_system = NavigationSystem()

def estimate_distance(depth_map, x_center, y_center):
    """
    Estimate valid distance based on the depth map value at the center of the object.
    """
    try:
        depth_val = depth_map[int(y_center), int(x_center)]
        if depth_val <= 0:
            return -1
        distance = 1000.0 / (depth_val + 1e-6)
        return min(distance, 10.0)
    except IndexError:
        return -1

@app.websocket("/ws/navigate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected.")
    frame_count = 0
    try:
        while True:
            # Receive base64 encoded frame
            data = await websocket.receive_text()
            
            # Decode frame
            img_data = base64.b64decode(data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue

            frame_count += 1
            frame_height, frame_width = frame.shape[:2]

            # 1. Detect Objects
            objects = detector.detect(frame)
            
            # 2. Compute Depth Map
            depth_map = depth_estimator.estimate_depth(frame)
            
            indoor_map.clear_map()

            for obj in objects:
                x1, y1, x2, y2 = obj['bounding_box']
                x_center = (x1 + x2) / 2
                y_center = (y1 + y2) / 2
                
                # 3. Estimate Distance
                distance = estimate_distance(depth_map, x_center, y_center)
                obj['distance'] = distance
                obj['direction'] = nav_system.determine_direction(x_center, frame_width)

                # 4. Update Occupancy Grid
                grid_x = int((x_center / frame_width) * config.MAP_WIDTH)
                grid_y = int((y_center / frame_height) * config.MAP_HEIGHT)
                indoor_map.mark_obstacle(grid_x, grid_y)

            # 5. Compute Navigation Path
            start_node = (config.MAP_WIDTH // 2, config.MAP_HEIGHT - 1)
            goal_node = (config.MAP_WIDTH // 2, 0)
            
            if frame_count % 5 == 0:
                path = planner.search(start_node, goal_node)

            # 6. Generate Navigation Instruction
            instruction = nav_system.get_instruction(objects, frame_width)
            
            # Only send non-empty and non-default commands to avoid spamming TTS
            response = {
                 "instruction": instruction if instruction != "Move forward." else "",
            }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
