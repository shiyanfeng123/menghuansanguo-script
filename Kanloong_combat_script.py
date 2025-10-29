"""
梦幻三国战斗自动操作脚本
功能：自动执行主角和武将的战斗操作
"""

import time
import random
from serveScript import MyThread

class CombatAutoScript:
	def __init__(self, thread_instance):
		"""
		初始化战斗自动操作
		:param thread_instance: MyThread 实例，用于访问大漠对象和区域定义
		"""
		self.thread = thread_instance
		
		# 战斗相关区域定义（需要根据实际游戏界面调整）
		self.enemy_region = None      # 敌军区域 (left)
		self.ally_region = None       # 己方区域 (right)
		self.main_char_region = None  # 主角区域
		self.general_region = None    # 武将区域
		
		# 回合数识别区域（"25"显示的区域）
		self.turn_indicator_region = None
		
		# 武将图片路径
		self.general_images = {
			'刘备': 'serveAssets/images/generals/liubei.bmp',
			'魔化关羽': 'serveAssets/images/generals/guanyu.bmp',
			'曹操': 'serveAssets/images/generals/caocao.bmp'
		}
		
		# 技能图片路径（需要根据实际技能图标添加）
		self.skill_images = {
			# 主角技能
			'主角群体攻击1': 'serveAssets/images/skills/main_group1.bmp',
			'主角群体攻击2': 'serveAssets/images/skills/main_group2.bmp',
			'主角群体攻击3': 'serveAssets/images/skills/main_group3.bmp',
			
			# 辅助武将技能
			'加血': 'serveAssets/images/skills/heal.bmp',
			'加速': 'serveAssets/images/skills/speed.bmp',
			'加攻击': 'serveAssets/images/skills/attack.bmp',
			'控制': 'serveAssets/images/skills/control.bmp',
			'清除状态': 'serveAssets/images/skills/cleanse.bmp',
			
			# 输出武将技能
			'武将群体攻击': 'serveAssets/images/skills/general_group.bmp',
		}
		
		# 物品图片
		self.item_images = {
			'红药': 'serveAssets/images/items/red_potion.bmp',
			'蓝药': 'serveAssets/images/items/blue_potion.bmp',
		}
		
		# 控制开关
		self.keep_support_general = False  # 是否保证辅助武将在场
		self.enable_main_heal = True       # 主角加血开关
		self.enable_main_summon = True     # 主角召唤开关
		
		# 刘备辅助技能释放顺序
		self.support_skill_sequence = ['加攻击', '加血', '加速', '控制', '清除状态']
		self.current_skill_index = 0  # 当前技能索引
		
		# 武将追踪信息（存储每个账号的武将信息）
		self.general_tracking = {}  # {account_index: {general_name: {'type': 'support/dps', 'deployed_turn': turn_number}}}
		self.current_turn = 0  # 当前回合数
		self.support_general_account = None  # 哪个账号有辅助武将（场上）
		
		# 敌军状态图片路径（需要检测的四种状态）
		self.enemy_status_images = {
			'状态1': 'serveAssets/images/status/status1.bmp',
			'状态2': 'serveAssets/images/status/status2.bmp',
			'状态3': 'serveAssets/images/status/status3.bmp',
			'状态4': 'serveAssets/images/status/status4.bmp',
		}
		
		# 主角图片路径（用于检测主角存活状态）
		self.main_char_images = {
			'主角1': 'serveAssets/images/chars/char1.bmp',
			'主角2': 'serveAssets/images/chars/char2.bmp',
			'主角3': 'serveAssets/images/chars/char3.bmp',
		}
		
		# 背包武将图片（用于检测背包中是否有可用武将）
		self.bag_general_images = {
			'刘备': 'serveAssets/images/bag/liubei_bag.bmp',
			'魔化关羽': 'serveAssets/images/bag/guanyu_bag.bmp',
			'曹操': 'serveAssets/images/bag/caocao_bag.bmp',
		}
		
		# 账号状态
		self.account_dm = [
			self.thread.dm,      # 主账号
			self.thread.win1_dm, # 账号1
			self.thread.win2_dm  # 账号2
		]
		
		# 左侧按钮区域定义（根据截图，操作按钮在左侧）
		self.left_button_region = (0, 400, 300, 680)  # 修复此行  # 左侧按钮区域 (x, y, w, h)
		self.skill_panel_region = None   # 技能面板区域（点击按钮后显示）
		self.summon_panel_region = None  # 召唤面板区域
		self.item_panel_region = None    # 道具面板区域
		
		# 按钮图片路径
		self.button_images = {
			'技能按钮': 'serveAssets/images/buttons/skill_btn.bmp',
			'召唤按钮': 'serveAssets/images/buttons/summon_btn.bmp',
			'道具按钮': 'serveAssets/images/buttons/item_btn.bmp',
		}
		
		# 三个账号的角色站位区域（需要实际测量后填入）
		self.account_regions = [
			{
				'ally_char_1': (100, 100, 200, 200),  # 主角1位置
				'ally_char_2': (150, 100, 250, 200),  # 主角2位置
				'ally_char_3': (200, 100, 300, 200),  # 主角3位置
				'ally_general_1': (100, 300, 200, 400),  # 武将1位置
				'ally_general_2': (150, 300, 250, 400),  # 武将2位置
				'ally_general_3': (200, 300, 300, 400),  # 武将3位置
			}
		] * 3  # 假设三个账号区域相同，实际需要分别定义
		
	def init_combat_tracking(self):
		"""
		初始化战斗追踪（第一回合调用）
		检测所有账号的武将情况并初始化追踪数据
		"""
		self.general_tracking = {}
		self.current_turn = 0
		self.support_general_account = None
		
		# 检测每个账号的武将
		for i in range(3):
			if not self.account_dm[i]:
				continue
			
			generals = self.get_all_generals(i)
			self.general_tracking[i] = {}
			
			for general in generals:
				general_name = general['name']
				self.general_tracking[i][general_name] = {
					'type': general['type'],
					'deployed_turn': self.current_turn  # 第一回合
				}
				
				# 记录哪个账号有辅助武将
				if general['type'] == 'support':
					self.support_general_account = i
	
	def set_combat_regions(self, enemy_region, ally_region, main_char_region, general_region, turn_region, left_button_region=None):
		"""
		设置战斗区域
		:param enemy_region: 敌军区域 (x, y, w, h)
		:param ally_region: 己方区域 (x, y, w, h)
		:param main_char_region: 主角区域 (x, y, w, h)
		:param general_region: 武将区域 (x, y, w, h)
		:param turn_region: 回合指示器区域 (x, y, w, h)
		:param left_button_region: 左侧按钮区域 (x, y, w, h)
		"""
		self.enemy_region = enemy_region
		self.ally_region = ally_region
		self.main_char_region = main_char_region
		self.general_region = general_region
		self.turn_indicator_region = turn_region
		if left_button_region:
			self.left_button_region = left_button_region
		
	def is_my_turn(self, dm_object):
		"""
		判断是否是己方回合（通过检测"25"是否显示）
		:param dm_object: 大漠对象
		:return: True if 己方回合, False otherwise
		"""
		x, y, w, h = self.turn_indicator_region
		result = dm_object.FindStrEx(int(x), int(y), int(w), int(h), "25", "ffffff-000000", 1.0)
		return int(result.split('|')[0]) >= 0
		
	def find_general(self, general_name, account_index):
		"""
		在指定账号中查找武将
		:param general_name: 武将名称（'刘备', '魔化关羽', '曹操'）
		:param account_index: 账号索引（0=主账号, 1=账号1, 2=账号2）
		:return: ResXy 对象 or False
		"""
		if account_index < 0 or account_index >= len(self.account_dm):
			return False
		
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return False
			
		x, y, w, h = self.ally_region
		image_path = self.general_images.get(general_name, '')
		if not image_path:
			return False
			
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9999, 0)
		if pos and len(pos) > 0:
			pos_list = pos.split(',')
			if len(pos_list) >= 2:
				return self.thread.ResXy(int(pos_list[0]), int(pos_list[1]))
		return False
		
	def has_support_general_alive(self, account_index):
		"""
		检查指定账号是否有辅助武将存活
		:param account_index: 账号索引
		:return: True if 刘备存活, False otherwise
		"""
		return self.find_general('刘备', account_index) != False
		
	def get_all_generals(self, account_index):
		"""
		获取指定账号中所有在场的武将列表
		:param account_index: 账号索引
		:return: 武将列表，每个元素包含武将名称和类型
		"""
		generals = []
		general_info = [
			('刘备', 'support'),
			('魔化关羽', 'dps'),
			('曹操', 'dps')
		]
		
		for general_name, general_type in general_info:
			if self.find_general(general_name, account_index):
				generals.append({
					'name': general_name,
					'type': general_type
				})
		
		return generals
		
	def update_general_tracking(self, account_index):
		"""
		更新武将追踪信息（检测阵亡的武将）
		"""
		if account_index not in self.general_tracking:
			self.general_tracking[account_index] = {}
		
		current_generals = self.get_all_generals(account_index)
		current_general_names = {g['name'] for g in current_generals}
		
		# 检测哪些武将阵亡了
		for general_name in list(self.general_tracking[account_index].keys()):
			if general_name not in current_general_names:
				# 武将阵亡
				if self.general_tracking[account_index][general_name]['type'] == 'support':
					# 辅助武将阵亡
					self.support_general_account = None
				del self.general_tracking[account_index][general_name]
				print(f"账号{account_index}的武将{general_name}阵亡了")
		
		# 检测新上场的武将
		for general in current_generals:
			general_name = general['name']
			if general_name not in self.general_tracking[account_index]:
				# 新武将上场
				self.general_tracking[account_index][general_name] = {
					'type': general['type'],
					'deployed_turn': self.current_turn
				}
				if general['type'] == 'support':
					self.support_general_account = account_index
	
	def get_team_status(self, account_index):
		"""
		获取指定账号的完整队伍状态
		:param account_index: 账号索引
		:return: 包含主角和武将状态的字典
		"""
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return None
		
		# 检测主角存活状态
		main_chars = []
		for char_name, char_image in self.main_char_images.items():
			x, y, w, h = self.main_char_region
			pos = dm_object.FindPic(int(x), int(y), int(w), int(h), char_image, "000000", 0.9999, 0)
			if pos and len(pos) > 0:
				main_chars.append(char_name)
		
		# 获取在场武将
		generals = self.get_all_generals(account_index)
		
		# 检测是否有辅助武将
		has_support = any(g['type'] == 'support' for g in generals)
		
		return {
			'main_chars': main_chars,           # 存活的男主角列表
			'generals': generals,               # 在场武将列表
			'has_support': has_support,         # 是否有辅助武将
			'general_count': len(generals)      # 武将数量
		}
		
	def check_bag_for_general(self, account_index, general_name):
		"""
		检查背包中是否有指定武将
		:param account_index: 账号索引
		:param general_name: 武将名称
		:return: True if 背包中有该武将
		"""
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return False
		
		# 背包区域（需要根据实际游戏界面设置）
		bag_region = (0, 0, 500, 500)  # 示例区域，需要实际测量
		
		image_path = self.bag_general_images.get(general_name, '')
		if not image_path:
			return False
		
		x, y, w, h = bag_region
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9999, 0)
		return pos and len(pos) > 0
		
	def check_bag_for_support_general(self, account_index):
		"""
		检查背包中是否有辅助武将
		:param account_index: 账号索引
		:return: True if 背包中有辅助武将（刘备）
		"""
		return self.check_bag_for_general(account_index, '刘备')
		
	def need_summon_support_general(self, account_index):
		"""
		判断是否需要召唤辅助武将（刘备）
		:param account_index: 账号索引
		:return: True if 需要召唤刘备, False otherwise
		"""
		if not self.keep_support_general:
			return False
			
		generals = self.get_all_generals(account_index)
		has_support = any(g['name'] == '刘备' for g in generals)
		
		# 如果没有辅助武将，需要召唤
		return not has_support
		
	def can_summon_general(self, account_index):
		"""
		判断是否可以召唤武将（检查武将数量是否少于2个）
		:param account_index: 账号索引
		:return: True if 可以召唤（少于2个武将）, False otherwise
		"""
		generals = self.get_all_generals(account_index)
		# 每个主角最多可以出战2个武将
		return len(generals) < 2
		
	def has_enemy_status(self, account_index):
		"""
		检测敌军是否有需要清除的状态（四种状态之一）
		:param account_index: 账号索引
		:return: True if 检测到状态, False otherwise
		"""
		dm_object = self.account_dm[account_index]
		if not dm_object or not self.enemy_region:
			return False
		
		# 在敌军区域检测四种状态
		x, y, w, h = self.enemy_region
		
		for status_name, status_image_path in self.enemy_status_images.items():
			pos = dm_object.FindPic(int(x), int(y), int(w), int(h), status_image_path, "000000", 0.9999, 0)
			if pos and len(pos) > 0:
				# 检测到任何一种状态，返回True
				return True
		
		return False
		
	def click_left_button(self, button_name, dm_object):
		"""
		点击左侧操作按钮（技能/召唤/道具）
		:param button_name: 按钮名称
		:param dm_object: 大漠对象
		:return: True if 点击成功
		"""
		image_path = self.button_images.get(button_name, '')
		if not image_path:
			return False
			
		x, y, w, h = self.left_button_region
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9999, 0)
		if pos and len(pos) > 0:
			pos_list = pos.split(',')
			if len(pos_list) >= 2:
				dm_object.MoveTo(int(pos_list[0]), int(pos_list[1]))
				time.sleep(0.1)
				dm_object.LeftClick()
				time.sleep(0.2)  # 等待面板弹出
				return True
		return False
		
	def click_skill_icon(self, skill_name, dm_object, panel_region):
		"""
		在技能面板中点击技能图标
		:param skill_name: 技能名称
		:param dm_object: 大漠对象
		:param panel_region: 技能面板区域
		:return: True if 点击成功
		"""
		image_path = self.skill_images.get(skill_name, '')
		if not image_path:
			return False
			
		x, y, w, h = panel_region
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9999, 0)
		if pos and len(pos) > 0:
			pos_list = pos.split(',')
			if len(pos_list) >= 2:
				dm_object.MoveTo(int(pos_list[0]), int(pos_list[1]))
				time.sleep(0.1)
				dm_object.LeftClick()
				time.sleep(0.2)  # 等待选择目标状态
				return True
		return False
		
	def use_skill_workflow(self, skill_name, dm_object, target_type='enemy'):
		"""
		使用技能的完整流程：点击按钮 -> 选择技能 -> 选择目标
		:param skill_name: 技能名称
		:param dm_object: 大漠对象
		:param target_type: 目标类型 'enemy' or 'ally'
		:return: True if 成功
		"""
		# 1. 点击技能按钮
		if not self.click_left_button('技能按钮', dm_object):
			return False
		
		# 2. 在技能面板中选择技能（需要设置技能面板区域）
		panel_region = self.skill_panel_region if self.skill_panel_region else (0, 400, 300, 680)
		if not self.click_skill_icon(skill_name, dm_object, panel_region):
			return False
		
		# 3. 选择目标
		if target_type == 'enemy' and self.enemy_region:
			self.click_enemy_unit(dm_object, self.enemy_region)
		elif target_type == 'ally' and self.ally_region:
			self.click_ally_unit(dm_object, self.ally_region)
		
		return True
		
	def click_ally_unit(self, dm_object, ally_region):
		"""
		随机点击一个友军单位
		:param dm_object: 大漠对象
		:param ally_region: 友军区域
		:return: True if 点击成功
		"""
		x, y, w, h = ally_region
		# 在友军区域随机选择一个位置
		random_x = x + random.randint(0, w // 3)
		random_y = y + random.randint(0, h // 2)
		
		dm_object.MoveTo(random_x, random_y)
		time.sleep(0.1)
		dm_object.LeftClick()
		return True
		
	def click_enemy_unit(self, dm_object, enemy_region):
		"""
		随机点击一个敌军单位
		:param dm_object: 大漠对象
		:param enemy_region: 敌军区域
		:return: True if 点击成功
		"""
		x, y, w, h = enemy_region
		# 在敌军区域随机选择一个位置
		random_x = x + random.randint(0, w // 3)
		random_y = y + random.randint(0, h // 2)
		
		dm_object.MoveTo(random_x, random_y)
		time.sleep(0.1)
		dm_object.LeftClick()
		return True
		
	def use_potion(self, dm_object, ally_region):
		"""
		使用药品（随机选择友军使用）
		:param dm_object: 大漠对象
		:param ally_region: 友军区域
		:return: True if 使用成功
		"""
		# 简化实现，实际需要识别药品图标和位置
		self.click_ally_unit(dm_object, ally_region)
		return True
		
	def main_char_action(self, account_index):
		"""
		主角操作：尝试释放群体攻击，如果全部CD则给武将吃药
		:param account_index: 账号索引
		"""
		dm_object = self.account_dm[account_index]
		if not dm_object or not self.thread:
			return
		
		# 尝试使用群体攻击
		group_attack_skills = ['主角群体攻击1', '主角群体攻击2', '主角群体攻击3']
		skill_used = False
		
		for skill_name in group_attack_skills:
			# 尝试使用技能，如果技能不在CD则使用
			if self.use_skill_workflow(skill_name, dm_object, target_type='enemy'):
				skill_used = True
				break
		
		# 如果所有技能都在CD，则给武将吃药
		if not skill_used and self.enable_main_heal:
			self.use_heal_item(dm_object)
			
	def general_action(self, general_type, account_index):
		"""
		武将操作
		:param general_type: 'support' 辅助武将 or 'dps' 输出武将
		:param account_index: 账号索引
		"""
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return
			
		if general_type == 'dps':
			# 输出武将：使用群体攻击
			self.use_skill_workflow('武将群体攻击', dm_object, target_type='enemy')
		elif general_type == 'support':
			# 辅助武将（刘备）：按策略释放技能
			has_status = self.has_enemy_status(account_index)
			
			if has_status:
				# 检测到敌军有状态，尝试清除状态
				# 清除状态技能有5回合CD，如果找不到图标则等待
				if self.use_skill_workflow('清除状态', dm_object, target_type='enemy'):
					# 成功使用清除状态技能
					pass
				# 如果技能在CD，不执行任何操作（等待CD结束）
			else:
				# 没有检测到状态，按顺序使用辅助技能
				skill_name = self.support_skill_sequence[self.current_skill_index % len(self.support_skill_sequence)]
				
				# 判断技能目标类型
				target_type = 'ally' if skill_name in ['加攻击', '加血', '加速'] else 'enemy'
				
				# 尝试使用技能
				if self.use_skill_workflow(skill_name, dm_object, target_type=target_type):
					# 成功使用技能，切换到下一个技能
					self.current_skill_index += 1
				# 如果技能在CD，保持当前索引（下次还会尝试这个技能）
	
	def use_heal_item(self, dm_object):
		"""
		使用加血道具
		:param dm_object: 大漠对象
		"""
		# 1. 点击道具按钮
		if not self.click_left_button('道具按钮', dm_object):
			return False
		
		# 2. 选择红药（需要在道具面板中实现）
		# TODO: 实现道具选择逻辑
		
		# 3. 选择友军目标
		if self.ally_region:
			self.click_ally_unit(dm_object, self.ally_region)
		
		return True
		
	def summon_general(self, exempt_account_index, target_account_index=None):
		"""
		召唤武将
		:param exempt_account_index: 执行召唤的账号（当前回合的账号）
		:param target_account_index: 目标账号（为哪个账号召唤，None表示为自己召唤）
		"""
		if target_account_index is None:
			target_account_index = exempt_account_index
		
		dm_object = self.account_dm[exempt_account_index]
		if not dm_object:
			return
		
		# 获取目标账号的队伍状态
		team_status = self.get_team_status(target_account_index)
		if not team_status:
			return
		
		# 检查是否可以召唤（武将数量少于2个）
		if team_status['general_count'] >= 2:
			return
		
		# 优先策略：检查是否需要辅助武将
		if self.keep_support_general and not team_status['has_support']:
			# 需要辅助武将，检查背包
			if self.check_bag_for_support_general(target_account_index):
				# 背包中有辅助武将，召唤刘备
				self._execute_summon(dm_object, '刘备', target_account_index)
				return
		
		# 如果没有辅助武将需求或背包中没有辅助武将，召唤输出武将
		output_generals = ['魔化关羽', '曹操']
		for general_name in output_generals:
			if self.check_bag_for_general(target_account_index, general_name):
				self._execute_summon(dm_object, general_name, target_account_index)
				return
		
	def _execute_summon(self, dm_object, general_name, account_index):
		"""
		执行召唤操作
		:param dm_object: 大漠对象
		:param general_name: 要召唤的武将名称
		:param account_index: 目标账号索引
		"""
		# TODO: 实现召唤按钮点击逻辑
		# 1. 点击召唤按钮
		# 2. 在武将列表中选择指定武将
		# 3. 确认召唤
		print(f"召唤武将 {general_name} 到账号 {account_index}")
		
	def check_and_summon_for_allies(self, current_account_index):
		"""
		检查队友账号是否需要召唤武将，优先召唤辅助武将
		:param current_account_index: 当前执行回合的账号索引
		"""
		# 检查所有账号
		for i in range(3):
			if i == current_account_index or not self.account_dm[i]:
				continue
			
			# 获取该账号的队伍状态
			team_status = self.get_team_status(i)
			if not team_status:
				continue
			
			# 每个账号的武将数量少于2个时，尝试为其召唤
			# 3个 contributor 加起来最多6个武将（每个最多2个）
			if team_status['general_count'] < 2:
				# 优先召唤辅助武将
				if self.keep_support_general and not team_status['has_support']:
					if self.check_bag_for_support_general(i):
						self.summon_general(current_account_index, target_account_index=i)
						return
				
				# 如果没有辅助武将，召唤输出武将
				output_generals = ['魔化关羽', '曹操']
				for general_name in output_generals:
					if self.check_bag_for_general(i, general_name):
						self.summon_general(current_account_index, target_account_index=i)
						return
			
	def auto_combat(self, account_index):
		"""
		自动战斗主循环
		:param account_index: 账号索引
		"""
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return
			
		# 检查是否是己方回合
		if not self.is_my_turn(dm_object):
			return
		
		# 0. 全局检测所有账号的队伍状态
		for i in range(3):
			if self.account_dm[i]:
				team_status = self.get_team_status(i)
				print(f"账号{i} 状态: 主角{len(team_status['main_chars'])}个, 武将{team_status['general_count']}个, 有辅助{team_status['has_support']}")
		
		# 1. 主角操作
		self.main_char_action(account_index)
		
		# 2. 检查是否需要召唤武将
		if self.enable_main_summon:
			# 优先检查是否需要为队友召唤武将
			self.check_and_summon_for_allies(account_index)
			
			# 为自己召唤武将
			self.summon_general(account_index)
		
		# 3. 武将操作
		# 获取所有在场的武将
		generals = self.get_all_generals(account_index)
		
		# 遍历每个武将，执行相应操作
		for general in generals:
			general_name = general['name']
			general_type = general['type']
			
			# 根据武将类型执行相应操作
			self.general_action(general_type, account_index)
			
			# 短暂延时，避免操作过快
			time.sleep(0.3)
		
	def run_combat_loop(self):
		"""
		战斗循环（在多开场景下，对每个账号执行）
		"""
		max_attempts = 100  # 最大执行次数
		attempt = 0
		
		while attempt < max_attempts:
			if self.thread and self.thread.stoped:
				break
				
			# 对每个有效的账号执行战斗操作
			for i in range(3):
				if self.account_dm[i]:
					self.auto_combat(i)
					
			time.sleep(0.5)  # 短暂延时
			attempt += 1


# 示例使用
if __name__ == "__main__":
	# 这个脚本需要在 MyThread 的上下文中运行
	# 使用方式：
	# 1. 在 MyFrame 中添加新的脚本选项 "战斗中自动"
	# 2. 在 MyThread.run() 方法中添加对应的脚本执行分支
	# 3. 调用 CombatAutoScript 的功能
	
	print("战斗自动操作脚本已加载")
	print("请将此功能集成到 serveScript.py 的 MyThread 类中")

