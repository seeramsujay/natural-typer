"""
Command-line interface for Human Typer.
"""

import platform
from typing import Optional

from .config import SAMPLE_TEXTS
from .human_typer import PYNPUT_AVAILABLE, HumanTyper


def run_interactive_demo(typer: HumanTyper) -> None:
    """Run an interactive demonstration of the typer."""
    current_platform = platform.system()
    
    print(f"\nDemo Mode - {len(SAMPLE_TEXTS)} sample texts available")
    print("-" * 50)
    
    sample_list = list(SAMPLE_TEXTS.values())[:4]  # Use first 4 samples for demo
    
    for i, text in enumerate(sample_list, 1):
        print(f"\nSample {i}: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if typer.use_keyboard:
            input(f"Press Enter when ready to set up sample {i}...")
            typer.type_text(text, use_hotkey=True)
            input("Press Enter to continue to next sample (or Ctrl+C to exit)...")
            typer.stop_hotkey_listener()
        else:
            input(f"Press Enter to simulate typing sample {i}...")
            typer.type_text(text, use_hotkey=False)
        
        print("-" * 50)
    
    print("\nDemo complete!")


def run_cli(
    text: Optional[str] = None,
    speed: int = 200,
    error_rate: float = 0.08,
    use_keyboard: bool = True,
) -> None:
    """
    Run the CLI interface.
    
    Args:
        text: Text to type (if None, runs interactive demo)
        speed: Typing speed in CPM
        error_rate: Error rate (0.0-1.0)
        use_keyboard: Whether to use keyboard simulation
    """
    current_platform = platform.system()
    
    print(f"Human Typer - Command Line Interface")
    print(f"Platform: {current_platform}")
    print("=" * 50)
    
    # Check keyboard availability
    if use_keyboard and not PYNPUT_AVAILABLE:
        print("Warning: pynput not available. Install with: pip install pynput")
        print("Falling back to console output mode.")
        use_keyboard = False
    
    # Create and configure typer
    typer = HumanTyper(use_keyboard=use_keyboard)
    typer.set_speed(speed)
    typer.set_error_rate(error_rate)
    
    if text:
        # Type provided text
        print(f"\nTyping: {text[:50]}{'...' if len(text) > 50 else ''}")
        if use_keyboard:
            print("Switch to your target application...")
            print("Press F6 to start typing, F6 again to stop.")
        print("=" * 50)
        
        typer.type_text(text, use_hotkey=use_keyboard, show_progress=True)
        
        if use_keyboard:
            # Wait for typing to complete
            import time
            while typer.is_typing:
                time.sleep(0.1)
            typer.stop_hotkey_listener()
    else:
        # Run interactive demo
        if use_keyboard:
            response = input("Use keyboard simulation? (y/n, default=y): ").lower()
            if response == 'n':
                typer = HumanTyper(use_keyboard=False)
                typer.set_speed(speed)
                typer.set_error_rate(error_rate)
        
        run_interactive_demo(typer)