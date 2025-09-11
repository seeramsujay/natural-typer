#!/usr/bin/env python3
"""
Human Typer - Main Entry Point

Provides a unified entry point for both GUI and CLI interfaces.
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.config import DEFAULT_ERROR_RATE, DEFAULT_SPEED_CPM


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Human Typer - Realistic human typing simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                  # Launch GUI (if available)
  %(prog)s --cli            # Force CLI mode
  %(prog)s --text "Hello"   # Type specific text
  %(prog)s --speed 300      # Set typing speed to 300 CPM
        """,
    )
    
    # Interface selection
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument(
        "--cli", action="store_true", help="Force command-line interface"
    )
    interface_group.add_argument(
        "--gui", action="store_true", help="Force graphical interface"
    )
    
    # Typing parameters
    parser.add_argument(
        "--text",
        type=str,
        help="Text to type (CLI mode only)",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=DEFAULT_SPEED_CPM,
        help=f"Typing speed in CPM (default: {DEFAULT_SPEED_CPM})",
    )
    parser.add_argument(
        "--error-rate",
        type=float,
        default=DEFAULT_ERROR_RATE,
        help=f"Error rate 0.0-1.0 (default: {DEFAULT_ERROR_RATE})",
    )
    parser.add_argument(
        "--no-keyboard",
        action="store_true",
        help="Disable keyboard simulation (console output only)",
    )
    
    args = parser.parse_args()
    
    # Determine interface to use
    use_gui = False
    
    # Check if tkinter is available
    try:
        import tkinter
        gui_available = True
    except ImportError:
        gui_available = False
    
    if args.gui:
        if not gui_available:
            print("Error: GUI requested but tkinter is not available.", file=sys.stderr)
            print("Install tkinter or use --cli flag.", file=sys.stderr)
            sys.exit(1)
        use_gui = True
    elif args.cli:
        use_gui = False
    elif args.text:
        # If text is provided, use CLI by default
        use_gui = False
    elif gui_available:
        # Default to GUI if available
        use_gui = True
    else:
        # Fallback to CLI
        use_gui = False
    
    # Launch appropriate interface
    if use_gui:
        from src.human_typer_gui import main as gui_main
        gui_main()
    else:
        from src.cli import run_cli
        run_cli(
            text=args.text,
            speed=args.speed,
            error_rate=args.error_rate,
            use_keyboard=not args.no_keyboard,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)