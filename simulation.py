"""
simulation.py
Enhanced simulation engine with real-time statistics display.
"""

import random
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from config import DEFAULT_MAX_TIMESTEPS, DEFAULT_SPAWN_RATE, PatronState


class Simulation:
    """Main simulation engine with enhanced visualization."""
    
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
        
        # Track statistics over time
        self.patron_counts = []
        self.queue_lengths = []
        self.timesteps_recorded = []
    
    def step(self):
        """Execute one timestep of the simulation."""
        # Spawn new patrons
        if random.random() < self.spawn_rate:
            self.park.spawn_patron(self.next_patron_id)
            self.next_patron_id += 1
            self.total_patrons_spawned += 1
        
        # Update all patrons
        initial_patron_count = len(self.park.patrons)
        for patron in self.park.patrons[:]:
            patron.step_change(self.park)
        
        # Track exits
        patrons_exited = initial_patron_count - len(self.park.patrons)
        self.total_patrons_exited += patrons_exited
        
        # Update all rides
        for ride in self.park.rides:
            ride.step_change()
        
        self.current_timestep += 1
        
        # Record statistics
        self.patron_counts.append(len(self.park.patrons))
        total_queue = sum(len(ride.queue) for ride in self.park.rides)
        self.queue_lengths.append(total_queue)
        self.timesteps_recorded.append(self.current_timestep)
    
    def run(self, interactive=False, plot_interval=5):
        """
        Run the simulation with enhanced visualization.
        
        Parameters:
            interactive (bool): If True, display real-time animation
            plot_interval (int): Update plot every N timesteps
            
        Returns:
            dict: Simulation statistics
        """
        if interactive:
            plt.ion()
            fig = plt.figure(figsize=(16, 10))
            gs = GridSpec(2, 2, figure=fig, height_ratios=[3, 1], hspace=0.3, wspace=0.3)
            
            ax_main = fig.add_subplot(gs[0, :])  # Main park view (top, full width)
            ax_stats = fig.add_subplot(gs[1, 0])  # Statistics graph (bottom left)
            ax_info = fig.add_subplot(gs[1, 1])   # Info panel (bottom right)
            ax_info.axis('off')
        
        while self.current_timestep < self.max_timesteps:
            self.step()
            
            if interactive and self.current_timestep % plot_interval == 0:
                # Clear and update main park view
                self.park.plot(ax_main)
                ax_main.set_title(f'Adventure World - Timestep {self.current_timestep}/{self.max_timesteps}',
                                 fontsize=14, weight='bold')
                
                # Update statistics graph
                self.plot_statistics(ax_stats)
                
                # Update info panel
                self.plot_info_panel(ax_info)
                
                plt.pause(0.01)
            
            # Console output
            if self.current_timestep % 50 == 0:
                print(f"Timestep {self.current_timestep}: "
                      f"{len(self.park.patrons)} in park, "
                      f"{self.total_patrons_spawned} spawned, "
                      f"{self.total_patrons_exited} exited")
        
        if interactive:
            plt.ioff()
            print("\nSimulation complete! Close the plot window to continue.")
            plt.show()
        
        return self.get_statistics()
    
    def plot_statistics(self, ax):
        """
        Plot real-time statistics graph.
        
        Parameters:
            ax: Matplotlib axes for statistics
        """
        ax.clear()
        
        if len(self.timesteps_recorded) > 1:
            ax.plot(self.timesteps_recorded, self.patron_counts, 'b-', 
                   linewidth=2, label='Patrons in Park')
            ax.plot(self.timesteps_recorded, self.queue_lengths, 'r-', 
                   linewidth=2, label='Total Queue Length')
            
            ax.set_xlabel('Timestep', fontsize=10)
            ax.set_ylabel('Count', fontsize=10)
            ax.set_title('Park Statistics Over Time', fontsize=11, weight='bold')
            ax.legend(loc='upper left', fontsize=9)
            ax.grid(True, alpha=0.3)
    
    def plot_info_panel(self, ax):
        """
        Plot information panel with current statistics.
        
        Parameters:
            ax: Matplotlib axes for info panel
        """
        ax.clear()
        ax.axis('off')
        
        # Get patron state counts
        state_counts = {state: 0 for state in PatronState}
        for patron in self.park.patrons:
            state_counts[patron.state] += 1
        
        # Build info text
        info_lines = [
            "═══ PARK STATISTICS ═══",
            f"",
            f"Timestep: {self.current_timestep}/{self.max_timesteps}",
            f"",
            f"PATRONS:",
            f"  • In Park: {len(self.park.patrons)}",
            f"  • Total Spawned: {self.total_patrons_spawned}",
            f"  • Total Exited: {self.total_patrons_exited}",
            f"",
            f"PATRON STATES:",
            f"  • Roaming: {state_counts[PatronState.ROAMING]}",
            f"  • Queuing: {state_counts[PatronState.QUEUING]}",
            f"  • Riding: {state_counts[PatronState.RIDING]}",
            f"  • Exiting: {state_counts[PatronState.EXITING]}",
            f"",
            f"RIDES:",
        ]
        
        for ride in self.park.rides:
            info_lines.append(f"  {ride.name}:")
            info_lines.append(f"    Queue: {len(ride.queue)} | "
                            f"Riding: {len(ride.riders)}/{ride.capacity}")
            info_lines.append(f"    State: {ride.state.value.upper()}")
            info_lines.append(f"    Served: {ride.total_riders_served} | "
                            f"Cycles: {ride.total_cycles}")
        
        # Display text
        info_text = '\n'.join(info_lines)
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', family='monospace',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    def get_statistics(self):
        """
        Get final simulation statistics.
        
        Returns:
            dict: Dictionary of statistics
        """
        total_queue_length = sum(len(ride.queue) for ride in self.park.rides)
        avg_queue_length = total_queue_length / len(self.park.rides) if self.park.rides else 0
        
        total_served = sum(ride.total_riders_served for ride in self.park.rides)
        total_cycles = sum(ride.total_cycles for ride in self.park.rides)
        
        return {
            'timesteps': self.current_timestep,
            'total_spawned': self.total_patrons_spawned,
            'total_exited': self.total_patrons_exited,
            'remaining_patrons': len(self.park.patrons),
            'total_rides': len(self.park.rides),
            'avg_queue_length': avg_queue_length,
            'total_queue_length': total_queue_length,
            'total_riders_served': total_served,
            'total_cycles': total_cycles,
        }
    
    def print_statistics(self):
        """Print detailed final simulation statistics."""
        stats = self.get_statistics()
        
        print("\n" + "═"*60)
        print("SIMULATION COMPLETE".center(60))
        print("═"*60)
        print(f"\n{'OVERALL STATISTICS':^60}")
        print("─"*60)
        print(f"  Total timesteps: {stats['timesteps']}")
        print(f"  Total patrons spawned: {stats['total_spawned']}")
        print(f"  Total patrons exited: {stats['total_exited']}")
        print(f"  Patrons remaining in park: {stats['remaining_patrons']}")
        print(f"\n{'RIDE STATISTICS':^60}")
        print("─"*60)
        print(f"  Total rides: {stats['total_rides']}")
        print(f"  Average queue length: {stats['avg_queue_length']:.2f}")
        print(f"  Total riders served: {stats['total_riders_served']}")
        print(f"  Total ride cycles: {stats['total_cycles']}")
        
        if stats['total_spawned'] > 0:
            exit_rate = (stats['total_exited'] / stats['total_spawned']) * 100
            print(f"  Exit rate: {exit_rate:.1f}%")
        
        print(f"\n{'INDIVIDUAL RIDE PERFORMANCE':^60}")
        print("─"*60)
        
        for ride in self.park.rides:
            print(f"\n  {ride.name}:")
            print(f"    Current state: {ride.state.value.upper()}")
            print(f"    Queue: {len(ride.queue)} patrons")
            print(f"    Currently riding: {len(ride.riders)}/{ride.capacity}")
            print(f"    Total served: {ride.total_riders_served}")
            print(f"    Cycles completed: {ride.total_cycles}")
            
            if ride.total_cycles > 0:
                avg_riders_per_cycle = ride.total_riders_served / ride.total_cycles
                efficiency = (avg_riders_per_cycle / ride.capacity) * 100
                print(f"    Avg riders/cycle: {avg_riders_per_cycle:.1f}")
                print(f"    Capacity efficiency: {efficiency:.1f}%")
        
        print("\n" + "═"*60 + "\n")