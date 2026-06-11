"""整点脚本 - 逻辑对齐serveScript.py"""
import time
import random

_e = None

_ZD_LIST = [
    {"ditu": "地图碧波潭", "city": "ya_assets/images/zhengdian/bibotan.bmp", "findAddress": "碧波潭", "delX": [0], "delY": []},
    {"ditu": "地图皇宫东院", "city": "ya_assets/images/zhengdian/huanggongdongyuan.bmp", "findAddress": "皇宫东院", "delX": [0], "delY": []},
    {"ditu": "地图徐州", "city": "ya_assets/images/zhengdian/xuzhou.bmp", "findAddress": "徐州", "delX": [845], "delY": [44]},
    {"ditu": "地图魔魂山", "city": "ya_assets/images/zhengdian/mohunshan.bmp", "findAddress": "魔魂山", "delX": [0], "delY": []},
    {"ditu": "地图九黎族祭坛", "city": "ya_assets/images/zhengdian/jitan.bmp", "findAddress": "九黎族祭坛", "delX": [0], "delY": []},
    {"ditu": "地图魔谷西", "city": "ya_assets/images/zhengdian/moguxi.bmp", "findAddress": "魔谷西", "delX": [858], "delY": [41]},
    {"ditu": "地图密林", "city": "ya_assets/images/zhengdian/milin.bmp", "findAddress": "密林", "delX": [0], "delY": []},
    {"ditu": "地图野外北", "city": "ya_assets/images/zhengdian/zhuojun.bmp", "findAddress": "野外北", "delX": [845, 794, 761, 740], "delY": [48, 42, 44]},
    {"ditu": "地图野外西", "city": "ya_assets/images/zhengdian/luoyang.bmp", "findAddress": "野外西", "delX": [853], "delY": [45]},
    {"ditu": "地图万花谷", "city": "ya_assets/images/zhengdian/luoyang.bmp", "findAddress": "万花谷", "delX": [0], "delY": []},
    {"ditu": "地图绿林路", "city": "ya_assets/images/zhengdian/zhuojun.bmp", "findAddress": "绿林路", "delX": [0], "delY": []},
    {"ditu": "地图洛阳大道", "city": "ya_assets/images/zhengdian/luoyang.bmp", "findAddress": "洛阳", "delX": [0], "delY": []},
    {"ditu": "地图城西", "city": "ya_assets/images/zhengdian/luoyang.bmp", "findAddress": "城西", "delX": [0], "delY": []},
    {"ditu": "地图官渡", "city": "ya_assets/images/zhengdian/xuchang.bmp", "findAddress": "官渡", "delX": [0], "delY": []},
]

_ZD49_LIST = [
    {"ditu": "地图碧波潭", "city": "ya_assets/images/zhengdian/bibotan.bmp", "findAddress": "碧波潭", "delX": [0], "delY": []},
    {"ditu": "地图皇宫东院", "city": "ya_assets/images/zhengdian/huanggongdongyuan.bmp", "findAddress": "皇宫东院", "delX": [0], "delY": []},
    {"ditu": "地图徐州", "city": "ya_assets/images/zhengdian/xuzhou.bmp", "findAddress": "徐州", "delX": [845], "delY": [44]},
    {"ditu": "地图魔魂山", "city": "ya_assets/images/zhengdian/mohunshan.bmp", "findAddress": "魔魂山", "delX": [0], "delY": []},
    {"ditu": "地图九黎族祭坛", "city": "ya_assets/images/zhengdian/jitan.bmp", "findAddress": "九黎族祭坛", "delX": [0], "delY": []},
    {"ditu": "地图魔谷西", "city": "ya_assets/images/zhengdian/moguxi.bmp", "findAddress": "魔谷西", "delX": [858], "delY": [41]},
    {"ditu": "地图野外北", "city": "ya_assets/images/zhengdian/zhuojun.bmp", "findAddress": "野外北", "delX": [845, 794, 761, 740], "delY": [48, 42, 44]},
    {"ditu": "地图野外西", "city": "ya_assets/images/zhengdian/luoyang.bmp", "findAddress": "野外西", "delX": [853], "delY": [45]},
]


