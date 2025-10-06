"""
rides.py
Enhanced rides with FIXED title positioning and better visibility.
"""

import math
import random
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Wedge
from abc import ABC, abstractmethod
from collections import deque
from config import RideState, PatronState, DEFAULT_LOADING_TIME, DEFAULT_UNLOAD_TIME


class Ride(ABC):
    """Abstract base class for all theme park rides."""
    
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
        self.popularity_score = 0
        
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
        
        # Add buffer zone
        buffer = 5
        return not (box1[2] + buffer < box2[0] or box1[0] > box2[2] + buffer or 
                   box1[3] + buffer < box2[1] or box1[1] > box2[3] + buffer)
    
    def add_to_queue(self, patron):
        """Add a patron to the ride's queue."""
        self.queue.append(patron)
        patron.state = PatronState.QUEUING
        patron.target_ride = self
        self.popularity_score += 1
        
        # Position patron in curved queue
        queue_position = len(self.queue) - 1
        box = self.get_bounding_box()
        
        # Create organized queue formation
        queue_spacing = 1.8
        patrons_per_row = max(3, int(self.width / queue_spacing))
        row = queue_position // patrons_per_row
        col = queue_position % patrons_per_row
        
        # Center the queue
        row_offset = (patrons_per_row * queue_spacing - self.width) / 2
        patron.x = box[0] + col * queue_spacing + queue_spacing/2 - row_offset
        patron.y = box[1] - 3 - row * 1.5
    
    def load_patrons(self):
        """Load patrons from queue onto the ride."""
        while len(self.riders) < self.capacity and len(self.queue) > 0:
            patron = self.queue.popleft()
            self.riders.append(patron)
            patron.state = PatronState.RIDING
            
            # Position rider on the ride
            patron.x = self.x
            patron.y = self.y
    
    def unload_patrons(self):
        """Unload all patrons from the ride."""
        if len(self.riders) > 0:
            print(f"  🎢 {self.name} unloading {len(self.riders)} patrons")
        
        self.total_riders_served += len(self.riders)
        
        for patron in self.riders:
            patron.state = PatronState.ROAMING
            patron.mark_ride_completed(self)  # FIXED: Mark ride as completed
            patron.immobile_timer = random.randint(2, 5)
            
            # Scatter them around the exit
            box = self.get_bounding_box()
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(self.width/2 + 3, self.width/2 + 6)
            patron.x = self.x + radius * math.cos(angle)
            patron.y = self.y + radius * math.sin(angle)
            
        self.riders.clear()
    
    def step_change(self):
        """Update the ride's state machine."""
        if self.state == RideState.IDLE:
            if len(self.queue) > 0:
                self.state = RideState.LOADING
                self.timer = self.loading_time
                print(f"  🎢 {self.name} starting to LOAD (queue: {len(self.queue)})")
                
        elif self.state == RideState.LOADING:
            self.load_patrons()
            self.timer -= 1
            
            if self.timer <= 0:
                if len(self.riders) > 0:
                    self.state = RideState.RUNNING
                    self.timer = self.duration
                    print(f"  🎢 {self.name} RUNNING with {len(self.riders)} riders")
                else:
                    self.state = RideState.IDLE
                    
        elif self.state == RideState.RUNNING:
            self.update_movement()
            self.timer -= 1
            
            if self.timer <= 0:
                self.state = RideState.UNLOADING
                self.timer = self.unload_time
                self.total_cycles += 1
                print(f"  🎢 {self.name} starting to UNLOAD")
                
        elif self.state == RideState.UNLOADING:
            self.timer -= 1
            
            if self.timer <= 0:
                self.unload_patrons()
                self.state = RideState.IDLE
    
    def get_state_color(self):
        """Get color based on ride state."""
        colors = {
            RideState.IDLE: '#e0e0e0',
            RideState.LOADING: '#fff9c4',
            RideState.RUNNING: '#c8e6c9',
            RideState.UNLOADING: '#ffccbc'
        }
        return colors.get(self.state, 'white')
    
    @abstractmethod
    def update_movement(self):
        """Update the visual movement/animation of the ride."""
        pass
    
    @abstractmethod
    def plot(self, ax):
        """Plot the ride on matplotlib axes."""
        pass


