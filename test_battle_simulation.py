"""
战斗模拟测试脚本
用于测试战斗播报窗口的功能
"""

import wx
import time
import threading
from Kanloong_combat_script import CombatAutoScript, BattleReportDialog

class MockThread:
	"""模拟的MyThread类，用于测试"""
	def __init__(self):
		self.overed = False
		self.stoped = False
		self.dm = None
		self.win1_dm = None
		self.win2_dm = None

class BattleSimulationApp(wx.App):
	"""战斗模拟应用程序"""
	def OnInit(self):
		# 创建模拟的线程对象
		self.mock_thread = MockThread()
		
		# 先创建窗口
		try:
			print("正在创建战斗播报窗口...")
			self.battle_report_dialog = BattleReportDialog(parent=None)
			self.battle_report_dialog.Show()
			print("战斗播报窗口已创建并显示")
		except Exception as e:
			print(f"创建窗口时出错: {e}")
			import traceback
			traceback.print_exc()
			return False
		
		# 创建战斗自动脚本实例
		self.combat_script = CombatAutoScript(self.mock_thread)
		# 手动设置窗口引用
		self.combat_script.battle_report_dialog = self.battle_report_dialog
		
		# 等待窗口完全加载
		time.sleep(0.5)
		
		# 启动模拟战斗的线程
		def start_simulation():
			time.sleep(1)  # 额外等待，确保窗口完全初始化
			self.simulate_battle()
		
		threading.Thread(target=start_simulation, daemon=True).start()
		print("模拟战斗线程已启动")
		
		return True
	
	def simulate_battle(self):
		"""模拟战斗过程"""
		print("模拟战斗线程已启动...")
		time.sleep(1)  # 等待窗口完全加载
		
		# 检查窗口是否可用
		if not self.combat_script.battle_report_dialog:
			print("错误：战斗播报窗口不存在！")
			return
		
		print("开始发送战斗信息...")
		
		# 模拟战斗初始化
		self.combat_script.report_battle_info("=" * 60, "system")
		time.sleep(0.2)
		self.combat_script.report_battle_info("战斗模拟开始", "system")
		time.sleep(0.2)
		self.combat_script.report_battle_info("=" * 60, "system")
		time.sleep(0.2)
		self.combat_script.report_battle_info("", "info")
		print("初始消息已发送")
		
		# 模拟3个回合的战斗
		for turn in range(1, 4):
			# 回合开始
			turn_msg = f"{'='*50}\n回合 {turn} 开始（25秒操作时间）\n{'='*50}"
			self.combat_script.report_battle_info(turn_msg, "turn")
			time.sleep(1)
			
			# 模拟队伍状态
			self.combat_script.report_battle_info("账号0 状态: 主角3个存活, 武将2个存活, 有辅助True, 敌人3个", "info")
			time.sleep(0.5)
			
			# 模拟主角操作
			self.combat_script.report_battle_info("账号0 使用技能 主角群体攻击1，标记CD（回合1）", "success")
			time.sleep(0.8)
			
			# 模拟武将操作
			self.combat_script.report_battle_info("账号0 武将 魔化关羽 使用技能 魔化关羽群攻1", "success")
			time.sleep(0.8)
			
			# 模拟刘备操作
			self.combat_script.report_battle_info("账号0 武将 刘备 使用技能 加攻击", "success")
			time.sleep(0.8)
			
			# 模拟一些事件
			if turn == 2:
				# 第二回合有人阵亡
				self.combat_script.report_battle_info("账号0的武将魔化关羽阵亡了", "warning")
				time.sleep(0.5)
				self.combat_script.report_battle_info("账号0 直接召唤武将 魔化关羽（武将数量少于2个）", "action")
				time.sleep(0.5)
				self.combat_script.report_battle_info("成功召唤武将 魔化关羽 到账号 0", "success")
			
			if turn == 3:
				# 第三回合使用药品
				self.combat_script.report_battle_info("账号0 所有技能CD，给血量低的 主角 主角1 使用恢复药", "success")
				time.sleep(0.5)
				self.combat_script.report_battle_info("账号0 使用药品 恢复药，标记CD（回合3）", "success")
			
			time.sleep(1)
			self.combat_script.report_battle_info("", "info")
		
		# 战斗结束
		self.combat_script.report_battle_info("=" * 60, "system")
		self.combat_script.report_battle_info("战斗模拟结束", "system")
		self.combat_script.report_battle_info("所有账号的主角 and 武将全部阵亡，停止自动战斗", "error")
		self.combat_script.report_battle_info("=" * 60, "system")

def main():
	"""主函数"""
	print("=" * 60)
	print("开始启动战斗模拟程序...")
	print("=" * 60)
	
	try:
		app = BattleSimulationApp()
		print(f"应用程序已创建，窗口引用: {app.battle_report_dialog}")
		if app.battle_report_dialog:
			print("[OK] 战斗播报窗口已创建")
			print("[OK] 窗口应该已显示在屏幕上")
			print("[OK] 开始运行主循环...")
		else:
			print("[ERROR] 警告：窗口未创建")
			print("程序可能无法正常工作")
		
		print("\n提示：如果窗口没有出现，请检查：")
		print("1. 是否安装了 wxPython: pip install wxPython")
		print("2. 窗口是否被其他窗口遮挡")
		print("3. 查看控制台的错误信息")
		print("\n正在启动主循环...\n")
		
		app.MainLoop()
	except Exception as e:
		print(f"\n[ERROR] 启动应用程序时出错: {e}")
		import traceback
		traceback.print_exc()
		input("\n按回车键退出...")

if __name__ == "__main__":
	main()

