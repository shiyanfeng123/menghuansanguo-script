#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试所有必需的库是否可以正常导入"""

import sys

libraries = [
    ('keyboard', 'keyboard'),
    ('wxPython', 'wx'),
    ('psutil', 'psutil'),
    ('comtypes', 'comtypes'),
    ('pyttsx3', 'pyttsx3'),
    ('requests', 'requests'),
]

print("正在测试库导入...")
print("-" * 50)

failed = []
success = []

for lib_name, import_name in libraries:
    try:
        __import__(import_name)
        print(f"✓ {lib_name} ({import_name}) - 导入成功")
        success.append(lib_name)
    except ImportError as e:
        print(f"✗ {lib_name} ({import_name}) - 导入失败: {e}")
        failed.append(lib_name)

print("-" * 50)
print(f"\n成功: {len(success)}/{len(libraries)}")
if failed:
    print(f"失败: {len(failed)}/{len(libraries)}")
    print(f"失败的库: {', '.join(failed)}")
    sys.exit(1)
else:
    print("所有库都已成功安装并可以导入！")
    sys.exit(0)

