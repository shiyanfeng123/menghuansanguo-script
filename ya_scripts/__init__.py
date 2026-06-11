from .dungeon import (
    guandu, hong, zhanhun, mojing, liandan, wuxing, rongdong,
    bamen, guandu_jy, yunyou_jy, laoshu_jy, heifeng,
    qingyuan, yinghun, sangumaolu, mingjiang_tz, mingjiang_cg,
    bangpai, kuangchan, longdao, longzhu, shuasunce,
    zhanhun_new, zhanhun49,
)
from .zhengdian import zhengdian
from .richang import richang, richang49, level49_all
from .guaji import bishuishuxue, wokou, longchao, senluodian
from .event import xigua, gongcheng, longwangling, yinmofu, chuansongfu
from .combined import guandu_hong_zd, mojing_hong_zd
from .combat import zidongzhandou

SCRIPT_REGISTRY = {
    "官渡": (guandu, "dungeon", False),
    "嗜血战场(精英)": (hong, "dungeon", False),
    "战魂楼(精英)": (zhanhun, "dungeon", True),
    "魔镜": (mojing, "dungeon", True),
    "炼丹": (liandan, "dungeon", False),
    "五行": (wuxing, "dungeon", False),
    "溶洞": (rongdong, "dungeon", False),
    "80精英": (bamen, "dungeon", False),
    "官渡精英": (guandu_jy, "dungeon", False),
    "云游精英": (yunyou_jy, "dungeon", False),
    "100精英": (laoshu_jy, "dungeon", False),
    "黑风山寨": (heifeng, "dungeon", True),
    "青渊": (qingyuan, "dungeon", False),
    "英魂秘境(精英)": (yinghun, "dungeon", False),
    "三顾茅庐": (sangumaolu, "dungeon", False),
    "名将挑战赛": (mingjiang_tz, "dungeon", False),
    "名将闯关": (mingjiang_cg, "dungeon", False),
    "帮派任务": (bangpai, "dungeon", False),
    "矿产": (kuangchan, "dungeon", False),
    "龙岛": (longdao, "dungeon", False),
    "龙珠": (longzhu, "dungeon", False),
    "刷孙策": (shuasunce, "dungeon", False),
    "炼狱战魂楼": (zhanhun_new, "dungeon", True),
    "49战魂": (zhanhun49, "dungeon", False),
    "整点": (zhengdian, "zhengdian", True),
    "抢龙": (zhengdian, "zhengdian", False),
    "49整点": (zhengdian, "zhengdian", False),
    "日常": (richang, "daily", False),
    "49日常": (richang49, "daily", False),
    "49一键": (level49_all, "daily", False),
    "战魂+红+整点": (guandu_hong_zd, "combined", False),
    "战魂+红+魔镜+整点": (mojing_hong_zd, "combined", False),
    "挂机+整点": (bishuishuxue, "guaji", True),
    "老鼠": (bishuishuxue, "guaji", False),
    "倭寇": (wokou, "guaji", False),
    "森罗殿": (senluodian, "guaji", False),
    "龙珠挂机": (longchao, "guaji", False),
    "西瓜保卫战": (xigua, "event", False),
    "怪物攻城": (gongcheng, "event", False),
    "龙王令": (longwangling, "event", False),
    "引魔符": (yinmofu, "event", False),
    "传送符": (chuansongfu, "event", False),
    "自动战斗": (zidongzhandou, "combat", False),
}


def get_script_names():
    return list(SCRIPT_REGISTRY.keys())


def get_script(name):
    entry = SCRIPT_REGISTRY.get(name)
    return entry[0] if entry else None
