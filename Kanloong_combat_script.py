"""
梦幻三国战斗自动操作脚本
功能：自动执行主角和武将的战斗操作
"""

import time
import random
# 修复：避免循环引用，移除直接导入
# from serveScript import MyThread  # 不再需要直接导入

# 定义 ResXy 类（避免循环引用）
class ResXy:
	"""坐标结果类"""
	def __init__(self, x, y):
		self.x = x
		self.y = y

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
			'恢复药': 'serveAssets/images/items/recovery_potion.bmp',  # 恢复药（加血又加蓝，2回合CD）
			'红药': 'serveAssets/images/items/recovery_potion.bmp',    # 恢复药的别名
			'蓝药': 'serveAssets/images/items/blue_potion.bmp',
			'复活药': 'serveAssets/images/items/revive_potion.bmp',   # 复活药
		}
		
		# 控制开关
		self.keep_support_general = False  # 是否保证辅助武将在场
		self.enable_main_heal = True       # 主角加血开关
		self.enable_main_summon = True     # 主角召唤开关
		
		# 刘备辅助技能释放顺序
		self.support_skill_sequence = ['加攻击', '加血', '加速', '控制', '清除状态']
		self.current_skill_index = 0  # 当前技能索引
		
		# 技能CD配置（回合数）
		self.skill_cd_config = {
			# 刘备技能
			'加血': 2,           # 2回合CD
			'清除状态': 4,        # 4回合CD
			'加攻击': 0,         # 无CD
			'加速': 0,           # 无CD
			'控制': 0,           # 无CD
			# 主角技能
			'主角群体攻击1': 2,   # 2回合CD
			'主角群体攻击2': 3,   # 3回合CD
			'主角群体攻击3': 2,   # 2回合CD
			# 武将技能
			'武将群体攻击': 0,     # 无CD
		}
		
		# 药品CD配置
		self.item_cd_config = {
			'恢复药': 2,         # 2回合CD（红药，加血又加蓝）
			'红药': 2,           # 恢复药的别名
			'复活药': 0,         # 无CD
			'蓝药': 0,           # 无CD
		}
		
		# 技能CD追踪 {account_index: {skill_name: last_used_turn}}
		self.skill_cd_tracking = {}
		
		# 药品CD追踪 {account_index: {item_name: last_used_turn}}
		self.item_cd_tracking = {}
		
		# 武将追踪信息（存储每个账号的武将信息）
		self.general_tracking = {}  # {account_index: {general_name: {'type': 'support/dps', 'deployed_turn': turn_number, 'position': (x, y)}}}
		self.current_turn = 0  # 当前回合数
		self.support_general_account = None  # 哪个账号有辅助武将（场上）
		self.turn_processed = False  # 当前回合是否已处理（防止重复更新回合数）
		self._last_turn_state = False  # 上一回合状态（用于检测回合变化）
		
		# 敌军状态图片路径（需要检测的四种状态）
		self.enemy_status_images = {
			'状态1': 'serveAssets/images/status/status1.bmp',
			'状态2': 'serveAssets/images/status/status2.bmp',
			'状态3': 'serveAssets/images/status/status3.bmp',
			'状态4': 'serveAssets/images/status/status4.bmp',
		}
		
		# 敌人图片路径（用于识别敌人的位置）
		self.enemy_images = {
			'敌人1': 'serveAssets/images/enemies/enemy1.bmp',
			'敌人2': 'serveAssets/images/enemies/enemy2.bmp',
			'敌人3': 'serveAssets/images/enemies/enemy3.bmp',
			# 可以添加更多敌人的图片路径
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
		
		# 血量条图片（用于检测血量低的单位）
		# 识别到这张图片说明单位血量低，需要加血
		self.low_hp_indicator_image = 'serveAssets/images/ui/low_hp_bar.bmp'  # 血量低的标识图片
		
		# 9个血量条检测区域（每个角色和武将都有专门的区域）
		# 顺序：主角1、主角2、主角3、武将1、武将2、武将3、武将4、武将5、武将6
		# 格式：[(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
		self.hp_bar_regions = []  # 9个血量条区域列表，通过set_combat_regions设置
		
		# 血量条区域到单位的映射关系
		# {account_index: {region_index: (unit_type, unit_name, heal_position)}}
		# unit_type: 'main_char' 或 'general'
		# region_index: 0-8 (对应9个区域：0-2主角，3-8武将)
		# heal_position: (x, y) 加血点位
		self.hp_bar_unit_mapping = {}  # 血量条区域到单位的映射
		
		# 账号状态（延迟初始化，避免thread属性未设置时报错）
		# 注意：account_dm 会在首次使用时通过属性或方法来获取
		self._account_dm = None  # 延迟初始化的账号列表
		
		# 右侧按钮区域定义（根据实际游戏，操作按钮在右侧）
		self.right_button_region = None  # 右侧按钮区域 (x, y, w, h)，通过set_combat_regions设置
		self.skill_panel_region = None   # 技能面板区域（点击按钮后显示）
		self.summon_panel_region = None  # 召唤面板区域
		self.item_panel_region = None    # 道具面板区域
		
		# 主角、武将、敌人的确切点位存储
		# {account_index: {'main_chars': [(char_name, x, y), ...], 'generals': [(general_name, x, y), ...], 'enemies': [(enemy_name, x, y), ...]}}
		self.unit_positions = {}
		
		# 阵亡主角的位置存储（用于复活）
		# {account_index: {char_name: (x, y), ...}}
		self.dead_main_char_positions = {}
		
		# 敌人的固定点位配置（如果敌人位置是固定的，可以在这里配置）
		# {(account_index, enemy_index): (x, y)} 或 {(account_index, enemy_name): (x, y)}
		self.fixed_enemy_positions = {}
		
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
		检测所有账号的武将和主角情况并初始化追踪数据
		"""
		self.general_tracking = {}
		self.unit_positions = {}
		self.dead_main_char_positions = {}  # 初始化阵亡主角位置存储
		self.skill_cd_tracking = {}
		self.item_cd_tracking = {}
		self.current_turn = 0
		self.support_general_account = None
		self.turn_processed = False  # 修复：初始化时重置回合处理标志
		self._last_turn_state = False  # 修复：初始化回合状态标志
		
		# 检测每个账号的武将和主角
		for i in range(3):
			if not self.account_dm[i]:
				continue
			
			self.general_tracking[i] = {}
			self.unit_positions[i] = {
				'main_chars': [],
				'generals': [],
				'enemies': []
			}
			
			# 检测武将
			generals = self.get_all_generals(i)
			for general in generals:
				general_name = general['name']
				general_pos = self.find_general(general_name, i)
				if general_pos:
					self.general_tracking[i][general_name] = {
						'type': general['type'],
						'deployed_turn': self.current_turn,
						'position': (general_pos.x, general_pos.y)
					}
					self.unit_positions[i]['generals'].append((general_name, general_pos.x, general_pos.y))
					
					# 记录哪个账号有辅助武将
					if general['type'] == 'support':
						self.support_general_account = i
			
			# 检测主角
			team_status = self.get_team_status(i)
			if team_status:
				for char_name in team_status['main_chars']:
					char_pos = self.find_main_char(char_name, i)
					if char_pos:
						self.unit_positions[i]['main_chars'].append((char_name, char_pos.x, char_pos.y))
						print(f"账号{i} 主角 {char_name} 位置: ({char_pos.x}, {char_pos.y})")
			
			# 检测敌人位置（需要在战斗开始后检测）
			# self.detect_enemy_positions(i)  # 注释掉，在auto_combat中实时检测
	
	def set_combat_regions(self, enemy_region, ally_region, main_char_region, general_region, turn_region, right_button_region=None, hp_bar_regions=None):
		"""
		设置战斗区域
		:param enemy_region: 敌军区域 (x, y, w, h)
		:param ally_region: 己方区域 (x, y, w, h)
		:param main_char_region: 主角区域 (x, y, w, h)
		:param general_region: 武将区域 (x, y, w, h)
		:param turn_region: 回合指示器区域 (x, y, w, h)
		:param right_button_region: 右侧按钮区域 (x, y, w, h)
		:param hp_bar_regions: 9个血量条检测区域列表 [(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
		"""
		self.enemy_region = enemy_region
		self.ally_region = ally_region
		self.main_char_region = main_char_region
		self.general_region = general_region
		self.turn_indicator_region = turn_region
		if right_button_region:
			self.right_button_region = right_button_region
		if hp_bar_regions:
			if len(hp_bar_regions) == 9:
				self.hp_bar_regions = hp_bar_regions
			else:
				print(f"警告：血量条区域数量不正确，期望9个，实际{len(hp_bar_regions)}个")
		
	def is_my_turn(self, dm_object):
		"""
		判断是否是己方回合（通过检测右侧按钮区是否存在来判断）
		:param dm_object: 大漠对象
		:return: True if 己方回合, False otherwise
		"""
		if not self.right_button_region:
			# 如果没有设置按钮区域，使用原来的方法检测回合指示器
			if self.turn_indicator_region:
				x, y, w, h = self.turn_indicator_region
				result = dm_object.FindStrEx(int(x), int(y), int(w), int(h), "25", "ffffff-000000", 1.0)
				return int(result.split('|')[0]) >= 0
			return False
		
		# 通过检测右侧按钮区域是否存在来判断是否是我方回合
		# 如果按钮区域存在（可以识别到按钮），说明是我方回合
		try:
			if not isinstance(self.right_button_region, (tuple, list)) or len(self.right_button_region) != 4:
				return False
			x, y, w, h = self.right_button_region
			# 检测任意一个按钮是否存在（技能按钮、召唤按钮、道具按钮）
			for button_name in ['技能按钮', '召唤按钮', '道具按钮']:
				image_path = self.button_images.get(button_name, '')
				if image_path:
					try:
						pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9, 0)
						if pos and len(pos) > 0:
							return True
					except Exception as e:
						print(f"检测按钮 {button_name} 时出错: {e}")
						continue
		except (ValueError, TypeError) as e:
			print(f"判断回合状态时出错: {e}")
		return False
		
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
			
		if not self.ally_region:
			return False
			
		x, y, w, h = self.ally_region
		image_path = self.general_images.get(general_name, '')
		if not image_path:
			return False
			
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9999, 0)
		if pos and len(pos) > 0:
			try:
				pos_list = pos.split(',')
				if len(pos_list) >= 2:
					# 修复：验证是否为有效数字
					pos_x = int(pos_list[0])
					pos_y = int(pos_list[1])
					return ResXy(pos_x, pos_y)
			except (ValueError, IndexError) as e:
				print(f"解析武将 {general_name} 位置失败: {pos}, 错误: {e}")
				return False
		return False
	
	def find_main_char(self, char_name, account_index):
		"""
		在指定账号中查找主角
		:param char_name: 主角名称（'主角1', '主角2', '主角3'）
		:param account_index: 账号索引（0=主账号, 1=账号1, 2=账号2）
		:return: ResXy 对象 or False
		"""
		if account_index < 0 or account_index >= len(self.account_dm):
			return False
		
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return False
		
		if not self.main_char_region:
			return False
		
		x, y, w, h = self.main_char_region
		image_path = self.main_char_images.get(char_name, '')
		if not image_path:
			return False
		
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9999, 0)
		if pos and len(pos) > 0:
			try:
				pos_list = pos.split(',')
				if len(pos_list) >= 2:
					# 修复：验证是否为有效数字
					pos_x = int(pos_list[0])
					pos_y = int(pos_list[1])
					return ResXy(pos_x, pos_y)
			except (ValueError, IndexError) as e:
				print(f"解析主角 {char_name} 位置失败: {pos}, 错误: {e}")
				return False
		return False
	
	def detect_enemy_positions(self, account_index):
		"""
		检测并记录敌人的确切位置
		:param account_index: 账号索引
		"""
		if account_index not in self.unit_positions:
			self.unit_positions[account_index] = {'main_chars': [], 'generals': [], 'enemies': []}
		
		if not self.enemy_region or not self.account_dm[account_index]:
			return
		
		dm_object = self.account_dm[account_index]
		# 修复：再次确认区域格式正确后再解包
		if not isinstance(self.enemy_region, (tuple, list)) or len(self.enemy_region) != 4:
			return
		x, y, w, h = self.enemy_region
		
		# 检测所有敌人的位置
		enemy_positions = []
		for enemy_name, enemy_image_path in self.enemy_images.items():
			try:
				pos = dm_object.FindPic(int(x), int(y), int(w), int(h), enemy_image_path, "000000", 0.9999, 0)
				if pos and len(pos) > 0:
					try:
						pos_list = pos.split(',')
						if len(pos_list) >= 2:
							# 修复：验证是否为有效数字
							enemy_x = int(pos_list[0])
							enemy_y = int(pos_list[1])
							enemy_positions.append((enemy_name, enemy_x, enemy_y))
							print(f"账号{account_index} 检测到 {enemy_name} 位置: ({enemy_x}, {enemy_y})")
					except (ValueError, IndexError) as e:
						print(f"解析敌人 {enemy_name} 位置失败: {pos}, 错误: {e}")
						continue
			except Exception as e:
				print(f"检测敌人 {enemy_name} 时出错: {e}")
				continue
		
		# 更新敌人位置列表
		self.unit_positions[account_index]['enemies'] = enemy_positions
		
	def _get_account_dm(self):
		"""
		获取账号大漠对象列表（延迟初始化）
		:return: [dm, win1_dm, win2_dm] 列表
		"""
		if self._account_dm is None:
			# 延迟初始化，安全地获取账号对象
			try:
				self._account_dm = [
					getattr(self.thread, 'dm', None) if self.thread else None,      # 主账号
					getattr(self.thread, 'win1_dm', None) if self.thread else None, # 账号1
					getattr(self.thread, 'win2_dm', None) if self.thread else None  # 账号2
				]
			except AttributeError as e:
				print(f"获取账号对象时出错: {e}")
				self._account_dm = [None, None, None]
		return self._account_dm
	
	@property
	def account_dm(self):
		"""
		账号大漠对象列表属性（向后兼容）
		"""
		return self._get_account_dm()
	
	def has_support_general_alive(self, account_index):
		"""
		检查指定账号是否有辅助武将存活
		:param account_index: 账号索引
		:return: True if 刘备存活, False otherwise
		"""
		result = self.find_general('刘备', account_index)
		return result is not False and result is not None
		
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
		更新武将追踪信息（检测阵亡的武将和主角）
		"""
		if account_index not in self.general_tracking:
			self.general_tracking[account_index] = {}
		if account_index not in self.unit_positions:
			self.unit_positions[account_index] = {'main_chars': [], 'generals': [], 'enemies': []}
		
		# 检测武将阵亡
		current_generals = self.get_all_generals(account_index)
		current_general_names = {g['name'] for g in current_generals}
		
		# 检测哪些武将阵亡了
		dead_generals = []
		for general_name in list(self.general_tracking[account_index].keys()):
			if general_name not in current_general_names:
				# 武将阵亡
				if self.general_tracking[account_index][general_name]['type'] == 'support':
					# 辅助武将阵亡
					self.support_general_account = None
				dead_generals.append(general_name)
				print(f"账号{account_index}的武将{general_name}阵亡了")
				del self.general_tracking[account_index][general_name]
		
		# 修复：清空武将位置列表，重新填充所有存活武将的位置（与主角位置更新策略一致）
		self.unit_positions[account_index]['generals'] = []
		
		# 检测新上场的武将并更新所有存活武将的位置
		for general in current_generals:
			general_name = general['name']
			general_pos = self.find_general(general_name, account_index)
			pos = (general_pos.x, general_pos.y) if general_pos else None
			
			if general_name not in self.general_tracking[account_index]:
				# 新武将上场
				self.general_tracking[account_index][general_name] = {
					'type': general['type'],
					'deployed_turn': self.current_turn,
					'position': pos
				}
				if general['type'] == 'support':
					self.support_general_account = account_index
			else:
				# 更新已存在武将的位置信息（位置可能发生变化）
				self.general_tracking[account_index][general_name]['position'] = pos
			
			# 更新位置列表（所有存活武将）
			if general_pos:
				self.unit_positions[account_index]['generals'].append((general_name, general_pos.x, general_pos.y))
		
		# 检测主角阵亡（修复BUG：在清空列表前保存阵亡主角的位置）
		team_status = self.get_team_status(account_index)
		if team_status:
			current_main_chars = set(team_status['main_chars'])
			tracked_main_chars_dict = {}
			
			# 在清空列表前，保存所有追踪的主角位置
			for char_name, x, y in self.unit_positions[account_index]['main_chars']:
				tracked_main_chars_dict[char_name] = (x, y)
			
			tracked_main_chars = set(tracked_main_chars_dict.keys())
			
			# 检测阵亡的主角，并保存其位置信息（用于复活）
			dead_main_chars = tracked_main_chars - current_main_chars
			for char_name in dead_main_chars:
				print(f"账号{account_index}的主角{char_name}阵亡了")
				# 保存阵亡主角的位置到独立字典（用于后续复活）
				if account_index not in self.dead_main_char_positions:
					self.dead_main_char_positions[account_index] = {}
				if char_name in tracked_main_chars_dict:
					self.dead_main_char_positions[account_index][char_name] = tracked_main_chars_dict[char_name]
			
			# 更新主角位置列表
			self.unit_positions[account_index]['main_chars'] = []
			for char_name in current_main_chars:
				char_pos = self.find_main_char(char_name, account_index)
				if char_pos:
					self.unit_positions[account_index]['main_chars'].append((char_name, char_pos.x, char_pos.y))
					print(f"账号{account_index} 主角 {char_name} 存活，位置: ({char_pos.x}, {char_pos.y})")
	
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
		# 修复：检查区域是否已设置
		if not self.main_char_region:
			# 区域未设置，返回空列表（不影响其他状态的检测）
			pass
		else:
			for char_name, char_image in self.main_char_images.items():
				try:
					x, y, w, h = self.main_char_region
					pos = dm_object.FindPic(int(x), int(y), int(w), int(h), char_image, "000000", 0.9999, 0)
					if pos and len(pos) > 0:
						main_chars.append(char_name)
				except Exception as e:
					print(f"检测主角 {char_name} 时出错: {e}")
					continue
		
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
		# 修复：使用召唤面板区域或右侧按钮区域作为背包检测区域
		bag_region = self.summon_panel_region if self.summon_panel_region else (self.right_button_region if self.right_button_region else (0, 0, 500, 500))
		if isinstance(bag_region, tuple) and len(bag_region) == 4:
			pass  # 使用提供的区域
		else:
			bag_region = (0, 0, 500, 500)  # 备用默认区域
		
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
		
	def is_skill_ready(self, account_index, skill_name):
		"""
		检查技能是否可以使用（不在CD中）
		:param account_index: 账号索引
		:param skill_name: 技能名称
		:return: True if 技能可以使用, False otherwise
		"""
		cd_rounds = self.skill_cd_config.get(skill_name, 0)
		if cd_rounds == 0:
			return True  # 无CD技能
		
		if account_index not in self.skill_cd_tracking:
			self.skill_cd_tracking[account_index] = {}
		
		last_used_turn = self.skill_cd_tracking[account_index].get(skill_name, -999)
		turns_passed = self.current_turn - last_used_turn
		
		return turns_passed >= cd_rounds
	
	def is_item_ready(self, account_index, item_name):
		"""
		检查药品是否可以使用（不在CD中）
		:param account_index: 账号索引
		:param item_name: 药品名称
		:return: True if 药品可以使用, False otherwise
		"""
		cd_rounds = self.item_cd_config.get(item_name, 0)
		if cd_rounds == 0:
			return True  # 无CD药品
		
		if account_index not in self.item_cd_tracking:
			self.item_cd_tracking[account_index] = {}
		
		last_used_turn = self.item_cd_tracking[account_index].get(item_name, -999)
		turns_passed = self.current_turn - last_used_turn
		
		return turns_passed >= cd_rounds
	
	def mark_skill_used(self, account_index, skill_name):
		"""
		标记技能已使用（更新CD追踪）
		:param account_index: 账号索引
		:param skill_name: 技能名称
		"""
		if account_index not in self.skill_cd_tracking:
			self.skill_cd_tracking[account_index] = {}
		self.skill_cd_tracking[account_index][skill_name] = self.current_turn
		print(f"账号{account_index} 使用技能 {skill_name}，标记CD（回合{self.current_turn}）")
	
	def mark_item_used(self, account_index, item_name):
		"""
		标记药品已使用（更新CD追踪）
		:param account_index: 账号索引
		:param item_name: 药品名称
		"""
		if account_index not in self.item_cd_tracking:
			self.item_cd_tracking[account_index] = {}
		self.item_cd_tracking[account_index][item_name] = self.current_turn
		print(f"账号{account_index} 使用药品 {item_name}，标记CD（回合{self.current_turn}）")
	
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
		
	def click_right_button(self, button_name, dm_object):
		"""
		点击右侧操作按钮（技能/召唤/道具）
		:param button_name: 按钮名称
		:param dm_object: 大漠对象
		:return: True if 点击成功
		"""
		image_path = self.button_images.get(button_name, '')
		if not image_path or not self.right_button_region:
			return False
			
		x, y, w, h = self.right_button_region
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), image_path, "000000", 0.9, 0)
		if pos and len(pos) > 0:
			try:
				pos_list = pos.split(',')
				if len(pos_list) >= 2:
					# 修复：验证是否为有效数字
					btn_x = int(pos_list[0])
					btn_y = int(pos_list[1])
					dm_object.MoveTo(btn_x, btn_y)
					time.sleep(0.1)
					dm_object.LeftClick()
					time.sleep(0.2)  # 等待面板弹出
					return True
			except (ValueError, IndexError) as e:
				print(f"解析按钮 {button_name} 位置失败: {pos}, 错误: {e}")
				return False
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
			try:
				pos_list = pos.split(',')
				if len(pos_list) >= 2:
					# 修复：验证是否为有效数字
					skill_x = int(pos_list[0])
					skill_y = int(pos_list[1])
					dm_object.MoveTo(skill_x, skill_y)
					time.sleep(0.1)
					dm_object.LeftClick()
					time.sleep(0.2)  # 等待选择目标状态
					return True
			except (ValueError, IndexError) as e:
				print(f"解析技能 {skill_name} 位置失败: {pos}, 错误: {e}")
				return False
		return False
		
	def use_skill_workflow(self, skill_name, dm_object, target_type='enemy', account_index=0, target_x=None, target_y=None, enemy_index=0):
		"""
		使用技能的完整流程：检查CD -> 点击按钮 -> 选择技能 -> 选择目标
		:param skill_name: 技能名称
		:param dm_object: 大漠对象
		:param target_type: 目标类型 'enemy' or 'ally'
		:param account_index: 账号索引，用于获取目标的确切位置
		:param target_x: 目标X坐标（确切点位，可选）
		:param target_y: 目标Y坐标（确切点位，可选）
		:param enemy_index: 敌人索引（当target_type='enemy'时使用）
		:return: True if 成功
		"""
		# 0. 检查技能CD
		if not self.is_skill_ready(account_index, skill_name):
			print(f"账号{account_index} 技能 {skill_name} 还在CD中")
			return False
		
		# 1. 点击技能按钮
		if not self.click_right_button('技能按钮', dm_object):
			return False
		
		# 2. 在技能面板中选择技能（需要设置技能面板区域）
		panel_region = self.skill_panel_region if self.skill_panel_region else self.right_button_region
		if not self.click_skill_icon(skill_name, dm_object, panel_region):
			return False
		
		# 3. 选择目标（使用确切点位）
		click_success = False
		if target_type == 'enemy':
			click_success = self.click_enemy_unit(dm_object, self.enemy_region, account_index, enemy_index)
		elif target_type == 'ally':
			# 如果提供了确切坐标，使用提供的坐标
			if target_x is not None and target_y is not None:
				click_success = self.click_ally_unit(dm_object, target_x, target_y, account_index)
			else:
				# 从unit_positions获取友军位置
				if account_index in self.unit_positions:
					main_chars = self.unit_positions[account_index].get('main_chars', [])
					if main_chars:
						# 使用第一个主角的位置
						_, x, y = main_chars[0]
						click_success = self.click_ally_unit(dm_object, x, y, account_index)
		
		# 4. 只有成功完成所有步骤才标记技能已使用
		if click_success:
			self.mark_skill_used(account_index, skill_name)
			return True
		else:
			print(f"账号{account_index} 技能 {skill_name} 使用失败（目标选择失败）")
			return False
		
	def get_random_ally_position(self, account_index):
		"""
		随机获取一个己方队友的确切坐标（包括主角和武将）
		:param account_index: 账号索引
		:return: (x, y) 坐标元组，如果没有队友则返回 None
		"""
		if account_index not in self.unit_positions:
			return None
		
		all_allies = []
		# 获取所有主角位置
		all_allies.extend(self.unit_positions[account_index].get('main_chars', []))
		# 获取所有武将位置
		all_allies.extend(self.unit_positions[account_index].get('generals', []))
		
		if not all_allies:
			return None
		
		# 随机选择一个队友
		random_ally = random.choice(all_allies)
		# 返回 (name, x, y) 中的坐标
		_, x, y = random_ally
		return (x, y)
	
	def click_ally_unit(self, dm_object, target_x, target_y, account_index=None):
		"""
		点击友军单位（使用确切点位）
		:param dm_object: 大漠对象
		:param target_x: 目标X坐标（确切点位）
		:param target_y: 目标Y坐标（确切点位）
		:param account_index: 账号索引（可选，用于从unit_positions获取位置）
		:return: True if 点击成功
		"""
		dm_object.MoveTo(int(target_x), int(target_y))
		time.sleep(0.1)
		dm_object.LeftClick()
		print(f"点击友军位置: ({target_x}, {target_y})")
		return True
		
	def click_enemy_unit(self, dm_object, enemy_region, account_index=0, enemy_index=0):
		"""
		点击一个敌军单位（使用固定的确切位置）
		:param dm_object: 大漠对象
		:param enemy_region: 敌军区域（备用，如果找不到确切位置则使用）
		:param account_index: 账号索引，用于获取敌人位置列表
		:param enemy_index: 敌人索引（0=第一个敌人，1=第二个敌人，以此类推）
		:return: True if 点击成功
		"""
		# 1. 优先使用固定的配置位置（如果配置了固定坐标）
		enemy_key = (account_index, enemy_index)
		if enemy_key in self.fixed_enemy_positions:
			enemy_x, enemy_y = self.fixed_enemy_positions[enemy_key]
			dm_object.MoveTo(int(enemy_x), int(enemy_y))
			time.sleep(0.1)
			dm_object.LeftClick()
			print(f"使用固定坐标点击敌人位置: ({enemy_x}, {enemy_y})")
			return True
		
		# 2. 使用检测到的敌人位置（通过图片识别）
		if account_index in self.unit_positions:
			enemies = self.unit_positions[account_index].get('enemies', [])
			if enemies and enemy_index < len(enemies):
				enemy_name, enemy_x, enemy_y = enemies[enemy_index]
				dm_object.MoveTo(int(enemy_x), int(enemy_y))
				time.sleep(0.1)
				dm_object.LeftClick()
				print(f"点击敌人 {enemy_name} 位置: ({enemy_x}, {enemy_y})")
				return True
		
		# 3. 如果没有找到确切位置，使用区域中心位置（备用方案）
		try:
			if not isinstance(enemy_region, (tuple, list)) or len(enemy_region) != 4:
				print(f"敌军区域格式错误: {enemy_region}")
				return False
			x, y, w, h = enemy_region
			center_x = x + w // 2
			center_y = y + h // 2
			dm_object.MoveTo(center_x, center_y)
			time.sleep(0.1)
			dm_object.LeftClick()
			print(f"使用备用方案，点击敌军区域中心: ({center_x}, {center_y})")
			return True
		except (ValueError, TypeError) as e:
			print(f"使用备用方案点击敌军位置时出错: {e}")
			return False
		
	def use_item_workflow(self, item_name, dm_object, target_x, target_y, account_index):
		"""
		使用药品的完整流程：检查CD -> 点击按钮 -> 选择药品 -> 选择目标
		:param item_name: 药品名称
		:param dm_object: 大漠对象
		:param target_x: 目标X坐标（确切点位）
		:param target_y: 目标Y坐标（确切点位）
		:param account_index: 账号索引
		:return: True if 成功
		"""
		# 0. 检查药品CD
		if not self.is_item_ready(account_index, item_name):
			print(f"账号{account_index} 药品 {item_name} 还在CD中")
			return False
		
		# 1. 点击道具按钮
		if not self.click_right_button('道具按钮', dm_object):
			return False
		
		# 2. 选择药品（在道具面板中查找药品图片）
		item_image = self.item_images.get(item_name, '')
		if not item_image:
			print(f"未找到药品 {item_name} 图片")
			return False
		
		panel_region = self.item_panel_region if self.item_panel_region else self.right_button_region
		if panel_region:
			x, y, w, h = panel_region
			pos = dm_object.FindPic(int(x), int(y), int(w), int(h), item_image, "000000", 0.9, 0)
			if pos and len(pos) > 0:
				try:
					pos_list = pos.split(',')
					if len(pos_list) >= 2:
						# 修复：验证是否为有效数字
						item_x = int(pos_list[0])
						item_y = int(pos_list[1])
						dm_object.MoveTo(item_x, item_y)
						time.sleep(0.1)
						dm_object.LeftClick()
						time.sleep(0.2)  # 等待选择目标状态
						
						# 3. 点击目标位置（确切点位）
						dm_object.MoveTo(int(target_x), int(target_y))
						time.sleep(0.1)
						dm_object.LeftClick()
						print(f"使用药品 {item_name} 对位置 ({target_x}, {target_y}) 施放")
						
						# 4. 标记药品已使用
						self.mark_item_used(account_index, item_name)
						return True
				except (ValueError, IndexError) as e:
					print(f"解析药品 {item_name} 位置失败: {pos}, 错误: {e}")
					return False
		return False
	
	def _update_hp_bar_unit_mapping(self, account_index):
		"""
		更新血量条区域到单位的映射关系
		:param account_index: 账号索引
		"""
		if account_index not in self.hp_bar_unit_mapping:
			self.hp_bar_unit_mapping[account_index] = {}
		
		if account_index not in self.unit_positions:
			return
		
		# 获取存活的主角列表
		main_chars = self.unit_positions[account_index].get('main_chars', [])
		# 获取存活的武将列表
		generals = self.unit_positions[account_index].get('generals', [])
		
		# 清除旧的映射
		self.hp_bar_unit_mapping[account_index] = {}
		
		# 映射主角（region_index 0-2）
		for idx, (char_name, x, y) in enumerate(main_chars[:3]):
			region_index = idx  # 0, 1, 2
			self.hp_bar_unit_mapping[account_index][region_index] = ('main_char', char_name, (x, y))
		
		# 映射武将（region_index 3-8）
		for idx, (general_name, x, y) in enumerate(generals[:6]):
			region_index = idx + 3  # 3, 4, 5, 6, 7, 8
			self.hp_bar_unit_mapping[account_index][region_index] = ('general', general_name, (x, y))
	
	def detect_low_hp_units(self, account_index):
		"""
		检测账号中血量低的单位
		:param account_index: 账号索引
		:return: 列表，每个元素为 (unit_type, unit_name, heal_position)，按优先级排序
		"""
		if not self.hp_bar_regions or len(self.hp_bar_regions) != 9:
			return []
		
		if account_index not in self.account_dm:
			return []
		
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return []
		
		low_hp_units = []
		
		# 遍历9个血量条区域
		for region_index, hp_bar_region in enumerate(self.hp_bar_regions):
			try:
				if not isinstance(hp_bar_region, (tuple, list)) or len(hp_bar_region) != 4:
					continue
				
				x, y, w, h = hp_bar_region
				# 在血量条区域中查找血量低标识图片
				pos = dm_object.FindPic(int(x), int(y), int(w), int(h), self.low_hp_indicator_image, "000000", 0.9, 0)
				
				if pos and len(pos) > 0:
					# 识别到血量低的标识，查找对应的单位
					if account_index in self.hp_bar_unit_mapping:
						mapping = self.hp_bar_unit_mapping[account_index]
						if region_index in mapping:
							unit_type, unit_name, heal_position = mapping[region_index]
							low_hp_units.append((unit_type, unit_name, heal_position))
							print(f"账号{account_index} 检测到 {unit_type} {unit_name} 血量低，加血位置: {heal_position}")
			except Exception as e:
				print(f"账号{account_index} 检测血量条区域 {region_index} 时出错: {e}")
				continue
		
		return low_hp_units
		
	def main_char_action(self, account_index):
		"""
		主角操作：优先检测血量低的单位并加血，否则尝试释放群体攻击，如果全部CD则给血量低的单位或武将加血
		:param account_index: 账号索引
		"""
		# 添加边界检查
		if account_index < 0 or account_index >= len(self.account_dm):
			return
		
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return
		
		# 优先检测血量低的单位并加血
		if self.enable_main_heal:
			low_hp_units = self.detect_low_hp_units(account_index)
			if low_hp_units:
				# 优先给主角加血，然后是武将
				low_hp_units.sort(key=lambda x: (0 if x[0] == 'main_char' else 1, x[1]))
				
				for unit_type, unit_name, heal_position in low_hp_units:
					heal_x, heal_y = heal_position
					print(f"账号{account_index} 检测到 {unit_type} {unit_name} 血量低，使用恢复药加血")
					if self.use_item_workflow('恢复药', dm_object, heal_x, heal_y, account_index):
						# 成功给一个单位加血后，等待一下再检查下一个
						time.sleep(0.3)
						return  # 每回合只给一个单位加血，避免占用过多时间
		
		# 尝试使用群体攻击
		group_attack_skills = ['主角群体攻击1', '主角群体攻击2', '主角群体攻击3']
		skill_used = False
		
		for skill_name in group_attack_skills:
			# 尝试使用技能，如果技能不在CD则使用
			if self.use_skill_workflow(skill_name, dm_object, target_type='enemy', account_index=account_index):
				skill_used = True
				break
		
		# 如果所有技能都在CD，则检测血量并给血量低的单位加血
		if not skill_used and self.enable_main_heal:
			try:
				# 再次检测血量低的单位
				low_hp_units = self.detect_low_hp_units(account_index)
				if low_hp_units:
					# 给第一个血量低的单位加血
					unit_type, unit_name, heal_position = low_hp_units[0]
					heal_x, heal_y = heal_position
					print(f"账号{account_index} 所有技能CD，给血量低的 {unit_type} {unit_name} 使用恢复药")
					self.use_item_workflow('恢复药', dm_object, heal_x, heal_y, account_index)
				elif account_index in self.unit_positions:
					# 如果没有检测到血量低的单位，给随机武将使用恢复药（保持向后兼容）
					generals = self.unit_positions[account_index].get('generals', [])
					if generals:
						random_general = random.choice(generals)
						_, x, y = random_general
						print(f"账号{account_index} 所有技能CD，给随机武将使用恢复药")
						self.use_item_workflow('恢复药', dm_object, x, y, account_index)
			except Exception as e:
				print(f"账号{account_index} 给单位使用恢复药时出错: {e}")
			
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
			self.use_skill_workflow('武将群体攻击', dm_object, target_type='enemy', account_index=account_index)
		elif general_type == 'support':
			# 辅助武将（刘备）：按策略释放技能
			has_status = self.has_enemy_status(account_index)
			
			if has_status:
				# 检测到敌军有状态，优先尝试清除状态
				if self.is_skill_ready(account_index, '清除状态'):
					if self.use_skill_workflow('清除状态', dm_object, target_type='enemy', account_index=account_index):
						# 成功使用清除状态技能
						return
				# 如果清除状态技能CD，尝试使用其他技能
				# 继续执行下面的逻辑，尝试使用其他可用技能
			
			# 尝试使用辅助技能，如果当前技能CD则尝试其他技能
			skill_used = False
			start_index = self.current_skill_index % len(self.support_skill_sequence)
			
			# 从当前索引开始，尝试所有技能直到找到可用的
			for i in range(len(self.support_skill_sequence)):
				skill_index = (start_index + i) % len(self.support_skill_sequence)
				skill_name = self.support_skill_sequence[skill_index]
				
				# 判断技能目标类型
				target_type = 'ally' if skill_name in ['加攻击', '加血', '加速'] else 'enemy'
				
				# 如果是己方目标，随机选择一个队友坐标
				target_x, target_y = None, None
				if target_type == 'ally':
					ally_pos = self.get_random_ally_position(account_index)
					if ally_pos:
						target_x, target_y = ally_pos
					else:
						# 没有可用队友，跳过这个技能
						continue
				
				# 尝试使用技能
				if self.use_skill_workflow(skill_name, dm_object, target_type=target_type, 
				                          account_index=account_index, target_x=target_x, target_y=target_y):
					# 成功使用技能，切换到下一个技能
					self.current_skill_index = (skill_index + 1) % len(self.support_skill_sequence)
					skill_used = True
					break
			
			# 如果所有技能都在CD，打印信息
			if not skill_used:
				print(f"账号{account_index} 刘备的所有技能都在CD中")
		else:
			# 未知类型的武将，打印警告
			print(f"警告：账号{account_index} 武将类型未知: {general_type}")
	
	def use_revive_item(self, dm_object, target_x, target_y, account_index):
		"""
		使用复活药复活目标
		:param dm_object: 大漠对象
		:param target_x: 目标X坐标
		:param target_y: 目标Y坐标
		:param account_index: 账号索引
		:return: True if 成功
		"""
		return self.use_item_workflow('复活药', dm_object, target_x, target_y, account_index)
	
	def use_heal_item(self, dm_object, account_index, target_x=None, target_y=None):
		"""
		使用加血道具（恢复药）
		:param dm_object: 大漠对象
		:param account_index: 账号索引
		:param target_x: 目标X坐标（可选，如果不提供则随机选择武将）
		:param target_y: 目标Y坐标（可选）
		"""
		# 如果没有提供目标坐标，随机选择一个武将
		if target_x is None or target_y is None:
			if account_index in self.unit_positions:
				generals = self.unit_positions[account_index].get('generals', [])
				if generals:
					random_general = random.choice(generals)
					_, target_x, target_y = random_general
				else:
					return False
			else:
				return False
		
		# 使用恢复药（恢复药是加血又加蓝的）
		return self.use_item_workflow('恢复药', dm_object, target_x, target_y, account_index)
	
	def check_and_revive_dead_main_chars(self, account_index):
		"""
		检查并复活阵亡的主角
		:param account_index: 账号索引
		:return: True if 有复活操作
		"""
		# 更新追踪信息
		self.update_general_tracking(account_index)
		
		has_revive_action = False  # 记录是否有任何复活操作
		
		# 检查每个账号是否有主角阵亡
		for i in range(3):
			if not self.account_dm[i]:
				continue
			
			try:
				team_status = self.get_team_status(i)
				if not team_status:
					continue
				
				# 获取阵亡的主角位置（从之前的记录中查找）
				current_main_chars = set(team_status.get('main_chars', []))
				# 安全地获取追踪的主角列表
				unit_pos = self.unit_positions.get(i, {})
				main_chars_list = unit_pos.get('main_chars', [])
				tracked_main_chars = {char_name for char_name, _, _ in main_chars_list if len(main_chars_list) > 0 and isinstance(main_chars_list[0], (tuple, list)) and len(main_chars_list[0]) >= 3}
				dead_main_chars = tracked_main_chars - current_main_chars
				
				if not dead_main_chars:
					continue
				
				# 找到阵亡的主角位置（从dead_main_char_positions中获取）
				for dead_char_name in dead_main_chars:
					# 从dead_main_char_positions中获取阵亡主角的位置
					dead_char_pos = None
					if i in self.dead_main_char_positions:
						dead_char_pos = self.dead_main_char_positions[i].get(dead_char_name)
					
					if not dead_char_pos:
						# 如果dead_main_char_positions中没有，尝试从unit_positions的旧数据中查找
						# 这种情况应该很少发生，因为update_general_tracking会先保存位置
						print(f"警告：无法找到账号{i}的主角{dead_char_name}的位置，跳过复活")
						continue
					
					# 优先让队友账号的主角复活（如果队友账号的主角存活）
					revive_success = False
					for ally_index in range(3):
						if ally_index == i or not self.account_dm[ally_index]:
							continue
						
						try:
							ally_status = self.get_team_status(ally_index)
							if ally_status and len(ally_status['main_chars']) > 0:
								# 队友账号有存活的主角，用主角复活
								print(f"账号{ally_index}的主角复活账号{i}的主角{dead_char_name}")
								if self.use_revive_item(self.account_dm[ally_index], dead_char_pos[0], dead_char_pos[1], ally_index):
									revive_success = True
									has_revive_action = True
									break
						except Exception as e:
							print(f"账号{ally_index}复活账号{i}的主角{dead_char_name}时出错: {e}")
							continue
					
					# 如果队友主角都死了，用武将复活
					if not revive_success:
						try:
							# 检查当前账号是否有存活的武将
							team_status = self.get_team_status(i)
							if team_status and team_status['general_count'] > 0:
								# 用武将复活
								print(f"账号{i}的武将复活主角{dead_char_name}")
								# 需要找到武将按钮的位置，然后点击药品按钮
								# 这里需要武将也能点击药品按钮的逻辑
								if self.use_revive_item(self.account_dm[i], dead_char_pos[0], dead_char_pos[1], i):
									revive_success = True
									has_revive_action = True
						except Exception as e:
							print(f"账号{i}的武将复活主角{dead_char_name}时出错: {e}")
					
					if revive_success:
						time.sleep(0.5)  # 等待复活完成
						# 更新追踪信息
						self.update_general_tracking(i)
			except Exception as e:
				print(f"检查账号{i}的主角复活状态时出错: {e}")
				continue
		
		return has_revive_action
		
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
		
		# 检查是否可以召唤（武将数量少于2个，或者已经有2个但可以替换）
		# 注意：即使有2个武将，也可以替换，所以不在这里返回
		
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
		# 1. 点击召唤按钮
		if not self.click_right_button('召唤按钮', dm_object):
			print(f"无法点击召唤按钮，召唤失败")
			return False
		
		time.sleep(0.3)  # 等待召唤面板弹出
		
		# 2. 在召唤面板左侧查找要召唤的武将图片（背包中的武将）
		general_bag_image = self.bag_general_images.get(general_name, '')
		if not general_bag_image:
			print(f"未找到武将 {general_name} 的背包图片")
			return False
		
		# 在召唤面板区域查找武将图片
		panel_region = self.summon_panel_region if self.summon_panel_region else self.right_button_region
		if not panel_region:
			print("未设置召唤面板区域")
			return False
		
		x, y, w, h = panel_region
		pos = dm_object.FindPic(int(x), int(y), int(w), int(h), general_bag_image, "000000", 0.9, 0)
		if not pos or len(pos) == 0:
			print(f"在召唤面板中未找到武将 {general_name}")
			return False
		
		try:
			pos_list = pos.split(',')
			if len(pos_list) < 2:
				return False
			
			# 修复：验证是否为有效数字
			general_x = int(pos_list[0])
			general_y = int(pos_list[1])
			
			# 点击武将图片
			dm_object.MoveTo(general_x, general_y)
			time.sleep(0.1)
			dm_object.LeftClick()
			time.sleep(0.3)  # 等待响应
		except (ValueError, IndexError) as e:
			print(f"解析召唤武将 {general_name} 位置失败: {pos}, 错误: {e}")
			return False
		
		# 3. 检查是否需要替换武将（如果已有2个武将）
		team_status = self.get_team_status(account_index)
		if team_status and team_status['general_count'] >= 2:
			# 需要替换，找到出战时间最长的武将并点击其位置
			if account_index in self.general_tracking:
				# 找到出战回合最早的武将（出战时间最长）
				oldest_general = None
				oldest_turn = self.current_turn + 1
				
				for gen_name, gen_info in self.general_tracking[account_index].items():
					if gen_info.get('deployed_turn', self.current_turn) < oldest_turn:
						oldest_turn = gen_info.get('deployed_turn', self.current_turn)
						oldest_general = (gen_name, gen_info.get('position'))
				
				if oldest_general and oldest_general[1]:
					# 点击被替换武将的位置
					try:
						gen_name = oldest_general[0]
						gen_position = oldest_general[1]
						# 检查位置是否为元组格式 (x, y)
						if isinstance(gen_position, (tuple, list)) and len(gen_position) >= 2:
							gen_x, gen_y = gen_position[0], gen_position[1]
							print(f"需要替换武将 {gen_name}，点击位置 ({gen_x}, {gen_y})")
							dm_object.MoveTo(int(gen_x), int(gen_y))
							time.sleep(0.1)
							dm_object.LeftClick()
							time.sleep(0.2)
						else:
							print(f"武将 {gen_name} 的位置格式不正确: {gen_position}")
					except (ValueError, TypeError, IndexError) as e:
						print(f"解析武将位置失败: {e}")
		else:
			# 直接召唤，不需要替换
			print(f"直接召唤武将 {general_name}（武将数量少于2个）")
		
		# 召唤完成
		print(f"成功召唤武将 {general_name} 到账号 {account_index}")
		
		# 修复：召唤成功后立即更新武将追踪信息
		time.sleep(0.3)  # 等待召唤动画完成
		self.update_general_tracking(account_index)
		
		return True
		
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
			
	def check_has_any_alive_units(self):
		"""
		检查是否还有任何存活的主角或武将
		:return: True if 至少有一个主角或武将存活, False otherwise
		"""
		for i in range(3):
			if not self.account_dm[i]:
				continue
			
			team_status = self.get_team_status(i)
			if team_status:
				# 如果有存活的主角或武将，返回True
				if len(team_status['main_chars']) > 0 or team_status['general_count'] > 0:
					return True
		
		return False
	
	def auto_combat(self, account_index):
		"""
		自动战斗主循环
		:param account_index: 账号索引
		"""
		# 添加边界检查
		if account_index < 0 or account_index >= len(self.account_dm):
			return
		
		dm_object = self.account_dm[account_index]
		if not dm_object:
			return
		
		# 检查线程是否已停止
		if self.thread:
			if hasattr(self.thread, 'overed') and self.thread.overed:
				return
			if hasattr(self.thread, 'stoped') and self.thread.stoped:
				return
			
		# 检查是否是己方回合
		is_current_turn = self.is_my_turn(dm_object)
		
		# 修复：如果从非己方回合转为己方回合，重置处理标志
		if not hasattr(self, '_last_turn_state'):
			self._last_turn_state = False
		
		if is_current_turn and not self._last_turn_state:
			# 刚切换到己方回合，重置处理标志
			self.turn_processed = False
		
		self._last_turn_state = is_current_turn
		
		if not is_current_turn:
			return
		
		# 0. 更新回合数（修复BUG：防止重复更新）
		# 如果当前回合还未处理，则更新回合数并标记为已处理
		if not self.turn_processed:
			self.current_turn += 1
			self.turn_processed = True
			print(f"回合 {self.current_turn} 开始")
		
		# 0. 全局检测所有账号的队伍状态（包括主角和武将）
		for i in range(3):
			if self.account_dm[i]:
				try:
					team_status = self.get_team_status(i)
					if team_status:
						# 更新追踪信息（检测阵亡的武将和主角）
						self.update_general_tracking(i)
						# 检测敌人位置
						self.detect_enemy_positions(i)
						# 更新血量条区域到单位的映射
						self._update_hp_bar_unit_mapping(i)
						print(f"账号{i} 状态: 主角{len(team_status['main_chars'])}个存活, 武将{team_status['general_count']}个存活, 有辅助{team_status['has_support']}, 敌人{len(self.unit_positions.get(i, {'enemies': []})['enemies'])}个")
				except Exception as e:
					print(f"账号{i} 检测队伍状态时出错: {e}")
					continue
		
		# 0.1. 检查并复活阵亡的主角（优先级最高）
		self.check_and_revive_dead_main_chars(account_index)
		
		# 0.2. 检查是否还有存活的单位（主角或武将），如果没有则停止战斗
		if not self.check_has_any_alive_units():
			print("所有账号的主角 and 武将全部阵亡，停止自动战斗")
			# 停止战斗自动操作
			if self.thread and hasattr(self.thread, '_stop_combat_auto'):
				self.thread._stop_combat_auto()
			return
		
		# 1. 主角操作（只有在主角存活的情况下）
		team_status = self.get_team_status(account_index)
		if team_status and len(team_status['main_chars']) > 0:
			self.main_char_action(account_index)
		else:
			print(f"账号{account_index}的主角全部阵亡，跳过主角操作")
		
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
			# 检查是否应该停止（修复：兼容多种状态管理方式）
			if self.thread:
				# 优先检查 overed（停止标志）
				if hasattr(self.thread, 'overed') and self.thread.overed:
					break
				# 检查 stoped（暂停标志），暂停时跳过当前循环但继续等待
				if hasattr(self.thread, 'stoped') and self.thread.stoped:
					time.sleep(0.5)
					continue
			
			# 修复：不再在循环开始时重置标志，而是基于回合变化来重置（在auto_combat中处理）
				
			# 对每个有效的账号执行战斗操作
			for i in range(3):
				if self.account_dm[i]:
					self.auto_combat(i)
			
			# 如果当前回合已被处理，等待下一次循环
			# 这样确保每次循环只处理一次回合数更新
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

