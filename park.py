

import random
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from patron import Patron
from config import DEFAULT_PARK_WIDTH, DEFAULT_PARK_HEIGHT, COLOR_ENTRANCE, COLOR_EXIT


class TerrainObject:
    """Represents obstacles and decorations in the park."""
    
    def __init__(self, x, y, width, height, object_type="obstacle"):
        """Initialize a terrain object."""
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
            rect = FancyBboxPatch((box[0], box[1]), self.width, self.height,
                                 boxstyle="round,pad=0.3",
                                 facecolor='forestgreen', edgecolor='darkgreen',
                                 linewidth=2, alpha=0.7, zorder=1)
            ax.add_patch(rect)
            for i in range(3):
                cx = self.x + random.uniform(-self.width/3, self.width/3)
                cy = self.y + random.uniform(-self.height/3, self.height/3)
                tree = Circle((cx, cy), 0.8, facecolor='green', 
                             edgecolor='darkgreen', linewidth=1, alpha=0.8)
                ax.add_patch(tree)
                
        elif self.type == "boundary":
            rect = Rectangle((box[0], box[1]), self.width, self.height,
                           facecolor='#696969', edgecolor='black',
                           linewidth=3, alpha=0.8, zorder=1)
            ax.add_patch(rect)
        
        elif self.type == "pathway":
            rect = Rectangle((box[0], box[1]), self.width, self.height,
                           facecolor='#f5deb3', edgecolor='#daa520',
                           linewidth=1, alpha=0.5, zorder=0)
            ax.add_patch(rect)


