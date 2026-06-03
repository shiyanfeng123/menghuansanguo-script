# -*- coding: utf-8 -*-
# 自动生成脚本: 111
# 生成时间: 2026-06-03 16:12:46
# 总步骤: 4

import time


class Script_111:
    def __init__(self, thread):
        self.thread = thread
        self.dm = thread.dm
        self.base = 'user_scripts/111'

    def run(self):
        print('[111] 开始执行')

        # === 传送到地图 ===
        print('飞往官渡...')
        # TODO: 调用 go_in_ditu

        # === 等待出现 ===
        path = self.thread.get_resource_path(f'{self.base}/')
        result = self.thread.waitFor(path, (0,0,900,580), timeout=30)
        if not result:
            print('等待超时, 跳过')

        # === 等待 ===
        time.sleep(3.0)

        # === 点击文字 ===
        result = self.dm.FindStrFastE(0,0,900,580, '', '通用游戏字体(白绿黄青红黑底)', 0.9)
        parts = result.split('|')
        if int(parts[0]) >= 0:
            self.dm.MoveTo(int(parts[1])+15, int(parts[2])+15)
            time.sleep(0.3)
            self.dm.LeftClick()
            time.sleep(2.0)
            print(f'点击文字\'\'成功')
        else:
            print(f'未找到文字\'\', 跳过')

        print('[111] 执行完成')