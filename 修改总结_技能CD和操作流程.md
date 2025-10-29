# 修改总结：技能CD追踪和操作流程完善

## 已完成的修改

### 1. **技能CD配置**
- ✅ 添加了 `skill_cd_config` 字典，包含所有技能的CD配置
- ✅ 刘备技能：加血2回合CD，清除状态4回合CD，其他无CD
- ✅ 主角技能：两个2回合CD，一个3回合CD
- ✅ 其他技能无CD

### 2. **药品CD配置**
- ✅ 添加了 `арад_сd_config` 字典
- ✅ 恢复药：2回合CD（加血又加蓝）
- ✅ 其他药品无CD

### 3. **CD追踪机制**
- ✅ `skill_cd_tracking`: 追踪技能使用回合
- ✅ `item_cd_tracking`: 追踪药品使用回合
- ✅ `is_skill_ready()`: 检查技能是否可用
- ✅ `is_item_ready()`: 检查药品是否可用
- ✅ `mark_skill_used()`: 标记技能已使用
- ✅ `mark_item_used()`: 标记药品已使用

### 4. **操作流程改进**
- ✅ `use_skill_workflow()`: 添加了CD检查，使用确切点位
- ✅ `use_item_workflow()`: 新增药品使用流程，包含CD检查
- ✅ `click_ally_unit()`: 改为使用确切点位（不再是随机）
- ✅ `click_enemy_unit()`: 使用固定点位或检测位置

## 待完成的重要修改

### 1. **修复 use_revive_item 方法签名**
需要将：
```python
def use_revive_item(self, dm_object, target_x, target_y):
```
改为：
```python
def use_revive_item(self, dm_object, target_x, target_y, account_index):
    return self.use_item_workflow('复活药', dm_object, target_x, target_y, account_index)
```

### 2. **更新所有 use_revive_item 调用**
在 `check_and_revive_dead_main_chars` 方法中（第953和966行），需要添加 `account_index` 参数：
```python
# 第953行
if self.use_revive_item(self.account_dm[ally_index], dead_char_pos[0], dead_char_pos[1], ally_index):

# 第966行  
if self.use_revive_item(self.account_dm[i], dead_char_pos[0], dead_char_pos[1], i):
```

### 3. **完善召唤武将流程 (_execute_summon)**
需要实现完整的召唤流程：
1. 点击召唤按钮
2. 在面板左侧找到要召唤的武将图片（背包中的）
3. 点击武将图片
4. 如果武将数量 < 2，直接召唤
5. 如果武将数量 = 2，找到出战时间更长的武将，点击其确切点位进行替换

### 4. **武将出战时间追踪**
需要在 `general_tracking` 中维护 `deployed_turn`，并在需要替换时找到出战时间最长的武将。

### 5. **添加召唤面板区域配置**
需要在图片路径中添加背包武将图片路径，并设置 `summon_panel_region`。

### 6. **完善辅助技能的目标选择**
对于"加血"等需要指定友军位置的技能，需要从 `unit_positions` 获取确切坐标。

### 7. **更新回合计数**
需要在战斗循环中正确更新 `self.current_turn`。

## 文件修改位置汇总

- 第847-884行：`use_revive_item` 方法需要修改
- 第953行：`use_revive_item` 调用需要添加参数
- 第966行：`use_revive_item` 调用需要添加参数
- 第1005-1010行：`_execute_summon` 方法需要完整实现
- 第838-844行：辅助技能使用需要添加目标位置参数
- `auto_combat` 方法：需要更新回合计数

