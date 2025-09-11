# Human Typer

A Python library for simulating realistic human typing behavior with configurable error patterns and timing variations.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)

## Overview

Human Typer simulates human typing patterns including:
- Variable typing speed with natural fluctuations
- Realistic error injection based on keyboard layout proximity
- Error correction behavior with configurable probabilities
- Character transposition and doubling patterns
- Natural pauses and hesitations

The library provides both programmatic API access and ready-to-use GUI/CLI interfaces.

## Architecture

```
human-typer/
├── src/
│   ├── human_typer.py      # Core typing simulation engine
│   ├── human_typer_gui.py  # Tkinter-based GUI interface
│   ├── cli.py              # Command-line interface
│   └── config.py           # Configuration constants
├── main.py                 # Unified entry point
└── tests/                  # Test suite
```

## Installation

### Requirements
- Python 3.9 or higher
- pynput (for keyboard simulation)
- tkinter (for GUI, typically included with Python)

### From Source
```bash
git clone https://github.com/FizzWizzleDazzle/Human-Typer.git
cd Human-Typer
pip install -r requirements.txt
```

### Dependencies
```
pynput>=1.8.1    # Keyboard/mouse control
pyinstaller>=5.0 # Executable building (optional)
```

## Usage

### Command Line Interface

```bash
# Launch with default GUI (if tkinter available)
python main.py

# Force CLI mode
python main.py --cli

# Type specific text
python main.py --text "Your text here" --speed 250 --error-rate 0.05

# Console output only (no keyboard simulation)
python main.py --cli --no-keyboard
```

### Programmatic API

```python
from src.human_typer import HumanTyper

# Initialize typer
typer = HumanTyper(use_keyboard=True)

# Configure parameters
typer.set_speed(200)           # Characters per minute
typer.set_error_rate(0.08)     # 8% error probability
typer.set_correction_rate(0.85) # 85% correction probability

# Type text with F6 hotkey control
typer.type_text("Your text here", use_hotkey=True, show_progress=True)

# Or type immediately without hotkey
typer.type_text("Your text here", use_hotkey=False)
```

### Configuration Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `speed` | 50-500 CPM | 200 | Base typing speed in characters per minute |
| `error_rate` | 0.0-1.0 | 0.08 | Probability of making typing errors |
| `correction_rate` | 0.0-1.0 | 0.85 | Probability of correcting errors |
| `speed_variance` | 0-100 | 50 | CPM variation range |
| `pause_probability` | 0.0-1.0 | 0.05 | Probability of thinking pauses |

## Error Simulation

### Error Types

1. **Adjacent Key Errors**: Based on QWERTY keyboard layout proximity
   - Example: 'hello' → 'hwllo' (e→w)

2. **Character Transposition**: Swapping of adjacent characters
   - Example: 'the' → 'teh'

3. **Character Doubling**: Accidental double key press
   - Example: 'test' → 'tesst'

4. **Character Omission**: Missing keystrokes (corrected automatically)

### Keyboard Layout Mapping

The system uses a QWERTY layout map to determine adjacent keys for realistic error generation. Each key maps to its physical neighbors on a standard keyboard.

## GUI Features

- Real-time typing progress visualization
- Hotkey status indicator (F6 for start/stop)
- Persistent settings storage (~/.human_typer_settings.json)
- Text file loading and sample text selection
- Configurable typing parameters via sliders

## Keyboard Control

### F6 Hotkey System
- Press F6 to start typing
- Press F6 again to stop
- 0.5-second delay after activation for focus switching
- Automatic focus release from text input fields

### Platform Support
- **Windows**: Native support via pynput
- **macOS**: Requires accessibility permissions
- **Linux**: X11/Wayland support required

## Technical Details

### Threading Model
- Typing occurs in separate thread to prevent GUI blocking
- Hotkey listener runs in daemon thread
- Thread-safe callback system for progress updates

### Timing Algorithm
```python
base_delay = 60.0 / speed_cpm
variation = random.uniform(-variance/speed, variance/speed)
final_delay = max(0.05, base_delay + variation)
```

### Error Injection Process
1. Calculate error probability based on settings
2. Select error type (adjacent key, transposition, doubling)
3. Inject error into typing stream
4. Apply correction based on correction probability
5. Ensure final output matches intended text

## System Requirements

### Permissions
- **macOS**: System Preferences → Security & Privacy → Accessibility
- **Linux**: May require input group membership or root access
- **Windows**: Generally works without special permissions

### Performance
- Minimal CPU usage (<1% during typing)
- Memory footprint: ~20-30 MB
- Thread count: 2-3 active threads during operation

## Building Executables

### Windows
```bash
pyinstaller --onefile --windowed \
    --name "HumanTyper" \
    --add-data "src/*.py;src" \
    main.py
```

### Cross-platform Build Script
```bash
python scripts/build.py
```

## Testing

```bash
# Run test suite
python -m pytest tests/

# Quick functional test
python tests/quick_test.py
```

## API Reference

### HumanTyper Class

```python
class HumanTyper:
    def __init__(self, use_keyboard: bool = True)
    def type_text(self, text: str, use_hotkey: bool = True, show_progress: bool = True)
    def set_speed(self, cpm: int)
    def set_error_rate(self, rate: float)
    def set_correction_rate(self, rate: float)
    def set_callbacks(self, on_start: Callable, on_stop: Callable, on_progress: Callable)
    def stop_typing(self)
    def stop_hotkey_listener(self)
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'pynput'` | Install pynput: `pip install pynput` |
| Keyboard simulation not working | Check system permissions, verify pynput installation |
| F6 hotkey not responding | Ensure application has focus, check accessibility permissions |
| GUI not launching | Install tkinter: `apt-get install python3-tk` (Linux) |

### Debug Mode

Enable debug output by setting environment variable:
```bash
export HUMAN_TYPER_DEBUG=1
python main.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Project Status

Active development. Current version: 1.0.0

### Roadmap
- [ ] Multi-language keyboard layout support
- [ ] Typing pattern profiles (fast/slow/accurate/sloppy)
- [ ] Recording and playback of typing sessions
- [ ] Statistical analysis of typing patterns
- [ ] WebSocket API for remote control