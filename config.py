"""
config.py
Enhanced configuration with better visual settings for Adventure World.
"""

from enum import Enum


class RideState(Enum):
    """States that a ride can be in"""
    IDLE = "idle"
    LOADING = "loading"
    RUNNING = "running"
    UNLOADING = "unloading"


class PatronState(Enum):
    """States that a patron can be in"""
    ROAMING = "roaming"
    QUEUING = "queuing"
    RIDING = "riding"
    EXITING = "exiting"


# Default simulation parameters
DEFAULT_PARK_WIDTH = 100
DEFAULT_PARK_HEIGHT = 100
DEFAULT_SPAWN_RATE = 0.2
DEFAULT_MAX_TIMESTEPS = 500
DEFAULT_PATRON_MOVE_SPEED = 0.5
DEFAULT_PATRON_IMMOBILE_TIME = 5

# Ride defaults
DEFAULT_LOADING_TIME = 3
DEFAULT_UNLOAD_TIME = 2

# Colors for patron states
COLOR_ROAMING = 'limegreen'
COLOR_QUEUING = 'dodgerblue'
COLOR_RIDING = 'magenta'
COLOR_EXITING = 'orange'

# Colors for park elements
COLOR_ENTRANCE = 'g^'
COLOR_EXIT = 'rv'
COLOR_OBSTACLE = 'gray'
COLOR_BOUNDARY = 'darkgray'

# Ride colors
COLOR_PIRATE_SHIP = 'saddlebrown'
COLOR_FERRIS_WHEEL = 'steelblue'
COLOR_SPIDER_RIDE = 'crimson'

# State colors
COLOR_STATE_IDLE = 'lightgray'
COLOR_STATE_LOADING = 'lightyellow'
COLOR_STATE_RUNNING = 'lightgreen'
COLOR_STATE_UNLOADING = 'lightcoral'