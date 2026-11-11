import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from human_typer import HumanTyper

def test_human_typer_init():
    typer = HumanTyper(use_keyboard=False)
    assert typer.use_keyboard is False
    settings = typer.get_current_settings()
    assert "speed" in settings
    assert "error_rate" in settings
    assert "correction_rate" in settings

def test_set_speed_and_rates():
    typer = HumanTyper(use_keyboard=False)
    typer.set_speed(250)
    typer.set_error_rate(0.05)
    typer.set_correction_rate(0.95)

    settings = typer.get_current_settings()
    assert settings["speed"] == 250
    assert settings["error_rate"] == 0.05
    assert settings["correction_rate"] == 0.95

def test_adjacent_key_error():
    typer = HumanTyper(use_keyboard=False)
    # Testing key error mapping for known keys
    err = typer._get_adjacent_key_error('s')
    assert isinstance(err, str)
    assert len(err) == 1

def test_typing_delay():
    typer = HumanTyper(use_keyboard=False)
    typer.set_speed(300)
    delay = typer._get_typing_delay()
    assert delay > 0.0
