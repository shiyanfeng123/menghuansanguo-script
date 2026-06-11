"""日常脚本 - 对齐serveScript.py richangeScript逻辑"""
import time

_e = None


def richang(engine):
    global _e
    _e = engine
    sel = engine.richangSelection
    if not sel:
        sel = []
    times = 7 if "V" in sel else 5

    if "整" in sel:
        from ya_scripts.zhengdian import zhengdian
        zhengdian(engine)

    if "战" in sel:
        if not engine.find_str("洛阳", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图洛阳大道",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "洛阳", "", "", True,
            )
        time.sleep(1)
        for i in range(int(engine.zhanhunCount) if engine.zhanhunCount else 5):
            if engine.overed:
                return
            from ya_scripts.dungeon import zhanhun
            zhanhun(engine)

    if "镇" in sel:
        if not engine.find_str("洛阳", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图洛阳大道",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "洛阳", "", "", True,
            )
        time.sleep(1)
        for i in range(int(engine.lianyuCount) if engine.lianyuCount else 5):
            if engine.overed:
                return
            from ya_scripts.dungeon import zhanhun
            zhanhun(engine)

    if "噬" in sel:
        if not engine.find_str("洛阳", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图洛阳大道",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "洛阳", "", "", True,
            )
        time.sleep(1)
        for i in range(int(engine.shihunCount) if engine.shihunCount else 5):
            if engine.overed:
                return
            from ya_scripts.dungeon import zhanhun
            zhanhun(engine)

    if engine.overed:
        return

    if "溶" in sel:
        if not engine.find_str("绿林路", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图绿林路",
                "ya_assets/images/zhengdian/zhuojun.bmp",
                "绿林路", "", "", True,
            )
        time.sleep(1)
        for i in range(3):
            if engine.overed:
                return
            from ya_scripts.dungeon import rongdong
            rongdong(engine)
        time.sleep(1)

    if engine.overed:
        return

    if "丹" in sel:
        if not engine.find_str("五指峡谷", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图五指峡谷",
                "ya_assets/images/zhengdian/zhuojun.bmp",
                "五指峡谷", "驿站五指峡谷", "", True,
            )
        for i in range(5):
            if engine.overed:
                return
            from ya_scripts.dungeon import liandan
            liandan(engine)
        time.sleep(1)

    if engine.overed:
        return

    if "五" in sel:
        if not engine.find_str("野外西", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图野外西",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "野外西", "驿站城西", "", True,
            )
        time.sleep(1)
        for i in range(3):
            if engine.overed:
                return
            from ya_scripts.dungeon import wuxing
            wuxing(engine)
        time.sleep(1)

    if engine.overed:
        return

    if "云" in sel:
        if not engine.find_str("嵩山", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图嵩山",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "嵩山", "", "", True,
            )
        time.sleep(1)
        from ya_scripts.dungeon import yunyou_jy
        yunyou_jy(engine)
        time.sleep(1)

    if "名" in sel:
        if not engine.find_str("洛阳", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图洛阳大道",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "洛阳", "", "", True,
            )
        time.sleep(1)
        for i in range(8):
            if engine.overed:
                return
            from ya_scripts.dungeon import mingjiang_tz
            mingjiang_tz(engine)
        time.sleep(1)

    if "卖" in sel:
        time.sleep(1)
        engine.clear_hide_map()
        time.sleep(1)

    if engine.overed:
        return

    if "八" in sel:
        if not engine.find_str("许昌", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图许昌城",
                "ya_assets/images/zhengdian/xuchang.bmp",
                "许昌", "驿站许昌", "", True,
            )
        time.sleep(1)
        from ya_scripts.dungeon import bamen
        bamen(engine)
        time.sleep(1)

    if "鼠" in sel:
        if not engine.find_str("碧水地穴", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图碧水地穴",
                "ya_assets/images/zhengdian/xiangyang.bmp",
                "碧水地穴", "驿站襄阳", "", True,
            )
        time.sleep(1)
        from ya_scripts.dungeon import laoshu_jy
        laoshu_jy(engine)
        time.sleep(1)

    if "英" in sel:
        if not engine.find_pic(
            "ya_assets/images/hong/luanshipo.bmp",
            engine.dituLocation, 0,
        ):
            engine.go_in_ditu(
                "地图乱石坡",
                "ya_assets/images/zhengdian/xiangyang.bmp",
                "ya_assets/images/hong/luanshipo.bmp",
                "驿站襄阳", "", True,
            )
        time.sleep(1)
        for i in range(times):
            if engine.overed:
                return
            from ya_scripts.dungeon import yinghun
            yinghun(engine)

    if "庐" in sel:
        if not engine.find_pic(
            "ya_assets/images/sangumaolu/xinye.bmp",
            engine.dituLocation, 0,
        ):
            engine.go_in_ditu(
                "地图新野",
                "ya_assets/images/zhengdian/xiangyang.bmp",
                "ya_assets/images/sangumaolu/xinye.bmp",
                "驿站襄阳", "", True,
            )
        time.sleep(1)
        for i in range(5):
            if engine.overed:
                return
            from ya_scripts.dungeon import sangumaolu
            sangumaolu(engine)

    if engine.overed:
        return

    if "红" in sel:
        if not engine.find_str("虎牢关外", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图虎牢关外",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "虎牢关外", "", "", True,
            )
        time.sleep(1)
        for i in range(times):
            if engine.overed:
                return
            from ya_scripts.dungeon import hong
            hong(engine)

    if "渊" in sel:
        if not engine.find_str("虎牢关外", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图虎牢关外",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "虎牢关外", "", "", True,
            )
        time.sleep(1)
        for i in range(int(engine.qingyuanCount) if engine.qingyuanCount else 3):
            if engine.overed:
                return
            from ya_scripts.dungeon import qingyuan
            qingyuan(engine)

    if "帮" in sel:
        if not engine.find_str("城西", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图城西",
                "ya_assets/images/zhengdian/luoyang.bmp",
                "城西", "", "", True,
            )
        time.sleep(1)
        engine.findAndClickPic(
            "城西",
            "ya_assets/images/longdao/bangpai.bmp|ya_assets/images/longdao/bangpai1.bmp",
            "帮派大本营",
            engine.gameBottomLocation,
            "ya_assets/images/longdao/dabenying.bmp",
            engine.dituLocation,
            "0.107,0.156",
        )
        from ya_scripts.dungeon import bangpai
        bangpai(engine)

    if engine.overed:
        return

    if "官" in sel:
        if not engine.find_str("官渡", engine.dituLocation, 0):
            engine.go_in_ditu(
                "地图官渡",
                "ya_assets/images/zhengdian/xuchang.bmp",
                "官渡", "驿站城西", "驿站许昌", True,
            )
        time.sleep(1)
        from ya_scripts.dungeon import guandu_jy
        guandu_jy(engine)

    time.sleep(1)
    if engine.overed:
        return

    if "镜" in sel:
        engine.scriptName = "魔镜"
        from ya_scripts.dungeon import mojing
        mojing(engine)
    else:
        engine.scriptName = "官渡"
        from ya_scripts.dungeon import guandu
        guandu(engine)


def richang49(engine):
    global _e
    _e = engine
    tasks = [
        ("炼丹", 5), ("五行", 3), ("溶洞", 3), ("官渡", 1),
    ]
    _run_chain(tasks)


def level49_all(engine):
    global _e
    _e = engine
    tasks = [
        ("战魂楼(精英)", 6), ("嗜血战场(精英)", 7),
        ("炼丹", 5), ("五行", 3), ("溶洞", 3), ("官渡", 1),
    ]
    _run_chain(tasks)


def _run_chain(tasks):
    from ya_scripts import SCRIPT_REGISTRY
    for name, count in tasks:
        if _e.check_stop():
            return
        fn = SCRIPT_REGISTRY.get(name, (None,))[0]
        if fn:
            for _ in range(count):
                if _e.check_stop():
                    return
                fn(_e)
