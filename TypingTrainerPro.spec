# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/workspace/src/typing_trainer/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/workspace/src/typing_trainer/ui/styles.qss', 'typing_trainer/ui/'), ('/workspace/src/typing_trainer/config/defaults.toml', 'typing_trainer/config/')],
    hiddenimports=['PySide6', 'sqlmodel', 'pydantic_settings', 'structlog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TypingTrainerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TypingTrainerPro',
)
