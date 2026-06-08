"""
梦幻三国 - 内存读写引擎
通过 ReadProcessMemory 直接读取游戏内存，替代图色识别。
支持 Windows 10/11 的 VirtualAllocEx 远程内存分配（用于 AoB 扫描）。

