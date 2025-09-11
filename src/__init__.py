"""
Human Typer Package

A library for simulating realistic human typing behavior.
"""

from .human_typer import HumanTyper, PYNPUT_AVAILABLE
from .config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_SPEED_CPM,
    DEFAULT_ERROR_RATE,
    DEFAULT_CORRECTION_RATE,
)

__version__ = APP_VERSION
__all__ = [
    "HumanTyper",
    "PYNPUT_AVAILABLE",
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_SPEED_CPM",
    "DEFAULT_ERROR_RATE",
    "DEFAULT_CORRECTION_RATE",
]