class PirateShip(Ride):
    """A spectacular pirate ship ride."""
    
    def __init__(self, name, x, y, capacity=10, duration=20):
        super().__init__(name, x, y, width=12, height=10, capacity=capacity, duration=duration)
        self.angle = 0
        self.swing_speed = 0.18
        self.max_angle = math.pi / 2.8
        self.direction = 1
        
    def update_movement(self):
        """Update the swinging motion."""
        if self.state == RideState.RUNNING:
            self.angle += self.swing_speed * self.direction
            if abs(self.angle) >= self.max_angle:
                self.direction *= -1
    
    def plot(self, ax):
        """Plot the pirate ship with FIXED title positioning."""
        box = self.get_bounding_box()
        
        # Platform base
        platform = FancyBboxPatch((box[0], box[1]), self.width, 2.5,
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#8b4513', edgecolor='#654321',
                                 linewidth=2, zorder=2)
        ax.add_patch(platform)
        
        # Support pillars
        pillar_color = '#654321'
        ax.plot([self.x - 4, self.x - 4], [box[1], self.y], 
               color=pillar_color, linewidth=5, solid_capstyle='round', zorder=3)
        ax.plot([self.x + 4, self.x + 4], [box[1], self.y], 
               color=pillar_color, linewidth=5, solid_capstyle='round', zorder=3)
        
        # Ship arm with gradient effect
        ship_length = 7
        end_x = self.x + ship_length * math.sin(self.angle)
        end_y = self.y + ship_length * math.cos(self.angle)
        
        # Draw thick arm
        ax.plot([self.x, end_x], [self.y, end_y], 'k-', 
               linewidth=6, solid_capstyle='round', zorder=4)
        
        # Ship body (boat shape)
        ship_width = 4
        ship_height = 1.8
        ship_angle = self.angle
        
        # Create boat polygon
        bow_x = end_x + ship_width * math.cos(ship_angle + math.pi/2)
        bow_y = end_y + ship_width * math.sin(ship_angle + math.pi/2)
        stern_x = end_x + ship_width * math.cos(ship_angle - math.pi/2)
        stern_y = end_y + ship_width * math.sin(ship_angle - math.pi/2)
        
        # Draw ship hull
        ship_color = '#8b4513' if self.state == RideState.RUNNING else '#a0826d'
        ship = patches.Polygon([[bow_x, bow_y], [stern_x, stern_y], 
                               [end_x, end_y + ship_height]], 
                              facecolor=ship_color, edgecolor='#654321',
                              linewidth=2.5, zorder=5)
        ax.add_patch(ship)
        
        # Add sail decoration when running
        if self.state == RideState.RUNNING:
            sail_x = end_x - 1.5 * math.sin(self.angle)
            sail_y = end_y - 1.5 * math.cos(self.angle)
            ax.plot([end_x, sail_x], [end_y, sail_y + 2.5], 
                   'r-', linewidth=2.5, alpha=0.7, zorder=5)
        
        # Pivot point
        pivot = Circle((self.x, self.y), 0.7, 
                      facecolor='darkred', edgecolor='black', 
                      linewidth=2, zorder=6)
        ax.add_patch(pivot)
        
        # State glow effect
        glow_color = self.get_state_color()
        glow = Circle((self.x, self.y), self.width/1.4, 
                     facecolor=glow_color, alpha=0.3, zorder=1)
        ax.add_patch(glow)
        
        # FIXED TITLE - Always on top, positioned BELOW ride
        title_y = box[1] - 2.5  # Position below the ride
        title_box = FancyBboxPatch((self.x - 5.5, title_y - 0.6), 11, 1.2,
                                  boxstyle="round,pad=0.3",
                                  facecolor='wheat', edgecolor='brown',
                                  linewidth=2.5, alpha=0.95, zorder=100)  # HIGH Z-ORDER
        ax.add_patch(title_box)
        ax.text(self.x, title_y, self.name, ha='center', va='center',
               fontsize=12, weight='bold', color='#654321', zorder=101)
        
        # Status display ABOVE ride
        status = f'Queue: {len(self.queue)} | Riding: {len(self.riders)}/{self.capacity}'
        ax.text(self.x, box[3] + 1.5, status, ha='center', fontsize=10,
               bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                        edgecolor='brown', linewidth=2, alpha=0.95), zorder=100)


