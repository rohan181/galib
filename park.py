"""
park.py
Enhanced Park with improved visualization for Adventure World.
"""

import random
import matplotlib.patches as patches
from patron import Patron
from config import DEFAULT_PARK_WIDTH, DEFAULT_PARK_HEIGHT, COLOR_ENTRANCE, COLOR_EXIT
from config import COLOR_OBSTACLE, COLOR_BOUNDARY


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
        """Plot the terrain object with enhanced visuals."""
        box = self.get_bounding_box()
        
        if self.type == "obstacle":
            # Obstacles as rocks/trees
            rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                     linewidth=2, edgecolor='darkgreen', 
                                     facecolor='forestgreen', alpha=0.6)
            ax.add_patch(rect)
            # Add texture with circles
            ax.plot(self.x, self.y, 'o', color='darkgreen', markersize=8)
            
        elif self.type == "boundary":
            # Boundaries as walls
            rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                     linewidth=3, edgecolor='black', 
                                     facecolor=COLOR_BOUNDARY, alpha=0.7,
                                     linestyle='-')
            ax.add_patch(rect)


class Park:
    """Manages the theme park environment with enhanced visualization."""
    
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
        # Top wall
        self.terrain_objects.append(TerrainObject(self.width/2, self.height - 1, 
                                                  self.width, 2, "boundary"))
        # Bottom wall
        self.terrain_objects.append(TerrainObject(self.width/2, 1, 
                                                  self.width, 2, "boundary"))
        # Left wall
        self.terrain_objects.append(TerrainObject(1, self.height/2, 
                                                  2, self.height, "boundary"))
        # Right wall
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
        Plot the entire park with enhanced visuals.
        
        Parameters:
            ax: Matplotlib axes object
        """
        ax.clear()
        ax.set_xlim(-2, self.width + 2)
        ax.set_ylim(-2, self.height + 2)
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f8f0')  # Light green background for park
        
        # Draw grass pattern (optional decorative element)
        for i in range(0, int(self.width), 10):
            for j in range(0, int(self.height), 10):
                ax.plot(i, j, '.', color='lightgreen', markersize=2, alpha=0.3)
        
        # Plot terrain objects (boundaries and obstacles)
        for obj in self.terrain_objects:
            obj.plot(ax)
        
        # Plot entrances with enhanced markers
        for i, entrance in enumerate(self.entrances):
            ax.plot(entrance[0], entrance[1], COLOR_ENTRANCE, markersize=15, 
                   label='Entrance' if i == 0 else '', zorder=10)
            # Add entrance label
            ax.text(entrance[0], entrance[1] + 2, 'ENTRANCE', ha='center',
                   fontsize=8, weight='bold', 
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        # Plot exits with enhanced markers
        for i, exit_point in enumerate(self.exits):
            ax.plot(exit_point[0], exit_point[1], COLOR_EXIT, markersize=15,
                   label='Exit' if i == 0 else '', zorder=10)
            # Add exit label
            ax.text(exit_point[0], exit_point[1] - 2, 'EXIT', ha='center',
                   fontsize=8, weight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        # Plot all rides
        for ride in self.rides:
            ride.plot(ax)
        
        # Plot all patrons
        for patron in self.patrons:
            patron.plot(ax)
        
        # Add grid for reference
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        
        # Create legend with unique labels only
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), 
                 loc='upper right', fontsize=9, framealpha=0.9)