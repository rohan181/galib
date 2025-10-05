"""
rides.py
Ride classes for Adventure World theme park simulation.
"""

import math
import matplotlib.patches as patches
from abc import ABC, abstractmethod
from collections import deque
from config import RideState, PatronState, DEFAULT_LOADING_TIME, DEFAULT_UNLOAD_TIME


class Ride(ABC):
    """
    Abstract base class for all theme park rides.
    Defines common attributes and methods that all rides must implement.
    """
    
    def __init__(self, name, x, y, width, height, capacity, duration):
        """
        Initialize a ride.
        
        Parameters:
            name (str): Name of the ride
            x (float): X-coordinate of ride center
            y (float): Y-coordinate of ride center
            width (float): Width of ride bounding box
            height (float): Height of ride bounding box
            capacity (int): Maximum number of patrons per cycle
            duration (int): Duration of ride in timesteps
        """
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
        
    def get_bounding_box(self):
        """
        Get the bounding box of the ride.
        
        Returns:
            tuple: (x_min, y_min, x_max, y_max)
        """
        x_min = self.x - self.width / 2
        y_min = self.y - self.height / 2
        x_max = self.x + self.width / 2
        y_max = self.y + self.height / 2
        return (x_min, y_min, x_max, y_max)
    
    def overlaps_with(self, other_ride):
        """
        Check if this ride overlaps with another ride.
        
        Parameters:
            other_ride (Ride): Another ride to check against
            
        Returns:
            bool: True if rides overlap, False otherwise
        """
        box1 = self.get_bounding_box()
        box2 = other_ride.get_bounding_box()
        
        return not (box1[2] < box2[0] or box1[0] > box2[2] or 
                   box1[3] < box2[1] or box1[1] > box2[3])
    
    def add_to_queue(self, patron):
        """
        Add a patron to the ride's queue.
        
        Parameters:
            patron (Patron): Patron to add to queue
        """
        self.queue.append(patron)
        patron.state = PatronState.QUEUING
    
    def load_patrons(self):
        """Load patrons from queue onto the ride up to capacity."""
        while len(self.riders) < self.capacity and len(self.queue) > 0:
            patron = self.queue.popleft()
            self.riders.append(patron)
            patron.state = PatronState.RIDING
    
    def unload_patrons(self):
        """Unload all patrons from the ride."""
        for patron in self.riders:
            patron.state = PatronState.ROAMING
        self.riders.clear()
    
    def step_change(self):
        """
        Update the ride's state for one timestep.
        Manages the ride's state machine.
        """
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
                
        elif self.state == RideState.UNLOADING:
            self.timer -= 1
            
            if self.timer <= 0:
                self.unload_patrons()
                self.state = RideState.IDLE
    
    @abstractmethod
    def update_movement(self):
        """Update the visual movement/animation of the ride."""
        pass
    
    @abstractmethod
    def plot(self, ax):
        """Plot the ride on matplotlib axes."""
        pass


class PirateShip(Ride):
    """A pirate ship ride that swings back and forth in an arc."""
    
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
        """Plot the pirate ship ride."""
        box = self.get_bounding_box()
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=2, edgecolor='brown', facecolor='wheat', alpha=0.3)
        ax.add_patch(rect)
        
        ship_length = 4
        end_x = self.x + ship_length * math.sin(self.angle)
        end_y = self.y + ship_length * math.cos(self.angle)
        
        ax.plot([self.x, end_x], [self.y, end_y], 'k-', linewidth=3)
        ax.plot(self.x, self.y, 'ro', markersize=8)
        
        ax.text(self.x, box[1] - 0.5, self.name, ha='center', fontsize=9, weight='bold')
        ax.text(self.x, box[3] + 0.3, f'Queue: {len(self.queue)}', ha='center', fontsize=7)


class FerrisWheel(Ride):
    """A Ferris wheel that rotates continuously."""
    
    def __init__(self, name, x, y, capacity=16, duration=30):
        super().__init__(name, x, y, width=10, height=10, capacity=capacity, duration=duration)
        self.angle = 0
        self.rotation_speed = 0.1
        self.radius = 4
        
    def update_movement(self):
        """Update the rotation."""
        if self.state == RideState.RUNNING:
            self.angle += self.rotation_speed
            if self.angle >= 2 * math.pi:
                self.angle -= 2 * math.pi
    
    def plot(self, ax):
        """Plot the Ferris wheel."""
        box = self.get_bounding_box()
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.2)
        ax.add_patch(rect)
        
        circle = patches.Circle((self.x, self.y), self.radius, 
                               fill=False, edgecolor='blue', linewidth=2)
        ax.add_patch(circle)
        
        num_spokes = 8
        for i in range(num_spokes):
            spoke_angle = self.angle + (2 * math.pi * i / num_spokes)
            spoke_x = self.x + self.radius * math.cos(spoke_angle)
            spoke_y = self.y + self.radius * math.sin(spoke_angle)
            ax.plot([self.x, spoke_x], [self.y, spoke_y], 'b-', linewidth=1, alpha=0.5)
        
        ax.plot(self.x, self.y, 'bo', markersize=6)
        
        ax.text(self.x, box[1] - 0.5, self.name, ha='center', fontsize=9, weight='bold')
        ax.text(self.x, box[3] + 0.3, f'Queue: {len(self.queue)}', ha='center', fontsize=7)


class SpiderRide(Ride):
    """A spider/hurricane ride that rotates with extending arms."""
    
    def __init__(self, name, x, y, capacity=12, duration=25):
        super().__init__(name, x, y, width=12, height=12, capacity=capacity, duration=duration)
        self.angle = 0
        self.rotation_speed = 0.12
        self.arm_length = 4
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
        """Plot the spider ride."""
        box = self.get_bounding_box()
        rect = patches.Rectangle((box[0], box[1]), self.width, self.height,
                                 linewidth=2, edgecolor='red', facecolor='lightyellow', alpha=0.2)
        ax.add_patch(rect)
        
        num_arms = 6
        for i in range(num_arms):
            arm_angle = self.angle + (2 * math.pi * i / num_arms)
            current_length = self.arm_length * (0.5 + 0.5 * self.arm_extension)
            arm_x = self.x + current_length * math.cos(arm_angle)
            arm_y = self.y + current_length * math.sin(arm_angle)
            ax.plot([self.x, arm_x], [self.y, arm_y], 'r-', linewidth=2)
            ax.plot(arm_x, arm_y, 'ro', markersize=6)
        
        ax.plot(self.x, self.y, 'ko', markersize=8)
        
        ax.text(self.x, box[1] - 0.5, self.name, ha='center', fontsize=9, weight='bold')
        ax.text(self.x, box[3] + 0.3, f'Queue: {len(self.queue)}', ha='center', fontsize=7)