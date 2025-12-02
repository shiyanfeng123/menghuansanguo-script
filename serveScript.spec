# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['serveScript.py'],
    pathex=[],
    binaries=[],
    datas=[('serveAssets', 'serveAssets'),('version_info.txt', 'version_info.txt')],
    hiddenimports=[
        'Kanloong_combat_script_copy',
        'wx.lib.scrolledpanel',
        'wx.lib.scrolledpanel.scrolled',
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
    name='脚本v25.12.1',
    version='version_info.txt',  # 元组格式
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
    icon=['serveAssets\\images\\script.ico'],
)
