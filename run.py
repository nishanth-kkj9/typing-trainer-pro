#!/usr/bin/env python3
"""Convenience script to run Typing Trainer Pro without pip install."""
import sys
from pathlib import Path

# Add src/ to path so imports resolve when running directly
src = Path(__file__).parent / "src"
sys.path.insert(0, str(src.resolve()))

from typing_trainer.main import main

main()
