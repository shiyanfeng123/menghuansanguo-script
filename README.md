# 梦幻三国自动脚本

自动化的游戏脚本工具，支持87种不同的游戏脚本类型。

## 系统要求

- **操作系统**: Windows 10/11
- **Python版本**: Python 3.8 - 3.11
- **屏幕分辨率**: 1920x1080 (推荐)
- **浏览器**: Chrome 或 Edge (游戏所在浏览器)

## 安装步骤

### 1. 安装 Python

如果你还没有安装 Python，请访问 [Python官网](https://www.python.org/downloads/) 下载并安装 Python 3.8-3.11 版本。

**重要**: 安装时勾选 "Add Python to PATH"

### 2. 安装依赖包

打开命令提示符（CMD）或 PowerShell，进入项目目录，然后运行：

```bash
# 安装依赖包
pip install -r requirements.txt
```

如果pip下载较慢，可以使用国内镜像：

```bash
# 使用清华大学镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 下载大漠插件

这个项目使用了"大漠插件"（dm.dll）进行游戏自动化。大漠插件需要单独获取。

#### 获取大漠插件的方法：
1. 访问大漠插件官网：https://www.zy.com/down/
2. 注册并登录账号
3. 下载大漠插件（dm.dll）
4. 将 `dm.dll` 放在项目根目录下
5. 需要通过 `regsvr32` 注册插件（可能需要管理员权限）

**注册命令**：
```bash
regsvr32 dm.dll
```

**注意**：大漠插件是付费的Windows自动化工具，需要购买授权后才能使用。

### 4. 配置游戏环境

#### 系统设置：
1. 屏幕分辨率设置为 **1920x1080**
2. 系统缩放比例设置为 **100%**
3. 浏览器缩放比例设置为 **100%**（游戏中不显示白边）

#### 游戏设置：
- 确保游戏窗口标题包含程序识别的关键词
- 建议使用无边框窗口模式

## 运行项目

### 方法1：直接运行 Python 文件

```bash
python serveScript.py
```

### 方法2：打包成可执行文件

如果你想打包成独立的exe文件：

```bash
# 打包命令
pyinstaller -F -w --add-data "serveAssets;serveAssets" --icon=serveAssets\images\script.ico .\serveScript.py

# 或者使用 spec 文件
pyinstaller serveScript.spec
```

打包后的exe文件在 `dist` 目录下。

## 使用方法

### 启动脚本

1. 运行程序后会显示GUI窗口
2. 点击 **"设置游戏信息"** 按钮配置：
   - 游戏名称
   - 脚本类型
   - 队友信息
   - 其他参数

3. 点击 **"开始脚本(F5)"** 或按 `F5` 键开始运行

### 快捷键

- **F5**: 开始脚本
- **F6**: 暂停脚本
- **F7**: 继续脚本
- **F8**: 重置脚本

### 支持的脚本类型

#### 副本类
- 官渡
- 黑风山寨
- 魔镜
- 战魂楼
- 嗜血战场
- 溶洞
- 炼丹
- 五行

#### 挂机类
- 挂机+整点
- 龙珠
- 老鼠
- 倭寇
- 森罗殿

#### 组合脚本
- 战魂+红+整点
- 日常任务
- 挂机+整点

#### 特殊功能
- 整点活动
- 名将闯关
- 怪物攻城
- 矿产
- 龙王令
- 引魔符

... 共87种脚本类型

## 依赖说明

### 必需的 Python 包

- `wxPython`: GUI框架，提供窗口界面
- `keyboard`: 键盘监听和模拟
- `psutil`: 进程监控和系统信息
- `pywin32`: Windows API调用（COM组件）
- `requests`: HTTP请求（检查更新）
- `pyttsx3`: 文本转语音

### 第三方工具

- **大漠插件 (dm.dll)**: Windows自动化工具（需要单独获取和授权）

### 标准库

以下模块是Python标准库，无需安装：
- `random`, `time`, `threading`
- `ctypes`, `subprocess`
- `datetime`, `uuid`
- `json`, `os`, `sys`
- `collections`, `gc`

## 常见问题

### Q: 报错 "No module named 'wx'"
**A**: 运行 `pip install wxPython` 安装wxPython

### Q: 报错 "No module named 'keyboard'"
**A**: 运行 `pip install keyboard` 安装keyboard模块

### Q: 找不到游戏窗口
**A**: 
- 检查游戏窗口标题是否正确
- 确保游戏窗口是可见的（不要最小化）
- 检查游戏名称配置

### Q: 大漠插件未授权
**A**: 需要购买大漠插件授权，并在官方平台绑定账号

### Q: 图片识别不准确
**A**:
- 确保屏幕分辨率为1920x1080
- 确保系统缩放为100%
- 检查游戏画面是否正常显示

### Q: 队友识别失败
**A**: 
- 在设置中正确配置队友名称
- 确保队友在队伍中
- 尝试刷新地图（按T键）

## 开发者信息

- **交流群**: 955753707
- **项目地址**: Gitee

## 版本更新

当前版本：**v25.10.4**

程序会自动检查更新，或者点击界面上的"检查更新"按钮查看最新版本。

## 免责声明

本脚本仅供学习交流使用，请勿用于商业用途。使用自动化脚本可能导致游戏账号被封禁，请自行承担风险。

## 许可证

本项目仅供学习交流使用。


