"""
simulation.py
Main simulation engine for Adventure World.
"""

import random
import matplotlib.pyplot as plt
from config import DEFAULT_MAX_TIMESTEPS, DEFAULT_SPAWN_RATE


class Simulation:
    """Main simulation engine that drives the theme park simulation."""
    
    def __init__(self, park, max_timesteps=DEFAULT_MAX_TIMESTEPS, spawn_rate=DEFAULT_SPAWN_RATE):
        """
        Initialize the simulation.
        
        Parameters:
            park (Park): The park to simulate
            max_timesteps (int): Maximum number of timesteps to run
            spawn_rate (float): Probability of spawning patron per timestep
        """
        self.park = park
        self.max_timesteps = max_timesteps
        self.spawn_rate = spawn_rate
        self.current_timestep = 0
        self.next_patron_id = 1
        
        self.total_patrons_spawned = 0
        self.total_patrons_exited = 0
    
    def step(self):
        """Execute one timestep of the simulation."""
        if random.random() < self.spawn_rate:
            self.park.spawn_patron(self.next_patron_id)
            self.next_patron_id += 1
            self.total_patrons_spawned += 1
        
        for patron in self.park.patrons[:]:
            patron.step_change(self.park)
        
        for ride in self.park.rides:
            ride.step_change()
        
        self.current_timestep += 1
    
    def run(self, interactive=False, plot_interval=5):
        """
        Run the simulation.
        
        Parameters:
            interactive (bool): If True, display animation
            plot_interval (int): Update plot every N timesteps
            
        Returns:
            dict: Simulation statistics
        """
        if interactive:
            plt.ion()
            fig, ax = plt.subplots(figsize=(12, 10))
        
        while self.current_timestep < self.max_timesteps:
            self.step()
            
            if interactive and self.current_timestep % plot_interval == 0:
                self.park.plot(ax)
                plt.pause(0.01)
            
            if self.current_timestep % 50 == 0:
                print(f"Timestep {self.current_timestep}: "
                      f"{len(self.park.patrons)} patrons in park, "
                      f"{self.total_patrons_spawned} total spawned")
        
        if interactive:
            plt.ioff()
            plt.show()
        
        return self.get_statistics()
    
    def get_statistics(self):
        """
        Get simulation statistics.
        
        Returns:
            dict: Dictionary of statistics
        """
        total_queue_length = sum(len(ride.queue) for ride in self.park.rides)
        avg_queue_length = total_queue_length / len(self.park.rides) if self.park.rides else 0
        
        return {
            'timesteps': self.current_timestep,
            'total_spawned': self.total_patrons_spawned,
            'remaining_patrons': len(self.park.patrons),
            'total_rides': len(self.park.rides),
            'avg_queue_length': avg_queue_length,
            'total_queue_length': total_queue_length
        }
    
    def print_statistics(self):
        """Print final simulation statistics."""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("SIMULATION COMPLETE")
        print("="*50)
        print(f"Total timesteps: {stats['timesteps']}")
        print(f"Total patrons spawned: {stats['total_spawned']}")
        print(f"Patrons remaining in park: {stats['remaining_patrons']}")
        print(f"Total rides: {stats['total_rides']}")
        print(f"Average queue length: {stats['avg_queue_length']:.2f}")
        
        for ride in self.park.rides:
            print(f"\n{ride.name}:")
            print(f"  Current queue: {len(ride.queue)} patrons")
            print(f"  Currently riding: {len(ride.riders)} patrons")
            print(f"  State: {ride.state.value}")