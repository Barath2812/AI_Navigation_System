import heapq
from mapping import IndoorMap

class AStarPlanner:
    def __init__(self, indoor_map: IndoorMap):
        self.map = indoor_map

    def heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(self, node):
        """Get valid empty neighbor cells."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-way movement
        # Optional: Add diagonals by adding (1,1), (-1,1), (1,-1), (-1,-1)
        
        result = []
        for dx, dy in directions:
            nx, ny = node[0] + dx, node[1] + dy
            if self.map.is_free(nx, ny):
                result.append((nx, ny))
        return result

    def search(self, start, goal):
        """
        A* Search algorithm.
        start: tuple (x, y)
        goal: tuple (x, y)
        Returns a list of tuples representing the path from start to goal, or [] if no path.
        """
        if not self.map.is_free(*start) or not self.map.is_free(*goal):
            return []

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for next_node in self.neighbors(current):
                new_cost = cost_so_far[current] + 1 # cost is 1 for straight movements
                
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(next_node, goal)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        # Reconstruct path
        path = []
        if goal in came_from:
            current = goal
            while current != start:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            
        return path
