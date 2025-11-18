"""
测试战斗脚本初始化，定位坐标越界错误
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Kanloong_combat_script import CombatAutoScript
    
    # 创建一个模拟的 thread_instance
    class MockThread:
        def __init__(self):
            self.dm = None  # 模拟大漠对象未初始化
            self.win1_dm = None
            self.win2_dm = None
        
        def get_resource_path(self, path):
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    
    print("=" * 60)
    print("测试1: 创建 CombatAutoScript 实例")
    print("=" * 60)
    try:
        mock_thread = MockThread()
        combat_script = CombatAutoScript(mock_thread)
        print("✓ CombatAutoScript 实例创建成功")
    except Exception as e:
        print(f"✗ 创建实例失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("测试2: 调用 init_combat_tracking()")
    print("=" * 60)
    try:
        combat_script.init_combat_tracking()
        print("✓ init_combat_tracking() 调用成功（应该跳过初始化）")
    except Exception as e:
        print(f"✗ init_combat_tracking() 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("测试3: 检查 account_dm 属性")
    print("=" * 60)
    try:
        account_dm = combat_script.account_dm
        print(f"✓ account_dm = {account_dm}")
    except Exception as e:
        print(f"✗ 访问 account_dm 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("测试4: 检查 get_account_count()")
    print("=" * 60)
    try:
        count = combat_script.get_account_count()
        print(f"✓ get_account_count() = {count}")
    except Exception as e:
        print(f"✗ get_account_count() 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    
except Exception as e:
    print(f"测试脚本执行失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

