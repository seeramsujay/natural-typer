"""
Human Typer Mimicker - Cross-Platform GUI Version

A tkinter-based graphical interface for the Human Typer Mimicker.
Features F6 hotkey support and cross-platform compatibility.
"""

import json
import os
import platform
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Add src directory to path if running from different location
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from human_typer import PYNPUT_AVAILABLE, HumanTyper
    from config import (
        DEFAULT_SPEED_CPM,
        DEFAULT_ERROR_RATE,
        DEFAULT_CORRECTION_RATE,
        DEFAULT_WINDOW_SIZE,
        SETTINGS_FILE,
        MAX_TEXT_LENGTH_WARNING,
        MIN_SPEED_CPM,
        MAX_SPEED_CPM,
    )
except ImportError:
    # Fallback for different project structures
    sys.path.insert(0, os.path.dirname(src_dir))
    from human_typer import PYNPUT_AVAILABLE, HumanTyper
    from config import (
        DEFAULT_SPEED_CPM,
        DEFAULT_ERROR_RATE,
        DEFAULT_CORRECTION_RATE,
        DEFAULT_WINDOW_SIZE,
        SETTINGS_FILE,
        MAX_TEXT_LENGTH_WARNING,
        MIN_SPEED_CPM,
        MAX_SPEED_CPM,
    )