class FerrisWheel(Ride):
    """A majestic Ferris wheel."""
    
    def __init__(self, name, x, y, capacity=16, duration=30):
        super().__init__(name, x, y, width=14, height=14, capacity=capacity, duration=duration)
        self.angle = 0
        self.rotation_speed = 0.08
        self.radius = 6
        
    def update_movement(self):
        """Update the rotation."""
        if self.state == RideState.RUNNING:
            self.angle += self.rotation_speed
            if self.angle >= 2 * math.pi:
                self.angle -= 2 * math.pi
    
    def plot(self, ax):
        """Plot the Ferris wheel with FIXED title positioning."""
        box = self.get_bounding_box()
        
        # Base platform
        base = FancyBboxPatch((self.x - 2.5, box[1]), 5, 2,
                             boxstyle="round,pad=0.1",
                             facecolor='steelblue', edgecolor='navy',
                             linewidth=2.5, zorder=2)
        ax.add_patch(base)
        
        # State glow
        glow_color = self.get_state_color()
        glow = Circle((self.x, self.y), self.radius + 1.5, 
                     facecolor=glow_color, alpha=0.4, zorder=1)
        ax.add_patch(glow)
        
        # Main wheel frame
        wheel = Circle((self.x, self.y), self.radius, 
                      fill=False, edgecolor='steelblue', 
                      linewidth=5, zorder=3)
        ax.add_patch(wheel)
        
        # Inner support ring
        inner_ring = Circle((self.x, self.y), self.radius * 0.3, 
                           fill=False, edgecolor='navy', 
                           linewidth=2.5, zorder=4, linestyle='--')
        ax.add_patch(inner_ring)
        
        # Spokes and gondolas
        num_gondolas = 8
        for i in range(num_gondolas):
            spoke_angle = self.angle + (2 * math.pi * i / num_gondolas)
            
            # Spoke from center to outer rim
            spoke_x = self.x + self.radius * math.cos(spoke_angle)
            spoke_y = self.y + self.radius * math.sin(spoke_angle)
            ax.plot([self.x, spoke_x], [self.y, spoke_y], 
                   color='steelblue', linewidth=3, alpha=0.7, zorder=3)
            
            # Gondola position
            gondola_x = self.x + self.radius * 0.95 * math.cos(spoke_angle)
            gondola_y = self.y + self.radius * 0.95 * math.sin(spoke_angle)
            
            # Gondola appearance based on state
            if self.state == RideState.RUNNING:
                gondola_color = 'gold'
            else:
                gondola_color = 'lightblue'
            
            # Draw gondola as rectangle
            gondola_width = 1
            gondola_height = 0.8
            gondola = FancyBboxPatch(
                (gondola_x - gondola_width/2, gondola_y - gondola_height/2),
                gondola_width, gondola_height,
                boxstyle="round,pad=0.05",
                facecolor=gondola_color, edgecolor='navy',
                linewidth=2, zorder=5)
            ax.add_patch(gondola)
        
        # Center hub with decorative details
        hub = Circle((self.x, self.y), 0.8, 
                    facecolor='navy', edgecolor='gold', 
                    linewidth=3, zorder=6)
        ax.add_patch(hub)
        
        # Center star decoration
        ax.plot(self.x, self.y, '*', color='gold', 
               markersize=18, zorder=7)
        
        # FIXED TITLE - Always on top, positioned BELOW ride
        title_y = box[1] - 2.5
        title_box = FancyBboxPatch((self.x - 5.5, title_y - 0.6), 11, 1.2,
                                  boxstyle="round,pad=0.3",
                                  facecolor='lightblue', edgecolor='navy',
                                  linewidth=2.5, alpha=0.95, zorder=100)
        ax.add_patch(title_box)
        ax.text(self.x, title_y, self.name, ha='center', va='center',
               fontsize=12, weight='bold', color='navy', zorder=101)
        
        # Status ABOVE ride
        status = f'Queue: {len(self.queue)} | Riding: {len(self.riders)}/{self.capacity}'
        ax.text(self.x, box[3] + 1.5, status, ha='center', fontsize=10,
               bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                        edgecolor='steelblue', linewidth=2, alpha=0.95), zorder=100)


