"""
patron.py
FIXED: Smart Patron system with working exit behavior and personality types.
"""

import math
import random
from config import PatronState, DEFAULT_PATRON_MOVE_SPEED, DEFAULT_PATRON_IMMOBILE_TIME
from config import COLOR_ROAMING, COLOR_EXITING


class Patron:
    """Represents a visitor with intelligent ride-seeking behavior."""
    
    def __init__(self, patron_id, x, y, name=None, personality="balanced"):
        """Initialize a patron with personality-based behavior."""
        self.id = patron_id
        self.name = name if name else f"Patron_{patron_id}"
        self.x = x
        self.y = y
        self.state = PatronState.ROAMING
        self.target_ride = None
        self.immobile_timer = DEFAULT_PATRON_IMMOBILE_TIME
        
        # Personality system - NEW!
        self.personality = personality
        
        # Set attributes based on personality
        if personality == "thrill_seeker":
            self.desired_rides = random.randint(4, 6)  # Wants more rides
            self.move_speed = DEFAULT_PATRON_MOVE_SPEED * 1.3  # Faster movement
            self.patience = random.randint(15, 25)  # More patient in queues
        elif personality == "casual":
            self.desired_rides = random.randint(1, 3)  # Fewer rides
            self.move_speed = DEFAULT_PATRON_MOVE_SPEED * 0.8  # Slower movement
            self.patience = random.randint(3, 8)  # Less patient
        else:  # balanced
            self.desired_rides = random.randint(2, 4)
            self.move_speed = DEFAULT_PATRON_MOVE_SPEED + random.uniform(-0.1, 0.15)
            self.patience = random.randint(5, 15)
        
        # Smart visiting system
        self.visited_rides = set()  # Track which rides visited
        self.rides_completed = 0  # Counter for completed rides
        self.current_target = None  # Specific ride heading to
        
        # Path visualization
        self.path_history = [(x, y)]
        self.max_history = 30
        
        # Statistics
        self.time_in_park = 0
        self.time_queuing = 0
        self.time_riding = 0
        self.time_roaming = 0
        
        # Additional personality trait
        self.adventure_level = random.random()
        
    def step_change(self, park):
        """Update patron behavior for one timestep."""
        self.time_in_park += 1
        
        if self.state == PatronState.QUEUING:
            self.time_queuing += 1
        elif self.state == PatronState.RIDING:
            self.time_riding += 1
        elif self.state == PatronState.ROAMING:
            self.time_roaming += 1
        
        if self.immobile_timer > 0:
            self.immobile_timer -= 1
            return
        
        if self.state == PatronState.ROAMING:
            self.intelligent_roam(park)
        elif self.state == PatronState.QUEUING:
            self.check_queue_patience(park)
        elif self.state == PatronState.RIDING:
            pass  # Enjoying the ride
        elif self.state == PatronState.EXITING:
            self.move_to_exit(park)
        
        # Update path history
        if self.state in [PatronState.ROAMING, PatronState.EXITING]:
            self.path_history.append((self.x, self.y))
            if len(self.path_history) > self.max_history:
                self.path_history.pop(0)
    
    def intelligent_roam(self, park):
        """Smart roaming that visits all rides."""
        # FIXED: Check if completed enough rides and ready to exit
        if self.rides_completed >= self.desired_rides:
            # Exit chance varies by personality
            if self.personality == "thrill_seeker":
                exit_chance = 0.05  # Less likely to leave early
            elif self.personality == "casual":
                exit_chance = 0.12  # More likely to leave
            else:
                exit_chance = 0.08  # Balanced
            
            if random.random() < exit_chance:
                self.state = PatronState.EXITING
                self.current_target = None
                return
        
        # Find unvisited rides
        unvisited_rides = [r for r in park.rides if r not in self.visited_rides]
        
        # If no target, pick a new one
        if self.current_target is None or self.current_target in self.visited_rides:
            if unvisited_rides:
                # Prefer unvisited rides
                self.current_target = random.choice(unvisited_rides)
            elif park.rides:
                # If visited all, pick a favorite to revisit
                self.current_target = random.choice(park.rides)
        
        # Move toward current target
        if self.current_target:
            dx = self.current_target.x - self.x
            dy = self.current_target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            # If close enough, try to join queue
            if distance < 15:
                queue_size = len(self.current_target.queue)
                
                # Queue tolerance varies by personality
                if self.personality == "thrill_seeker":
                    max_acceptable_queue = self.current_target.capacity * 3
                elif self.personality == "casual":
                    max_acceptable_queue = self.current_target.capacity * 1.5
                else:
                    max_acceptable_queue = self.current_target.capacity * 2
                
                # More likely to join if haven't visited this ride
                join_chance = 0.5 if self.current_target not in self.visited_rides else 0.3
                
                if queue_size < max_acceptable_queue and random.random() < join_chance:
                    self.current_target.add_to_queue(self)
                    return
            
            # Calculate movement with some wandering
            if distance > 1:
                angle_to_target = math.atan2(dy, dx)
                wander = random.uniform(-0.3, 0.3)
                angle = angle_to_target + wander
                
                new_x = self.x + self.move_speed * math.cos(angle)
                new_y = self.y + self.move_speed * math.sin(angle)
                
                if park.is_valid_position(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                else:
                    # If blocked, try random direction
                    angle = random.uniform(0, 2 * math.pi)
                    new_x = self.x + self.move_speed * math.cos(angle)
                    new_y = self.y + self.move_speed * math.sin(angle)
                    if park.is_valid_position(new_x, new_y):
                        self.x = new_x
                        self.y = new_y
        else:
            # Random walk if no target
            angle = random.uniform(0, 2 * math.pi)
            new_x = self.x + self.move_speed * math.cos(angle)
            new_y = self.y + self.move_speed * math.sin(angle)
            
            if park.is_valid_position(new_x, new_y):
                self.x = new_x
                self.y = new_y
    
    def check_queue_patience(self, park):
        """Check if patron gets impatient in queue."""
        for ride in park.rides:
            if self in ride.queue:
                queue_position = list(ride.queue).index(self)
                if queue_position > self.patience and random.random() < 0.05:
                    ride.queue.remove(self)
                    self.state = PatronState.ROAMING
                    self.current_target = None
                break
    
    def mark_ride_completed(self, ride):
        """
        FIXED: Mark a ride as completed (called when unloading from ride).
        
        Parameters:
            ride: The ride that was just completed
        """
        self.visited_rides.add(ride)
        self.rides_completed += 1
        self.current_target = None  # Clear target to find new ride
        
        # Debug output
        if self.rides_completed == 1:
            print(f"  👤 Patron {self.id} ({self.personality}) completed first ride! ({self.rides_completed}/{self.desired_rides})")
    
    def move_to_exit(self, park):
        """Move patron toward nearest exit."""
        if len(park.exits) > 0:
            nearest_exit = min(park.exits, key=lambda e: 
                             math.sqrt((self.x - e[0])**2 + (self.y - e[1])**2))
            
            dx = nearest_exit[0] - self.x
            dy = nearest_exit[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 2:
                # Debug output
                print(f"  👋 Patron {self.id} ({self.personality}) exiting after {self.rides_completed} rides!")
                park.remove_patron(self)
            else:
                self.x += self.move_speed * dx / distance
                self.y += self.move_speed * dy / distance
    
    def plot(self, ax):
        """Plot the patron with enhanced visuals."""
        # Draw movement trail with gradient
        if len(self.path_history) > 1 and self.state == PatronState.ROAMING:
            for i in range(len(self.path_history) - 1):
                alpha = (i + 1) / len(self.path_history) * 0.4
                color = 'green' if self.current_target else 'gray'
                ax.plot([self.path_history[i][0], self.path_history[i+1][0]],
                       [self.path_history[i][1], self.path_history[i+1][1]],
                       color=color, alpha=alpha, linewidth=1)
        
        # Draw line to target ride
        if self.current_target and self.state == PatronState.ROAMING:
            ax.plot([self.x, self.current_target.x], [self.y, self.current_target.y],
                   'g--', alpha=0.2, linewidth=0.5)
        
        # Plot patron with state-specific appearance
        if self.state == PatronState.ROAMING:
            color = 'limegreen' if self.current_target else 'yellowgreen'
            ax.plot(self.x, self.y, 'o', color=color, markersize=7, 
                   markeredgecolor='darkgreen', markeredgewidth=1.5, 
                   label='Roaming', zorder=5)
            
        elif self.state == PatronState.EXITING:
            ax.plot(self.x, self.y, 's', color='orange', markersize=7,
                   markeredgecolor='darkorange', markeredgewidth=1.5, 
                   label='Exiting', zorder=5)
            
        elif self.state == PatronState.QUEUING:
            ax.plot(self.x, self.y, '^', color='dodgerblue', markersize=8,
                   markeredgecolor='navy', markeredgewidth=1.5, 
                   label='Queuing', zorder=5)
            
        elif self.state == PatronState.RIDING:
            ax.plot(self.x, self.y, '*', color='gold', markersize=12,
                   markeredgecolor='orange', markeredgewidth=2, 
                   label='Riding', zorder=5)
        
        # Show completed rides count as small number
        if self.state in [PatronState.ROAMING, PatronState.EXITING]:
            if self.rides_completed > 0:
                ax.text(self.x, self.y + 1.2, str(self.rides_completed), 
                       fontsize=7, ha='center', weight='bold',
                       color='white', 
                       bbox=dict(boxstyle='circle', facecolor='green', 
                                alpha=0.8, pad=0.2))