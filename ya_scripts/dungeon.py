# -*- coding: utf-8 -*-
"""副本脚本集合 - 所有副本类型脚本函数"""
import time

_e = None
_zhanhun_floor = 21
_mojing_mode = "mihuan"
_heifeng_mode = "da"


def guandu(engine):
    """官渡副本"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_guandu_once, loop_mode="infinite", count=1, zhengdian_at=58, fallback="guandu")


def _guandu_once():
    isIn = _e.waitFor("官渡", timeout=5)
    if not isIn:
        _e.feiFb("副本曹操", is_elite=True)
    _e.findAndClickPic(
        "官渡",
        "ya_assets/images/guandu/caocao1.bmp", "ya_assets/images/guandu/caocao.bmp",
        "进入", "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp",
        "0.038,0.134", ""
    )
    if _e.check_stop():
        return
    _e.color_format = "b@0ff000-000000|00ff00-000000|ffff00-000000|0ff000-000000|fff200-000000"
    _e.waitForAAndClickB("曹操大帐", "进官渡1")
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "曹操大帐",
        "曹袁战场", "曹袁战场",
        "曹袁战场", "曹袁战场",
        "0.078,0.127", ""
    )
    if _e.check_stop():
        return
    hbj_poss = ["0.111,0.125", "0.085,0.125", "0.065,0.123"]
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "曹袁战场",
        "河北军", "ya_assets/images/guandu/hbj2.bmp|ya_assets/images/guandu/hbj1.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.165,0.124", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "曹袁战场",
        "河北军", "河北军",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.144,0.126", ""
    )
    for pos in hbj_poss:
        _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        _e.findAndClickPic(
            "曹袁战场",
            "河北军", "河北军",
            "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
            pos, ""
        )
        _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "曹袁战场",
        "河北军", "ya_assets/images/guandu/hbj2.bmp|ya_assets/images/guandu/hbj1.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.052,0.125", ""
    )
    if _e.overed:
        return
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "曹袁战场",
        "ya_assets/images/guandu/yanliang.bmp", "ya_assets/images/guandu/yanliang1.bmp|ya_assets/images/guandu/yanliang2.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.097,0.126", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    if _e.check_stop():
        return
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "曹袁战场",
        "官渡文丑", "ya_assets/images/guandu/wenchou1.bmp|ya_assets/images/guandu/wenchou2.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.081,0.122", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    if _e.check_stop():
        return
    _e.findAndClickPic(
        "曹袁战场",
        "ya_assets/images/xiaolvren.bmp|ya_assets/images/guandu/caochengxiang.bmp", "知道了",
        "鸟巢粮仓", "鸟巢粮仓",
        "0.192,0.129", ""
    )
    _e.findAndClickPic(
        "鸟巢粮仓",
        "魂殿", "魂殿",
        "魂殿", "魂殿",
        "0.184,0.134", ""
    )
    _e.findAndClickPic(
        "魂殿",
        "文丑之魂", "ya_assets/images/guandu/wenchou3.bmp|ya_assets/images/guandu/wenchou4.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.167,0.103", ""
    )
    _e.hundianFlag = True
    _e.findAndClickPic(
        "魂殿",
        "鸟巢粮仓", "鸟巢粮仓",
        "鸟巢粮仓", "鸟巢粮仓",
        "0.138,0.12", ""
    )
    if _e.overed:
        return
    if _e.check_stop():
        return
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "鸟巢粮仓",
        "ya_assets/images/guandu/cyq.bmp|ya_assets/images/guandu/cyq3.bmp", "淳于琼",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.161,0.129", ""
    )
    _e.hundianFlag = False
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    if _e.check_stop():
        return
    if _e.overed:
        return
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "鸟巢粮仓",
        "官渡袁绍", "ya_assets/images/guandu/yuanshao1.bmp|ya_assets/images/guandu/yuanshao2.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.152,0.124", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    if _e.overed:
        return
    if _e.check_stop():
        return
    _e.outScript("鸟巢粮仓")


def hong(engine):
    """嗜血战场"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_hong_once, loop_mode="count", count=7, fallback="guandu")


def _hong_once():
    _e.feiFb("地图虎牢关外", is_elite=True)
    _e.findAndClickPic(
        "虎牢关外",
        "ya_assets/images/zhengdian/xiaolvren2.bmp|ya_assets/images/zhengdian/xiaolvren.bmp", "ya_assets/images/zhengdian/xiaolvren2.bmp|ya_assets/images/zhengdian/xiaolvren.bmp",
        "进入|进精英", "进入|进精英",
        "0.127,0.129", ""
    )
    _e.waitForAAndClickB("军营", "进入|进精英")
    _e.confidenceNum = 0.9
    if _e.overed:
        return
    isIn = _e.waitFor("军营", timeout=8)
    if not isIn:
        print("红没次数了")
        return False
    if _e.overed:
        return
    gonbin_poss = ["0.121,0.125", "0.064,0.125", "0.036,0.12"]
    for i in range(3):
        if _e.overed:
            return
        _e.findAndClickPic(
            "军营",
            "弓兵", "弓兵",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            gonbin_poss[i], ""
        )
    _e.findAndClickPic(
        "军营",
        "军粮营", "军粮营",
        "军粮营", "军粮营",
        "0.158,0.146", "", "down"
    )
    huweibin_poss = ["0.144,0.124", "0.1,0.118", "0.035,0.124"]
    for i in range(2):
        if _e.overed:
            return
        _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        _e.findAndClickPic(
            "军粮营",
            "护卫兵", "ya_assets/images/hong/huweibin1.bmp|ya_assets/images/hong/huweibin2.bmp",
            "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
            huweibin_poss[i], ""
        )
        _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.waitFor("军粮营", timeout=5)
    _e.addBloud()
    _e.findAndClickPic(
        "军粮营",
        "护粮将领", "ya_assets/images/hong/huliangjianglin1.bmp|ya_assets/images/hong/huliangjianglin2.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        huweibin_poss[2], ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "军粮营",
        "训兵营", "训兵营",
        "训兵营", "训兵营",
        "0.015,0.127", ""
    )
    qibin_poss = ["0.136,0.112", "0.104,0.148", "0.06,0.124", "0.121,0.131"]
    for i in range(3):
        _e.findAndClickPic(
            "训兵营",
            "骑兵", "ya_assets/images/hong/qibin1.bmp|ya_assets/images/hong/qibin2.bmp",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            qibin_poss[i], ""
        )
    if _e.overed:
        return
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.waitFor("训兵营", timeout=5)
    _e.addBloud()
    _e.findAndClickPic(
        "训兵营",
        "训兵将领", "ya_assets/images/hong/shenjinxi1.bmp|ya_assets/images/hong/shenjinxi2.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        qibin_poss[3], ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "训兵营",
        "军营", "军营",
        "军营", "军营",
        "0.106,0.091", ""
    )
    if _e.overed:
        return
    _e.addBloud()
    _e.findAndClickPic(
        "军营",
        "ya_assets/images/hong/chuansongmen3.bmp", "ya_assets/images/hong/chuansongmen3.bmp",
        "帐篷", "帐篷",
        "", ""
    )
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "帐篷",
        "控魂巫师", "控魂巫师",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.09,0.127", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.outScript("帐篷")
    return True


