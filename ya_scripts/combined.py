"""
组合脚本：战魂+红+整点、战魂+红+魔镜+整点
移植自 serveScript.py 中 guanduAndHongAndZd() / mojingAndHongAndZd()
"""

import time
from datetime import datetime, timedelta


def _wait_for_zhengdian():
    now = datetime.now()
    if now.minute >= 58:
        return
    next_hour = (now.hour + 1) % 24
    target_times = [
        datetime(now.year, now.month, now.day, 11, 58, 0),
        datetime(now.year, now.month, now.day, 13, 58, 0),
        datetime(now.year, now.month, now.day, 16, 58, 0),
        datetime(now.year, now.month, now.day, 21, 58, 0),
        datetime(now.year, now.month, now.day, 22, 58, 0),
        datetime(now.year, now.month, now.day, 23, 58, 0),
    ]
    for t in target_times:
        if t > now:
            wait_seconds = (t - now).total_seconds()
            print(f"等待整点({t.strftime('%H:%M')})，还需{wait_seconds / 60:.0f}分钟...")
            time.sleep(min(wait_seconds, 10))
            return


def guandu_hong_zd(engine):
    from ya_scripts.dungeon import zhanhun, hong
    from ya_scripts.zhengdian import zhengdian

    zhanhun_count = getattr(engine, 'zhanhunCount', 3)
    hong_count = 2

    print("开始 战魂+红+整点 组合脚本")
    engine.scriptName = "战魂+红+整点"

    while not engine.overed:
        if engine.check_stop():
            return

        for _ in range(zhanhun_count):
            if engine.overed or engine.check_stop():
                return
            zhanhun(engine)
            time.sleep(1)

        for _ in range(hong_count):
            if engine.overed or engine.check_stop():
                return
            hong(engine)
            time.sleep(1)

        engine.outScript(role="main")
        time.sleep(2)

        _wait_for_zhengdian()
        if engine.overed or engine.check_stop():
            return

        engine.zhengdian_flag = False
        zhengdian(engine)
        time.sleep(2)

        engine.scriptName = "战魂+红+整点"


def mojing_hong_zd(engine):
    from ya_scripts.dungeon import zhanhun, hong, mojing
    from ya_scripts.zhengdian import zhengdian

    zhanhun_count = getattr(engine, 'zhanhunCount', 3)
    hong_count = 2
    mojing_count = 2

    print("开始 战魂+红+魔镜+整点 组合脚本")
    engine.scriptName = "战魂+红+魔镜+整点"

    while not engine.overed:
        if engine.check_stop():
            return

        for _ in range(zhanhun_count):
            if engine.overed or engine.check_stop():
                return
            zhanhun(engine)
            time.sleep(1)

        for _ in range(hong_count):
            if engine.overed or engine.check_stop():
                return
            hong(engine)
            time.sleep(1)

        for _ in range(mojing_count):
            if engine.overed or engine.check_stop():
                return
            mojing(engine)
            time.sleep(1)

        engine.outScript(role="main")
        time.sleep(2)

        _wait_for_zhengdian()
        if engine.overed or engine.check_stop():
            return

        engine.zhengdian_flag = False
        zhengdian(engine)
        time.sleep(2)

        engine.scriptName = "战魂+红+魔镜+整点"
