"""
adventureworld.py
Main program for Adventure World theme park simulation.

Usage:
    Interactive mode: python3 adventureworld.py -i
    Batch mode: python3 adventureworld.py -f map.csv -p params.csv
"""

import argparse
import sys
from park import Park, TerrainObject
from a import PirateShip, FerrisWheel, SpiderRide
from simulation import Simulation


def create_sample_park():
    """Create a sample park with several rides."""
    park = Park(width=100, height=100)
    
    park.add_ride(PirateShip("Pirate's Revenge", 25, 25, capacity=8, duration=15))
    park.add_ride(FerrisWheel("Sky View", 75, 25, capacity=12, duration=25))
    park.add_ride(SpiderRide("Tornado", 50, 70, capacity=10, duration=20))
    
    park.add_terrain_object(TerrainObject(50, 45, 10, 5, "obstacle"))
    
    return park


def interactive_mode():
    """Run simulation in interactive mode with user prompts."""
    print("="*60)
    print("ADVENTURE WORLD - INTERACTIVE MODE")
    print("="*60)
    
    try:
        num_rides = int(input("Number of rides (1-5): "))
        num_rides = max(1, min(5, num_rides))
        
        max_timesteps = int(input("Simulation duration (timesteps, e.g., 300): "))
        
        spawn_rate = float(input("Patron spawn rate (0.0-1.0, e.g., 0.3): "))
        spawn_rate = max(0.0, min(1.0, spawn_rate))
        
        show_animation = input("Show animation? (y/n): ").lower() == 'y'
        
    except ValueError:
        print("Invalid input. Using default values.")
        num_rides = 3
        max_timesteps = 300
        spawn_rate = 0.3
        show_animation = True
    
    print(f"\nCreating park with {num_rides} rides...")
    park = Park(width=100, height=100)
    
    ride_types = [
        lambda n: PirateShip(f"Pirate Ship {n}", 25, 25 + n*15, capacity=8, duration=15),
        lambda n: FerrisWheel(f"Ferris Wheel {n}", 75, 25 + n*15, capacity=12, duration=25),
        lambda n: SpiderRide(f"Spider {n}", 50, 50 + n*15, capacity=10, duration=20)
    ]
    
    for i in range(num_rides):
        ride = ride_types[i % len(ride_types)](i + 1)
        park.add_ride(ride)
    
    park.add_terrain_object(TerrainObject(50, 45, 8, 4, "obstacle"))
    
    print("Starting simulation...")
    sim = Simulation(park, max_timesteps=max_timesteps, spawn_rate=spawn_rate)
    sim.run(interactive=show_animation)
    sim.print_statistics()


def batch_mode(map_file, param_file):
    """
    Run simulation in batch mode using configuration files.
    
    Parameters:
        map_file (str): Path to map configuration file
        param_file (str): Path to parameter configuration file
    """
    print("="*60)
    print("ADVENTURE WORLD - BATCH MODE")
    print("="*60)
    print(f"Map file: {map_file}")
    print(f"Parameter file: {param_file}")
    
    try:
        params = load_parameters(param_file)
        park = load_map(map_file)
        
        max_timesteps = params.get('max_timesteps', 300)
        spawn_rate = params.get('spawn_rate', 0.3)
        
        print(f"\nRunning simulation with:")
        print(f"  Max timesteps: {max_timesteps}")
        print(f"  Spawn rate: {spawn_rate}")
        print(f"  Rides: {len(park.rides)}")
        
        sim = Simulation(park, max_timesteps=max_timesteps, spawn_rate=spawn_rate)
        sim.run(interactive=False)
        sim.print_statistics()
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def load_parameters(param_file):
    """
    Load parameters from CSV file.
    
    Parameters:
        param_file (str): Path to parameter file
        
    Returns:
        dict: Dictionary of parameters
    """
    params = {}
    with open(param_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    try:
                        if '.' in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    except ValueError:
                        params[key] = value
    
    return params


def load_map(map_file):
    """
    Load park layout from CSV file.
    
    Parameters:
        map_file (str): Path to map file
        
    Returns:
        Park: Configured park object
    """
    park = Park(width=100, height=100)
    
    with open(map_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 1:
                    continue
                
                obj_type = parts[0].lower()
                
                if obj_type == 'pirateship' and len(parts) >= 6:
                    name, x, y, capacity, duration = parts[1], float(parts[2]), float(parts[3]), int(parts[4]), int(parts[5])
                    park.add_ride(PirateShip(name, x, y, capacity, duration))
                
                elif obj_type == 'ferriswheel' and len(parts) >= 6:
                    name, x, y, capacity, duration = parts[1], float(parts[2]), float(parts[3]), int(parts[4]), int(parts[5])
                    park.add_ride(FerrisWheel(name, x, y, capacity, duration))
                
                elif obj_type == 'spiderride' and len(parts) >= 6:
                    name, x, y, capacity, duration = parts[1], float(parts[2]), float(parts[3]), int(parts[4]), int(parts[5])
                    park.add_ride(SpiderRide(name, x, y, capacity, duration))
                
                elif obj_type == 'obstacle' and len(parts) >= 5:
                    x, y, width, height = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    park.add_terrain_object(TerrainObject(x, y, width, height, "obstacle"))
    
    return park


def main():
    """Main entry point for the program."""
    parser = argparse.ArgumentParser(
        description='Adventure World Theme Park Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python3 adventureworld.py -i
    
  Batch mode:
    python3 adventureworld.py -f map1.csv -p params1.csv
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('-f', '--map-file', type=str,
                       help='Map configuration file (batch mode)')
    parser.add_argument('-p', '--param-file', type=str,
                       help='Parameter configuration file (batch mode)')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.map_file and args.param_file:
        batch_mode(args.map_file, args.param_file)
    else:
        parser.print_help()
        print("\nError: Must specify either -i for interactive mode")
        print("       or both -f and -p for batch mode")
        sys.exit(1)


if __name__ == "__main__":
    main()