class SpiderRide(Ride):
    """An thrilling spider/octopus ride."""
    
    def __init__(self, name, x, y, capacity=12, duration=25):
        super().__init__(name, x, y, width=16, height=16, capacity=capacity, duration=duration)
        self.angle = 0
        self.rotation_speed = 0.15
        self.arm_length = 6.5
        self.arm_extension = 0
        self.extension_speed = 0.06
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
        """Plot the spider ride with FIXED title positioning."""
        box = self.get_bounding_box()
        
        # Base platform
        base = Circle((self.x, self.y), 2.5,
                     facecolor='darkred', edgecolor='black',
                     linewidth=2.5, zorder=2)
        ax.add_patch(base)
        
        # State glow
        glow_color = self.get_state_color()
        glow = Circle((self.x, self.y), self.width/2, 
                     facecolor=glow_color, alpha=0.3, zorder=1)
        ax.add_patch(glow)
        
        # Arms with gradient
        num_arms = 6
        for i in range(num_arms):
            arm_angle = self.angle + (2 * math.pi * i / num_arms)
            current_length = self.arm_length * (0.6 + 0.4 * self.arm_extension)
            
            # Draw arm with segments for 3D effect
            segments = 8
            for seg in range(segments):
                seg_ratio = seg / segments
                next_ratio = (seg + 1) / segments
                
                x1 = self.x + current_length * seg_ratio * math.cos(arm_angle)
                y1 = self.y + current_length * seg_ratio * math.sin(arm_angle)
                x2 = self.x + current_length * next_ratio * math.cos(arm_angle)
                y2 = self.y + current_length * next_ratio * math.sin(arm_angle)
                
                # Varying width and color
                width = 5 - seg_ratio * 2.5
                alpha = 0.5 + 0.5 * seg_ratio
                ax.plot([x1, x2], [y1, y2], color='red', 
                       linewidth=width, alpha=alpha, 
                       solid_capstyle='round', zorder=3)
            
            # End car with rotation indicator
            arm_x = self.x + current_length * math.cos(arm_angle)
            arm_y = self.y + current_length * math.sin(arm_angle)
            
            # Car color based on state
            if self.state == RideState.RUNNING:
                car_color = 'red'
                car_edge = 'darkred'
                car_size = 1.5
            else:
                car_color = 'pink'
                car_edge = 'red'
                car_size = 1.2
            
            # Draw car as circle with spin indicator
            car = Circle((arm_x, arm_y), car_size,
                        facecolor=car_color, edgecolor=car_edge,
                        linewidth=2.5, zorder=5)
            ax.add_patch(car)
            
            # Spin lines for effect
            if self.state == RideState.RUNNING:
                spin_angle = self.angle * 3
                for j in range(4):
                    line_angle = spin_angle + (math.pi / 2 * j)
                    lx = arm_x + 0.7 * math.cos(line_angle)
                    ly = arm_y + 0.7 * math.sin(line_angle)
                    ax.plot([arm_x, lx], [arm_y, ly], 
                           color='yellow', linewidth=2, alpha=0.8, zorder=6)
        
        # Central motor housing
        motor = Circle((self.x, self.y), 1.5,
                      facecolor='darkred', edgecolor='black',
                      linewidth=3, zorder=7)
        ax.add_patch(motor)
        
        # Center decoration
        ax.plot(self.x, self.y, 'o', color='yellow', 
               markersize=12, zorder=8)
        
        # FIXED TITLE - Always on top, positioned BELOW ride
        title_y = box[1] - 2.5
        title_box = FancyBboxPatch((self.x - 5.5, title_y - 0.6), 11, 1.2,
                                  boxstyle="round,pad=0.3",
                                  facecolor='mistyrose', edgecolor='darkred',
                                  linewidth=2.5, alpha=0.95, zorder=100)
        ax.add_patch(title_box)
        ax.text(self.x, title_y, self.name, ha='center', va='center',
               fontsize=12, weight='bold', color='darkred', zorder=101)
        
        # Status ABOVE ride
        status = f'Queue: {len(self.queue)} | Riding: {len(self.riders)}/{self.capacity}'
        ax.text(self.x, box[3] + 1.5, status, ha='center', fontsize=10,
               bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                        edgecolor='red', linewidth=2, alpha=0.95), zorder=100)