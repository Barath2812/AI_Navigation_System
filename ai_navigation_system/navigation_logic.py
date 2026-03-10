import config

class NavigationSystem:
    def __init__(self):
        self.stop_threshold = config.STOP_DISTANCE_THRESHOLD
        self.safe_threshold = config.SAFE_DISTANCE_THRESHOLD

    def determine_direction(self, x_center, frame_width):
        """
        Determine if the object is on the left, center, or right of the frame.
        """
        if x_center < frame_width * 0.33:
            return "left"
        elif x_center < frame_width * 0.66:
            return "center"
        else:
            return "right"

    def determine_warning_message(self, label, distance, direction):
        """
        Return appropriate navigation instructions based on distance and direction.
        """
        if distance < 0:
            return None # Distance not available
            
        if distance < self.stop_threshold:
            return f"Stop. {label} is very close."
        elif distance < self.safe_threshold:
            if direction == "left":
                return f"{label} ahead on the left. Turn right."
            elif direction == "right":
                return f"{label} ahead on the right. Turn left."
            else:
                return f"{label} ahead in the center. Obstacle ahead."
        else:
            return "Path is safe. Move forward."
            
    def get_instruction(self, objects, frame_width):
        """
        Process detected objects and return an accumulated or highest-priority navigation instruction.
        Returns empty string if safe.
        """
        if not objects:
            return "Move forward."
            
        # Find closest object
        closest_obj = min([obj for obj in objects if obj.get('distance', float('inf')) > 0], 
                          key=lambda x: x.get('distance', float('inf')), default=None)
                          
        if closest_obj:
            x1, y1, x2, y2 = closest_obj['bounding_box']
            x_center = (x1 + x2) / 2
            direction = self.determine_direction(x_center, frame_width)
            distance = closest_obj.get('distance', -1)
            
            # Save for visualization
            closest_obj['direction'] = direction
            
            return self.determine_warning_message(closest_obj['label'], distance, direction)
            
        return "Move forward."
