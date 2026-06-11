"""活动类脚本 - 逻辑对齐serveScript.py"""
import time

_e = None


def xigua(engine):
    global _e
    _e = engine
    engine.heifengCount += 1
    print(f"第{engine.heifengCount}次西瓜保卫战.")
    _e.findAndClickPic(
        "ya_assets/images/xigua/nongshe.bmp",
        "ya_assets/images/xiaolvren.bmp|ya_assets/images/xigua/guanong.bmp|ya_assets/images/xigua/guanong1.bmp",
        "进入",
        "ya_assets/images/xigua/xiguatian.bmp",
        "ya_assets/images/xigua/xiguatian.bmp",
        "0.083,0.113", ""
    )
    _e.auto_move_and_click1(
        (735, 52, 894, 87),
        "ya_assets/images/xigua/xiaodao.bmp",
    )
    _e.findAndClickPic(
        "ya_assets/images/xigua/xiaodao.bmp",
        "ya_assets/images/chuansongmen.bmp",
        "ya_assets/images/chuansongmen.bmp",
        "ya_assets/images/xigua/nongshe.bmp",
        "ya_assets/images/xigua/nongshe.bmp",
        "", ""
    )
    return True


def gongcheng(engine):
    global _e
    _e = engine
    _e.beginFun()
    is_fei = _e.feiCity("ya_assets/images/zhengdian/zhuojun.bmp")
    if is_fei:
        _e.zhengdian_by_xiaolvren_for_gongcheng("野外北", 0,
                                                  [845, 794, 761, 740],
                                                  [48, 42, 44], 1)
        is_in = _e.waitFor("野外北", _e.dituLocation, 5)
        if is_in:
            _e.click(int(_e.locationX + 790), int(_e.locationY + 75))
            time.sleep(0.5)
            _e.zhengdian_by_xiaolvren_for_gongcheng("野外北", 0,
                                                      [845, 794, 761, 740],
                                                      [48, 42, 44], 1)
            is_in1 = _e.waitFor("野外北", _e.dituLocation, 5)
            if is_in1:
                _e.click(int(_e.locationX + 830), int(_e.locationY + 75))
                time.sleep(0.5)
                _e.zhengdian_by_xiaolvren_for_gongcheng("野外北", 0,
                                                          [845, 794, 761, 740],
                                                          [48, 42, 44], 1)
        time.sleep(0.5)
    is_fei = _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
    if is_fei:
        _e.zhengdian_by_xiaolvren_for_gongcheng("野外西", 0, [853], [45], 1)
        is_in = _e.waitFor("野外西", _e.dituLocation, 5)
        if is_in:
            _e.click(int(_e.locationX + 790), int(_e.locationY + 75))
            time.sleep(0.5)
            _e.zhengdian_by_xiaolvren_for_gongcheng("野外西", 0, [853], [45], 1)
            is_in1 = _e.waitFor("野外西", _e.dituLocation, 5)
            if is_in1:
                _e.click(int(_e.locationX + 830), int(_e.locationY + 75))
                time.sleep(0.5)
                _e.zhengdian_by_xiaolvren_for_gongcheng("野外西", 0, [853], [45], 1)
        time.sleep(0.5)
    is_fei = _e.feiCity("ya_assets/images/zhengdian/luoyang.bmp")
    if is_fei:
        _e.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
        is_in = _e.waitFor("万花谷", _e.dituLocation, 5)
        if is_in:
            _e.click(int(_e.locationX + 790), int(_e.locationY + 75))
            time.sleep(0.5)
            _e.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
            is_in1 = _e.waitFor("万花谷", _e.dituLocation, 5)
            if is_in1:
                _e.click(int(_e.locationX + 830), int(_e.locationY + 75))
                time.sleep(0.5)
                _e.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
        time.sleep(0.5)
    while _e.find_str("魔军", _e.gameBottomLocation, _e.color_format, _e.confidenceNum):
        mojun_loc = _e.find_str("魔军", _e.gameBottomLocation, _e.color_format, _e.confidenceNum)
        if mojun_loc:
            _e.click(mojun_loc.x, mojun_loc.y)
        gongcheng_loc = _e.waitFor("攻城", _e.gameBottomLocation, 5)
        if gongcheng_loc:
            _e.click(gongcheng_loc.x, gongcheng_loc.y)
        zdzd_loc = _e.waitFor("ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp", _e.gameBottomLocation, 5)
        if zdzd_loc:
            _e.waitFor("万花谷", _e.dituLocation, 50)
            time.sleep(1)


