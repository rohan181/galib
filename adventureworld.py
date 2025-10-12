"""
adventureworld.py
Main program with intelligent ride positioning and enhanced visuals.
"""

import argparse
import sys
from park import Park, TerrainObject
from a import PirateShip, FerrisWheel, SpiderRide, RollerCoaster  # UPDATED: Added RollerCoaster
from simulation import Simulation
from config import DEFAULT_MAX_TIMESTEPS, DEFAULT_SPAWN_RATE  # ADDED: Import defaults


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
    
    # Define ride types with varied configurations - NOW WITH 4 TYPES!
    ride_configs = [
        lambda pos: PirateShip("Pirate's Revenge", pos[0], pos[1], 
                              capacity=10, duration=20),
        lambda pos: FerrisWheel("Sky Wheel", pos[0], pos[1], 
                               capacity=16, duration=30),
        lambda pos: SpiderRide("Octopus Spin", pos[0], pos[1], 
                              capacity=12, duration=25),
        lambda pos: RollerCoaster("Thunder Run", pos[0], pos[1],     # NEW RIDE TYPE!
                                 capacity=8, duration=15),
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
        
        # Patron strategy selection
        print("\n👤 Patron Movement Strategy:")
        print("   1. Balanced (default) - Mix of casual and thrill-seekers")
        print("   2. Casual - Slow, less patient, fewer rides")
        print("   3. Thrill-Seekers - Fast, patient, many rides")
        print("   4. Random Mix - Completely random behaviors")
        
        strategy_choice = input("Select patron strategy (1-4) [1]: ").strip()
        if strategy_choice == '2':
            patron_strategy = 'casual'
        elif strategy_choice == '3':
            patron_strategy = 'thrill_seeker'
        elif strategy_choice == '4':
            patron_strategy = 'random'
        else:
            patron_strategy = 'balanced'
        
        # NEW: Time of day selection
        print("\n⏰ Time of Day:")
        print("   1. Morning 🌅 - Fewer visitors, normal operations")
        print("   2. Afternoon ☀️ (default) - Peak visitors")
        print("   3. Evening 🌆 - Moderate visitors, slower rides")
        print("   4. Night 🌙 - Few visitors, slowest operations")
        
        time_choice = input("Select time of day (1-4) [2]: ").strip()
        if time_choice == '1':
            time_of_day = 'morning'
        elif time_choice == '3':
            time_of_day = 'evening'
        elif time_choice == '4':
            time_of_day = 'night'
        else:
            time_of_day = 'afternoon'
        
        show_animation = input("\n🎬 Show live animation? (y/n): ").lower() == 'y'
        
    except ValueError:
        print("\n⚠️  Invalid input. Using default values...")
        num_rides = 3
        max_timesteps = 400
        spawn_rate = 0.3
        patron_strategy = 'balanced'
        time_of_day = 'afternoon'
        show_animation = True
    
    print("\n" + "─" * 60)
    print(f"⚙️  Configuration:")
    print(f"   • Rides: {num_rides}")
    print(f"   • Duration: {max_timesteps} timesteps")
    print(f"   • Spawn rate: {spawn_rate}")
    print(f"   • Patron strategy: {patron_strategy.upper()}")
    print(f"   • Time of day: {time_of_day.upper()}")
    print(f"   • Animation: {'ON' if show_animation else 'OFF'}")
    print("─" * 60 + "\n")
    
    # Create optimized park
    park = create_optimized_park(num_rides)
    
    # Set patron strategy in park
    park.patron_strategy = patron_strategy
    
    # Run simulation with time of day
    print("🚀 Starting simulation...\n")
    sim = Simulation(park, max_timesteps=max_timesteps, 
                    spawn_rate=spawn_rate, time_of_day=time_of_day)
    sim.run(interactive=show_animation, plot_interval=3)
    sim.print_statistics()


    

def demo_mode():
    """Run a quick demonstration with preset configurations."""
    print("=" * 60)
    print("🎡 ADVENTURE WORLD - DEMO MODE 🎢".center(60))
    print("=" * 60)
    print()
    print("🎬 Running preset demonstration...")
    print("   No files or user input required!")
    print()
    
    # Preset configurations
    demos = [
        {
            'name': 'Small Park',
            'num_rides': 3,
            'max_timesteps': 300,
            'spawn_rate': 0.25,
            'show_animation': False
        },
        {
            'name': 'Medium Park',
            'num_rides': 4,
            'max_timesteps': 500,
            'spawn_rate': 0.30,
            'show_animation': False
        },
        {
            'name': 'Large Park',
            'num_rides': 5,
            'max_timesteps': 700,
            'spawn_rate': 0.35,
            'show_animation': False
        }
    ]
    
    print("📋 Available Demo Scenarios:")
    for i, demo in enumerate(demos, 1):
        print(f"   {i}. {demo['name']}: {demo['num_rides']} rides, "
              f"{demo['max_timesteps']} timesteps, "
              f"spawn rate {demo['spawn_rate']}")
    
    print()
    choice = input("Select demo (1-3) or press Enter for default [2]: ").strip()
    
    # Select demo
    if choice == '1':
        selected = demos[0]
    elif choice == '3':
        selected = demos[2]
    else:
        selected = demos[1]  # Default
    
    print()
    print("─" * 60)
    print(f"🎯 Running: {selected['name']}")
    print("─" * 60)
    print(f"   • Rides: {selected['num_rides']}")
    print(f"   • Duration: {selected['max_timesteps']} timesteps")
    print(f"   • Spawn rate: {selected['spawn_rate']}")
    print(f"   • Animation: {'ON' if selected['show_animation'] else 'OFF'}")
    print("─" * 60 + "\n")
    
    # Create park and run simulation
    park = create_optimized_park(selected['num_rides'])
    
    print("🚀 Starting simulation...\n")
    sim = Simulation(park, 
                    max_timesteps=selected['max_timesteps'], 
                    spawn_rate=selected['spawn_rate'])
    sim.run(interactive=selected['show_animation'])
    sim.print_statistics()


def batch_mode(map_file, param_file):
    """Run simulation in batch mode with comprehensive error handling."""
    print("=" * 60)
    print("🎡 ADVENTURE WORLD - BATCH MODE 🎢".center(60))
    print("=" * 60)
    print(f"📄 Map file: {map_file}")
    print(f"📄 Parameter file: {param_file}")
    print()
    
    # Validate files exist
    import os
    map_exists = os.path.exists(map_file)
    param_exists = os.path.exists(param_file)
    
    if not map_exists or not param_exists:
        print("❌ FILE ERROR DETECTED:")
        if not map_exists:
            print(f"   • Map file '{map_file}' NOT FOUND")
            print(f"   • Expected at: {os.path.abspath(map_file)}")
        if not param_exists:
            print(f"   • Parameter file '{param_file}' NOT FOUND")
            print(f"   • Expected at: {os.path.abspath(param_file)}")
        
        print("\n" + "─" * 60)
        print("💡 FALLBACK: Using default configuration")
        print("─" * 60)
        
        # Use defaults
        params = {
            'max_timesteps': DEFAULT_MAX_TIMESTEPS,
            'spawn_rate': DEFAULT_SPAWN_RATE
        }
        park = create_optimized_park(num_rides=3)
        print("✓ Created default park with 3 rides")
        print("✓ Using default parameters")
        
    else:
        # Load files with error handling
        params = load_parameters(param_file)
        if params is None:
            print("⚠️  Parameter file invalid - using defaults")
            params = {
                'max_timesteps': DEFAULT_MAX_TIMESTEPS,
                'spawn_rate': DEFAULT_SPAWN_RATE
            }
        
        park = load_map(map_file)
        if park is None or len(park.rides) == 0:
            print("⚠️  Map file invalid - using default park")
            park = create_optimized_park(num_rides=3)
    
    max_timesteps = params.get('max_timesteps', DEFAULT_MAX_TIMESTEPS)
    spawn_rate = params.get('spawn_rate', DEFAULT_SPAWN_RATE)
    
    print("\n⚙️  Final Configuration:")
    print(f"   • Max timesteps: {max_timesteps}")
    print(f"   • Spawn rate: {spawn_rate}")
    print(f"   • Rides: {len(park.rides)}")
    print("─" * 60 + "\n")
    
    print("🚀 Starting simulation...\n")
    sim = Simulation(park, max_timesteps=max_timesteps, spawn_rate=spawn_rate)
    sim.run(interactive=False)
    sim.print_statistics()


def load_parameters(param_file):
    """
    Load parameters from CSV file with COMPREHENSIVE error handling.
    
    Returns:
        dict: Parameters dictionary, or None if loading fails
    """
    import os
    
    # File existence check
    if not os.path.exists(param_file):
        print(f"\n❌ PARAMETER FILE ERROR:")
        print(f"   File '{param_file}' does not exist")
        print(f"   Looking in: {os.path.abspath(param_file)}")
        print(f"\n💡 HOW TO FIX:")
        print(f"   Create file '{param_file}' with content:")
        print(f"   ─────────────────────────────────")
        print(f"   # Parameter file")
        print(f"   max_timesteps, 1000")
        print(f"   spawn_rate, 0.3")
        print(f"   ─────────────────────────────────\n")
        return None
    
    # Permission check
    if not os.access(param_file, os.R_OK):
        print(f"❌ PERMISSION ERROR: Cannot read '{param_file}'")
        return None
    
    # File size check
    if os.path.getsize(param_file) == 0:
        print(f"❌ EMPTY FILE: '{param_file}' contains no data")
        return None
    
    try:
        params = {}
        line_count = 0
        valid_params = 0
        
        with open(param_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                line_count += 1
                
                # Check format
                if ',' not in line:
                    print(f"⚠️  Line {line_num}: Missing comma - '{line}'")
                    print(f"   Expected: parameter_name, value")
                    continue
                
                parts = line.split(',')
                if len(parts) < 2:
                    print(f"⚠️  Line {line_num}: Invalid format - '{line}'")
                    continue
                
                key = parts[0].strip()
                value_str = parts[1].strip()
                
                if not key:
                    print(f"⚠️  Line {line_num}: Empty parameter name")
                    continue
                
                if not value_str:
                    print(f"⚠️  Line {line_num}: Empty value for '{key}'")
                    continue
                
                # Parse value
                try:
                    if '.' in value_str:
                        value = float(value_str)
                    else:
                        value = int(value_str)
                    params[key] = value
                    valid_params += 1
                except ValueError:
                    # Try as string
                    params[key] = value_str
                    print(f"⚠️  Line {line_num}: '{value_str}' not a number, stored as string")
                    valid_params += 1
        
        if valid_params == 0:
            print(f"❌ NO VALID PARAMETERS: '{param_file}' has no usable data")
            return None
        
        print(f"✓ Loaded {valid_params} parameter(s) from '{param_file}'")
        for key, value in params.items():
            print(f"   • {key} = {value}")
        
        return params
        
    except PermissionError:
        print(f"❌ PERMISSION DENIED: Cannot read '{param_file}'")
        return None
    except UnicodeDecodeError:
        print(f"❌ ENCODING ERROR: '{param_file}' is not a valid text file")
        return None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR loading '{param_file}': {e}")
        return None


def load_map(map_file):
    """
    Load park layout from CSV file with COMPREHENSIVE error handling.
    
    Returns:
        Park: Configured park, or None if loading fails
    """
    import os
    
    # File existence check
    if not os.path.exists(map_file):
        print(f"\n❌ MAP FILE ERROR:")
        print(f"   File '{map_file}' does not exist")
        print(f"   Looking in: {os.path.abspath(map_file)}")
        print(f"\n💡 HOW TO FIX:")
        print(f"   Create file '{map_file}' with content:")
        print(f"   ─────────────────────────────────────────────────────")
        print(f"   # Map file - Format: RideType, Name, X, Y, Capacity, Duration")
        print(f"   PirateShip, Pirate's Revenge, 40, 45, 10, 20")
        print(f"   FerrisWheel, Sky Wheel, 160, 45, 16, 30")
        print(f"   SpiderRide, Octopus Spin, 40, 105, 12, 25")
        print(f"   RollerCoaster, Thunder Run, 100, 75, 8, 15")
        print(f"   obstacle, 100, 40, 8, 8")
        print(f"   ─────────────────────────────────────────────────────\n")
        return None
    
    # Permission check
    if not os.access(map_file, os.R_OK):
        print(f"❌ PERMISSION ERROR: Cannot read '{map_file}'")
        return None
    
    # File size check
    if os.path.getsize(map_file) == 0:
        print(f"❌ EMPTY FILE: '{map_file}' contains no data")
        return None
    
    try:
        park = Park(width=200, height=150)
        rides_to_add = []
        line_count = 0
        error_count = 0
        valid_lines = 0
        
        with open(map_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                line_count += 1
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 1:
                    continue
                
                obj_type = parts[0].lower()
                
                try:
                    # PIRATE SHIP
                    if obj_type == 'pirateship':
                        if len(parts) < 6:
                            print(f"⚠️  Line {line_num}: PirateShip needs 6 values")
                            print(f"   Format: PirateShip, Name, X, Y, Capacity, Duration")
                            print(f"   Got: {len(parts)} values")
                            error_count += 1
                            continue
                        
                        name = parts[1]
                        x, y = float(parts[2]), float(parts[3])
                        capacity, duration = int(parts[4]), int(parts[5])
                        rides_to_add.append(PirateShip(name, x, y, capacity, duration))
                        valid_lines += 1
                    
                    # FERRIS WHEEL
                    elif obj_type == 'ferriswheel':
                        if len(parts) < 6:
                            print(f"⚠️  Line {line_num}: FerrisWheel needs 6 values")
                            print(f"   Format: FerrisWheel, Name, X, Y, Capacity, Duration")
                            error_count += 1
                            continue
                        
                        name = parts[1]
                        x, y = float(parts[2]), float(parts[3])
                        capacity, duration = int(parts[4]), int(parts[5])
                        rides_to_add.append(FerrisWheel(name, x, y, capacity, duration))
                        valid_lines += 1
                    
                    # SPIDER RIDE
                    elif obj_type == 'spiderride':
                        if len(parts) < 6:
                            print(f"⚠️  Line {line_num}: SpiderRide needs 6 values")
                            print(f"   Format: SpiderRide, Name, X, Y, Capacity, Duration")
                            error_count += 1
                            continue
                        
                        name = parts[1]
                        x, y = float(parts[2]), float(parts[3])
                        capacity, duration = int(parts[4]), int(parts[5])
                        rides_to_add.append(SpiderRide(name, x, y, capacity, duration))
                        valid_lines += 1
                    
                    # ROLLER COASTER - NEW!
                    elif obj_type == 'rollercoaster':
                        if len(parts) < 6:
                            print(f"⚠️  Line {line_num}: RollerCoaster needs 6 values")
                            print(f"   Format: RollerCoaster, Name, X, Y, Capacity, Duration")
                            error_count += 1
                            continue
                        
                        name = parts[1]
                        x, y = float(parts[2]), float(parts[3])
                        capacity, duration = int(parts[4]), int(parts[5])
                        rides_to_add.append(RollerCoaster(name, x, y, capacity, duration))
                        valid_lines += 1
                    
                    # OBSTACLE
                    elif obj_type == 'obstacle':
                        if len(parts) < 5:
                            print(f"⚠️  Line {line_num}: obstacle needs 5 values")
                            print(f"   Format: obstacle, X, Y, Width, Height")
                            error_count += 1
                            continue
                        
                        x, y = float(parts[1]), float(parts[2])
                        width, height = float(parts[3]), float(parts[4])
                        park.add_terrain_object(TerrainObject(x, y, width, height, "obstacle"))
                        valid_lines += 1
                    
                    # UNKNOWN TYPE
                    else:
                        print(f"⚠️  Line {line_num}: Unknown object type '{parts[0]}'")
                        print(f"   Valid types: PirateShip, FerrisWheel, SpiderRide, RollerCoaster, obstacle")
                        error_count += 1
                
                except ValueError as e:
                    print(f"❌ Line {line_num}: NUMBER FORMAT ERROR")
                    print(f"   {e}")
                    print(f"   Line content: {line}")
                    error_count += 1
                except IndexError as e:
                    print(f"❌ Line {line_num}: MISSING VALUES")
                    print(f"   {e}")
                    error_count += 1
                except Exception as e:
                    print(f"❌ Line {line_num}: UNEXPECTED ERROR - {e}")
                    error_count += 1
        
        # Summary
        print(f"\n📊 MAP FILE SUMMARY:")
        print(f"   • Total lines processed: {line_count}")
        print(f"   • Valid objects: {valid_lines}")
        print(f"   • Errors encountered: {error_count}")
        
        if valid_lines == 0:
            print(f"\n❌ NO VALID OBJECTS: '{map_file}' has no usable rides or terrain")
            return None
        
        # Add rides with overlap checking
        print(f"\n🎢 Adding rides to park...")
        print("─" * 50)
        
        rides_added = 0
        for ride in rides_to_add:
            if park.add_ride(ride):
                rides_added += 1
            else:
                print(f"🔄 Repositioning {ride.name} due to overlap...")
                positions = park.get_optimal_ride_positions(len(rides_to_add))
                repositioned = False
                for pos in positions:
                    ride.x, ride.y = pos
                    if park.add_ride(ride):
                        rides_added += 1
                        repositioned = True
                        break
                if not repositioned:
                    print(f"❌ Could not place {ride.name} - SKIPPED")
        
        print("─" * 50)
        print(f"✓ Map loaded: {rides_added}/{len(rides_to_add)} rides added successfully\n")
        
        if rides_added == 0:
            print(f"❌ CRITICAL: No rides could be added to park")
            return None
        
        return park
        
    except PermissionError:
        print(f"❌ PERMISSION DENIED: Cannot read '{map_file}'")
        return None
    except UnicodeDecodeError:
        print(f"❌ ENCODING ERROR: '{map_file}' is not a valid text file")
        return None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR loading '{map_file}': {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point with THREE modes."""
    parser = argparse.ArgumentParser(
        description='🎡 Adventure World Theme Park Simulation 🎢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Demo mode (quickest - preset configurations):
    python3 adventureworld.py -d
    python3 adventureworld.py --demo
    
  Interactive mode (custom settings with prompts):
    python3 adventureworld.py -i
    
  Batch mode (load from files):
    python3 adventureworld.py -f map1.csv -p params1.csv
    
  Handle missing files gracefully:
    python3 adventureworld.py -f missing.csv -p params1.csv
    (Will use defaults and continue)

Features:
  ✓ THREE flexible modes of operation
  ✓ FOUR different ride types with phases/cycles
  ✓ Robust error handling for missing/invalid files
  ✓ Automatic fallback to default configurations
  ✓ Detailed error messages with fix suggestions
  ✓ Intelligent ride positioning
  ✓ Real-time visualization
        """
    )
    
    # Mode selection arguments
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('-d', '--demo', action='store_true',
                           help='Run in demo mode with preset configurations')
    mode_group.add_argument('-i', '--interactive', action='store_true',
                           help='Run in interactive mode with user prompts')
    
    # Batch mode arguments
    parser.add_argument('-f', '--map-file', type=str,
                       help='Map configuration file (batch mode)')
    parser.add_argument('-p', '--param-file', type=str,
                       help='Parameter configuration file (batch mode)')
    
    args = parser.parse_args()
    
    # Determine which mode to run
    if args.demo:
        demo_mode()
    
    elif args.interactive:
        interactive_mode()
    
    elif args.map_file and args.param_file:
        batch_mode(args.map_file, args.param_file)
    
    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("⚠️  USAGE ERROR - Must specify a mode:")
        print()
        print("   THREE MODES AVAILABLE:")
        print("   ─────────────────────────────────────────────")
        print("   1. Demo Mode (fastest):")
        print("      python3 adventureworld.py -d")
        print()
        print("   2. Interactive Mode (customizable):")
        print("      python3 adventureworld.py -i")
        print()
        print("   3. Batch Mode (file-based):")
        print("      python3 adventureworld.py -f map1.csv -p params1.csv")
        print("   ─────────────────────────────────────────────")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()