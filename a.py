"""
rides.py
Enhanced Ride classes with improved visualization for Adventure World.
"""

import math
import matplotlib.patches as patches
from abc import ABC, abstractmethod
from collections import deque
from config import RideState, PatronState, DEFAULT_LOADING_TIME, DEFAULT_UNLOAD_TIME


class Ride(ABC):
    """
    Abstract base class for all theme park rides.
    """
    
    def __init__(self, name, x, y, width, height, capacity, duration):
        """Initialize a ride."""
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.capacity = capacity
        self.duration = duration
        
        self.state = RideState.IDLE
        self.queue = deque()
        self.riders = []
        self.timer = 0
        self.loading_time = DEFAULT_LOADING_TIME
        self.unload_time = DEFAULT_UNLOAD_TIME
        
        # Statistics
        self.total_riders_served = 0
        self.total_cycles = 0
        
    def get_bounding_box(self):
        """Get the bounding box of the ride."""
        x_min = self.x - self.width / 2
        y_min = self.y - self.height / 2
        x_max = self.x + self.width / 2
        y_max = self.y + self.height / 2
        return (x_min, y_min, x_max, y_max)
    
    def overlaps_with(self, other_ride):
        """Check if this ride overlaps with another ride."""
        box1 = self.get_bounding_box()
        box2 = other_ride.get_bounding_box()
        
        return not (box1[2] < box2[0] or box1[0] > box2[2] or 
                   box1[3] < box2[1] or box1[1] > box2[3])
    
    def add_to_queue(self, patron):
        """Add a patron to the ride's queue."""
        self.queue.append(patron)
        patron.state = PatronState.QUEUING
        patron.target_ride = self
        
        # Position patron in queue visually
        queue_position = len(self.queue) - 1
        box = self.get_bounding_box()
        
        # Create a curved queue line
        queue_spacing = 1.2
        patrons_per_row = max(1, int(self.width / queue_spacing))
        row = queue_position // patrons_per_row
        col = queue_position % patrons_per_row
        
        patron.x = box[0] + col * queue_spacing + 0.5
        patron.y = box[1] - 1.5 - row * queue_spacing
    
    def load_patrons(self):
        """Load patrons from queue onto the ride."""
        while len(self.riders) < self.capacity and len(self.queue) > 0:
            patron = self.queue.popleft()
            self.riders.append(patron)
            patron.state = PatronState.RIDING
            
            # Position rider on the ride
            rider_idx = len(self.riders) - 1
            patron.x = self.x
            patron.y = self.y
    
    def unload_patrons(self):
        """Unload all patrons from the ride."""
        self.total_riders_served += len(self.riders)
        
        for patron in self.riders:
            patron.state = PatronState.ROAMING
            patron.rides_visited += 1
            patron.immobile_timer = 3
            
            # Place them near the exit of the ride
            box = self.get_bounding_box()
            angle = random.uniform(0, 2 * math.pi)
            patron.x = self.x + (self.width/2 + 2) * math.cos(angle)
            patron.y = self.y + (self.height/2 + 2) * math.sin(angle)
            
        self.riders.clear()
    
    def step_change(self):
        """Update the ride's state for one timestep."""
        if self.state == RideState.IDLE:
            if len(self.queue) > 0:
                self.state = RideState.LOADING
                self.timer = self.loading_time
                
        elif self.state == RideState.LOADING:
            self.load_patrons()
            self.timer -= 1
            
            if self.timer <= 0 or len(self.riders) >= self.capacity:
                if len(self.riders) > 0:
                    self.state = RideState.RUNNING
                    self.timer = self.duration
                else:
                    self.state = RideState.IDLE
                    
        elif self.state == RideState.RUNNING:
            self.update_movement()
            self.timer -= 1
            
            if self.timer <= 0:
                self.state = RideState.UNLOADING
                self.timer = self.unload_time
                self.total_cycles += 1
                
        elif self.state == RideState.UNLOADING:
            self.timer -= 1
            
            if self.timer <= 0:
                self.unload_patrons()
                self.state = RideState.IDLE
    
    def get_state_color(self):
        """Get color based on ride state."""
        if self.state == RideState.IDLE:
            return 'lightgray'
        elif self.state == RideState.LOADING:
            return 'lightyellow'
        elif self.state == RideState.RUNNING:
            return 'lightgreen'
        elif self.state == RideState.UNLOADING:
            return 'lightcoral'
    
    @abstractmethod
    def update_movement(self):
        """Update the visual movement/animation of the ride."""
        pass
    
    @abstractmethod
    def plot(self, ax):
        """Plot the ride on matplotlib axes."""
        pass


