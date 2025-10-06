"""
adventureworld.py
Main program with intelligent ride positioning and enhanced visuals.
"""

"""
adventureworld.py
Main program with intelligent ride positioning and enhanced visuals.
"""

import argparse
import sys
from park import Park, TerrainObject
from a import PirateShip, FerrisWheel, SpiderRide
from simulation import Simulation


def create_optimized_park(num_rides=3):
    """
    Create a BIGGER park with optimally positioned rides.
    
    Parameters:
        num_rides (int): Number of rides to create (1-6)
        
    Returns:
        Park: Configured park with optimally placed rides
    """
    park = Park(width=280, height=200)  # PERFECT SPACING PARK!
    
    # Get optimal positions
    positions = park.get_optimal_ride_positions(num_rides)
    
    # Define ride types with varied configurations
    ride_configs = [
        lambda pos: PirateShip("Pirate's Revenge", pos[0], pos[1], 
                              capacity=10, duration=20),
        lambda pos: FerrisWheel("Sky Wheel", pos[0], pos[1], 
                               capacity=16, duration=30),
        lambda pos: SpiderRide("Octopus Spin", pos[0], pos[1], 
                              capacity=12, duration=25),
        lambda pos: PirateShip("Galleon Swing", pos[0], pos[1], 
                              capacity=8, duration=18),
        lambda pos: FerrisWheel("Giant Wheel", pos[0], pos[1], 
                               capacity=20, duration=35),
        lambda pos: SpiderRide("Spider Web", pos[0], pos[1], 
                              capacity=10, duration=22)
    ]
    
    print("\n🎢 Creating Adventure World Park...")
    print(f"📍 Positioning {num_rides} rides optimally...")
    print("─" * 50)
    
    # Add rides at optimal positions
    for i in range(min(num_rides, len(positions))):
        ride = ride_configs[i](positions[i])
        park.add_ride(ride)
    
    # Add some decorative obstacles between rides
    if num_rides >= 2:
        # Add trees/gardens between rides for aesthetics
        park.add_terrain_object(TerrainObject(park.width/2, park.height/2, 
                                             6, 6, "obstacle"))
    
    print("─" * 50)
    print(f"✓ Park created successfully with {len(park.rides)} rides!\n")
    
    return park


def interactive_mode():
    """Run simulation in interactive mode with user prompts."""
    print("=" * 60)
    print("🎡 ADVENTURE WORLD - INTERACTIVE MODE 🎢".center(60))
    print("=" * 60)
    print()
    
    try:
        num_rides = int(input("🎢 Number of rides (1-6): "))
        num_rides = max(1, min(6, num_rides))
        
        max_timesteps = int(input("⏱️  Simulation duration in timesteps (200-1000): "))
        max_timesteps = max(200, min(1000, max_timesteps))
        
        spawn_rate = float(input("👥 Patron spawn rate (0.1-0.5 recommended): "))
        spawn_rate = max(0.05, min(0.8, spawn_rate))
        
        show_animation = input("🎬 Show live animation? (y/n): ").lower() == 'y'
        
    except ValueError:
        print("\n⚠️  Invalid input. Using default values...")
        num_rides = 3
        max_timesteps = 400
        spawn_rate = 0.3
        show_animation = True
    
    print("\n" + "─" * 60)
    print(f"⚙️  Configuration:")
    print(f"   • Rides: {num_rides}")
    print(f"   • Duration: {max_timesteps} timesteps")
    print(f"   • Spawn rate: {spawn_rate}")
    print(f"   • Animation: {'ON' if show_animation else 'OFF'}")
    print("─" * 60 + "\n")
    
    # Create optimized park
    park = create_optimized_park(num_rides)
    
    # Run simulation
    print("🚀 Starting simulation...\n")
    sim = Simulation(park, max_timesteps=max_timesteps, spawn_rate=spawn_rate)
    sim.run(interactive=show_animation, plot_interval=3)
    sim.print_statistics()


def batch_mode(map_file, param_file):
    """Run simulation in batch mode using configuration files."""
    print("=" * 60)
    print("🎡 ADVENTURE WORLD - BATCH MODE 🎢".center(60))
    print("=" * 60)
    print(f"📄 Map file: {map_file}")
    print(f"📄 Parameter file: {param_file}")
    print()
    
    try:
        params = load_parameters(param_file)
        park = load_map(map_file)
        
        max_timesteps = params.get('max_timesteps', 400)
        spawn_rate = params.get('spawn_rate', 0.3)
        
        print("⚙️  Configuration:")
        print(f"   • Max timesteps: {max_timesteps}")
        print(f"   • Spawn rate: {spawn_rate}")
        print(f"   • Rides: {len(park.rides)}")
        print("─" * 60 + "\n")
        
        print("🚀 Starting simulation...\n")
        sim = Simulation(park, max_timesteps=max_timesteps, spawn_rate=spawn_rate)
        sim.run(interactive=False)
        sim.print_statistics()
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)


def load_parameters(param_file):
    """Load parameters from CSV file."""
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
    """Load park layout from CSV file with optimal positioning fallback."""
    park = Park(width=100, height=100)
    
    rides_to_add = []
    
    with open(map_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 1:
                    continue
                
                obj_type = parts[0].lower()
                
                if obj_type == 'pirateship' and len(parts) >= 6:
                    name, x, y = parts[1], float(parts[2]), float(parts[3])
                    capacity, duration = int(parts[4]), int(parts[5])
                    rides_to_add.append(
                        PirateShip(name, x, y, capacity, duration))
                
                elif obj_type == 'ferriswheel' and len(parts) >= 6:
                    name, x, y = parts[1], float(parts[2]), float(parts[3])
                    capacity, duration = int(parts[4]), int(parts[5])
                    rides_to_add.append(
                        FerrisWheel(name, x, y, capacity, duration))
                
                elif obj_type == 'spiderride' and len(parts) >= 6:
                    name, x, y = parts[1], float(parts[2]), float(parts[3])
                    capacity, duration = int(parts[4]), int(parts[5])
                    rides_to_add.append(
                        SpiderRide(name, x, y, capacity, duration))
                
                elif obj_type == 'obstacle' and len(parts) >= 5:
                    x, y = float(parts[1]), float(parts[2])
                    width, height = float(parts[3]), float(parts[4])
                    park.add_terrain_object(
                        TerrainObject(x, y, width, height, "obstacle"))
    
    # Add rides with overlap checking
    print("\n🎢 Loading rides from map file...")
    print("─" * 50)
    
    for ride in rides_to_add:
        if not park.add_ride(ride):
            # If overlap, try to reposition
            print(f"🔄 Attempting to reposition {ride.name}...")
            positions = park.get_optimal_ride_positions(len(rides_to_add))
            for pos in positions:
                ride.x, ride.y = pos
                if park.add_ride(ride):
                    break
    
    print("─" * 50 + "\n")
    
    return park


def main():
    """Main entry point for the program."""
    parser = argparse.ArgumentParser(
        description='🎡 Adventure World Theme Park Simulation 🎢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode (recommended):
    python3 adventureworld.py -i
    
  Batch mode:
    python3 adventureworld.py -f map1.csv -p params1.csv
    
Features:
  ✓ Intelligent ride positioning
  ✓ Smart patrons that visit all rides
  ✓ Real-time statistics and visualization
  ✓ Beautiful animated graphics
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode (recommended)')
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
        print("\n" + "=" * 60)
        print("⚠️  Error: Must specify either -i for interactive mode")
        print("          or both -f and -p for batch mode")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()