_ZHANHUN_BOSS = {
    1: "张宝", 2: "张梁", 3: "张角", 4: "文丑",
    5: "颜良", 6: "华雄", 7: "孙策", 8: "典韦",
    9: "郭嘉", 10: "刘备", 11: "曹操", 12: "袁绍",
    13: "张飞", 14: "大乔", 15: "关羽", 16: "吕布",
    17: "张飞", 18: "关羽", 19: "吕布", 20: "吕布",
    21: "刘备", 22: "袁绍", 23: "曹操", 24: "吕布", 25: "吕布",
}


def zhanhun(engine, floor=25):
    global _e, _zhanhun_floor
    _e = engine
    _zhanhun_floor = floor
    engine.beginFun()
    engine.run_loop(_zhanhun_once, loop_mode="count", count=1, fallback="guandu")


def _zhanhun_once():
    outFbLocation = _e.find_pic_or_str(
        "ya_assets/images/outFb.bmp|ya_assets/images/outFb1.bmp", _e.gameLocation, 0
    )
    if outFbLocation:
        _e.click(outFbLocation.x, outFbLocation.y)
        _e.click(outFbLocation.x, outFbLocation.y)
        time.sleep(2)
    if _e.overed:
        return
    _e.feiFb("地图洛阳大道", is_elite=True)
    _e.findAndClickPic(
        "ya_assets/images/zhanhun/luoyang.bmp",
        "ya_assets/images/zhanhun/zhanhuntiaozhan.bmp", "ya_assets/images/zhanhun/zhanhuntiaozhan1.bmp",
        "进精英", "进精英",
        "0.067,0.132", ""
    )
    _e.waitForAAndClickB("ya_assets/images/zhanhun/1.bmp", "进精英")
    isIn = _e.waitFor("战魂", timeout=15)
    if not isIn:
        print("战魂没次数了")
        return False
    for f in range(1, _zhanhun_floor + 1):
        if _e.overed:
            return
        boss = _ZHANHUN_BOSS[f]
        boss_img2 = boss
        if boss == "张梁":
            boss_img2 = "ya_assets/images/zhanhun/zhangliang1.bmp|ya_assets/images/zhanhun/zhangliang2.bmp"
        elif boss == "刘备":
            boss_img2 = "ya_assets/images/zhanhun/liubei.bmp|ya_assets/images/zhanhun/liubei1.bmp"
        _e.findAndClickPic(
            f"ya_assets/images/zhanhun/{f}.bmp",
            boss, boss_img2,
            "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
            "0.098,0.113", ""
        )
        if f == 20:
            _e.waitFor("ya_assets/images/xiulian.bmp", timeout=30)
            if _zhanhun_floor == 20:
                _e.outScript("战魂")
                return True
        if f >= 20 and f < _zhanhun_floor:
            next_boss = _ZHANHUN_BOSS[f + 1]
            _e.waitForAAndClickB(
                f"ya_assets/images/zhanhun/{f + 1}.bmp",
                "ya_assets/images/zhanhun/chuansongmen.bmp"
            )
        if f >= 21:
            _e.waitFor("ya_assets/images/xiulian.bmp", timeout=30)
            _e.addBloud()
            res = _e.waitForTwo(
                f"ya_assets/images/zhanhun/{f}.bmp",
                "洛阳",
                timeout=10
            )
            if res == 2:
                print(f"{f}层没打过")
                return True
            if _zhanhun_floor == f:
                _e.outScript(f"ya_assets/images/zhanhun/{f}.bmp")
                return True
            if f < _zhanhun_floor:
                next_boss = _ZHANHUN_BOSS[f + 1]
                _e.waitForAAndClickB(
                    f"ya_assets/images/zhanhun/{f + 1}.bmp",
                    "ya_assets/images/zhanhun/chuansongmen.bmp",
                    target_a2=next_boss
                )
        elif f < 20 and f < _zhanhun_floor:
            next_boss = _ZHANHUN_BOSS[f + 1]
            _e.waitForAAndClickB(
                f"ya_assets/images/zhanhun/{f + 1}.bmp",
                "ya_assets/images/zhanhun/chuansongmen.bmp",
                target_a2=next_boss
            )
    _e.outScript(f"ya_assets/images/zhanhun/{_zhanhun_floor}.bmp")
    return True


def mojing(engine, mode="mihuan"):
    """魔镜"""
    global _e, _mojing_mode
    _e = engine
    _mojing_mode = mode
    count_map = {"mihuan": 15, "yu": 6, "zhangliao": 6, "yanbing": 6}
    engine.beginFun()
    engine.run_loop(
        _mojing_once, loop_mode="count",
        count=count_map.get(mode, 6), fallback="guandu"
    )


def _mojing_once():
    _e.feiFb("副本魔镜使者", is_elite=False)
    _e.findAndClickPic(
        "城西",
        "ya_assets/images/mojing/mojingshizhe.bmp|ya_assets/images/mojing/mojingshizhe1.bmp", "ya_assets/images/mojing/mojingshizhe.bmp|ya_assets/images/mojing/mojingshizhe1.bmp",
        "镜像地层", "镜像地层",
        "0.14,0.124", ""
    )
    _e.waitForAAndClickB("镜像地层", "进入")
    isIn = _e.waitFor("镜像地层", timeout=5)
    if not isIn:
        print("魔镜没了")
        return False

    if _mojing_mode == "mihuan":
        _mojing_mihuan()
    elif _mojing_mode == "yu":
        _mojing_yu()
    elif _mojing_mode == "zhangliao":
        _mojing_zhangliao()
    elif _mojing_mode == "yanbing":
        _mojing_yanbing()

    _e.outScript()
    return True


