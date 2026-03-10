# config.py

# Camera settings
CAMERA_ID = 0

# Mapping and Grid settings
GRID_SIZE = 50       # Assuming 50 cm or another unit depending on grid implementation
MAP_WIDTH = 200      # Example width for the occupancy grid
MAP_HEIGHT = 200     # Example height for the occupancy grid

# Navigation settings
SAFE_DISTANCE_THRESHOLD = 1.5  # meters
STOP_DISTANCE_THRESHOLD = 0.7  # meters

# Detection settings
OBJECT_CONFIDENCE_THRESHOLD = 0.5
YOLO_MODEL_NAME = "yolov8n.pt"  # Alternatively "yolov10n.pt"

# Voice settings
VOICE_RATE = 150
