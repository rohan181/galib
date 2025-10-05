"""
patron.py
Patron class for Adventure World theme park simulation.
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
        
    def step_change(self, park):
        """
        Update patron behavior for one timestep.
        
        Parameters:
            park (Park): The park object containing rides and terrain
        """
        if self.immobile_timer > 0:
            self.immobile_timer -= 1
            return
        
        if self.state == PatronState.ROAMING:
            self.roam(park)
        elif self.state == PatronState.QUEUING:
            pass
        elif self.state == PatronState.RIDING:
            pass
        elif self.state == PatronState.EXITING:
            self.move_to_exit(park)
    
    def roam(self, park):
        """
        Random or directed movement while roaming.
        
        Parameters:
            park (Park): The park object
        """
        for ride in park.rides:
            distance = math.sqrt((self.x - ride.x)**2 + (self.y - ride.y)**2)
            if distance < 6:
                if random.random() < 0.1:
                    ride.add_to_queue(self)
                    return
        
        angle = random.uniform(0, 2 * math.pi)
        new_x = self.x + self.move_speed * math.cos(angle)
        new_y = self.y + self.move_speed * math.sin(angle)
        
        if park.is_valid_position(new_x, new_y):
            self.x = new_x
            self.y = new_y
        
        if random.random() < 0.005:
            self.state = PatronState.EXITING
    
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
        Plot the patron on matplotlib axes.
        
        Parameters:
            ax: Matplotlib axes object
        """
        if self.state in [PatronState.ROAMING, PatronState.EXITING]:
            color = COLOR_ROAMING if self.state == PatronState.ROAMING else COLOR_EXITING
            ax.plot(self.x, self.y, 'o', color=color, markersize=4)