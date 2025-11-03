# CombatAutoScript 使用指南

## 📚 概述

`CombatAutoScript` 是一个战斗自动化脚本类，用于自动执行游戏战斗中的操作，包括：
- 主角自动释放技能
- 主角自动使用药品加血
- 主角自动召唤武将
- 武将自动释放技能
- 实时战斗播报窗口

## 🔧 基本使用步骤

### 1. 导入类

```python
from Kanloong_combat_script import CombatAutoScript
```

### 2. 初始化实例（所有配置已自动完成）

```python
# thread_instance 是你的 MyThread 实例（或其他包含大漠对象的线程实例）
combat_script = CombatAutoScript(thread_instance)
```

**✅ 重要：所有配置已在 `__init__` 方法中根据游戏截图（900x580窗口）自动配置完成，无需手动设置！**

**自动配置的内容包括：**
- ✅ 战斗区域（enemy_region, ally_region, main_char_region等）
- ✅ 血量条区域（9个区域的坐标）
- ✅ 敌人固定位置（3个账号，每个账号3个敌人位置）
- ✅ 己方单位位置（主角和武将的中心点）
- ✅ 技能/道具/武将图片路径
- ✅ 面板区域（技能面板、召唤面板、道具面板）

**注意：** `thread_instance` 需要包含以下属性或方法：
- `dm`: 主窗口的大漠对象（账号0）
- `win1_dm`: 窗口1的大漠对象（账号1，可选）
- `win2_dm`: 窗口2的大漠对象（账号2，可选）
- `get_resource_path()`: 获取资源文件路径的方法

### 3. 可选：自定义配置（如果需要修改默认值）

如果你想修改某些配置，可以在初始化后覆盖默认值：

```python
# 如果需要重新设置战斗区域（一般不需要）
combat_script.set_combat_regions(
    enemy_region=(0, 200, 500, 580),
    ally_region=(500, 200, 900, 580),
    main_char_region=(680, 250, 900, 550),
    general_region=(480, 250, 700, 550),
    turn_region=(400, 0, 500, 50),
    right_button_region=(400, 450, 600, 580),
    hp_bar_regions=[...]  # 9个区域
)

# 如果需要重新设置敌人位置（一般不需要）
combat_script.set_fixed_enemy_positions(
    account_index=0,
    enemy_positions=[
        (150, 300),  # 敌人1中心点
        (150, 375),  # 敌人2中心点
        (150, 450),  # 敌人3中心点
    ]
)
```

**默认配置说明（已固定，无需修改）：**
- 游戏窗口：900x580
- 敌人位置（左侧）：(150, 300), (150, 375), (150, 450)
- 主角位置（右侧最右）：(775, 310), (775, 380), (775, 450)
- 武将位置（主角前方）：前排(595, 310/380/450)，后排(655, 310/380/450)

### 5. 配置控制开关（可选）

```python
# 是否保证辅助武将在场（自动召唤刘备）
combat_script.keep_support_general = False

# 主角是否自动加血
combat_script.enable_main_heal = True

# 主角是否自动召唤武将
combat_script.enable_main_summon = True
```

### 6. 初始化战斗追踪（必需，在战斗开始时调用）

```python
# 在战斗开始时（第一回合）调用
combat_script.current_turn = 1  # 设置当前回合数
combat_script.init_combat_tracking()  # 初始化追踪信息
```

### 7. 启动战斗循环

```python
# 方式1：在新线程中运行
import threading

def combat_thread():
    combat_script.run_combat_loop()

thread = threading.Thread(target=combat_thread, daemon=True)
thread.start()

# 方式2：在现有的循环中调用
while True:
    # 检查是否是己方回合
    for i in range(3):  # 遍历3个账号
        if combat_script.account_dm and len(combat_script.account_dm) > i:
            combat_script.auto_combat(i)
    time.sleep(0.5)
```

## 📋 完整示例（简化版）