class HumanTyperGUI:
    """Cross-platform graphical interface for the Human Typer Mimicker."""

    def __init__(self, root):
        self.root = root
        self.root.title(f"Human Typer Mimicker - {platform.system()}")
        self.root.geometry("850x750")
        self.root.resizable(True, True)

        # Settings file path
        self.settings_file = SETTINGS_FILE

        # Configure style based on platform
        self.configure_style()

        # Initialize variables
        self.typer = None
        self.typing_thread = None
        self.is_typing = False
        self.hotkey_listening = False
        self.characters_typed = 0
        self.total_characters = 0

        # Load saved settings
        self.load_settings()

        # Sample texts
        self.sample_texts = {
            "Lorem Ipsum": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "The Quick Brown Fox": "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
            "Programming Text": "def hello_world():\\n    print('Hello, world!')\\n    return True\\n\\nif __name__ == '__main__':\\n    hello_world()",
            "Typing Test": "The five boxing wizards jump quickly. Pack my box with five dozen liquor jugs. How vexingly quick daft zebras jump!",
            "Platform Test": f"This text is being typed on {platform.system()} {platform.release()} with cross-platform Human Typer support!",
            "F6 Hotkey Demo": "Press F6 to start typing this text! Press F6 again to stop. This demonstrates the new hotkey functionality.",
        }

        # Create main interface
        self.create_widgets()
        self.update_status()

        # Apply loaded settings to widgets
        self.apply_loaded_settings()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_style(self):
        """Configure GUI style based on platform."""
        style = ttk.Style()

        # Platform-specific theming
        if platform.system() == "Windows":
            try:
                style.theme_use("vista")
            except:
                style.theme_use("clam")
        elif platform.system() == "Darwin":  # macOS
            try:
                style.theme_use("aqua")
            except:
                style.theme_use("clam")
        else:  # Linux and others
            style.theme_use("clam")

        # Custom style for accent button
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title with platform info
        title_text = f"Human Typer Mimicker - {platform.system()}"
        title_label = ttk.Label(main_frame, text=title_text, font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Platform:").grid(row=0, column=0, sticky=tk.W)
        platform_text = f"{platform.system()} {platform.release()}"
        ttk.Label(status_frame, text=platform_text).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(status_frame, text="Keyboard Simulation:").grid(row=1, column=0, sticky=tk.W)
        self.status_label = ttk.Label(
            status_frame, text="", foreground="green" if PYNPUT_AVAILABLE else "red"
        )
        self.status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(status_frame, text="Hotkey Support:").grid(row=2, column=0, sticky=tk.W)
        hotkey_status = "F6 Available ✓" if PYNPUT_AVAILABLE else "Not Available ✗"
        hotkey_color = "green" if PYNPUT_AVAILABLE else "red"
        ttk.Label(status_frame, text=hotkey_status, foreground=hotkey_color).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0)
        )

        # Text input frame
        text_frame = ttk.LabelFrame(main_frame, text="Text to Type", padding="10")
        text_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Text input area
        self.text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=8, width=60)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Default text
        default_text = "Hello! This is the Human Typer Mimicker with F6 hotkey support. Press F6 to start typing!"
        self.text_input.insert("1.0", default_text)

        # Button frame for text operations
        text_button_frame = ttk.Frame(text_frame)
        text_button_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Button(text_button_frame, text="Load from File", command=self.load_text_file).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(text_button_frame, text="Clear Text", command=self.clear_text).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # Sample text dropdown
        ttk.Label(text_button_frame, text="Sample:").pack(side=tk.LEFT, padx=(10, 5))
        self.sample_var = tk.StringVar()
        sample_combo = ttk.Combobox(
            text_button_frame,
            textvariable=self.sample_var,
            values=list(self.sample_texts.keys()),
            state="readonly",
            width=15,
        )
        sample_combo.pack(side=tk.LEFT, padx=(0, 5))
        sample_combo.bind("<<ComboboxSelected>>", self.load_sample_text)

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Typing Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)

        # Speed setting
        ttk.Label(settings_frame, text="Typing Speed (CPM):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.speed_var = tk.StringVar(value=str(DEFAULT_SPEED_CPM))
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)

        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=MIN_SPEED_CPM,
            to=MAX_SPEED_CPM,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self.update_speed_label,
        )
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.speed_label = ttk.Label(speed_frame, text="200 CPM", width=10)
        self.speed_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Error rate setting
        ttk.Label(settings_frame, text="Error Rate (%):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.error_var = tk.StringVar(value=str(int(DEFAULT_ERROR_RATE * 100)))
        error_frame = ttk.Frame(settings_frame)
        error_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)

        self.error_scale = ttk.Scale(
            error_frame,
            from_=0,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.error_var,
            command=self.update_error_label,
        )
        self.error_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.error_label = ttk.Label(error_frame, text="8%", width=10)
        self.error_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Correction rate setting
        ttk.Label(settings_frame, text="Correction Rate (%):").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.correction_var = tk.StringVar(value=str(int(DEFAULT_CORRECTION_RATE * 100)))
        correction_frame = ttk.Frame(settings_frame)
        correction_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)

        self.correction_scale = ttk.Scale(
            correction_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.correction_var,
            command=self.update_correction_label,
        )
        self.correction_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.correction_label = ttk.Label(correction_frame, text="85%", width=10)
        self.correction_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Keyboard simulation checkbox
        self.keyboard_var = tk.BooleanVar(value=PYNPUT_AVAILABLE)
        keyboard_check = ttk.Checkbutton(
            settings_frame, text="Use Keyboard Simulation", variable=self.keyboard_var
        )
        keyboard_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        if not PYNPUT_AVAILABLE:
            keyboard_check.configure(state="disabled")

        # Hotkey mode
        self.hotkey_var = tk.BooleanVar(value=True)
        hotkey_check = ttk.Checkbutton(
            settings_frame, text="Use F6 Hotkey (recommended)", variable=self.hotkey_var
        )
        hotkey_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        if not PYNPUT_AVAILABLE:
            hotkey_check.configure(state="disabled")

        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        # Start/Stop button
        self.start_button = ttk.Button(
            control_frame,
            text="Start Typing (F6)",
            command=self.start_typing,
            style="Accent.TButton",
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(
            control_frame, text="Stop (F6)", command=self.stop_typing, state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)

        # Hotkey status indicator
        self.hotkey_status_var = tk.StringVar(value="Hotkey: Inactive")
        self.hotkey_status_label = ttk.Label(
            progress_frame, textvariable=self.hotkey_status_var, font=("Arial", 10, "bold")
        )
        self.hotkey_status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Progress info
        self.progress_var = tk.StringVar(value="Ready to type...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate", maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))

        # Help frame with improved layout
        help_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        help_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        help_frame.columnconfigure(0, weight=1)
        help_frame.columnconfigure(1, weight=1)

        # Create two columns for instructions
        quick_start_text = (
            "Quick Start:\\n"
            "1. Enter or load text\\n"
            "2. Click 'Start Typing'\\n"
            "3. Switch to target app\\n"
            "4. Press F6 to begin"
        )

        controls_text = (
            "Controls:\\n"
            "• F6: Start/Stop typing\\n"
            "• Focus auto-releases\\n"
            "• 0.5s delay before typing\\n"
            "• Watch status indicator"
        )

        ttk.Label(help_frame, text=quick_start_text, justify=tk.LEFT).grid(
            row=0, column=0, sticky=tk.NW, padx=(0, 20)
        )
        ttk.Label(help_frame, text=controls_text, justify=tk.LEFT).grid(
            row=0, column=1, sticky=tk.NW
        )

        # Configure grid weights for responsiveness
        main_frame.rowconfigure(2, weight=1)

    def update_speed_label(self, value):
        """Update the speed label when scale changes."""
        speed = int(float(value))
        self.speed_label.config(text=f"{speed} CPM")
        # Auto-save settings on change
        self.save_settings()

    def update_error_label(self, value):
        """Update the error rate label when scale changes."""
        error = int(float(value))
        self.error_label.config(text=f"{error}%")
        # Auto-save settings on change
        self.save_settings()

    def update_correction_label(self, value):
        """Update the correction rate label when scale changes."""
        correction = int(float(value))
        self.correction_label.config(text=f"{correction}%")
        # Auto-save settings on change
        self.save_settings()

    def update_status(self):
        """Update the status display."""
        if PYNPUT_AVAILABLE:
            self.status_label.config(text="Available ✓", foreground="green")
        else:
            self.status_label.config(text="Not Available ✗", foreground="red")

    def load_text_file(self):
        """Load text from a file."""
        file_path = filedialog.askopenfilename(
            title="Select Text File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.text_input.delete("1.0", tk.END)
                    self.text_input.insert("1.0", content)
                messagebox.showinfo("Success", f"Loaded text from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def clear_text(self):
        """Clear the text input area."""
        self.text_input.delete("1.0", tk.END)

    def load_sample_text(self, event=None):
        """Load selected sample text."""
        selected = self.sample_var.get()
        if selected in self.sample_texts:
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", self.sample_texts[selected])

    def start_typing(self):
        """Start the typing process."""
        try:
            if self.is_typing:
                return

            # Get text to type
            text = self.text_input.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Warning", "Please enter some text to type.")
                return

            # Validate text length
            if len(text) > MAX_TEXT_LENGTH_WARNING:
                response = messagebox.askyesno(
                    "Warning",
                    f"The text is quite long ({len(text)} characters). This may take a while. Continue?",
                )
                if not response:
                    return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get text: {str(e)}")
            return

        try:
            # Create and configure typer
            use_keyboard = self.keyboard_var.get()
            self.typer = HumanTyper(use_keyboard=use_keyboard)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize typer: {str(e)}")
            return

        # Configure settings
        speed = int(float(self.speed_var.get()))
        error_rate = float(self.error_var.get()) / 100
        correction_rate = float(self.correction_var.get()) / 100

        self.typer.set_speed(speed)
        self.typer.set_error_rate(error_rate)
        self.typer.set_correction_rate(correction_rate)

        # Set up callbacks
        self.typer.set_callbacks(
            on_start=self.on_typing_start,
            on_stop=self.on_typing_stop,
            on_progress=self.on_typing_progress,
        )

        # Start typing
        use_hotkey = self.hotkey_var.get() and use_keyboard

        if use_hotkey:
            # Release focus from text input to prevent interference
            self.root.focus_set()
            self.hotkey_listening = True
            self.hotkey_status_var.set("Hotkey: LISTENING (Press F6)")
            self.hotkey_status_label.config(foreground="green")
            self.progress_var.set("Ready! Press F6 to start typing...")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.progress_var.set("Typing started...")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

        # Start in separate thread to avoid blocking GUI
        self.typing_thread = threading.Thread(
            target=lambda: self.typer.type_text(text, use_hotkey=use_hotkey, show_progress=False),
            daemon=True,
        )
        self.typing_thread.start()

        self.total_characters = len(text)
        self.characters_typed = 0

    def stop_typing(self):
        """Stop the typing process."""
        try:
            if self.typer:
                self.typer.stop_typing()
                self.typer.stop_hotkey_listener()

            self.on_typing_stop()
        except Exception as e:
            print(f"Error stopping typing: {e}")
            # Still try to update UI
            self.on_typing_stop()

    def on_typing_start(self):
        """Called when typing starts."""
        self.is_typing = True
        self.hotkey_listening = False
        self.root.after(0, lambda: self.hotkey_status_var.set("Hotkey: TYPING (Press F6 to stop)"))
        self.root.after(0, lambda: self.hotkey_status_label.config(foreground="orange"))
        self.root.after(0, lambda: self.progress_var.set("Typing in progress..."))
        self.root.after(0, lambda: self.progress_bar.config(mode="determinate"))

    def on_typing_stop(self):
        """Called when typing stops."""
        self.is_typing = False
        self.hotkey_listening = False
        self.root.after(0, lambda: self.hotkey_status_var.set("Hotkey: Inactive"))
        self.root.after(0, lambda: self.hotkey_status_label.config(foreground="black"))
        self.root.after(0, lambda: self.progress_var.set("Typing complete!"))
        self.root.after(0, lambda: self.start_button.config(state="normal"))
        self.root.after(0, lambda: self.stop_button.config(state="disabled"))
        self.root.after(0, lambda: self.progress_bar.config(value=100))

    def on_typing_progress(self, typed: int, total: int):
        """Called to update typing progress."""
        if total > 0:
            percentage = (typed / total) * 100
            self.root.after(
                0,
                lambda: self.progress_var.set(
                    f"Typing: {typed}/{total} characters ({percentage:.1f}%)"
                ),
            )
            self.root.after(0, lambda: self.progress_bar.config(value=percentage))

    def load_settings(self):
        """Load saved settings from file."""
        self.settings = {
            "speed": 200,
            "error_rate": 8,
            "correction_rate": 85,
            "use_keyboard": True,
            "use_hotkey": True,
            "window_geometry": "850x750",
        }

        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r") as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Could not load settings: {e}")

    def save_settings(self):
        """Save current settings to file."""
        try:
            current_settings = {
                "speed": int(float(self.speed_var.get())),
                "error_rate": int(float(self.error_var.get())),
                "correction_rate": int(float(self.correction_var.get())),
                "use_keyboard": self.keyboard_var.get(),
                "use_hotkey": self.hotkey_var.get(),
                "window_geometry": self.root.geometry(),
            }

            with open(self.settings_file, "w") as f:
                json.dump(current_settings, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")

    def apply_loaded_settings(self):
        """Apply loaded settings to GUI widgets."""
        try:
            # Apply window geometry
            self.root.geometry(self.settings["window_geometry"])

            # Apply speed setting
            self.speed_var.set(str(self.settings["speed"]))
            self.speed_label.config(text=f"{self.settings['speed']} CPM")

            # Apply error rate
            self.error_var.set(str(self.settings["error_rate"]))
            self.error_label.config(text=f"{self.settings['error_rate']}%")

            # Apply correction rate
            self.correction_var.set(str(self.settings["correction_rate"]))
            self.correction_label.config(text=f"{self.settings['correction_rate']}%")

            # Apply keyboard settings
            self.keyboard_var.set(self.settings["use_keyboard"] and PYNPUT_AVAILABLE)
            self.hotkey_var.set(self.settings["use_hotkey"] and PYNPUT_AVAILABLE)
        except Exception as e:
            print(f"Could not apply settings: {e}")

    def on_closing(self):
        """Handle window closing."""
        # Save settings before closing
        self.save_settings()

        if self.is_typing:
            self.stop_typing()

        if self.typer:
            self.typer.stop_hotkey_listener()

        self.root.destroy()

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = HumanTyperGUI(root)
    app.run()


if __name__ == "__main__":
    main()