class PirateShip(Ride):
    """A pirate ship ride that swings back and forth."""
    
    def __init__(self, name, x, y, capacity=10, duration=20):
        super().__init__(name, x, y, width=8, height=6, capacity=capacity, duration=duration)
        self.angle = 0
        self.swing_speed = 0.15
        self.max_angle = math.pi / 3
        self.direction = 1
        
    def update_movement(self):
        """Update the swinging motion."""
        if self.state == RideState.RUNNING:
            self.angle += self.swing_speed * self.direction
            
            if abs(self.angle) >= self.max_angle:
                self.direction *= -1
    
    def plot(self, ax):
        """Plot the pirate ship with enhanced visuals."""
        box = self.get_bounding_box()
        
        # Background box with state color
        state_color = self.get_state_color()
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=2, edgecolor='saddlebrown', 
                                 facecolor=state_color, alpha=0.6)
        ax.add_patch(rect)
        
        # Draw the ship
        ship_length = 5
        end_x = self.x + ship_length * math.sin(self.angle)
        end_y = self.y + ship_length * math.cos(self.angle)
        
        # Ship arm
        ax.plot([self.x, end_x], [self.y, end_y], 'k-', linewidth=4)
        
        # Ship body
        ship_width = 2
        ship_angle = self.angle + math.pi/2
        ship_x1 = end_x + ship_width * math.cos(ship_angle)
        ship_y1 = end_y + ship_width * math.sin(ship_angle)
        ship_x2 = end_x - ship_width * math.cos(ship_angle)
        ship_y2 = end_y - ship_width * math.sin(ship_angle)
        
        ax.fill([ship_x1, ship_x2, end_x], [ship_y1, ship_y2, end_y], 
               color='saddlebrown', alpha=0.8)
        
        # Pivot point
        ax.plot(self.x, self.y, 'o', color='darkred', markersize=10)
        
        # Labels
        ax.text(self.x, box[1] - 0.8, self.name, ha='center', 
               fontsize=10, weight='bold', bbox=dict(boxstyle='round', 
               facecolor='wheat', alpha=0.8))
        
        # Status info
        status = f'Q:{len(self.queue)} R:{len(self.riders)}/{self.capacity}'
        ax.text(self.x, box[3] + 0.5, status, ha='center', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        # State indicator
        ax.text(box[2] + 0.5, self.y, self.state.value.upper()[:3], 
               fontsize=7, rotation=90, va='center',
               bbox=dict(boxstyle='round', facecolor=state_color, alpha=0.9))


class FerrisWheel(Ride):
    """A Ferris wheel that rotates continuously."""
    
    def __init__(self, name, x, y, capacity=16, duration=30):
        super().__init__(name, x, y, width=10, height=10, capacity=capacity, duration=duration)
        self.angle = 0
        self.rotation_speed = 0.1
        self.radius = 4.5
        
    def update_movement(self):
        """Update the rotation."""
        if self.state == RideState.RUNNING:
            self.angle += self.rotation_speed
            if self.angle >= 2 * math.pi:
                self.angle -= 2 * math.pi
    
    def plot(self, ax):
        """Plot the Ferris wheel with enhanced visuals."""
        box = self.get_bounding_box()
        
        # Background
        state_color = self.get_state_color()
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=2, edgecolor='steelblue', 
                                 facecolor=state_color, alpha=0.4)
        ax.add_patch(rect)
        
        # Main wheel
        circle = patches.Circle((self.x, self.y), self.radius, 
                               fill=False, edgecolor='steelblue', linewidth=3)
        ax.add_patch(circle)
        
        # Spokes and gondolas
        num_gondolas = 8
        for i in range(num_gondolas):
            spoke_angle = self.angle + (2 * math.pi * i / num_gondolas)
            spoke_x = self.x + self.radius * math.cos(spoke_angle)
            spoke_y = self.y + self.radius * math.sin(spoke_angle)
            
            # Spoke
            ax.plot([self.x, spoke_x], [self.y, spoke_y], 'b-', 
                   linewidth=1.5, alpha=0.6)
            
            # Gondola
            gondola_color = 'gold' if self.state == RideState.RUNNING else 'lightblue'
            ax.plot(spoke_x, spoke_y, 's', color=gondola_color, 
                   markersize=8, markeredgecolor='navy', markeredgewidth=1)
        
        # Center hub
        ax.plot(self.x, self.y, 'o', color='navy', markersize=8)
        
        # Labels
        ax.text(self.x, box[1] - 0.8, self.name, ha='center', 
               fontsize=10, weight='bold', 
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        status = f'Q:{len(self.queue)} R:{len(self.riders)}/{self.capacity}'
        ax.text(self.x, box[3] + 0.5, status, ha='center', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        ax.text(box[2] + 0.5, self.y, self.state.value.upper()[:3], 
               fontsize=7, rotation=90, va='center',
               bbox=dict(boxstyle='round', facecolor=state_color, alpha=0.9))


class SpiderRide(Ride):
    """A spider/hurricane ride with rotating extending arms."""
    
    def __init__(self, name, x, y, capacity=12, duration=25):
        super().__init__(name, x, y, width=12, height=12, capacity=capacity, duration=duration)
        self.angle = 0
        self.rotation_speed = 0.12
        self.arm_length = 5
        self.arm_extension = 0
        self.extension_speed = 0.05
        self.extending = True
        
    def update_movement(self):
        """Update rotation and arm extension."""
        if self.state == RideState.RUNNING:
            self.angle += self.rotation_speed
            if self.angle >= 2 * math.pi:
                self.angle -= 2 * math.pi
            
            if self.extending:
                self.arm_extension += self.extension_speed
                if self.arm_extension >= 1.0:
                    self.arm_extension = 1.0
                    self.extending = False
            else:
                self.arm_extension -= self.extension_speed
                if self.arm_extension <= 0.0:
                    self.arm_extension = 0.0
                    self.extending = True
    
    def plot(self, ax):
        """Plot the spider ride with enhanced visuals."""
        box = self.get_bounding_box()
        
        # Background
        state_color = self.get_state_color()
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=2, edgecolor='crimson', 
                                 facecolor=state_color, alpha=0.3)
        ax.add_patch(rect)
        
        # Arms
        num_arms = 6
        for i in range(num_arms):
            arm_angle = self.angle + (2 * math.pi * i / num_arms)
            current_length = self.arm_length * (0.5 + 0.5 * self.arm_extension)
            
            # Arm gradient effect
            segments = 10
            for seg in range(segments):
                seg_start = (seg / segments) * current_length
                seg_end = ((seg + 1) / segments) * current_length
                
                x1 = self.x + seg_start * math.cos(arm_angle)
                y1 = self.y + seg_start * math.sin(arm_angle)
                x2 = self.x + seg_end * math.cos(arm_angle)
                y2 = self.y + seg_end * math.sin(arm_angle)
                
                alpha = 0.3 + 0.7 * (seg / segments)
                ax.plot([x1, x2], [y1, y2], 'r-', linewidth=3, alpha=alpha)
            
            # End car
            arm_x = self.x + current_length * math.cos(arm_angle)
            arm_y = self.y + current_length * math.sin(arm_angle)
            car_color = 'red' if self.state == RideState.RUNNING else 'pink'
            ax.plot(arm_x, arm_y, 'o', color=car_color, markersize=10,
                   markeredgecolor='darkred', markeredgewidth=2)
        
        # Center
        ax.plot(self.x, self.y, 'o', color='darkred', markersize=12)
        
        # Labels
        ax.text(self.x, box[1] - 0.8, self.name, ha='center', 
               fontsize=10, weight='bold',
               bbox=dict(boxstyle='round', facecolor='mistyrose', alpha=0.8))
        
        status = f'Q:{len(self.queue)} R:{len(self.riders)}/{self.capacity}'
        ax.text(self.x, box[3] + 0.5, status, ha='center', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        ax.text(box[2] + 0.5, self.y, self.state.value.upper()[:3], 
               fontsize=7, rotation=90, va='center',
               bbox=dict(boxstyle='round', facecolor=state_color, alpha=0.9))


import random  # Add this at the top with other imports