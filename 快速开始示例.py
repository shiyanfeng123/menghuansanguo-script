# CombatAutoScript 快速开始示例
# 所有配置已根据游戏截图固定，无需手动配置

from Kanloong_combat_script import CombatAutoScript
import threading
import time

# 假设你有一个包含大漠对象的线程实例
class MyThread:
    def __init__(self):
        self.dm = None  # 账号0的大漠对象
        self.win1_dm = None  # 账号1的大漠对象（可选）
        self.win2_dm = None  # 账号2的大漠对象（可选）
        self.overed = False
        self.stoped = False
        
    def get_resource_path(self, path):
        """获取资源文件路径"""
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, path)

# 1. 创建线程实例（你的实际线程类）
thread_instance = MyThread()

# 2. 创建战斗脚本实例（所有配置已在__init__中固定）
combat_script = CombatAutoScript(thread_instance)

# 注意：以下配置已在__init__方法中自动完成，无需手动设置：
# - 战斗区域（enemy_region, ally_region, main_char_region等）
# - 血量条区域（hp_bar_regions）
# - 敌人固定位置（fixed_enemy_positions）
# - 己方单位位置（unit_positions）
# - 技能/道具/武将图片路径

# 如果需要自定义配置，可以覆盖默认值：
# combat_script.enable_main_heal = True        # 主角自动加血
# combat_script.enable_main_summon = True     # 主角自动召唤
# combat_script.keep_support_general = False   # 是否保证辅助武将在场

# 3. 在战斗开始时初始化追踪（第一回合时调用）
def start_combat():
    combat_script.current_turn = 1
    combat_script.init_combat_tracking()
    print("战斗追踪已初始化")

# 4. 启动战斗循环（在单独线程中运行）
def run_combat_loop():
    """战斗循环"""
    while True:
        # 检查是否停止
        if thread_instance.overed:
            break
        if thread_instance.stoped:
            time.sleep(0.5)
            continue
        
        # 对每个账号执行战斗操作
        for i in range(3):
            if combat_script.account_dm and len(combat_script.account_dm) > i:
                if combat_script.account_dm[i]:
                    combat_script.auto_combat(i)
        
        time.sleep(0.5)

# 使用示例：
if __name__ == "__main__":
    # 方式1：使用内置的run_combat_loop方法（推荐）
    combat_thread = threading.Thread(target=combat_script.run_combat_loop, daemon=True)
    combat_thread.start()
    
    # 或者方式2：使用自定义循环
    # combat_thread = threading.Thread(target=run_combat_loop, daemon=True)
    # combat_thread.start()
    
    # 等待战斗开始...
    # 当进入战斗后，调用：
    start_combat()
    
    # 主线程继续运行其他逻辑
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止战斗...")
        thread_instance.overed = True