```python
from Kanloong_combat_script import CombatAutoScript
import threading
import time

# 假设你有一个 MyThread 实例
class MyThread(threading.Thread):
    def __init__(self):
        super().__init__()
        # 初始化大漠对象
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

# 创建线程实例
thread_instance = MyThread()

# ✅ 步骤1：创建战斗脚本实例（所有配置已自动完成）
combat_script = CombatAutoScript(thread_instance)
# 注意：所有区域配置、敌人位置、单位位置都已根据游戏截图自动配置！

# ✅ 步骤2：可选配置（如果需要修改默认行为）
combat_script.enable_main_heal = True        # 主角自动加血
combat_script.enable_main_summon = True     # 主角自动召唤
combat_script.keep_support_general = False   # 是否保证辅助武将在场

# ✅ 步骤3：等待进入战斗... 当进入战斗后：

# 初始化战斗追踪（第一回合时调用）
combat_script.current_turn = 1
combat_script.init_combat_tracking()
print("战斗追踪已初始化")

# ✅ 步骤4：启动战斗循环（使用内置方法，最简单）
combat_thread = threading.Thread(target=combat_script.run_combat_loop, daemon=True)
combat_thread.start()

# 主线程继续运行其他逻辑
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("停止战斗...")
    thread_instance.overed = True
```

**就是这么简单！** 所有配置都已自动完成，你只需要：
1. 创建实例
2. 进入战斗时初始化追踪
3. 启动战斗循环

就是这么简单！

## 🎯 关键配置项说明

### 必需配置（已自动完成）

1. **战斗区域** ✅
   - 已在 `__init__` 中根据游戏截图（900x580）自动配置
   - 格式：`(x, y, w, h)`，其中 `w, h` 是结束坐标

2. **敌人固定位置** ✅
   - 已在 `__init__` 中自动配置，3个账号每个账号3个敌人位置
   - 默认敌人位置：(150, 300), (150, 375), (150, 450)

3. **初始化追踪** ⚠️ （需要手动调用）
   - 必须在第一回合时调用 `combat_script.init_combat_tracking()`
   - 用于追踪武将和主角状态

### 可选配置

1. **控制开关**
   - `keep_support_general`: 是否保证辅助武将在场
   - `enable_main_heal`: 主角是否自动加血
   - `enable_main_summon`: 主角是否自动召唤

2. **技能图片路径**
   - 默认使用 `serveAssets/images/auto/` 下的图片
   - 如果需要修改，可以修改 `__init__` 方法中的 `skill_images` 字典

3. **CD 配置**
   - 默认CD配置在 `__init__` 方法中的 `skill_cd_config` 字典
   - 可以根据实际情况调整

## 📝 注意事项

1. **坐标系统**
   - 所有坐标基于 900x580 的游戏窗口
   - 如果游戏窗口大小不同，需要按比例调整坐标

2. **多账号支持**
   - 支持最多3个账号同时战斗
   - 每个账号需要单独设置敌人位置

3. **线程安全**
   - 战斗循环应该在单独的线程中运行
   - 主线程用于GUI和游戏操作

4. **资源文件**
   - 确保所有图片资源文件存在于 `serveAssets/images/auto/` 目录
   - 图片文件名必须与代码中的配置一致

5. **战斗播报窗口**
   - 自动创建战斗播报窗口，实时显示战斗信息
   - 窗口会在初始化时自动创建并显示

## 🔍 调试建议

1. **检查坐标**
   - 使用截图工具确认坐标是否正确
   - 可以先用鼠标点击测试坐标是否能正确选中目标

2. **检查图片资源**
   - 确保所有图片文件存在
   - 图片应该是BMP格式

3. **查看日志**
   - 所有操作都会打印到控制台
   - 战斗播报窗口也会显示实时信息

4. **测试单个功能**
   - 可以先测试单个功能（如主角技能、召唤等）
   - 确认单个功能正常后再启用全部功能

## ❓ 常见问题

**Q: 如何确定坐标是否正确？**
A: 可以使用截图工具查看游戏窗口坐标，或者先用简单的鼠标点击测试。

**Q: 如果游戏窗口大小不是900x580怎么办？**
A: 需要按比例调整所有坐标。例如，如果窗口是1800x1160（2倍大小），所有坐标都要乘以2。

**Q: 如何停止战斗循环？**
A: 设置 `thread_instance.overed = True` 或 `thread_instance.stoped = True`。

**Q: 战斗播报窗口没有显示？**
A: 确保wxPython已安装，并且有wx应用程序实例正在运行。