def longwangling(engine):
    global _e
    _e = engine
    if _e.overed:
        return
    print("开始打龙王令")
    time.sleep(0.5)
    _e.findAndClickPic(
        "洛阳",
        "ya_assets/images/longzhixintiao1.bmp",
        "ya_assets/images/longzhixintiao.bmp",
        "进龙王令",
        "进龙王令",
        "0.077,0.143", ""
    )
    in_pos = _e.waitFor("进龙王令", _e.gameBottomLocation)
    if in_pos:
        _e.click(in_pos.x, in_pos.y)
    waitRes = _e.waitForTwo(
        "ya_assets/images/queding.bmp",
        "摘星楼",
        _e.gameBottomLocation,
        _e.dituLocation,
    )
    if waitRes == 1:
        queding_pos = _e.waitFor("ya_assets/images/queding.bmp", _e.gameBottomLocation)
        if queding_pos:
            _e.click(queding_pos.x, queding_pos.y)
    if _e.overed:
        return
    if _e.check_stop():
        return
    _e.findAndClickPic(
        "摘星楼",
        "ya_assets/images/xiaolvren.bmp",
        "ya_assets/images/queding.bmp",
        "挑战龙",
        "挑战龙",
        "0.167,0.144", ""
    )
    _e.waitForAAndClickB("修罗级", "挑战龙")
    _e.waitForAAndClickB("挑战龙", "修罗级")
    _e.waitFor("ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp", _e.gameBottomLocation)
    _e.waitForAAndClickB("修罗级", "ya_assets/images/xiaolvren.bmp")
    _e.waitForAAndClickB("修罗级", "离开")


def yinmofu(engine):
    global _e
    _e = engine
    if _e.overed:
        return
    _e.guanDuCount += 1
    print(f"开始打第{_e.guanDuCount}张引魔符")
    if _e.guanDuCount % 100 == 0:
        print("卖装备")
        _e.clearBag()
        time.sleep(1)
    time.sleep(0.3)
    bagPos = _e.waitFor("ya_assets/images/beibao.bmp", _e.gameBottomLocation, 5)
    if bagPos:
        _e.click(bagPos.x, bagPos.y)
        time.sleep(0.5)
    time.sleep(0.1)
    _e.confidenceNum = 0.7
    _e.press_keys_until_image_found(
        "ya_assets/images/ymf.bmp|ya_assets/images/ymf1.bmp|ya_assets/images/ymf2.bmp|ya_assets/images/ymf3.bmp|ya_assets/images/ymf4.bmp",
        "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp",
        _e.gameLocation,
        _e.gameBottomLocation,
        "使用",
    )
    _e.confidenceNum = 0.9
    if _e.overed:
        return
    if _e.check_stop():
        return
    huodetongbi_pos = _e.waitFor("获得铜币", _e.gameBottomLocation)
    if huodetongbi_pos:
        _e.click(huodetongbi_pos.x, huodetongbi_pos.y)


def chuansongfu(engine):
    global _e
    _e = engine
    if _e.overed:
        return
    _e.guanDuCount += 1
    print(f"开始打第{_e.guanDuCount}张传送符")
    time.sleep(0.3)
    bagPos = _e.waitFor("ya_assets/images/beibao.bmp", _e.gameBottomLocation, 5)
    if bagPos:
        _e.click(bagPos.x, bagPos.y)
        time.sleep(0.5)
    time.sleep(0.1)
    _e.confidenceNum = 0.5
    _e.press_keys_until_image_found(
        "ya_assets/images/chuansongfu.bmp|ya_assets/images/chuansongfu1.bmp|ya_assets/images/chuansongfu2.bmp|ya_assets/images/chuansongfu3.bmp|ya_assets/images/chuansongfu4.bmp|ya_assets/images/chuansongfu5.bmp",
        "天外天",
        _e.gameLocation,
        _e.dituLocation,
        "使用",
    )
    _e.confidenceNum = 0.9
    chanchu_pos = [
        "0.121,0.112", "0.104,0.103", "0.078,0.108",
        "0.067,0.118", "0.046,0.106", "0.038,0.113",
    ]
    _e.key_press("e")
    time.sleep(0.5)
    _e.findAndClickPic(
        "天外天",
        "地穴蟾蜍",
        "ya_assets/images/richang/chanchu.bmp",
        "ya_assets/images/zdzd.bmp",
        "ya_assets/images/zdzd.bmp",
        "0.14,0.119", ""
    )
    for i in range(6):
        _e.findAndClickPic(
            "天外天",
            "地穴蟾蜍",
            "ya_assets/images/richang/chanchu.bmp",
            "ya_assets/images/zdzd.bmp",
            "ya_assets/images/zdzd.bmp",
            chanchu_pos[i], ""
        )
    waitForTwoRes = _e.waitForTwo("出现", "运气太烂", _e.gameBottomLocation)
    if waitForTwoRes == 2:
        print("没有守财奴")
        return True
    time.sleep(0.5)
    _e.key_press("g")
    if _e.overed:
        return
    if _e.check_stop():
        return
    _e.waitFor("洛阳", _e.dituLocation)
