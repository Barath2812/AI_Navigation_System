import numpy as np
import config

class IndoorMap:
    def __init__(self):
        self.width = config.MAP_WIDTH
        self.height = config.MAP_HEIGHT
        self.grid = np.zeros((self.height, self.width), dtype=int)

    def clear_map(self):
        """Reset the map to all free space (0)."""
        self.grid.fill(0)

    def mark_obstacle(self, x, y):
        """Mark a specific cell as an obstacle (1)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = 1

    def is_free(self, x, y):
        """Check if a cell is free (0). True if free, False if out of bounds or obstacle."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 0
        return False
        
    def get_grid(self):
        """Return the internal occupancy grid array."""
        return self.grid