class Park:
    """PERFECT SPACING park - optimized for 1-6 rides."""
    
    def __init__(self, width=280, height=200):  # EVEN BIGGER for perfect spacing!
        """Initialize the park with extra large dimensions."""
        self.width = width
        self.height = height
        self.rides = []
        self.patrons = []
        self.terrain_objects = []
        
        # Entrances and exits at corners
        self.entrances = [
            (25, 25),
            (width - 25, 25),
            (width/2, 25)
        ]
        self.exits = [
            (25, height - 25),
            (width - 25, height - 25),
            (width/2, height - 25)
        ]
        
        self._setup_park()
    
    def _setup_park(self):
        """Setup park boundaries."""
        wall_thickness = 5
        self.terrain_objects.append(
            TerrainObject(self.width/2, wall_thickness/2, 
                         self.width, wall_thickness, "boundary"))
        self.terrain_objects.append(
            TerrainObject(self.width/2, self.height - wall_thickness/2, 
                         self.width, wall_thickness, "boundary"))
        self.terrain_objects.append(
            TerrainObject(wall_thickness/2, self.height/2, 
                         wall_thickness, self.height, "boundary"))
        self.terrain_objects.append(
            TerrainObject(self.width - wall_thickness/2, self.height/2, 
                         wall_thickness, self.height, "boundary"))
    
    def get_optimal_ride_positions(self, num_rides):
        """
        Calculate PERFECT positions for 1-6 rides with NO overlaps.
        
        Parameters:
            num_rides (int): Number of rides (1-6)
            
        Returns:
            list: List of (x, y) positions
        """
        positions = []
        
        if num_rides == 1:
            # Single ride in center
            positions = [(self.width/2, self.height/2)]
            
        elif num_rides == 2:
            # Two rides side by side with huge spacing
            positions = [
                (self.width * 0.3, self.height/2),
                (self.width * 0.7, self.height/2)
            ]
            
        elif num_rides == 3:
            # Triangle formation
            positions = [
                (self.width/2, self.height * 0.35),
                (self.width * 0.3, self.height * 0.65),
                (self.width * 0.7, self.height * 0.65)
            ]
            
        elif num_rides == 4:
            # Square formation
            positions = [
                (self.width * 0.3, self.height * 0.35),
                (self.width * 0.7, self.height * 0.35),
                (self.width * 0.3, self.height * 0.65),
                (self.width * 0.7, self.height * 0.65)
            ]
            
        elif num_rides == 5:
            # Pentagon-like formation
            positions = [
                (self.width * 0.25, self.height * 0.3),
                (self.width * 0.75, self.height * 0.3),
                (self.width * 0.25, self.height * 0.7),
                (self.width * 0.75, self.height * 0.7),
                (self.width * 0.5, self.height * 0.5)
            ]
            
        elif num_rides == 6:
            # 2 rows of 3
            positions = [
                (self.width * 0.25, self.height * 0.35),
                (self.width * 0.5, self.height * 0.35),
                (self.width * 0.75, self.height * 0.35),
                (self.width * 0.25, self.height * 0.65),
                (self.width * 0.5, self.height * 0.65),
                (self.width * 0.75, self.height * 0.65)
            ]
        
        else:
            # For more than 6, use grid
            cols = 3
            rows = math.ceil(num_rides / cols)
            margin = 40
            x_spacing = (self.width - 2*margin) / (cols + 1)
            y_spacing = (self.height - 2*margin) / (rows + 1)
            
            for i in range(num_rides):
                col = i % cols
                row = i // cols
                x = margin + (col + 1) * x_spacing
                y = margin + (row + 1) * y_spacing
                positions.append((x, y))
        
        return positions[:num_rides]
    
    def add_ride(self, ride):
        """Add a ride to the park if it doesn't overlap."""
        for existing_ride in self.rides:
            if ride.overlaps_with(existing_ride):
                print(f"⚠ Cannot add {ride.name}: overlaps with {existing_ride.name}")
                return False
        
        self.rides.append(ride)
        print(f"✓ Added {ride.name} at ({ride.x:.1f}, {ride.y:.1f})")
        return True
    
    def add_patron(self, patron):
        """Add a patron to the park."""
        self.patrons.append(patron)
    
    def remove_patron(self, patron):
        """Remove a patron from the park."""
        if patron in self.patrons:
            self.patrons.remove(patron)
    
    def spawn_patron(self, patron_id):
        """Spawn a new patron at a random entrance."""
        entrance = random.choice(self.entrances)
        x = entrance[0] + random.uniform(-2, 2)
        y = entrance[1] + random.uniform(-2, 2)
        patron = Patron(patron_id, x, y)
        self.add_patron(patron)
        return patron
    
    def is_valid_position(self, x, y):
        """Check if a position is valid for patron movement."""
        if x < 12 or x > self.width - 12 or y < 12 or y > self.height - 12:
            return False
        
        for obj in self.terrain_objects:
            if obj.type != "pathway" and obj.contains_point(x, y):
                return False
        
        for ride in self.rides:
            box = ride.get_bounding_box()
            buffer = 2
            if (box[0] - buffer <= x <= box[2] + buffer and 
                box[1] - buffer <= y <= box[3] + buffer):
                return False
        
        return True
    
    def add_terrain_object(self, terrain_obj):
        """Add a terrain object to the park."""
        self.terrain_objects.append(terrain_obj)
    
    def plot(self, ax):
        """Plot the park with PERFECT spacing and NO overlaps."""
        ax.clear()
        ax.set_xlim(-20, self.width + 20)
        ax.set_ylim(-20, self.height + 20)
        ax.set_aspect('equal')
        
        # Beautiful background
        ax.set_facecolor('#e8f5e9')
        
        # Minimal grass texture
        for i in range(0, int(self.width), 20):
            for j in range(0, int(self.height), 20):
                if random.random() < 0.2:
                    ax.plot(i, j, '.', color='#81c784', 
                           markersize=1.5, alpha=0.3)
        
        # Plot terrain
        for obj in self.terrain_objects:
            obj.plot(ax)
        
        # Plot entrances
        for i, entrance in enumerate(self.entrances):
            platform = FancyBboxPatch(
                (entrance[0] - 4, entrance[1] - 4), 8, 8,
                boxstyle="round,pad=0.4",
                facecolor='lightgreen', edgecolor='green',
                linewidth=3, alpha=0.8, zorder=2)
            ax.add_patch(platform)
            
            ax.plot(entrance[0], entrance[1], COLOR_ENTRANCE, 
                   markersize=24, label='Entrance' if i == 0 else '', 
                   zorder=10)
            
            ax.text(entrance[0], entrance[1] - 7, '⬇ ENTER', 
                   ha='center', fontsize=13, weight='bold',
                   color='white',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='green', 
                            edgecolor='darkgreen', linewidth=3, alpha=0.95),
                   zorder=10)
        
        # Plot exits
        for i, exit_point in enumerate(self.exits):
            platform = FancyBboxPatch(
                (exit_point[0] - 4, exit_point[1] - 4), 8, 8,
                boxstyle="round,pad=0.4",
                facecolor='lightcoral', edgecolor='red',
                linewidth=3, alpha=0.8, zorder=2)
            ax.add_patch(platform)
            
            ax.plot(exit_point[0], exit_point[1], COLOR_EXIT, 
                   markersize=24, label='Exit' if i == 0 else '', 
                   zorder=10)
            
            ax.text(exit_point[0], exit_point[1] + 7, 'EXIT ⬆', 
                   ha='center', fontsize=13, weight='bold',
                   color='white',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='red', 
                            edgecolor='darkred', linewidth=3, alpha=0.95),
                   zorder=10)
        
        # Plot all rides (rides draw their own titles ABOVE them)
        for ride in self.rides:
            ride.plot(ax)
        
        # Plot all patrons
        for patron in self.patrons:
            patron.plot(ax)
        
        # Subtle grid
        ax.grid(True, alpha=0.12, linestyle=':', linewidth=0.5, color='gray')
        
        # Legend
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            ax.legend(by_label.values(), by_label.keys(), 
                     loc='upper right', fontsize=12, framealpha=0.95,
                     edgecolor='black', fancybox=True, shadow=True)
        
        # Park title at very top
        ax.text(self.width/2, self.height + 12, 
               '🎢 ADVENTURE WORLD THEME PARK 🎡', 
               ha='center', fontsize=18, weight='bold',
               bbox=dict(boxstyle='round,pad=0.7', facecolor='gold', 
                        edgecolor='black', linewidth=3.5, alpha=0.98),
               zorder=2000)
        
        # Stats at very bottom
        info_text = f'🎢 {len(self.rides)} Rides  |  👥 {len(self.patrons)} Visitors'
        ax.text(self.width/2, -12, info_text, ha='center',
               fontsize=13, weight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        alpha=0.95, edgecolor='black', linewidth=2.5),
               zorder=2000)