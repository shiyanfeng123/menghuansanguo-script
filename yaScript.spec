# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ya_game_scripts.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images', 'images'),
        ('serveAssets', 'serveAssets'),
        ('ya_assets', 'ya_assets'),
    ],
    hiddenimports=[
        'ya_engine',
        'ya_kanloong_combat',
        'ya_auth',
        'ScriptEngine',
        'ScriptFactory',
    ],
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
    a.binaries,
    a.datas,
    [],
    name='梦幻三国脚本',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['images\\script.ico'],
)
