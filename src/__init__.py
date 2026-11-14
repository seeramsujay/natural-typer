"""
Human Typer Package

A library for simulating realistic human typing behavior.
"""

from .config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_CORRECTION_RATE,
    DEFAULT_ERROR_RATE,
    DEFAULT_SPEED_CPM,
)
from .human_typer import PYNPUT_AVAILABLE, HumanTyper

__version__ = APP_VERSION
__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_CORRECTION_RATE",
    "DEFAULT_ERROR_RATE",
    "DEFAULT_SPEED_CPM",
    "PYNPUT_AVAILABLE",
    "HumanTyper",
]