def _mojing_mihuan():
    _e.findAndClickPic(
        "镜像地层",
        "吃人妖", "吃人妖",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp", "进入|知道了")
    _e.waitForAAndClickB("遗迹镜像", "进入|知道了")
    _e.findAndClickPic(
        "遗迹镜像",
        "狮王魂", "狮王魂",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp", "进入|知道了")
    _e.waitForAAndClickB("迷幻境", "进入|知道了")
    _e.findAndClickPic(
        "迷幻境",
        "虚", "虚",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.findAndClickPic(
        "迷幻境",
        "实", "实",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )


def _mojing_yu():
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "镜像地层", "吃人妖", "吃人妖",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.155,0.121", "left"
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "镜像地层",
        "ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp",
        "进入|知道了", "遗迹镜像", "遗迹镜像", "", ""
    )
    _e.findAndClickPic(
        "遗迹镜像", "狮王魂", "狮王魂",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.118,0.125", ""
    )
    _e.findAndClickPic(
        "遗迹镜像",
        "ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp",
        "进入|知道了", "迷幻境", "迷幻境", "", ""
    )
    _e.color_format = "ffffff-00000|00ff00-000000|ff0000-000000"
    _e.findAndClickPic(
        "迷幻境", "虚", "虚",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.056,0.143", "right"
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "迷幻境", "实", "实",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.152,0.132", ""
    )
    _e.findAndClickPic(
        "迷幻境",
        "ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp",
        "进入|知道了", "狱境", "狱境", "", ""
    )
    _e.findAndClickPic(
        "狱境", "黑无常之魂", "黑无常之魂",
        "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp",
        "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp", "0.11,0.12", ""
    )
    _e.color_format = "ffffff-00000|00ff00-000000|ff0000-000000"
    _e.findAndClickPic(
        "狱境", "白无常之魂", "白无常之魂",
        "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp",
        "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp", "0.163,0.116", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT


def _mojing_zhangliao():
    _mojing_yu()
    _e.findAndClickPic(
        "狱境",
        "ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp",
        "进入|知道了", "炎冰境", "炎冰境", "", ""
    )
    _e.findAndClickPic(
        "炎冰境", "冰魔", "冰魔",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.05,0.125", ""
    )


def _mojing_yanbing():
    _mojing_zhangliao()
    _e.color_format = "ffffff-00000|00ff00-000000|ff0000-000000"
    _e.findAndClickPic(
        "炎冰境", "炎魔",
        "ya_assets/images/zhengdian/huoyan1.bmp|ya_assets/images/zhengdian/huoyan2.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.172,0.127", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "炎冰境", "炎兄",
        "ya_assets/images/zhengdian/huoyan1.bmp|ya_assets/images/zhengdian/huoyan2.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.156,0.127", ""
    )
    _e.findAndClickPic(
        "炎冰境",
        "ya_assets/images/mojing/xiaolvren.bmp|ya_assets/images/mojing/xiaolvren111.bmp",
        "进入|知道了", "印魔殿", "印魔殿", "", ""
    )
    _e.findAndClickPic(
        "印魔殿", "北境", "北境", "北境", "北境", "0.122,0.075", ""
    )
    _e.findAndClickPic(
        "北境", "四神", "四神",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.098,0.125", ""
    )
    _e.findAndClickPic(
        "北境", "印魔殿", "印魔殿", "印魔殿", "印魔殿", "0.101,0.172", ""
    )
    _e.findAndClickPic(
        "印魔殿", "西境", "西境", "西境", "西境", "0.182,0.115", ""
    )
    _e.findAndClickPic(
        "西境", "四神", "四神",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.104,0.137", ""
    )
    _e.findAndClickPic(
        "西境", "ya_assets/images/chuansongmen.bmp", "ya_assets/images/chuansongmen.bmp",
        "印魔殿", "印魔殿", "", ""
    )
    _e.findAndClickPic(
        "印魔殿", "南境", "南境", "南境", "南境", "0.123,0.153", ""
    )
    _e.findAndClickPic(
        "南境", "四神", "四神",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.1,0.139", ""
    )
    _e.findAndClickPic(
        "南境", "印魔殿", "印魔殿", "印魔殿", "印魔殿", "0.102,0.113", ""
    )
    _e.findAndClickPic(
        "印魔殿", "东境", "东境", "东境", "东境", "0.053,0.117", ""
    )
    _e.findAndClickPic(
        "东境", "四神", "四神",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.107,0.137", ""
    )
    _e.findAndClickPic(
        "东境", "ya_assets/images/chuansongmen.bmp", "ya_assets/images/chuansongmen.bmp",
        "印魔殿", "印魔殿", "", ""
    )
    _e.findAndClickPic(
        "印魔殿", "魔将", "魔将",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "0.135,0.101", ""
    )


def liandan(engine):
    """炼丹"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_liandan_once, loop_mode="count", count=5, fallback="guandu")


def _liandan_once():
    _e.feiFb("副本南华老人", is_elite=False)
    _e.findAndClickPic(
        "五指峡谷",
        "ya_assets/images/richang/nanhualaoren.bmp", "ya_assets/images/richang/nanhualaoren1.bmp",
        "进入", "进入",
        "0.164,0.131", ""
    )
    _e.waitForAAndClickB("南天门", "进入")
    isIn = _e.waitFor("南天门", timeout=5)
    if not isIn:
        print("炼丹没次数了")
        return False
    _e.findAndClickPic(
        "南天门",
        "左门", "左门",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp",
        "0.111,0.131", ""
    )
    _e.findAndClickPic(
        "南天门",
        "右门", "右门",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", ""
    )
    _e.waitForAAndClickB("天宫小道", "进入")
    _e.waitFor("天宫小道", timeout=5)
    _e.waitForAAndClickB("炼丹房", "ya_assets/images/richang/liandanchuansongmen.bmp")
    for _ in range(5):
        _e.findAndClickPic(
            "炼丹房",
            "炼丹童", "炼丹童",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "down"
        )
    _e.findAndClickPic(
        "炼丹房",
        "炼丹童", "炼丹童",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    for _ in range(4):
        _e.findAndClickPic(
            "炼丹房",
            "炼丹童", "炼丹童",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
        )
    _e.outScript()
    return True


def wuxing(engine):
    """五行"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_wuxing_once, loop_mode="count", count=3, fallback="guandu")


def _wuxing_once():
    _e.feiFb("地图野外西", is_elite=True)
    _e.findAndClickPic(
        "野外西",
        "ya_assets/images/richang/laoban1.bmp", "ya_assets/images/richang/laoban.bmp",
        "进五行", "进五行",
        "0.041,0.134", ""
    )
    _e.waitForAAndClickB("五行圣殿", "进五行")
    isIn = _e.waitFor("五行圣殿", timeout=5)
    if not isIn:
        print("五行没次数了")
        return False
    _e.findAndClickPic(
        "五行圣殿",
        "大乔", "大乔",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.findAndClickPic(
        "五行圣殿",
        "神火系", "神火系",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.findAndClickPic(
        "五行圣殿",
        "神金系", "神金系",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitFor("五行圣殿", timeout=5)
    _e.findAndClickPic(
        "五行圣殿",
        "张辽", "张辽",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.findAndClickPic(
        "五行圣殿",
        "神木系", "神木系",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.outScript()
    return True


def rongdong(engine):
    """溶洞"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_rongdong_once, loop_mode="count", count=3, fallback="guandu")


def _rongdong_once():
    _e.feiFb("地图绿林路", is_elite=False)
    _e.findAndClickPic(
        "绿林路",
        "ya_assets/images/richang/longtianxiao2.bmp", "ya_assets/images/richang/longtianxiao.bmp",
        "进入", "进入",
        "0.065,0.124", ""
    )
    _e.waitForAAndClickB("遗忘之林", "进入")
    isIn = _e.waitFor("遗忘之林", timeout=5)
    if not isIn:
        print("溶洞没次数了")
        return False
    for _ in range(3):
        _e.findAndClickPic(
            "遗忘之林",
            "远古干尸", "远古干尸",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
        )
    _e.findAndClickPic(
        "遗忘之林",
        "暴力熊", "暴力熊",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitForAAndClickB("远古溶洞", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "远古溶洞",
        "永恒之火", "永恒之火",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.outScript()
    return True


def bamen(engine):
    """八门(80精英)"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_bamen_once, loop_mode="count", count=1, fallback="guandu")


def _bamen_once():
    _e.feiFb("副本分身", is_elite=True)
    _e.findAndClickPic(
        "许昌",
        "ya_assets/images/richang/zuocifenshen.bmp", "ya_assets/images/richang/zuocifenshen1.bmp",
        "进精英", "进精英",
        "0.108,0.134", ""
    )
    _e.waitForAAndClickB("魔岛入口", "进精英")
    isIn = _e.waitFor("魔岛入口", timeout=5)
    if not isIn:
        print("80精英没次数了")
        return False
    _e.waitForAAndClickB("凶", "凶")
    _e.findAndClickPic(
        "凶",
        "妖族", "妖族",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("地牢", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "地牢",
        "穷奇", "穷奇",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("地牢二层", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "地牢二层",
        "妖化", "妖化",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("魔岛枢纽", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "魔岛枢纽",
        "妖化郭嘉", "妖化郭嘉",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.outScript()
    return True


def guandu_jy(engine):
    """官渡精英"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_guandu_jy_once, loop_mode="count", count=1, fallback="guandu")


def _guandu_jy_once():
    isIn = _e.waitFor("官渡", timeout=5)
    if not isIn:
        _e.feiFb("副本曹操", is_elite=True)
    _e.findAndClickPic(
        "官渡",
        "ya_assets/images/guandu/caocao1.bmp", "ya_assets/images/guandu/caocao.bmp",
        "进精英", "进精英",
        "0.038,0.134", ""
    )
    _e.waitForAAndClickB("大帐", "进精英")
    isIn = _e.waitFor("大帐", timeout=5)
    if not isIn:
        print("官渡精英没次数了")
        return False
    _e.waitFor("大帐", timeout=5)
    _e.waitForAAndClickB("战场", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "战场",
        "ya_assets/images/guandu/hbj2.bmp|ya_assets/images/guandu/hbj1.bmp", "ya_assets/images/guandu/hbj2.bmp|ya_assets/images/guandu/hbj1.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitFor("战场", timeout=5)
    _e.findAndClickPic(
        "战场",
        "ya_assets/images/guandu/yanliang.bmp", "ya_assets/images/guandu/yanliang1.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.findAndClickPic(
        "战场",
        "ya_assets/images/guandu/wenchou.bmp", "ya_assets/images/guandu/wenchou1.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("大帐", "ya_assets/images/guandu/jy1chuansongmen.bmp")
    _e.waitFor("大帐", timeout=5)
    _e.waitForAAndClickB("知道了", "ya_assets/images/xiaolvren.bmp")
    _e.waitForAAndClickB("粮仓", "知道了")
    _e.waitForAAndClickB("魂殿", "ya_assets/images/guandu/jygohundianchuansongmen.bmp")
    _e.waitFor("魂殿", timeout=5)
    _e.findAndClickPic(
        "魂殿",
        "文丑之魂", "文丑之魂",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.findAndClickPic(
        "魂殿",
        "董卓", "董卓",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("粮仓", "ya_assets/images/guandu/hundianchuansongmen.bmp")
    _e.findAndClickPic(
        "粮仓",
        "ya_assets/images/guandu/cyq1.bmp", "ya_assets/images/guandu/cyq2.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", ""
    )
    _e.waitFor("粮仓", timeout=5)
    _e.findAndClickPic(
        "粮仓",
        "ya_assets/images/guandu/yuanshao1.bmp|ya_assets/images/guandu/yuanshao2.bmp", "",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", ""
    )
    _e.outScript()


def yunyou_jy(engine):
    """云游精英"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_yunyou_jy_once, loop_mode="count", count=1, fallback="guandu")


def _yunyou_jy_once():
    _e.feiFb("副本仙人", is_elite=True)
    _e.findAndClickPic(
        "嵩山",
        "ya_assets/images/richang/yunyouxianren1.bmp|ya_assets/images/richang/yunyouxianren.bmp", "ya_assets/images/richang/yunyouxianren1.bmp|ya_assets/images/richang/yunyouxianren.bmp",
        "进精英", "进精英",
        "", "up"
    )
    _e.waitForAAndClickB("东海之极", "进精英")
    isIn = _e.waitFor("东海之极", timeout=5)
    if not isIn:
        print("云游精英没次数了")
        return False
    _e.waitForAAndClickB("鬼气林", "ya_assets/images/richang/yunyou1chuansongmen.bmp")
    _e.findAndClickPic(
        "鬼气林",
        "黑无常", "黑无常",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitFor("鬼气林", timeout=5)
    _e.waitForAAndClickB("东海之极", "ya_assets/images/richang/guiqilinchuansongmen.bmp")
    _e.waitFor("东海之极", timeout=5)
    _e.waitForAAndClickB("东海之极", "ya_assets/images/richang/zixiaxianzi.bmp|ya_assets/images/richang/jintianti.bmp|ya_assets/images/richang/jintianti1.bmp|ya_assets/images/richang/jintianti2.bmp")
    _e.waitForAAndClickB("天梯", "进天梯")
    _e.findAndClickPic(
        "天梯",
        "天界", "天界",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("云端", "ya_assets/images/chuansongmen.bmp")
    _e.waitFor("云端", timeout=5)
    _e.findAndClickPic(
        "天界精英",
        "天界分身", "天界分身",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitForAAndClickB("云端", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "地狱",
        "地狱分", "地狱分",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "right"
    )
    _e.waitForAAndClickB("云端", "ya_assets/images/richang/diyuchuansongmen.bmp")
    _e.waitFor("云端", timeout=5)
    _e.waitForAAndClickB("人界", "人界")
    _e.findAndClickPic(
        "人界",
        "人界分身", "人界分身",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitForAAndClickB("云端", "ya_assets/images/richang/renjiechuansongmen.bmp")
    _e.findAndClickPic(
        "云端",
        "巨灵神", "巨灵神",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp",
        "", ""
    )
    _e.outScript()
    return True


def laoshu_jy(engine):
    """老鼠精英(100精英)"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_laoshu_jy_once, loop_mode="count", count=1, fallback="guandu")


def _laoshu_jy_once():
    _e.feiFb("副本猎鼠人", is_elite=True)
    _e.findAndClickPic(
        "碧水地穴",
        "ya_assets/images/richang/lieshuren.bmp", "ya_assets/images/richang/lieshuren1.bmp",
        "进精英", "进精英",
        "", ""
    )
    _e.waitForAAndClickB("鼠穴入口", "进精英")
    isIn = _e.waitFor("鼠穴入口", timeout=5)
    if not isIn:
        print("老鼠精英没次数了")
        return False
    _e.findAndClickPic(
        "鼠穴入口",
        "妖鼠头领", "妖鼠头领",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitForAAndClickB("鼠穴", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "鼠穴",
        "暗杀鼠", "暗杀鼠",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitForAAndClickB("鼠巢内", "ya_assets/images/chuansongmen.bmp")
    _e.findAndClickPic(
        "鼠巢内",
        "鼠长老", "鼠长老",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitForAAndClickB("鼠大厅", "ya_assets/images/richang/shuchaoneichuansongmen1.bmp")
    _e.findAndClickPic(
        "鼠大厅",
        "碧水鼠王", "碧水鼠王",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "up"
    )
    _e.waitForAAndClickB("鼠巢内", "ya_assets/images/chuansongmen.bmp")
    _e.waitFor("鼠巢内", timeout=5)
    _e.waitForAAndClickB("鼠殿", "ya_assets/images/richang/shuchaoneichuansongmen2.bmp")
    _e.findAndClickPic(
        "鼠殿",
        "碧水鼠王", "碧水鼠王",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "down"
    )
    _e.outScript()
    return True


def heifeng(engine, mode="da"):
    """黑风山寨"""
    global _e, _heifeng_mode
    _e = engine
    _heifeng_mode = mode
    count_map = {"da": 3, "er": 5, "longzhu": 3, "da_quancheng": 2, "er_quancheng": 3}
    engine.beginFun()
    engine.run_loop(
        _heifeng_once, loop_mode="count",
        count=engine.heifengCount if engine.heifengCount > 0 else count_map.get(mode, 3), fallback="guandu"
    )


def _heifeng_once():
    _e.feiFb("地图五层", is_elite=False)
    _e.findAndClickPic(
        "五层",
        "ya_assets/images/heifeng/11.bmp", "ya_assets/images/heifeng/bashanhu.bmp",
        "黑风山寨", "黑风山寨",
        "", "up"
    )
    _e.waitForAAndClickB("黑风山寨", "黑风山寨")

    if _heifeng_mode in ("da", "da_quancheng"):
        _heifeng_da()
    elif _heifeng_mode in ("er", "er_quancheng"):
        _heifeng_er()
    elif _heifeng_mode == "longzhu":
        _heifeng_longzhu()

    _e.outScript()
    return True


def _heifeng_er():
    for _ in range(2):
        _e.findAndClickPic(
            "黑风山寨",
            "ya_assets/images/heifeng/daozei1.bmp|ya_assets/images/heifeng/daozei2.bmp", "ya_assets/images/heifeng/daozei1.bmp|ya_assets/images/heifeng/daozei2.bmp",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
        )
    _e.waitFor("黑风山寨", timeout=5)
    _e.findAndClickPic(
        "黑风山寨",
        "头目", "头目",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )
    _e.waitFor("黑风山寨", timeout=5)
    _e.waitForAAndClickB("山寨本营", "ya_assets/images/heifeng/heifeng1chuansongmen.bmp|ya_assets/images/heifeng/heifeng1chuansongmen1.bmp")
    _e.waitFor("山寨本营", timeout=5)
    _e.waitForAAndClickB("山寨内堂", "ya_assets/images/heifeng/chuansongmen2.bmp")
    _e.findAndClickPic(
        "山寨内堂",
        "当家", "当家",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "up"
    )


def _heifeng_da():
    _heifeng_er()
    _e.waitForAAndClickB("ya_assets/images/heifeng/midong.bmp", "ya_assets/images/heifeng/midong.bmp")
    _e.findAndClickPic(
        "ya_assets/images/heifeng/midong.bmp",
        "当家", "当家",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "up"
    )


def _heifeng_longzhu():
    for _ in range(2):
        _e.findAndClickPic(
            "黑风山寨",
            "拳师", "拳师",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
        )
    _e.waitFor("黑风山寨", timeout=5)
    _e.findAndClickPic(
        "黑风山寨",
        "头目", "头目",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp", "", "left"
    )


def qingyuan(engine):
    """青渊"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_qingyuan_once, loop_mode="count", count=3, fallback="guandu")


def _qingyuan_once():
    isIn = _e.waitFor("虎牢关外", timeout=5)
    if not isIn:
        _e.feiFb("地图虎牢关外", is_elite=True)
    _e.findAndClickPic(
        "虎牢关外",
        "ya_assets/images/hong/sunjian1.bmp", "孙坚",
        "进入", "进入",
        "0.07,0.125", ""
    )
    _e.waitForAAndClickB("ya_assets/images/hong/qingyuan1.bmp", "进入")
    isIn = _e.waitFor("ya_assets/images/hong/qingyuan1.bmp", timeout=8)
    if not isIn:
        print("青渊没次数了")
        return False
    _e.findAndClickPic(
        "ya_assets/images/hong/qingyuan1.bmp",
        "龙守卫", "龙守卫",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.addBloud()
    _e.findAndClickPic(
        "ya_assets/images/hong/qingyuan1.bmp",
        "冰龙王", "冰龙王",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.addBloud()
    _e.findAndClickPic(
        "ya_assets/images/hong/qingyuan1.bmp",
        "ya_assets/images/hong/chuansongmen.bmp", "ya_assets/images/hong/chuansongmen.bmp",
        "ya_assets/images/hong/qingyuan2.bmp", "ya_assets/images/hong/qingyuan2.bmp",
        "", ""
    )
    _e.addBloud()
    _e.findAndClickPic(
        "ya_assets/images/hong/qingyuan2.bmp",
        "青龙圣兽", "青龙圣兽",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.outScript("ya_assets/images/hong/qingyuan2.bmp")
    return True


def yinghun(engine):
    """英魂秘境"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_yinghun_once, loop_mode="count", count=1, fallback="guandu")


def _yinghun_once():
    _e.feiFb("地图虎牢关外", is_elite=False)
    _e.findAndClickPic(
        "ya_assets/images/hong/luanshipo.bmp",
        "ya_assets/images/hong/nanhualaoxian.bmp", "ya_assets/images/hong/nanhualaoxian1.bmp",
        "进入", "进入",
        "0.022,0.138", ""
    )
    _e.waitForAAndClickB("魂息平原", "进入")
    if _e.overed:
        return
    isIn = _e.waitFor("魂息平原", timeout=8)
    if not isIn:
        print("英魂秘境没次数了")
        return False
    _e.addBloud()
    _e.findAndClickPic(
        "魂息平原",
        "怨灵", "怨灵",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.findAndClickPic(
        "魂息平原",
        "怨灵", "怨灵",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.waitFor("魂息平原")
    _e.addBloud()
    _e.findAndClickPic(
        "魂息平原",
        "秘境英魂|英魂之火|怨灵", "ya_assets/images/richang/yinghunzhihuo1.bmp|ya_assets/images/richang/yinghunzhihuo2.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.072,0.146", ""
    )
    _e.waitFor("魂息平原")
    _e.addBloud()
    _e.findAndClickPic(
        "魂息平原",
        "秘境英魂|英魂之火|怨灵", "ya_assets/images/richang/yinghunzhihuo1.bmp|ya_assets/images/richang/yinghunzhihuo2.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "0.072,0.146", ""
    )
    _e.findAndClickPic(
        "魂息平原",
        "ya_assets/images/hong/youyingshenyuan.bmp", "ya_assets/images/hong/youyingshenyuan.bmp",
        "ya_assets/images/hong/youyingshenyuan.bmp", "ya_assets/images/hong/youyingshenyuan.bmp",
        "0.014,0.16", ""
    )
    _e.waitFor("ya_assets/images/hong/youyingshenyuan.bmp")
    _e.addBloud()
    _e.findAndClickPic(
        "ya_assets/images/hong/youyingshenyuan.bmp",
        "英魂之火", "ya_assets/images/richang/yinghunzhihuo1.bmp|ya_assets/images/richang/yinghunzhihuo2.bmp",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.waitFor("ya_assets/images/hong/youyingshenyuan.bmp")
    _e.addBloud()
    _e.findAndClickPic(
        "ya_assets/images/hong/youyingshenyuan.bmp",
        "吕布英魂", "吕布英魂",
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.outScript("ya_assets/images/hong/youyingshenyuan.bmp")
    return True


def sangumaolu(engine):
    """三顾茅庐"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_sangumaolu_once, loop_mode="count", count=1, fallback="guandu")


def _sangumaolu_once():
    isIn = _e.waitFor("ya_assets/images/sangumaolu/xinye.bmp", timeout=5)
    if not isIn:
        _e.feiFb("地图新野", is_elite=True)
    _e.confidenceNum = 0.8
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/xinye.bmp",
        "ya_assets/images/zhengdian/xiaolvren2.bmp|ya_assets/images/zhengdian/xiaolvren.bmp",
        "ya_assets/images/zhengdian/xiaolvren2.bmp|ya_assets/images/zhengdian/xiaolvren.bmp",
        "进入", "进入",
        "0.127,0.129", ""
    )
    _e.confidenceNum = 0.9
    time.sleep(1)
    _e.waitForAAndClickB(
        "ya_assets/images/sangumaolu/xinye.bmp",
        "进入",
        _e.dituLocation,
        _e.gameBottomLocation
    )
    _e.confidenceNum = 0.6
    _e.color_format = "b@ffff00-000000|0ff000-000000|00ff00-000000|fff200-000000"
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/xinye.bmp",
        "ya_assets/images/sangumaolu/liubei3.bmp|ya_assets/images/sangumaolu/liubei4.bmp|ya_assets/images/sangumaolu/qianwang.bmp|ya_assets/images/sangumaolu/qianwang1.bmp|ya_assets/images/sangumaolu/qianwang2.bmp",
        "前往茅庐",
        "ya_assets/images/sangumaolu/maolu.bmp",
        "ya_assets/images/sangumaolu/maolu.bmp",
        "", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/maolu.bmp",
        "ya_assets/images/sangumaolu/tongzi1.bmp|ya_assets/images/sangumaolu/tongzi2.bmp|ya_assets/images/sangumaolu/jinru.bmp|ya_assets/images/sangumaolu/jinru1.bmp|ya_assets/images/sangumaolu/jinru2.bmp",
        "进入阵法",
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.confidenceNum = 0.9
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "七星灯", "七星灯",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "占卜币", "占卜币",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "巨石阵兽", "巨石阵兽",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.076,0.115", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "占卜币", "占卜币",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.076,0.115", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/yanminzhenfa.bmp",
        "七星灯", "七星灯",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.076,0.115", ""
    )
    _e.confidenceNum = 0.6
    _e.color_format = "b@ffff00-000000|0ff000-000000|00ff00-000000|fff200-000000"
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/xinye.bmp",
        "ya_assets/images/sangumaolu/liubei3.bmp|ya_assets/images/sangumaolu/liubei4.bmp|ya_assets/images/sangumaolu/qianwang.bmp|ya_assets/images/sangumaolu/qianwang1.bmp|ya_assets/images/sangumaolu/qianwang2.bmp",
        "再次前往茅庐",
        "ya_assets/images/sangumaolu/maolu.bmp",
        "ya_assets/images/sangumaolu/maolu.bmp",
        "", ""
    )
    _e.confidenceNum = 0.9
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/maolu.bmp",
        "ya_assets/images/sangumaolu/tongzi1.bmp|ya_assets/images/sangumaolu/tongzi2.bmp|ya_assets/images/sangumaolu/jinru.bmp|ya_assets/images/sangumaolu/jinru1.bmp|ya_assets/images/sangumaolu/jinru2.bmp",
        "进入阵法",
        "ya_assets/images/sangumaolu/baguaqunmozhen.bmp",
        "ya_assets/images/sangumaolu/baguaqunmozhen.bmp",
        "", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.confidenceNum = 0.9
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/baguaqunmozhen.bmp",
        "七星灯", "七星灯",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.143,0.117", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/baguaqunmozhen.bmp",
        "占卜币", "占卜币",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.125,0.127", ""
    )
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/baguaqunmozhen.bmp",
        "八卦阵灵", "八卦阵灵",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.101,0.122", ""
    )
    _e.color_format = "b@ffff00-000000|0ff000-000000|00ff00-000000|fff200-000000"
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/xinye.bmp",
        "ya_assets/images/sangumaolu/liubei3.bmp|ya_assets/images/sangumaolu/liubei4.bmp|ya_assets/images/sangumaolu/qianwang.bmp|ya_assets/images/sangumaolu/qianwang1.bmp|ya_assets/images/sangumaolu/qianwang2.bmp",
        "再次前往茅庐",
        "ya_assets/images/sangumaolu/zhugelu.bmp",
        "ya_assets/images/sangumaolu/zhugelu.bmp",
        "", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "ya_assets/images/sangumaolu/zhugelu.bmp",
        "孔明",
        "ya_assets/images/sangumaolu/zhugeliang1.bmp",
        "ya_assets/images/sangumaolu/yiyanweiding.bmp|ya_assets/images/sangumaolu/yiyanweiding1.bmp|ya_assets/images/sangumaolu/yiyanweiding2.bmp",
        "ya_assets/images/sangumaolu/yiyanweiding.bmp|ya_assets/images/sangumaolu/yiyanweiding1.bmp|ya_assets/images/sangumaolu/yiyanweiding2.bmp",
        "0.076,0.16", ""
    )
    _e.confidenceNum = 0.9
    while not _e.find_pic_or_str(
        "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd11.bmp",
        _e.gameBottomLocation, 0
    ):
        if _e.check_stop():
            return
        time.sleep(0.001)
        _e.click(279, 347)
        _e.click_image(
            "ya_assets/images/sangumaolu/yiyanweiding.bmp|ya_assets/images/sangumaolu/yiyanweiding1.bmp|ya_assets/images/sangumaolu/yiyanweiding2.bmp",
            _e.gameBottomLocation, 0.6
        )
        time.sleep(0.5)
    _e.confidenceNum = 0.9
    _e.outScript("ya_assets/images/sangumaolu/zhugelu.bmp")
    return True


def mingjiang_tz(engine):
    """名将挑战赛"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_mingjiang_tz_once, loop_mode="count", count=1, fallback="guandu")


def _mingjiang_tz_once():
    isIn = _e.waitFor("洛阳", timeout=5)
    if not isIn:
        _e.feiFb("副本挑战赛", is_elite=True)
    _e.findAndClickPic(
        "洛阳",
        "ya_assets/images/zhanhun/zhanhuntiaozhan.bmp",
        "ya_assets/images/zhanhun/zhanhuntiaozhanditu.bmp",
        "进名将挑战", "进名将挑战",
        "0.067,0.132", ""
    )
    _e.waitForAAndClickB("武神殿", "进名将挑战")
    isIn = _e.waitFor("武神殿", timeout=8)
    if not isIn:
        print("名将没次数了")
        return False
    _e.findAndClickPic(
        "武神殿",
        "ya_assets/images/richang/mingjiangliubei2.bmp",
        "ya_assets/images/richang/mingjiangliubei.bmp",
        "挑战", "挑战",
        "0.156,0.144", ""
    )
    _e.waitForAAndClickB("ya_assets/images/zdzd.bmp", "挑战")
    _e.waitFor("ya_assets/images/zdzd.bmp")
    _e.findAndClickPic(
        "武神殿",
        "ya_assets/images/richang/mingjiangzhangfei1.bmp",
        "ya_assets/images/richang/mingjiangzhangfei.bmp",
        "挑战", "挑战",
        "0.142,0.115", ""
    )
    _e.waitForAAndClickB("ya_assets/images/zdzd.bmp", "挑战")
    _e.waitFor("ya_assets/images/zdzd.bmp")
    _e.findAndClickPic(
        "武神殿",
        "ya_assets/images/richang/mingjiangguanyu1.bmp",
        "ya_assets/images/richang/mingjiangguanyu.bmp",
        "挑战", "挑战",
        "0.043,0.144", ""
    )
    _e.waitForAAndClickB("ya_assets/images/zdzd.bmp", "挑战")
    _e.waitFor("ya_assets/images/zdzd.bmp")
    _e.findAndClickPic(
        "武神殿",
        "ya_assets/images/richang/mingjianglvbu1.bmp",
        "ya_assets/images/richang/mingjianglvbu.bmp",
        "挑战", "挑战",
        "0.063,0.113", ""
    )
    _e.waitForAAndClickB("ya_assets/images/zdzd.bmp", "挑战")
    _e.waitFor("ya_assets/images/zdzd.bmp")
    _e.findAndClickPic(
        "武神殿",
        "ya_assets/images/richang/tianwaitianshouwei.bmp",
        "ya_assets/images/richang/tianwaitianshouwei1.bmp",
        "进天外", "进天外",
        "0.063,0.113", ""
    )
    _e.waitForAAndClickB("天外天", "进天外")
    chanchu_pos = [
        "0.121,0.112",
        "0.104,0.103",
        "0.078,0.108",
        "0.067,0.118",
        "0.046,0.106",
        "0.038,0.113",
    ]
    _e.findAndClickPic(
        "天外天",
        "地穴蟾蜍",
        "ya_assets/images/richang/chanchu.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.14,0.119", ""
    )
    for i in range(6):
        _e.findAndClickPic(
            "天外天",
            "地穴蟾蜍",
            "ya_assets/images/richang/chanchu.bmp",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            chanchu_pos[i], "left"
        )
    waitForTwoRes = _e.waitForTwo("出现", "运气太烂")
    if waitForTwoRes == 2:
        print("没有守财奴")
        return True
    time.sleep(0.5)
    _e.key_press("g")
    _e.waitFor("洛阳")
    return True


def mingjiang_cg(engine):
    """名将闯关"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_mingjiang_cg_once, loop_mode="count", count=1, fallback="guandu")


def _mingjiang_cg_once():
    isIn = _e.waitFor("城西", timeout=5)
    if not isIn:
        _e.feiFb("地图城西", is_elite=True)
    _e.findAndClickPic(
        "城西",
        "名将使者",
        "ya_assets/images/mingjiangshizhe1.bmp|ya_assets/images/mingjiangshizhe2.bmp",
        "进入", "进入",
        "0.074,0.138", ""
    )
    _e.waitForAAndClickB("名战殿", "进入")
    isIn = _e.waitFor("名战殿", timeout=8)
    if not isIn:
        print("名将时间到了")
        return False
    time.sleep(0.5)
    _e.key_press("g")
    _e.waitFor("城西")
    return True


def bangpai(engine):
    """帮派任务"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_bangpai_once, loop_mode="count", count=22, fallback="guandu")


def _bangpai_once():
    _e.findAndClickPic(
        "ya_assets/images/longdao/dabenying.bmp",
        "ya_assets/images/longdao/guanjia1.bmp",
        "ya_assets/images/longdao/guanjia.bmp",
        "帮派大本营", "帮派大本营",
        "0.107,0.156", ""
    )


def kuangchan(engine):
    """矿产"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_kuangchan_once, loop_mode="count", count=1, fallback="guandu")


def _kuangchan_once():
    isIn = _e.waitFor("五层", timeout=5)
    if not isIn:
        _e.feiFb("地图五层", is_elite=True)
    _e.findAndClickPic(
        "五层",
        "ya_assets/images/heifeng/11.bmp",
        "ya_assets/images/heifeng/bashanhu.bmp",
        "破旧矿产", "破旧矿产",
        "0.166,0.12", "left"
    )
    _e.waitForAAndClickB("矿场洞窟", "破旧矿产")
    chikuang_poss = [
        "0.044,0.134",
        "0.072,0.136",
        "0.102,0.131",
        "0.127,0.139",
        "0.154,0.134",
    ]
    for i in range(5):
        _e.findAndClickPic(
            "矿场洞窟",
            "矿工凶灵",
            "ya_assets/images/heifeng/xiongling1.bmp|ya_assets/images/heifeng/xiongling2.bmp",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            chikuang_poss[i], "right"
        )
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "矿场洞窟",
        "吃矿小鬼", "吃矿小鬼",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.184,0.132", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.waitForAAndClickB("矿场内", "ya_assets/images/chuansongmen.bmp")
    chikuang_poss1 = [
        "0.125,0.127",
        "0.163,0.141",
        "0.188,0.12",
        "0.063,0.137",
        "0.032,0.139",
    ]
    _e.findAndClickPic(
        "矿场内",
        "矿工凶灵",
        "ya_assets/images/heifeng/xiongling2.bmp",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.097,0.138", "right"
    )
    for i in range(4):
        _e.findAndClickPic(
            "矿场内",
            "矿工凶灵",
            "ya_assets/images/heifeng/xiongling1.bmp|ya_assets/images/heifeng/xiongling2.bmp",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            chikuang_poss1[i], "left"
        )
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "矿场内",
        "吃矿小鬼", "吃矿小鬼",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        chikuang_poss1[4], ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.findAndClickPic(
        "矿场内",
        "岩石洞", "岩石洞",
        "岩石洞", "岩石洞",
        "0.043,0.12", ""
    )
    liankuang_poss = ["0.144,0.132", "0.11,0.144", "0.087,0.131", "0.066,0.139"]
    for i in range(4):
        _e.findAndClickPic(
            "岩石洞",
            "炼矿小鬼",
            "ya_assets/images/heifeng/liankuang1.bmp|ya_assets/images/heifeng/liankuang2.bmp",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            liankuang_poss[i], "left"
        )
    _e.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
    _e.findAndClickPic(
        "岩石洞",
        "炎魔神", "炎魔神",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.05,0.127", ""
    )
    _e.color_format = _e.DEFAULT_COLOR_FORMAT
    _e.outScript("岩石洞")
    return True


def longdao(engine):
    """龙岛"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_longdao_once, loop_mode="infinite", fallback="guandu")


def _longdao_once():
    isIn = _e.waitFor("城西", timeout=5)
    if not isIn:
        _e.feiFb("地图城西", is_elite=True)
    _e.findAndClickPic(
        "城西",
        "ya_assets/images/longdao/bangpai.bmp",
        "ya_assets/images/longdao/bangpai1.bmp",
        "进龙岛", "进龙岛",
        "0.123,0.139", ""
    )
    _e.waitForAAndClickB("龙岛", "进龙岛")
    isIn = _e.waitFor("龙岛", timeout=8)
    if not isIn:
        print("龙岛没次数了")
        return False
    _e.findAndClickPic(
        "龙岛",
        "ya_assets/images/mojing/xiaolvren.bmp",
        "ya_assets/images/mojing/xiaolvren.bmp",
        "挑战龙族", "挑战龙族",
        "", ""
    )
    _e.waitForAAndClickB("ya_assets/images/zdzd.bmp", "挑战龙族")
    _e.waitFor("ya_assets/images/zdzd.bmp")
    _e.findAndClickPic(
        "龙岛",
        "进入", "进入",
        "密洞", "密洞",
        "", ""
    )
    _e.findAndClickPic(
        "密洞",
        "金龙王", "金龙王",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.036,0.131", ""
    )
    _e.findAndClickPic(
        "密洞",
        "龙巢", "龙巢",
        "龙巢", "龙巢",
        "0.182,0.127", ""
    )
    longchao_poss = [
        "0.02,0.113",
        "0.036,0.131",
        "0.048,0.117",
        "0.075,0.131",
        "0.091,0.122",
        "0.121,0.144",
        "0.142,0.143",
        "0.153,0.131",
    ]
    for index, item in enumerate(longchao_poss):
        move_key = "right" if index < 5 else ""
        _e.findAndClickPic(
            "龙巢",
            "龙孙|龙孙一|龙子|龙子一",
            "ya_assets/images/longdao/longsun.bmp|ya_assets/images/longdao/longsun1.bmp|ya_assets/images/longdao/longzi.bmp|ya_assets/images/longdao/longzi1.bmp",
            "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
            "ya_assets/images/zdzd111.bmp|ya_assets/images/zdzd.bmp",
            item, move_key
        )
    _e.findAndClickPic(
        "龙巢",
        "地狱炎龙", "五爪金龙",
        "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
        "0.183,0.134", ""
    )
    _e.outScript("龙巢")
    return True


def longzhu(engine):
    """龙珠"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_longzhu_once, loop_mode="count", count=1, fallback="guandu")


def _longzhu_once():
    _e.findAndClickPic(
        "洛阳",
        "ya_assets/images/longzhu/laoyufu.bmp",
        "ya_assets/images/longzhu/laoyufu1.bmp",
        "龙巢", "龙巢",
        "0.1,0.139", ""
    )
    _e.waitForAAndClickB("ya_assets/images/longzhu/longchaojingwai.bmp", "龙巢")
    isIn = _e.waitFor("ya_assets/images/longzhu/longchaojingwai.bmp", timeout=8)
    if not isIn:
        print("龙巢没次数了")
        return False
    longzhuPos = [
        "0.161,0.127",
        "0.134,0.134",
        "0.094,0.12",
        "0.063,0.136",
        "0.028,0.122",
    ]
    for item in longzhuPos:
        _e.findAndClickPic(
            "ya_assets/images/longzhu/longchaojingwai.bmp",
            "寻宝者", "寻宝者",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            item, "left"
        )
    _e.findAndClickPic(
        "ya_assets/images/longzhu/longchaojingwai.bmp",
        "ya_assets/images/longzhu/chuansongmen.bmp",
        "ya_assets/images/longzhu/chuansongmen.bmp",
        "ya_assets/images/longzhu/longchaorukou.bmp",
        "ya_assets/images/longzhu/longchaorukou.bmp",
        "", ""
    )
    longzhuPos1 = [
        "0.172,0.129",
        "0.15,0.122",
        "0.13,0.132",
        "0.094,0.122",
        "0.074,0.127",
    ]
    for item in longzhuPos1:
        _e.findAndClickPic(
            "ya_assets/images/longzhu/longchaorukou.bmp",
            "寻宝者", "挖宝人",
            "ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd.bmp",
            item, "left"
        )
    _e.findAndClickPic(
        "ya_assets/images/longzhu/longchaorukou.bmp",
        "ya_assets/images/longzhu/chuansongmen.bmp",
        "ya_assets/images/longzhu/chuansongmen.bmp",
        "ya_assets/images/longzhu/longchaojingnei.bmp",
        "ya_assets/images/longzhu/longchaojingnei.bmp",
        "", ""
    )
    time.sleep(0.2)
    _e.key_press("g")
    _e.waitFor("退出挂机")
    _e.findAndClickPic(
        "ya_assets/images/longzhu/longchaojingnei.bmp",
        "ya_assets/images/longzhu/chuansongmen.bmp",
        "ya_assets/images/longzhu/chuansongmen.bmp",
        "ya_assets/images/longzhu/longchaoxue.bmp",
        "ya_assets/images/longzhu/longchaoxue.bmp",
        "", ""
    )
    time.sleep(0.2)
    _e.key_press("g")
    time.sleep(5)
    _e.waitFor("退出挂机")
    _e.outScript("ya_assets/images/longzhu/longchaoxue.bmp")
    return True


def shuasunce(engine):
    """刷孙策"""
    global _e
    _e = engine
    engine.beginFun()
    engine.run_loop(_shuasunce_once, loop_mode="infinite", count=1, zhengdian_at=58)


def _shuasunce_once():
    _e.findAndClickPic(
        "ya_assets/images/guaji/yuhuayuan.bmp",
        "ya_assets/images/guaji/wangyun.bmp|ya_assets/images/guaji/wangyun1.bmp",
        "进入", "进入", "", ""
    )
    _e.waitForAAndClickB(
        "ya_assets/images/guaji/zhanchang.bmp", "进入",
        _e.dituLocation, _e.gameBottomLocation
    )
    zhanchang_poss = [
        "0.183,0.117", "0.163,0.103", "0.141,0.12",
        "0.117,0.11", "0.094,0.115", "0.063,0.11", "0.047,0.118",
    ]
    for pos in zhanchang_poss:
        if _e.overed:
            return
        _e.findAndClickPic(
            "ya_assets/images/guaji/zhanchang.bmp",
            "战场一", "战场一", "left",
            "ya_assets/images/zdzd111.bmp", "", pos
        )
    if _e.overed:
        return
    with _e.condition:
        if _e.stopped:
            _e.condition.wait()
    _e.outScript("ya_assets/images/guaji/zhanchang.bmp")