def zhengdian(engine):
    global _e
    _e = engine
    if engine.overed:
        return
    floor = engine.zhengdianFloor
    if floor in ["全打", "龙+全打", "蛇+全打"]:
        _new_zhengdian()
    elif floor in ["龙（新）", "虎+牛+兔+猴+羊（新）"]:
        _old_zhengdian()
    elif floor == "走路":
        _go_zhengdian()
    elif floor in ["49整点", "49蛇+全打", "49龙+全打"]:
        _go_zhengdian49()
    else:
        _old_zhengdian()


def _old_zhengdian():
    _e.print_and_speak(f"打{int(time.localtime().tm_hour) + 1}点的整点")
    if _e.check_stop():
        return
    time.sleep(1.5)
    openTalkXY = _e.waitFor("ya_assets/images/openTalk.bmp", _e.talkLocation)
    if openTalkXY:
        _e.click(openTalkXY.x, openTalkXY.y)
        for _ in range(4):
            time.sleep(0.2)
            _e.click(openTalkXY.x, openTalkXY.y)
    time.sleep(0.5)
    bangpaiTalkXY = _e.waitFor("帮派", _e.talkLocation, 5)
    if bangpaiTalkXY:
        _e.click(bangpaiTalkXY.x, bangpaiTalkXY.y)
    time.sleep(1.5)
    huodongTalkXY = _e.waitFor("活动", _e.talkLocation, 5)
    if huodongTalkXY:
        _e.click(huodongTalkXY.x, huodongTalkXY.y)
    if not _e.downTalkLocation:
        _e.downTalkLocation = _e.waitFor("下箭头", _e.talkLocation, 10)
    time.sleep(0.5)
    while True:
        if _e.check_stop():
            return
        current_time = time.localtime()
        if current_time.tm_min == 0 and current_time.tm_sec == 0:
            break
        time.sleep(0.05)
    if _e.zhengdianFloor == "龙（新）" and int(time.localtime().tm_hour) in [3, 7, 11, 15, 19, 23]:
        zhengdian_res = _e.feiZhengDian(
            "ya_assets/images/zhengdian/longshengxiao.bmp|ya_assets/images/zhengdian/longshengxiao1.bmp|ya_assets/images/zhengdian/longshengxiao2.bmp",
            "ya_assets/images/zhengdian/bibotan.bmp|ya_assets/images/zhengdian/huanggongdongyuan.bmp|ya_assets/images/zhengdian/xuzhou.bmp|ya_assets/images/zhengdian/mohunshan.bmp|ya_assets/images/zhengdian/jitan.bmp|ya_assets/images/zhengdian/moguxi.bmp|ya_assets/images/zhengdian/milin.bmp",
            True
        )
        print(zhengdian_res)
    zhengdian_res = _e.feiZhengDian("虎", "九黎族祭坛", True, None, "老虎")
    print(zhengdian_res)
    _e.zhengdian_by_xiaolvren("九黎族祭坛", 0, 0, [], 1)
    if _e.downTalkLocation:
        _e.click(_e.downTalkLocation.x, _e.downTalkLocation.y)
        for _ in range(4):
            _e.scroll_up(_e.downTalkLocation.x, _e.downTalkLocation.y)
            time.sleep(0.06)
    zhengdian_res = _e.feiZhengDian("牛", "魔魂山", True, "九黎族祭坛", zhengdian_res)
    print(zhengdian_res)
    _e.zhengdian_by_xiaolvren("魔魂山", 0, 0, [], 2)
    zhengdian_res = _e.feiZhengDian("兔", "徐州", True, "魔魂山", zhengdian_res)
    print(zhengdian_res)
    _e.zhengdian_by_xiaolvren("徐州", 0, int(845 + _e.locationX), [int(44 + _e.locationY)], 2)
    zhengdian_res = _e.feiZhengDian("猴", "幽暗密林", True, "徐州", zhengdian_res)
    print(zhengdian_res)
    _e.zhengdian_by_xiaolvren("幽暗密林", 0, int(764 + _e.locationX), [int(45 + _e.locationY)], 1)
    _e.feiCity("ya_assets/images/zhengdian/xiangyang.bmp")
    _e.zhengdian_by_xiaolvren("魔谷西", 2, int(858 + _e.locationX), [int(41 + _e.locationY)], 1)
    closeTalkXY = _e.waitFor("ya_assets/images/closeTalk.bmp", _e.talkLocation)
    if closeTalkXY:
        _e.click(closeTalkXY.x, closeTalkXY.y)
        for _ in range(4):
            time.sleep(0.2)
            _e.click(closeTalkXY.x, closeTalkXY.y)
    time.sleep(0.5)
    _e.zhengdian_flag = False
    _zhengdian_after_route()


