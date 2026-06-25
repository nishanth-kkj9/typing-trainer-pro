#!/usr/bin/env python3
"""
PyInstaller build script for Typing Trainer Pro
Creates standalone executable for Windows/Mac/Linux
"""
import PyInstaller.__main__
import sys
import os

# Get the absolute path to the project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, 'src')

PyInstaller.__main__.run([
    '--name=TypingTrainerPro',
    '--onedir',
    '--windowed',
    '--icon=' + os.path.join(ROOT_DIR, 'assets', 'icons', 'app_icon.ico'),
    '--add-data=' + os.path.join(SRC_DIR, 'typing_trainer', 'ui', 'styles.qss') + ':typing_trainer/ui/',
    '--add-data=' + os.path.join(SRC_DIR, 'typing_trainer', 'config', 'defaults.toml') + ':typing_trainer/config/',
    '--hidden-import=PySide6',
    '--hidden-import=sqlmodel',
    '--hidden-import=pydantic_settings',
    '--hidden-import=structlog',
    '--clean',
    '--noconfirm',
    os.path.join(SRC_DIR, 'typing_trainer', 'main.py'),
])

print("\n✅ Build complete! Executable located in dist/TypingTrainerPro/")
if sys.platform == 'win32':
    print("📦 Windows: dist/TypingTrainerPro/TypingTrainerPro.exe")
elif sys.platform == 'darwin':
    print("🍎 macOS: dist/TypingTrainerPro.app")
else:
    print("🐧 Linux: dist/TypingTrainerPro/TypingTrainerPro")
