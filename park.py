"""
park.py
Park and terrain management for Adventure World simulation.
"""

import random
import matplotlib.patches as patches
from patron import Patron
from config import DEFAULT_PARK_WIDTH, DEFAULT_PARK_HEIGHT, COLOR_ENTRANCE, COLOR_EXIT


class TerrainObject:
    """Represents obstacles and boundaries in the park."""
    
    def __init__(self, x, y, width, height, object_type="obstacle"):
        """
        Initialize a terrain object.
        
        Parameters:
            x (float): X-coordinate of center
            y (float): Y-coordinate of center
            width (float): Width of object
            height (float): Height of object
            object_type (str): Type of terrain object
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = object_type
    
    def get_bounding_box(self):
        """Get bounding box of terrain object."""
        x_min = self.x - self.width / 2
        y_min = self.y - self.height / 2
        x_max = self.x + self.width / 2
        y_max = self.y + self.height / 2
        return (x_min, y_min, x_max, y_max)
    
    def contains_point(self, x, y):
        """Check if a point is inside this terrain object."""
        box = self.get_bounding_box()
        return box[0] <= x <= box[2] and box[1] <= y <= box[3]
    
    def plot(self, ax):
        """Plot the terrain object."""
        box = self.get_bounding_box()
        color = 'gray' if self.type == "obstacle" else 'lightgreen'
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=1, edgecolor='black', 
                                 facecolor=color, alpha=0.5)
        ax.add_patch(rect)


class Park:
    """Manages the theme park environment."""
    
    def __init__(self, width=DEFAULT_PARK_WIDTH, height=DEFAULT_PARK_HEIGHT):
        """
        Initialize the park.
        
        Parameters:
            width (float): Width of park
            height (float): Height of park
        """
        self.width = width
        self.height = height
        self.rides = []
        self.patrons = []
        self.terrain_objects = []
        self.entrances = [(5, height/2), (width-5, height/2)]
        self.exits = [(5, height/2), (width-5, height/2)]
        
        self._add_boundaries()
    
    def _add_boundaries(self):
        """Add boundary walls around the park."""
        self.terrain_objects.append(TerrainObject(self.width/2, self.height - 1, 
                                                  self.width, 2, "boundary"))
        self.terrain_objects.append(TerrainObject(self.width/2, 1, 
                                                  self.width, 2, "boundary"))
        self.terrain_objects.append(TerrainObject(1, self.height/2, 
                                                  2, self.height, "boundary"))
        self.terrain_objects.append(TerrainObject(self.width - 1, self.height/2, 
                                                  2, self.height, "boundary"))
    
    def add_ride(self, ride):
        """
        Add a ride to the park if it doesn't overlap.
        
        Parameters:
            ride (Ride): Ride to add
            
        Returns:
            bool: True if added successfully, False if overlaps
        """
        for existing_ride in self.rides:
            if ride.overlaps_with(existing_ride):
                print(f"Cannot add {ride.name}: overlaps with {existing_ride.name}")
                return False
        
        self.rides.append(ride)
        return True
    
    def add_patron(self, patron):
        """Add a patron to the park."""
        self.patrons.append(patron)
    
    def remove_patron(self, patron):
        """Remove a patron from the park."""
        if patron in self.patrons:
            self.patrons.remove(patron)
    
    def spawn_patron(self, patron_id):
        """
        Spawn a new patron at a random entrance.
        
        Parameters:
            patron_id (int): ID for the new patron
            
        Returns:
            Patron: The newly created patron
        """
        entrance = random.choice(self.entrances)
        patron = Patron(patron_id, entrance[0], entrance[1])
        self.add_patron(patron)
        return patron
    
    def is_valid_position(self, x, y):
        """
        Check if a position is valid.
        
        Parameters:
            x (float): X-coordinate
            y (float): Y-coordinate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if x < 2 or x > self.width - 2 or y < 2 or y > self.height - 2:
            return False
        
        for obj in self.terrain_objects:
            if obj.contains_point(x, y):
                return False
        
        for ride in self.rides:
            box = ride.get_bounding_box()
            if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                return False
        
        return True
    
    def add_terrain_object(self, terrain_obj):
        """Add a terrain object to the park."""
        self.terrain_objects.append(terrain_obj)
    
    def plot(self, ax):
        """
        Plot the entire park.
        
        Parameters:
            ax: Matplotlib axes object
        """
        ax.clear()
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect('equal')
        ax.set_title('Adventure World Theme Park')
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        
        for obj in self.terrain_objects:
            obj.plot(ax)
        
        for entrance in self.entrances:
            ax.plot(entrance[0], entrance[1], COLOR_ENTRANCE, markersize=12, label='Entrance')
        for exit_point in self.exits:
            ax.plot(exit_point[0], exit_point[1], COLOR_EXIT, markersize=12, label='Exit')
        
        for ride in self.rides:
            ride.plot(ax)
        
        for patron in self.patrons:
            patron.plot(ax)
        
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8)