import heapq
import pygame
from settings import TILESIZE
from support import import_csv_layout

class Node:
    # A* node
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # cost from starting_point to current_node
        self.h = 0  # heuristic cost to tatget
        self.f = 0  # total_cost = g + h
    
    def __lt__(self, other):
        return self.f < other.f

class AStarPathfinder:
    def __init__(self, boundary_layout, obstacle_sprites):
        self.boundary_layout = boundary_layout
        self.obstacle_sprites = obstacle_sprites
        self.grid = None
        self.grid_width = 0
        self.grid_height = 0
        
    def setup_grid(self):
        # Calculate the grid size from the map size (assuming the map is a standard grid)
        if not self.boundary_layout:
            return
            
        layout = self.boundary_layout
        self.grid_height = len(layout)
        self.grid_width = len(layout[0]) if self.grid_height > 0 else 0
        
        # Initialize the grid
        self.grid = [[True for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Mark the boundary obstacles
        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                if col != '-1':  # Boundary barrier
                    self.grid[row_index][col_index] = False
        
        # Mark other obstacles
        if self.obstacle_sprites:
            for sprite in self.obstacle_sprites:
                if hasattr(sprite, 'rect'):
                    grid_x = sprite.rect.centerx // TILESIZE
                    grid_y = sprite.rect.centery // TILESIZE
                    if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                        self.grid[grid_y][grid_x] = False
    
    def world_to_grid(self, world_pos):
        "Convert world coordinates to grid coordinates"
        x, y = world_pos
        grid_x = int(x // TILESIZE)
        grid_y = int(y // TILESIZE)
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_pos):
        """Convert grid coordinates to world coordinates"""
        grid_x, grid_y = grid_pos
        world_x = grid_x * TILESIZE + TILESIZE // 2
        world_y = grid_y * TILESIZE + TILESIZE // 2
        return (world_x, world_y)
    
    def get_neighbors(self, node):
        "Obtain the adjacent nodes of the current node (8 directions)"
        x, y = node.position
        neighbors = []
        
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0),  # Top right bottom left
                     (-1, -1), (1, -1), (1, 1), (-1, 1)] # Diagonal
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Check whether it is within the grid range and passable
            if (0 <= new_x < self.grid_width and 
                0 <= new_y < self.grid_height and 
                self.grid[new_y][new_x]):
                
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def heuristic(self, a, b):
        """Heuristic Function (Manhattan Distance)"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path(self, start_world, target_world):
        """Search for the path from the starting point to the goal"""
        start = self.world_to_grid(start_world)
        target = self.world_to_grid(target_world)
        
        # If the starting or ending point is impassable, return to an empty path
        if (not self.grid or 
            not (0 <= start[0] < self.grid_width and 0 <= start[1] < self.grid_height) or
            not (0 <= target[0] < self.grid_width and 0 <= target[1] < self.grid_height)):
            return []
        
        if not self.grid[start[1]][start[0]] or not self.grid[target[1]][target[0]]:
            return []
        
        # Initialize the open list and the closed list
        open_list = []
        closed_list = set()
        
        # Create the starting node
        start_node = Node(start)
        start_node.g = 0
        start_node.h = self.heuristic(start, target)
        start_node.f = start_node.g + start_node.h
        
        heapq.heappush(open_list, (start_node.f, start_node))
        
        while open_list:
            # Obtain the current node
            current_f, current_node = heapq.heappop(open_list)
            current_pos = current_node.position
            
            # If the goal is reached, reconstruct the path
            if current_pos == target:
                path = []
                while current_node:
                    world_pos = self.grid_to_world(current_node.position)
                    path.append(world_pos)
                    current_node = current_node.parent
                return path[::-1]  # Reverse the path from the starting point to the end point
            
            # Add to the closed list
            closed_list.add(current_pos)
            
            # Check the neighbors
            for neighbor_pos in self.get_neighbors(current_node):
                if neighbor_pos in closed_list:
                    continue
                
                # Create neighbor nodes
                neighbor_node = Node(neighbor_pos, current_node)
                
                # Calculate the cost
                # Diagonal movement is more costly
                dx = abs(neighbor_pos[0] - current_pos[0])
                dy = abs(neighbor_pos[1] - current_pos[1])
                move_cost = 1.4 if dx == 1 and dy == 1 else 1.0
                
                neighbor_node.g = current_node.g + move_cost
                neighbor_node.h = self.heuristic(neighbor_pos, target)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                
                # Diagonal movement is more costly
                found = False
                for i, (f, node) in enumerate(open_list):
                    if node.position == neighbor_pos:
                        found = True
                        if neighbor_node.g < node.g:
                            open_list[i] = (neighbor_node.f, neighbor_node)
                            heapq.heapify(open_list)
                        break
                
                if not found:
                    heapq.heappush(open_list, (neighbor_node.f, neighbor_node))
        
        return []  # The path was not found.