"""
Human Typer Mimicker

A Python script that simulates human typing behavior with realistic
mistakes, speed fluctuations, and corrections. Uses actual keyboard
simulation to work with any application.

Cross-platform support for Windows, macOS, and Linux.
"""

import platform
import random
import sys
import threading
import time
from typing import Callable, Dict, List, Optional

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, Listener

    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not installed. Install with: pip install pynput")
    print("Falling back to console output mode.")


class HumanTyper:
    """Simulates human typing with realistic behavior patterns using actual keyboard input."""

    def __init__(self, use_keyboard: bool = True):
        """
        Initialize the HumanTyper.

        Args:
            use_keyboard: Whether to use actual keyboard simulation (requires pynput)
        """
        # Initialize keyboard controller if available
        self.use_keyboard = use_keyboard and PYNPUT_AVAILABLE
        if self.use_keyboard:
            self.keyboard_controller = keyboard.Controller()
        else:
            self.keyboard_controller = None
            if use_keyboard:
                print("Note: Keyboard simulation not available. Using console output.")

        # Hotkey control
        self.is_typing = False
        self.should_stop = False
        self.typing_thread = None
        self.hotkey_listener = None

        # Callbacks for events
        self.on_start_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_progress_callback: Optional[Callable[[int, int], None]] = None

        # Define keyboard layout for adjacent key errors (QWERTY)
        self.keyboard_layout = {
            "q": ["w", "a", "s"],
            "w": ["q", "e", "s", "d"],
            "e": ["w", "r", "d", "f"],
            "r": ["e", "t", "f", "g"],
            "t": ["r", "y", "g", "h"],
            "y": ["t", "u", "h", "j"],
            "u": ["y", "i", "j", "k"],
            "i": ["u", "o", "k", "l"],
            "o": ["i", "p", "l"],
            "p": ["o", "l"],
            "a": ["q", "s", "z"],
            "s": ["a", "d", "z", "x"],
            "d": ["s", "f", "x", "c"],
            "f": ["d", "g", "c", "v"],
            "g": ["f", "h", "v", "b"],
            "h": ["g", "j", "b", "n"],
            "j": ["h", "k", "n", "m"],
            "k": ["j", "l", "m"],
            "l": ["k", "o", "p"],
            "z": ["a", "s", "x"],
            "x": ["z", "s", "d", "c"],
            "c": ["x", "d", "f", "v"],
            "v": ["c", "f", "g", "b"],
            "b": ["v", "g", "h", "n"],
            "n": ["b", "h", "j", "m"],
            "m": ["n", "j", "k"],
            " ": ["n", "b", "v", "c"],
        }

        # Typing speed configuration (characters per minute)
        self.base_speed = 200  # Base typing speed
        self.speed_variance = 50  # Speed can vary by this amount
        self.pause_probability = 0.05  # Probability of a thinking pause

        # Error configuration
        self.typo_probability = 0.08  # Probability of making a typo
        self.correction_probability = 0.85  # Probability of correcting a typo
        self.double_char_probability = 0.03  # Probability of double-typing a character
        self.char_swap_probability = 0.02  # Probability of swapping adjacent characters

    def _get_typing_delay(self) -> float:
        """Calculate realistic typing delay between characters."""
        # Base delay from typing speed (convert CPM to seconds per character)
        base_delay = 60.0 / self.base_speed

        # Add natural variation
        variation = random.uniform(
            -self.speed_variance / self.base_speed, self.speed_variance / self.base_speed
        )
        delay = base_delay + variation

        # Ensure minimum delay
        return max(0.05, delay)

    def _should_make_typo(self) -> bool:
        """Determine if a typo should be made."""
        return random.random() < self.typo_probability

    def _get_adjacent_key_error(self, char: str) -> str:
        """Get a random adjacent key for the given character.
        
        Args:
            char: The character to get an adjacent key error for
            
        Returns:
            str: A randomly selected adjacent key, maintaining case
        """
        char_lower = char.lower()
        if char_lower in self.keyboard_layout:
            adjacent_keys = self.keyboard_layout[char_lower]
            error_char = random.choice(adjacent_keys)
            return error_char.upper() if char.isupper() else error_char
        return char

    def _simulate_thinking_pause(self) -> None:
        """Simulate a natural thinking pause.
        
        Randomly introduces realistic pauses that occur during human typing
        when the typist is thinking or hesitating.
        """
        if random.random() < self.pause_probability:
            pause_duration = random.uniform(0.5, 2.0)
            time.sleep(pause_duration)

    def _output_character(self, char: str):
        """Output a character either via keyboard simulation or console."""
        if self.should_stop:
            return

        if self.use_keyboard and self.keyboard_controller:
            try:
                # Handle special characters based on platform
                if char == "\n":
                    self.keyboard_controller.press(Key.enter)
                    self.keyboard_controller.release(Key.enter)
                elif char == "\t":
                    self.keyboard_controller.press(Key.tab)
                    self.keyboard_controller.release(Key.tab)
                else:
                    self.keyboard_controller.press(char)
                    self.keyboard_controller.release(char)
            except AttributeError as e:
                # Handle specific keyboard errors
                if "dead" in str(e).lower():
                    # Skip dead keys
                    pass
                else:
                    print(f"Warning: Could not type character '{char}': {e}")
            except Exception as e:
                # Log but continue typing
                print(f"Warning: Error typing character '{char}': {e}")
        else:
            try:
                print(char, end="", flush=True)
            except UnicodeEncodeError:
                # Fallback for unsupported characters in console
                print("?", end="", flush=True)

    def _output_backspace(self):
        """Output a backspace either via keyboard simulation or console."""
        if self.should_stop:
            return

        if self.use_keyboard and self.keyboard_controller:
            self.keyboard_controller.press(Key.backspace)
            self.keyboard_controller.release(Key.backspace)
        else:
            print("\b \b", end="", flush=True)

    def _type_character(self, char: str, target_char: str) -> bool:
        """
        Type a single character with potential errors.

        Args:
            char: The character to type (may include errors)
            target_char: The target character we want to end up with

        Returns:
            bool: True if we ended up with the correct character
        """
        if self.should_stop:
            return False

        # Check for double character
        if random.random() < self.double_char_probability:
            self._output_character(char)
            time.sleep(self._get_typing_delay())
            # Output backspace to remove the double character
            self._output_backspace()
            time.sleep(self._get_typing_delay() * 0.5)

        # Check for typo
        if self._should_make_typo() and char == target_char:
            # Type wrong character first
            wrong_char = self._get_adjacent_key_error(char)
            self._output_character(wrong_char)
            time.sleep(self._get_typing_delay())

            # Always correct the typo to ensure we end up with the right text
            if random.random() < self.correction_probability:
                # Backspace and correct immediately
                self._output_backspace()
                time.sleep(self._get_typing_delay() * 0.5)
            else:
                # Still need to correct to match target, just with a slight delay
                time.sleep(self._get_typing_delay() * 0.3)
                self._output_backspace()
                time.sleep(self._get_typing_delay() * 0.5)

        # Type the correct character
        self._output_character(target_char)
        time.sleep(self._get_typing_delay())

        return True

    def _type_word(self, word: str) -> bool:
        """
        Type a complete word with potential character swapping.

        Args:
            word: The target word to type

        Returns:
            bool: True if word was typed successfully
        """
        if self.should_stop:
            return False

        if len(word) < 2:
            for char in word:
                if self.should_stop:
                    return False
                self._type_character(char, char)
            return True

        # Check for character swapping within the word
        if random.random() < self.char_swap_probability:
            # Choose two adjacent characters to swap
            swap_index = random.randint(0, len(word) - 2)

            # Type characters up to the swap point normally
            for i in range(swap_index):
                if self.should_stop:
                    return False
                self._type_character(word[i], word[i])

            # Type the swapped characters
            self._type_character(word[swap_index + 1], word[swap_index + 1])
            time.sleep(self._get_typing_delay())
            self._type_character(word[swap_index], word[swap_index])
            time.sleep(self._get_typing_delay())

            # Type the rest normally
            for i in range(swap_index + 2, len(word)):
                if self.should_stop:
                    return False
                self._type_character(word[i], word[i])

            # Maybe notice and correct the swap
            if random.random() < self.correction_probability:
                # Backspace to the swap point
                chars_to_delete = len(word) - swap_index
                for _ in range(chars_to_delete):
                    if self.should_stop:
                        return False
                    self._output_backspace()
                    time.sleep(self._get_typing_delay() * 0.3)

                # Brief pause before retyping
                time.sleep(self._get_typing_delay() * 2)

                # Retype correctly from the swap point
                for i in range(swap_index, len(word)):
                    if self.should_stop:
                        return False
                    self._type_character(word[i], word[i])
            else:
                # Still need to correct to ensure final text matches
                # Backspace the swapped portion and retype correctly
                chars_to_delete = len(word) - swap_index
                for _ in range(chars_to_delete):
                    if self.should_stop:
                        return False
                    self._output_backspace()
                    time.sleep(self._get_typing_delay() * 0.2)

                # Retype correctly
                for i in range(swap_index, len(word)):
                    if self.should_stop:
                        return False
                    self._type_character(word[i], word[i])

            return True
        else:
            # Type normally
            for char in word:
                if self.should_stop:
                    return False
                self._type_character(char, char)
            return True

    def _typing_worker(self, text: str):
        """Worker function that runs in a separate thread for typing."""
        try:
            self.is_typing = True
            self.should_stop = False

            if self.on_start_callback:
                try:
                    self.on_start_callback()
                except Exception as e:
                    print(f"Warning: Error in start callback: {e}")

            # Split into words but preserve spaces
            char_count = 0
            total_chars = len(text)
            i = 0

            while i < len(text) and not self.should_stop:
                try:
                    # Add thinking pauses occasionally
                    self._simulate_thinking_pause()

                    if text[i] == " ":
                        # Handle space
                        self._output_character(" ")
                        time.sleep(self._get_typing_delay())
                        i += 1
                        char_count += 1
                    else:
                        # Find the end of the current word
                        word_start = i
                        while i < len(text) and text[i] != " ":
                            i += 1
                        word = text[word_start:i]

                        # Type the word
                        if not self._type_word(word):
                            break
                        char_count += len(word)

                    # Update progress
                    if self.on_progress_callback:
                        try:
                            self.on_progress_callback(char_count, total_chars)
                        except Exception as e:
                            print(f"Warning: Error in progress callback: {e}")

                except KeyboardInterrupt:
                    # User interrupted, stop gracefully
                    self.should_stop = True
                    break
                except Exception as e:
                    print(f"Warning: Error during typing: {e}")
                    # Continue typing despite error
                    i += 1
                    char_count += 1

        except Exception as e:
            print(f"Critical typing error: {e}")
        finally:
            self.is_typing = False
            if self.on_stop_callback:
                try:
                    self.on_stop_callback()
                except Exception as e:
                    print(f"Warning: Error in stop callback: {e}")

    def type_text(self, text: str, use_hotkey: bool = True, show_progress: bool = True):
        """
        Type the given text with human-like behavior using keyboard simulation.

        Args:
            text: The text to type (will be typed exactly as specified)
            use_hotkey: If True, wait for F6 key press to start typing
            show_progress: Whether to show progress messages
        """
        if show_progress:
            if self.use_keyboard:
                if use_hotkey:
                    print(f"Text ready to type: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                    print("Press F6 to start typing! (F6 again to stop)")
                    print("=" * 50)
                else:
                    print(f"Will start typing immediately...")
                    print(f"Target text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                    print("=" * 50)
            else:
                print(f"Simulating typing: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                print("=" * 50)

        if use_hotkey and self.use_keyboard:
            self._start_hotkey_listener(text)
        else:
            # Start typing immediately
            self.typing_thread = threading.Thread(target=self._typing_worker, args=(text,))
            self.typing_thread.daemon = True
            self.typing_thread.start()

            if not self.use_keyboard:
                self.typing_thread.join()  # Wait for completion in console mode

    def _start_hotkey_listener(self, text: str):
        """Start listening for F6 hotkey."""
        if not PYNPUT_AVAILABLE:
            return

        def on_press(key):
            try:
                if key == Key.f6:
                    if not self.is_typing:
                        # Add a small delay to allow focus switch
                        def delayed_start():
                            time.sleep(0.5)  # Half second delay for focus switch
                            if not self.should_stop:
                                self._typing_worker(text)

                        # Start typing in a thread with delay
                        self.typing_thread = threading.Thread(target=delayed_start)
                        self.typing_thread.daemon = True
                        self.typing_thread.start()
                    else:
                        # Stop typing
                        self.stop_typing()
            except AttributeError:
                pass

        # Stop any existing listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()

        # Start new listener
        self.hotkey_listener = Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def stop_typing(self):
        """Stop typing if currently in progress."""
        if self.is_typing:
            self.should_stop = True
            if self.typing_thread and self.typing_thread.is_alive():
                self.typing_thread.join(timeout=1.0)

    def stop_hotkey_listener(self):
        """Stop the hotkey listener."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None

    def set_speed(self, cpm: int):
        """Set the base typing speed in characters per minute."""
        self.base_speed = max(50, min(500, cpm))

    def set_error_rate(self, rate: float):
        """Set the typo probability (0.0 to 1.0)."""
        self.typo_probability = max(0.0, min(1.0, rate))

    def set_correction_rate(self, rate: float):
        """Set the correction probability (0.0 to 1.0)."""
        self.correction_probability = max(0.0, min(1.0, rate))

    def set_callbacks(
        self,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ):
        """Set callback functions for typing events."""
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
        self.on_progress_callback = on_progress

    def get_current_settings(self) -> Dict:
        """Get the current configuration settings."""
        return {
            "speed": self.base_speed,
            "error_rate": self.typo_probability,
            "correction_rate": self.correction_probability,
            "use_keyboard": self.use_keyboard,
            "platform": platform.system(),
            "pynput_available": PYNPUT_AVAILABLE,
        }

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_typing()
        self.stop_hotkey_listener()


