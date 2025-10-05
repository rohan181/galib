"""
patron.py
Enhanced Patron class with improved visualization for Adventure World.
"""

import math
import random
from config import PatronState, DEFAULT_PATRON_MOVE_SPEED, DEFAULT_PATRON_IMMOBILE_TIME
from config import COLOR_ROAMING, COLOR_EXITING


class Patron:
    """Represents a visitor to the theme park."""
    
    def __init__(self, patron_id, x, y, name=None):
        """
        Initialize a patron.
        
        Parameters:
            patron_id (int): Unique identifier
            x (float): Starting x-coordinate
            y (float): Starting y-coordinate
            name (str): Optional name for the patron
        """
        self.id = patron_id
        self.name = name if name else f"Patron_{patron_id}"
        self.x = x
        self.y = y
        self.state = PatronState.ROAMING
        self.target_ride = None
        self.immobile_timer = DEFAULT_PATRON_IMMOBILE_TIME
        self.move_speed = DEFAULT_PATRON_MOVE_SPEED
        
        # Track rides visited and desired visits
        self.rides_visited = 0
        self.desired_rides = random.randint(2, 5)
        
        # For visualization - track movement history
        self.path_history = [(x, y)]
        self.max_history = 20
        
        # Time tracking
        self.time_in_park = 0
        self.time_queuing = 0
        self.time_riding = 0
        
    def step_change(self, park):
        """
        Update patron behavior for one timestep.
        
        Parameters:
            park (Park): The park object containing rides and terrain
        """
        self.time_in_park += 1
        
        if self.state == PatronState.QUEUING:
            self.time_queuing += 1
        elif self.state == PatronState.RIDING:
            self.time_riding += 1
        
        if self.immobile_timer > 0:
            self.immobile_timer -= 1
            return
        
        if self.state == PatronState.ROAMING:
            self.roam(park)
        elif self.state == PatronState.QUEUING:
            pass  # Wait in queue
        elif self.state == PatronState.RIDING:
            pass  # Enjoying the ride
        elif self.state == PatronState.EXITING:
            self.move_to_exit(park)
        
        # Update path history for trail effect
        if self.state in [PatronState.ROAMING, PatronState.EXITING]:
            self.path_history.append((self.x, self.y))
            if len(self.path_history) > self.max_history:
                self.path_history.pop(0)
    
    def roam(self, park):
        """
        Random or directed movement while roaming.
        
        Parameters:
            park (Park): The park object
        """
        # Check if patron has visited enough rides
        if self.rides_visited >= self.desired_rides:
            if random.random() < 0.02:
                self.state = PatronState.EXITING
                return
        
        # Actively seek nearby rides
        nearest_ride = None
        nearest_distance = float('inf')
        
        for ride in park.rides:
            distance = math.sqrt((self.x - ride.x)**2 + (self.y - ride.y)**2)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_ride = ride
        
        # If very close to a ride, high chance to join queue
        if nearest_distance < 8:
            # Don't join if queue is too long
            if len(nearest_ride.queue) < nearest_ride.capacity * 3:
                if random.random() < 0.3:
                    nearest_ride.add_to_queue(self)
                    self.target_ride = nearest_ride
                    return
        
        # Move toward nearest ride or random walk
        if nearest_ride and random.random() < 0.6:
            dx = nearest_ride.x - self.x
            dy = nearest_ride.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            angle_to_ride = math.atan2(dy, dx)
            angle = angle_to_ride + random.uniform(-0.5, 0.5)
            
            new_x = self.x + self.move_speed * math.cos(angle)
            new_y = self.y + self.move_speed * math.sin(angle)
        else:
            angle = random.uniform(0, 2 * math.pi)
            new_x = self.x + self.move_speed * math.cos(angle)
            new_y = self.y + self.move_speed * math.sin(angle)
        
        if park.is_valid_position(new_x, new_y):
            self.x = new_x
            self.y = new_y
    
    def move_to_exit(self, park):
        """
        Move patron toward nearest exit.
        
        Parameters:
            park (Park): The park object
        """
        if len(park.exits) > 0:
            nearest_exit = min(park.exits, key=lambda e: 
                             math.sqrt((self.x - e[0])**2 + (self.y - e[1])**2))
            
            dx = nearest_exit[0] - self.x
            dy = nearest_exit[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 1:
                park.remove_patron(self)
            else:
                self.x += self.move_speed * dx / distance
                self.y += self.move_speed * dy / distance
    
    def plot(self, ax):
        """
        Plot the patron with enhanced visuals.
        
        Parameters:
            ax: Matplotlib axes object
        """
        # Plot movement trail (fading path)
        if len(self.path_history) > 1 and self.state == PatronState.ROAMING:
            for i in range(len(self.path_history) - 1):
                alpha = (i + 1) / len(self.path_history) * 0.3
                ax.plot([self.path_history[i][0], self.path_history[i+1][0]],
                       [self.path_history[i][1], self.path_history[i+1][1]],
                       'g-', alpha=alpha, linewidth=0.5)
        
        # Plot patron with state-specific appearance
        if self.state == PatronState.ROAMING:
            ax.plot(self.x, self.y, 'o', color='limegreen', markersize=6, 
                   markeredgecolor='darkgreen', markeredgewidth=1, label='Roaming')
        elif self.state == PatronState.EXITING:
            ax.plot(self.x, self.y, 's', color='orange', markersize=6,
                   markeredgecolor='darkorange', markeredgewidth=1, label='Exiting')
        elif self.state == PatronState.QUEUING:
            ax.plot(self.x, self.y, '^', color='dodgerblue', markersize=6,
                   markeredgecolor='navy', markeredgewidth=1, label='Queuing')
        elif self.state == PatronState.RIDING:
            ax.plot(self.x, self.y, '*', color='magenta', markersize=8,
                   markeredgecolor='purple', markeredgewidth=1, label='Riding')