def _new_zhengdian():
    _e.print_and_speak(f"打{int(time.localtime().tm_hour) + 1}点的整点")
    if _e.check_stop():
        return
    time.sleep(0.5)
    while True:
        if _e.check_stop():
            return
        current_time = time.localtime()
        if (current_time.tm_min == 59 and current_time.tm_sec == 58) or \
           (current_time.tm_min == 59 and current_time.tm_sec == 59):
            break
        time.sleep(1)
    if _e.zhengdianFloor in ["蛇+全打", "全打"] and _is_snake_hour():
        shuffled = _ZD_LIST.copy()
        random.shuffle(shuffled)
        for item in shuffled:
            if _e.overed:
                return
            _e.feiCity(item["city"])
            _e.zhengdian_by_xiaolvren(item["findAddress"], 0, 0, [], 1)
    if _e.zhengdianFloor in ["龙+全打", "蛇+全打", "全打"] and _is_dragon_hour():
        shuffled = _ZD_LIST.copy()
        random.shuffle(shuffled)
        for item in shuffled:
            if _e.overed:
                return
            _e.feiCity(item["city"])
            _e.zhengdian_by_xiaolvren(item["findAddress"], 0, 0, [], 1)
    shuffled = _ZD_LIST.copy()
    random.shuffle(shuffled)
    for item in shuffled:
        if _e.overed:
            return
        _e.feiCity(item["city"])
        _e.zhengdian_by_xiaolvren(item["findAddress"], 0, 0, [], 1)
    _e.zhengdian_flag = False
    _zhengdian_after_route()


def _go_zhengdian():
    _e.print_and_speak(f"打{int(time.localtime().tm_hour) + 1}点的整点")
    if _e.check_stop():
        return
    _e.confidenceNum = 0.6
    _e.feiCity("ya_assets/images/zhengdian/xiangyang.bmp")
    _e.confidenceNum = 0.9
    _e.click(int(900 - 900 * 0.167), int(580 * 0.137))
    time.sleep(0.5)
    _e.click(int(900 - 900 * 0.167), int(580 * 0.137))
    time.sleep(0.5)
    while True:
        if _e.check_stop():
            return
        current_time = time.localtime()
        if (current_time.tm_min == 59 and current_time.tm_sec == 59) or \
           (current_time.tm_min == 0 and current_time.tm_sec == 0):
            break
        time.sleep(1)
    _e.findAndClickPic(
        "九黎族遗迹",
        "九黎族祭坛", "九黎族祭坛",
        "九黎族祭坛", "九黎族祭坛",
        "0.187,0.137", ""
    )
    time.sleep(1)
    _e.zhengdian_by_xiaolvren("九黎族祭坛", 0, [])
    time.sleep(0.5)
    _e.feiCity("ya_assets/images/zhengdian/xiangyang.bmp")
    _e.zhengdian_by_xiaolvren("魔魂山", 0, [])
    _e.feiCity("ya_assets/images/zhengdian/xiangyang.bmp")
    time.sleep(1)
    _e.zhengdian_by_xiaolvren("魔谷西", 2, [(int(856 + _e.locationX), int(46 + _e.locationY)), (int(857 + _e.locationX), int(46 + _e.locationY))])
    time.sleep(0.5)
    _e.zhengdian_flag = False
    _zhengdian_after_route()


def _go_zhengdian49():
    _e.print_and_speak(f"打{int(time.localtime().tm_hour) + 1}点的整点")
    if _e.check_stop():
        return
    shuffled = _ZD49_LIST.copy()
    random.shuffle(shuffled)
    while True:
        if _e.check_stop():
            return
        current_time = time.localtime()
        if (current_time.tm_min == 59 and current_time.tm_sec == 58) or \
           (current_time.tm_min == 59 and current_time.tm_sec == 59):
            break
        time.sleep(1)
    if _e.zhengdianFloor in ["49蛇+全打", "49整点", "49龙+全打"] and _is_snake_hour():
        shuffled_she = _ZD49_LIST.copy()
        random.shuffle(shuffled_she)
        for item in shuffled_she:
            if _e.overed:
                return
            _e.feiCity(item["city"])
            _e.zhengdian_by_xiaolvren(item["findAddress"], 0, 0, [], 1)
    if _e.zhengdianFloor in ["49蛇+全打", "49龙+全打", "49整点"] and _is_dragon_hour():
        shuffled_long = _ZD49_LIST.copy()
        random.shuffle(shuffled_long)
        for item in shuffled_long:
            if _e.overed:
                return
            _e.feiCity(item["city"])
            _e.zhengdian_by_xiaolvren(item["findAddress"], 0, 0, [], 1)
    for item in shuffled:
        if _e.overed:
            return
        _e.feiCity(item["city"])
        _e.zhengdian_by_xiaolvren(item["findAddress"], 0, 0, [], 1)
    _e.zhengdian_flag = False
    _zhengdian_after_route()


