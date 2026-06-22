# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

comtypes_imports = collect_submodules('comtypes')
win32ctypes_imports = collect_submodules('win32ctypes')

a = Analysis(
    ['serveScript.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('serveAssets', 'serveAssets'),
        ('user_scripts', 'user_scripts'),
        ('version_info.txt', 'version_info.txt'),
    ],
    hiddenimports=[
        'Kanloong_combat_script',
        'ScriptEngine',
        'ScriptFactory',
        'wx.lib.scrolledpanel',
        'wx.lib.scrolledpanel.scrolled',
        'comtypes',
        'comtypes.client',
        'comtypes.stream',
        'comtypes.automation',
        'comtypes.typeinfo',
        'comtypes.tools.tlbparser',
        'comtypes.persist',
        'comtypes.server',
        'comtypes.shell',
        'comtypes.npsupport',
        'win32ctypes',
        'win32ctypes.pywin32',
        'win32ctypes.pywin32.pywintypes',
        'win32ctypes.pywin32.win32api',
        'pythoncom',
        'pywintypes',
        'win32api',
        'win32com',
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'pyttsx3.drivers.nsss',
        'pyttsx3.drivers.espeak',
        'psutil',
        'keyboard',
    ] + comtypes_imports + win32ctypes_imports,
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
    name='脚本v26.6.1',
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
    icon=['serveAssets\\images\\script1.ico'],
)
