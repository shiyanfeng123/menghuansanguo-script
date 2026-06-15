# -*- coding: utf-8 -*-
r"""
副本测试运行器 + 文字图片自动收割

用法:
    python test_runner.py <脚本名>

示例:
    python test_runner.py 魔镜
    python test_runner.py 官渡
    python test_runner.py 黑风

支持脚本名:
    魔镜, 官渡, 黑风, 炼丹, 溶洞, 龙岛, 五行,
    战魂楼(精英), 炼狱战魂楼, 名将闯关, 名将挑战赛,
    嗜血战场(精英), 英魂秘境(精英), 官渡精英, 云游精英,
    80精英, 100精英, 刷孙策, 西瓜保卫战

说明:
    运行脚本前确保游戏窗口名为 "111" 且角色在正确的起始位置。
    运行时缺失的文字图片会被自动截图保存到 ya_assets/images/text/。
    脚本运行结束后会打印已截图和剩余缺失数量。
"""
import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ya_engine import GameEngine, GameWindow

DUNGEON_MAP = {
    "魔镜": "mojingWhile",
    "官渡": "guanduWhile",
    "黑风": "heifengWhile",
    "炼丹": "liandanWhile",
    "溶洞": "rongdongWhile",
    "龙岛": "longdaoScript",
    "五行": "wuxingWhile",
    "名将闯关": "mingjiangchuangguan",
    "名将挑战赛": "mingjiangtiaozhanWhile",
    "战魂楼(精英)": "zhanhunWhile",
    "炼狱战魂楼": "zhanhunNewScript",
    "嗜血战场(精英)": "hongWhile",
    "英魂秘境(精英)": "yinghunWhile",
    "官渡精英": "guanduJyScript",
    "云游精英": "yunyouJyScript",
    "80精英": "bamenScript",
    "100精英": "laoshuJyScript",
    "刷孙策": "shuasunceScript",
    "西瓜保卫战": "xiguaScriptWhile",
}


def main():
    if len(sys.argv) < 2:
        print("用法: python test_runner.py <脚本名>")
        print("可用脚本:", ", ".join(DUNGEON_MAP.keys()))
        return

    name = sys.argv[1]
    method_name = DUNGEON_MAP.get(name)
    if not method_name:
        print(f"未知脚本: {name}")
        print("可用脚本:", ", ".join(DUNGEON_MAP.keys()))
        return

    print("=" * 60)
    print(f"  副本测试: {name} ({method_name})")
    print("=" * 60)

    print("\n[1] 导入 ya_game_scripts ...")
    import ya_game_scripts as yag

    print("[2] 查找游戏窗口 '111' ...")
    engine = GameEngine()
    hwnd = engine.find_window("111")
    if not hwnd:
        print("[FAIL] 未找到窗口 '111'!")
        return
    print(f"  找到窗口: hwnd={hwnd}")

    win = GameWindow(hwnd)
    engine.main_win = win

    print("[3] 创建测试实例 ...")
    class DummyFrame:
        mac_address = ""
        mac_address1 = ""
        choice_line = ""
        has_script = ""
        user_name = ""
        end_time = ""
        zhanhunFloor = "25层"
        lianyu_count = "5"
        qingyuan_count = "5"
        zhanhun_count = "5"
        zhanhunFloorNew = "27层"
        mojingFloor = ""
        addBloudFlag = False
        teammate1_name = ""
        teammate2_name = ""
        zhengdianFloor = ""
        shihun_floor = ""
        shihun_count = "5"
        heifengFloor = ""
        teammate1_pos = 0
        teammate2_pos = 0
        team_leader_pos = 0
        afterZreo = ""
        richangSelection = []
        heifengCount = "9"
        enablePersistentLiubei = False
        liubeiCounts = {}

    instance = yag.MyThread(name, None)
    instance.frame = DummyFrame()
    instance.click_hwnd = hwnd
    instance.win1_hwnd = 0
    instance.win2_hwnd = 0
    instance.hasRefresh = True
    instance.locationX = 0
    instance.locationY = 0
    instance.locationWidth = win.capture._width
    instance.locationHeight = win.capture._height
    instance.dituLocation = (
        int(instance.locationWidth * 0.8), 0,
        instance.locationWidth, int(instance.locationHeight * 0.2))
    instance.gameLocation = (0, 0, instance.locationWidth, instance.locationHeight)
    instance.gameBottomLocation = (0, int(instance.locationHeight * 0.3), instance.locationWidth, instance.locationHeight)
    instance.gameLeftLocation = (0, int(instance.locationHeight * 0.3), int(instance.locationWidth * 0.7), instance.locationHeight)
    instance.talkLocation = (0, int(instance.locationHeight * 0.5), int(instance.locationWidth * 0.5), instance.locationHeight)

    def get_resource_path(self, relative_path):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    instance.get_resource_path = get_resource_path.__get__(instance)

    yag.engine = engine
    yag.engine.scriptName = name
    yag.engine.addBloudFlag = False
    yag.engine.zhengdianFloor = ""
    yag.engine.main_win = win

    def dummy_check_stop_or_over(self):
        return False
    instance.check_stop_or_over = dummy_check_stop_or_over.__get__(instance)

    method = getattr(yag.MyThread, method_name, None)
    if not method:
        print(f"[FAIL] 方法 {method_name} 不存在!")
        return

    print(f"[4] 开始运行 {name}...")
    print("    (按 Ctrl+C 停止)")
    print()

    before = _count_text_images()

    try:
        method(instance)
    except KeyboardInterrupt:
        print("\n[STOP] 用户中断")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    after = _count_text_images()
    captured = after - before
    total = _total_text_map()

    print()
    print("=" * 60)
    print(f"  运行完成: {name}")
    print(f"  本轮截图: {captured} 个")
    print(f"  已有图片: {after}/{total}")
    print("=" * 60)


def _count_text_images():
    text_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ya_assets", "images", "text")
    return sum(1 for f in os.listdir(text_dir) if f.endswith(".bmp"))


def _total_text_map():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ya_assets", "images", "text")
    txt_file = os.path.join(base, "文字图片替换清单.txt")
    count = 0
    if os.path.isfile(txt_file):
        with open(txt_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ".bmp" not in line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3 and parts[2].endswith(".bmp"):
                    count += 1
    return count


if __name__ == "__main__":
    main()
