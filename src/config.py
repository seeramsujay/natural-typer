"""
Configuration and constants for Human Typer.
"""

from pathlib import Path

# Application metadata
APP_NAME = "Human Typer"
APP_VERSION = "1.0.0"

# Default typing parameters
DEFAULT_SPEED_CPM = 200
DEFAULT_ERROR_RATE = 0.08
DEFAULT_CORRECTION_RATE = 0.85
DEFAULT_SPEED_VARIANCE = 50
DEFAULT_PAUSE_PROBABILITY = 0.05
DEFAULT_DOUBLE_CHAR_PROBABILITY = 0.03
DEFAULT_CHAR_SWAP_PROBABILITY = 0.02

# Speed limits
MIN_SPEED_CPM = 50
MAX_SPEED_CPM = 500

# Timing parameters
MIN_DELAY = 0.05
THINKING_PAUSE_MIN = 0.5
THINKING_PAUSE_MAX = 2.0
FOCUS_SWITCH_DELAY = 0.5

# GUI configuration
DEFAULT_WINDOW_SIZE = "850x750"
SETTINGS_FILE = Path.home() / ".human_typer_settings.json"

# Maximum text length for GUI warning
MAX_TEXT_LENGTH_WARNING = 10000

# Sample texts for demonstration
SAMPLE_TEXTS = {
    "Basic": "Hello, world! This is a test of the human typer.",
    "Quick Brown Fox": "The quick brown fox jumps over the lazy dog.",
    "Programming": "def hello_world():\n    print('Hello, world!')\n    return True",
    "Typing Test": "The five boxing wizards jump quickly. Pack my box with five dozen liquor jugs.",
    "Lorem Ipsum": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
}