def _is_dragon_hour():
    return int(time.localtime().tm_hour) in [3, 7, 11, 15, 19, 23]


def _is_snake_hour():
    return int(time.localtime().tm_hour) in [1, 5, 9, 13, 17, 21]


def _zhengdian_after_route():
    if _e.scriptName == "抢龙":
        return
    if int(time.localtime().tm_hour) == 0:
        after = _e.afterZreo
        if after == "官渡":
            _e.scriptName = "官渡"
            time.sleep(1)
            _e.feiFb("ya_assets/images/guandu/caocao1.bmp", is_elite=True)
            from ya_scripts.dungeon import guandu
            guandu(_e)
            return
        elif after == "魔镜":
            _e.scriptName = "魔镜"
            _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
            time.sleep(1)
            from ya_scripts.dungeon import mojing
            mojing(_e)
            return
        elif after == "日常":
            _e.scriptName = "日常"
            time.sleep(1)
            from ya_scripts.richang import richang
            richang(_e)
            return
        elif after == "49日常":
            _e.scriptName = "49日常"
            time.sleep(1)
            from ya_scripts.richang import richang49
            richang49(_e)
            return
        elif after == "战魂+红+整点":
            _e.scriptName = "战魂+红+整点"
            time.sleep(1)
            from ya_scripts.dungeon import zhanhun, hong
            zhanhun(_e)
            hong(_e)
            zhengdian(_e)
            return
        elif after == "战魂+红+魔镜+整点":
            _e.scriptName = "战魂+红+魔镜+整点"
            time.sleep(1)
            from ya_scripts.dungeon import zhanhun, hong, mojing
            zhanhun(_e)
            hong(_e)
            mojing(_e)
            zhengdian(_e)
            return
    if _e.scriptName == "官渡":
        time.sleep(1)
        _e.feiFb("ya_assets/images/guandu/caocao1.bmp", is_elite=True)
        from ya_scripts.dungeon import guandu
        guandu(_e)
    elif _e.scriptName in ("魔镜", "测试"):
        time.sleep(2)
        _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
        time.sleep(1)
        from ya_scripts.dungeon import mojing
        mojing(_e)
    elif _e.scriptName == "黑风":
        time.sleep(1)
        _e.feiCity("ya_assets/images/zhengdian/zhuojun.bmp")
        from ya_scripts.dungeon import heifeng
        heifeng(_e)
    elif _e.scriptName == "倭寇":
        time.sleep(1)
        _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
        time.sleep(2)
        _e.guajiAndzhengdianScript("ya_assets/images/guaji/wokou.bmp|ya_assets/images/guaji/wokou1.bmp")
    elif _e.scriptName == "龙珠":
        time.sleep(1)
        _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
        time.sleep(2)
        _e.guajiAndzhengdianScript("ya_assets/images/guaji/longchao.bmp|ya_assets/images/guaji/longchao1.bmp")
    elif _e.scriptName == "老鼠":
        time.sleep(1)
        _e.feiCity("ya_assets/images/zhengdian/xiangyang.bmp")
        time.sleep(2)
        _e.guajiAndzhengdianScript("ya_assets/images/guaji/bishuishuxue.bmp|ya_assets/images/guaji/bishuishuxue1.bmp")
    elif _e.scriptName == "森罗殿":
        time.sleep(1)
        _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
        time.sleep(2)
        _e.guajiAndzhengdianScript("ya_assets/images/guaji/senluodian.bmp|ya_assets/images/guaji/senluodian1.bmp")
    elif _e.scriptName == "挂机+整点":
        time.sleep(1)
        _e.guajiAndzhengdianScript()
