"""
Script to fix all TODO_DELETE and TODO_MIGRATE markers in ya_game_scripts.py
"""
import re

filepath = r"c:\Users\syf\Desktop\project\menghuansanguo-script\ya_game_scripts.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()
    lines = content.split("\n")

print(f"Total lines: {len(lines)}")

# ============================================================
# Step 1: Delete all TODO_DELETE lines
# ============================================================
count_delete = 0
new_lines = []
for line in lines:
    if "# TODO_DELETE:" in line:
        count_delete += 1
        continue
    new_lines.append(line)
lines = new_lines
print(f"Deleted {count_delete} TODO_DELETE lines")

# ============================================================
# Step 2: prepare - rebuild string for regex processing
# ============================================================
content = "\n".join(lines)

# ============================================================
# Step 2a: Migrate find_pic method (self.dm.FindPicEx + GetPicSize)
# Old: (x1,y1,x2,y2) region format from dm.FindPicEx
# New: engine.find_pic(path, (x1,y1,x2-x1,y2-y1), conf, role, dir)
# Return changes from ResXy center calc to MatchResult.x/.y directly
# ============================================================

# --- find_pic (main window) ---
old_find_pic = r'''    # 找图方法
    def find_pic\(self, image_path, image_region, find_dir\):
        if self\.overed:
            return
        find_path = image_path
        # picSize = # TODO_MIGRATE: self\.dm\.GetPicSize\(image_path\)
        # picSize = picSize\.split\(','\)
        # picW, picH = picSize\[0\], picSize\[1\]
        x, y, w, h = image_region
        pos = # TODO_MIGRATE: self\.dm\.FindPicEx\(int\(x\), int\(y\), int\(w\), int\(h\), find_path, "",
                                self\.confidenceNum, find_dir\)
        if not pos:
            # if self\.confidenceNum == 0\.9:
            # 	self\.confidenceNum = 0\.8
            # 	find_res = self\.find_pic\(image_path, image_region, find_dir\)
            # 	self\.confidenceNum = 0\.9
            # 	return find_res
            return False
        pos = pos\.split\("\|"\)
        # if len\(pos\) == 1:
        # 	pos_res = pos\[0\]\.split\(','\)
        # else:
        # 	# 初始化最小值和对应的项
        # 	min_x_value = float\('inf'\)
        # 	min_item = None
        # 	# 遍历数组，找到第二个数值最小的那一项
        # 	for item in pos:
        # 		# 解析每一项
        # 		parts = item\.split\(','\)
        # 		x_value = int\(parts\[1\]\)
        # 		# 比较并更新最小值和对应的项
        # 		if x_value < min_x_value:
        # 			min_x_value = x_value
        # 			min_item = item
        # 	pos_res = min_item\.split\(','\)
        pos_res = pos\[0\]\.split\(","\)
        pics = image_path\.split\("\|"\)
        picSize = # TODO_MIGRATE: self\.dm\.GetPicSize\(pics\[int\(pos_res\[0\]\)\]\)
        picSize = picSize\.split\(","\)
        picW, picH = picSize\[0\], picSize\[1\]
        posX = int\(pos_res\[1\]\) \+ \(int\(picW\) \* 0\.5\)
        posY = int\(pos_res\[2\]\) \+ \(int\(picH\) \* 0\.5\)
        res = ResXy\(int\(posX\), int\(posY\)\)
        # TODO_DELETE: self\.dm\.FreePic\(image_path\)
        return res'''

# Note: the TODO_DELETE line was already removed in Step 1, so the pattern won't match exactly.
# Let me rewrite find_pic from scratch instead.

# Actually, let me rebuild lines after step 1 and work with a different approach.
# Step 1 is already done in memory. Let me re-read the current state.
# I'll work with line-by-line patterns instead.

print("Reconstructing content after step 1...")

# Let me re-read the file to get a clean state after step 1
# (but since we removed TODO_DELETE lines in memory, we have clean_lines)

# Actually the approach should be: construct the full replacement text and then apply.
# Let me use a more targeted approach.

# ============================================================
# Better approach: work line by line and handle each pattern
# ============================================================

# For find_pic method: We need to find the block and replace it
# Let's use the approach of building the replacement lines

def replace_method_find_pic(lines):
    """Replace the entire find_pic method"""
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == "    # 找图方法" and i + 1 < len(lines) and lines[i + 1].startswith("    def find_pic(self, image_path"):
            start_idx = i
        if start_idx is not None and i > start_idx and line.rstrip() == "        return res":
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        replacement = [
            "    # 找图方法",
            "    def find_pic(self, image_path, image_region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = image_region",
            "        result = engine.find_pic(image_path, (int(x), int(y), int(w - x), int(h - y)), self.confidenceNum, \"main\", find_dir)",
            "        if not result:",
            "            return False",
            "        return ResXy(int(result.x), int(result.y))",
            "        return res",
        ]
        # Actually we want to keep the "return res" line? No, the return is now in the method
        # The method should end with return ResXy(...). Let me fix.
        replacement = [
            "    # 找图方法",
            "    def find_pic(self, image_path, image_region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = image_region",
            "        result = engine.find_pic(image_path, (int(x), int(y), int(w - x), int(h - y)), self.confidenceNum, \"main\", find_dir)",
            "        if not result:",
            "            return False",
            "        return ResXy(int(result.x), int(result.y))",
        ]
        return lines[:start_idx] + replacement + lines[end_idx + 1:]
    return lines


lines = replace_method_find_pic(lines)
print("Replaced find_pic method")


# ============================================================
# Replace find_str method
# ============================================================
def replace_method_find_str(lines):
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == "    # 找字方法" and i + 1 < len(lines) and lines[i + 1].startswith("    def find_str(self, text, region, find_dir):"):
            start_idx = i
        if start_idx is not None and i > start_idx and line.rstrip().endswith("return False"):
            # Check if we're past the find_str method
            if any(kw in lines[i-2] for kw in ["find_str_result", "pos_res"]):
                end_idx = i
                break
    if start_idx is not None and end_idx is not None:
        replacement = [
            "    # 找字方法",
            "    def find_str(self, text, region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = region",
            "        result = engine.find_pic_or_str(text, (int(x), int(y), int(w - x), int(h - y)), find_dir, \"main\", self.confidenceNum)",
            "        if result:",
            "            return ResXy(int(result.x), int(result.y))",
            "        else:",
            "            return False",
        ]
        return lines[:start_idx] + replacement + lines[end_idx + 1:]
    return lines

lines = replace_method_find_str(lines)
print("Replaced find_str method")


# ============================================================
# Replace find_pic_team1 method
# ============================================================
def replace_method_find_pic_team1(lines):
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if "    # 找图方法z" in line.rstrip() and "def find_pic_team1" in line.rstrip() and i + 1 < len(lines):
            # Actually this comment is on its own line
            pass
        if line.rstrip() == "    # 找图方法z" and i + 1 < len(lines) and "def find_pic_team1" in lines[i + 1]:
            start_idx = i
        if start_idx is not None and i > start_idx and line.rstrip() == "        return res":
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        replacement = [
            "    # 找图方法z",
            "    def find_pic_team1(self, image_path, image_region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = image_region",
            "        result = engine.find_pic(image_path, (int(x), int(y), int(w - x), int(h - y)), self.confidenceNum, \"team1\", find_dir)",
            "        if not result:",
            "            return False",
            "        return ResXy(int(result.x), int(result.y))",
        ]
        return lines[:start_idx] + replacement + lines[end_idx + 1:]
    return lines

lines = replace_method_find_pic_team1(lines)
print("Replaced find_pic_team1 method")


# ============================================================
# Replace find_str_team1 method
# ============================================================
def replace_method_find_str_team1(lines):
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == "    # 找字方法" and i + 1 < len(lines) and "def find_str_team1" in lines[i + 1] and "team2" not in lines[i + 1]:
            start_idx = i
        if start_idx is not None and i > start_idx and line.rstrip().endswith("return False"):
            if any(kw in lines[i - 1] for kw in ["pos_res", "res"]):
                # Make sure we're at find_str_team1, not find_str
                end_idx = i
                break
    if start_idx is not None and end_idx is not None:
        replacement = [
            "    # 找字方法",
            "    def find_str_team1(self, text, region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = region",
            "        result = engine.find_pic_or_str(text, (int(x), int(y), int(w - x), int(h - y)), find_dir, \"team1\", self.confidenceNum)",
            "        if result:",
            "            return ResXy(int(result.x), int(result.y))",
            "        else:",
            "            return False",
        ]
        return lines[:start_idx] + replacement + lines[end_idx + 1:]
    return lines

lines = replace_method_find_str_team1(lines)
print("Replaced find_str_team1 method")


# ============================================================
# Replace find_pic_team2 method
# ============================================================
def replace_method_find_pic_team2(lines):
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == "    # 找图方法z" and i + 1 < len(lines) and "def find_pic_team2" in lines[i + 1]:
            start_idx = i
        if start_idx is not None and i > start_idx and line.rstrip() == "        return res":
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        replacement = [
            "    # 找图方法z",
            "    def find_pic_team2(self, image_path, image_region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = image_region",
            "        result = engine.find_pic(image_path, (int(x), int(y), int(w - x), int(h - y)), self.confidenceNum, \"team2\", find_dir)",
            "        if not result:",
            "            return False",
            "        return ResXy(int(result.x), int(result.y))",
        ]
        return lines[:start_idx] + replacement + lines[end_idx + 1:]
    return lines

lines = replace_method_find_pic_team2(lines)
print("Replaced find_pic_team2 method")


# ============================================================
# Replace find_str_team2 method
# ============================================================
def replace_method_find_str_team2(lines):
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == "    # 找字方法" and i + 1 < len(lines) and "def find_str_team2" in lines[i + 1]:
            start_idx = i
        if start_idx is not None and i > start_idx and line.rstrip().endswith("return False"):
            # Already past start_idx
            if "def find_str_team2" in lines[start_idx + 1]:
                end_idx = i
                break
    if start_idx is not None and end_idx is not None:
        replacement = [
            "    # 找字方法",
            "    def find_str_team2(self, text, region, find_dir):",
            "        if self.overed:",
            "            return",
            "        x, y, w, h = region",
            "        result = engine.find_pic_or_str(text, (int(x), int(y), int(w - x), int(h - y)), find_dir, \"team2\", self.confidenceNum)",
            "        if result:",
            "            return ResXy(int(result.x), int(result.y))",
            "        else:",
            "            return False",
        ]
        return lines[:start_idx] + replacement + lines[end_idx + 1:]
    return lines

lines = replace_method_find_str_team2(lines)
print("Replaced find_str_team2 method")

# ============================================================
# Now let's do the remaining replacements using regex on the content
# ============================================================
content = "\n".join(lines)
replacement_count = 0

# ============================================================
# Step 3: Replace fing_fei_in_image_or_str method
# ============================================================
old_fing_fei = '''    # 图中找图
    def fing_fei_in_image_or_str(self, base, base_region, fei_region,
                                 fei_image):
        if self.overed:
            return
        base_pos = self.find_pic_or_str(base, base_region, 0)
        if not base_pos:
            return False
        x, y, w, h = fei_region
        fei_pox = # TODO_MIGRATE: self.dm.FindPicEx(
            int(base_pos.x - x),
            int(base_pos.y - y),
            int(base_pos.x + w),
            int(base_pos.y + h),
            fei_image,
            "",
            0.6,
            0,
        )
        if not fei_pox or fei_pox is None:
            return False
        res_pos = fei_pox.split("|")
        res_pos = res_pos[0].split(",")
        pics = fei_image.split("|")
        picSize = # TODO_MIGRATE: self.dm.GetPicSize(pics[int(res_pos[0])])
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        posX = int(res_pos[1]) + (int(picW) * 0.5)
        posY = int(res_pos[2]) + (int(picH) * 0.5)
        res = ResXy(int(posX), int(posY))
        return res'''

new_fing_fei = '''    # 图中找图
    def fing_fei_in_image_or_str(self, base, base_region, fei_region,
                                 fei_image):
        if self.overed:
            return
        base_pos = self.find_pic_or_str(base, base_region, 0)
        if not base_pos:
            return False
        x, y, w, h = fei_region
        result = engine.find_pic(
            fei_image,
            (int(base_pos.x - x), int(base_pos.y - y), int(base_pos.x + w) - int(base_pos.x - x), int(base_pos.y + h) - int(base_pos.y - y)),
            0.6,
            "main",
            0,
        )
        if not result:
            return False
        return ResXy(int(result.x), int(result.y))'''

if old_fing_fei in content:
    content = content.replace(old_fing_fei, new_fing_fei)
    replacement_count += 1
    print("Replaced fing_fei_in_image_or_str method")
else:
    print("WARNING: Could not find fing_fei_in_image_or_str pattern")

# ============================================================
# Step 4: Replace huifu_yijian method
# ============================================================
old_huifu = '''    # 一键恢复
    def huifu_yijian(self, dm):
        self.huifuFlag = True
        if self.overed:
            return
        while True:
            if self.check_stop_or_over():
                return
            find_res = dm.FindPicEx(0, 0, 900, 590,
                         f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}",
                         "", self.confidenceNum, 0)
            if find_res:
                # 找到图片，解析坐标
                pos = find_res.split("|")
                pos_res = pos[0].split(",")
                pics = f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}".split("|")
                picSize = dm.GetPicSize(pics[int(pos_res[0])])
                picSize = picSize.split(",")
                picW, picH = picSize[0], picSize[1]
                posX = int(pos_res[1]) + (int(picW) * 0.5)
                posY = int(pos_res[2]) + (int(picH) * 0.5)
                dm.MoveTo(int(posX), int(posY))
                time.sleep(0.005)
                dm.LeftClick()
                break
        while True:
            if self.check_stop_or_over():
                return
            find_res = dm.FindStrFastE(0, 0, 900, 580, '一键恢复', self.color_format, self.confidenceNum)
            find_str_result = find_res.split("|")
            if int(find_str_result[0]) < 0:
                continue
            pos_res = find_str_result
            posX = pos_res[1]
            posY = pos_res[2]
            dm.MoveTo(int(posX), int(posY))
            time.sleep(0.5)
            dm.LeftClick()
            break
        time.sleep(0.5)
        while True:
            if self.check_stop_or_over():
                return
            find_res = dm.FindPicEx(0, 0, 900, 590,
                         f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}",
                         "", self.confidenceNum, 0)
            if find_res:
                # 找到图片，解析坐标
                pos = find_res.split("|")
                pos_res = pos[0].split(",")
                pics = f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}".split("|")
                picSize = dm.GetPicSize(pics[int(pos_res[0])])
                picSize = picSize.split(",")
                picW, picH = picSize[0], picSize[1]
                posX = int(pos_res[1]) + (int(picW) * 0.5)
                posY = int(pos_res[2]) + (int(picH) * 0.5)
                dm.MoveTo(int(posX), int(posY))
                time.sleep(0.005)
                dm.LeftClick()
                break
        self.huifuFlag = False'''

new_huifu = '''    # 一键恢复
    def huifu_yijian(self, dm):
        self.huifuFlag = True
        if self.overed:
            return
        role = "main"
        if dm == self.win1_dm:
            role = "team1"
        elif dm == self.win2_dm:
            role = "team2"
        while True:
            if self.check_stop_or_over():
                return
            result = engine.find_pic(
                f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}",
                (0, 0, 900, 590), self.confidenceNum, role, 0)
            if result:
                engine.move_to(int(result.x), int(result.y))
                time.sleep(0.005)
                engine.left_click(role=role)
                break
        while True:
            if self.check_stop_or_over():
                return
            result = engine.find_pic_or_str('一键恢复', (0, 0, 900, 580), 0, role, self.confidenceNum)
            if result:
                engine.move_to(int(result.x), int(result.y))
                time.sleep(0.5)
                engine.left_click(role=role)
                break
        time.sleep(0.5)
        while True:
            if self.check_stop_or_over():
                return
            result = engine.find_pic(
                f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}",
                (0, 0, 900, 590), self.confidenceNum, role, 0)
            if result:
                engine.move_to(int(result.x), int(result.y))
                time.sleep(0.005)
                engine.left_click(role=role)
                break
        self.huifuFlag = False'''

if old_huifu in content:
    content = content.replace(old_huifu, new_huifu)
    replacement_count += 1
    print("Replaced huifu_yijian method")
else:
    print("WARNING: Could not find huifu_yijian pattern")


# ============================================================
# Step 5: Replace _find_all_str method
# ============================================================
old_find_all_str = '''    def _find_all_str(self, text, region):
        x, y, w, h = region
        result = # TODO_MIGRATE: self.dm.FindStrFastE(
            int(x), int(y), int(w), int(h), text,
            self.color_format, self.confidenceNum
        )
        result = result.split("|")
        if int(result[0]) < 0:
            return []
        positions = []
        for i in range(0, len(result), 3):
            if i + 2 < len(result) and int(result[i]) >= 0:
                positions.append(ResXy(int(result[i + 1]), int(result[i + 2])))
        return positions'''

new_find_all_str = '''    def _find_all_str(self, text, region):
        x, y, w, h = region
        result = engine.find_pic_or_str(text, (int(x), int(y), int(w - x), int(h - y)), 0, "main", self.confidenceNum)
        if result:
            return [ResXy(int(result.x), int(result.y))]
        return []'''

if old_find_all_str in content:
    content = content.replace(old_find_all_str, new_find_all_str)
    replacement_count += 1
    print("Replaced _find_all_str method")
else:
    print("WARNING: Could not find _find_all_str pattern")


# ============================================================
# Step 6: Replace _find_all_pic method
# ============================================================
old_find_all_pic = '''    def _find_all_pic(self, image_path, region):
        x, y, w, h = region
        result = # TODO_MIGRATE: self.dm.FindPicEx(
            int(x), int(y), int(w), int(h), image_path, "",
            self.confidenceNum, 0
        )
        if not result:
            return []
        items = result.split("|")
        pics = image_path.split("|")
        positions = []
        for item in items:
            parts = item.split(",")
            pic_idx = int(parts[0])
            pic_size = # TODO_MIGRATE: self.dm.GetPicSize(pics[pic_idx]).split(",")
            cx = int(parts[1]) + int(int(pic_size[0]) * 0.5)
            cy = int(parts[2]) + int(int(pic_size[1]) * 0.5)
            positions.append(ResXy(cx, cy))
        return positions'''

new_find_all_pic = '''    def _find_all_pic(self, image_path, region):
        x, y, w, h = region
        results = engine.find_pic_all(image_path, (int(x), int(y), int(w - x), int(h - y)), self.confidenceNum, "main")
        if not results:
            return []
        positions = []
        for r in results:
            positions.append(ResXy(int(r.x), int(r.y)))
        return positions'''

if old_find_all_pic in content:
    content = content.replace(old_find_all_pic, new_find_all_pic)
    replacement_count += 1
    print("Replaced _find_all_pic method")
else:
    print("WARNING: Could not find _find_all_pic pattern")


# ============================================================
# Step 7: Replace _count_xiaolvren method
# ============================================================
old_count_xiaolvren = '''    # V3辅助方法：统计小地图上小绿人数量
    def _count_xiaolvren(self):
        try:
            xiaolvren_bmp = self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren.bmp")
            dx, dy, dw, dh = self.dituLocation
            result = # TODO_MIGRATE: self.dm.FindPicEx(dx, dy, dw, dh, xiaolvren_bmp, "", 0.9, 0)
            if not result:
                return 0
            return len(result.split("|"))
        except:
            return 0'''

new_count_xiaolvren = '''    # V3辅助方法：统计小地图上小绿人数量
    def _count_xiaolvren(self):
        try:
            xiaolvren_bmp = self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren.bmp")
            dx, dy, dw, dh = self.dituLocation
            results = engine.find_pic_all(xiaolvren_bmp, (int(dx), int(dy), int(dw - dx), int(dh - dy)), 0.9, "main")
            if not results:
                return 0
            return len(results)
        except:
            return 0'''

if old_count_xiaolvren in content:
    content = content.replace(old_count_xiaolvren, new_count_xiaolvren)
    replacement_count += 1
    print("Replaced _count_xiaolvren method")
else:
    print("WARNING: Could not find _count_xiaolvren pattern")


# ============================================================
# Step 8: Replace FindPicEx in zhengdian_by_xiaolvren
# ============================================================
old_zd_by_xl = '''    # 在地图通过小绿人打整点
    def zhengdian_by_xiaolvren(self, base_image, find_dir, npc_posx=[],
                               npc_possy=[], order=1):
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 3)
        if not base_image_res:
            return f"不在{base_image}"
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren.bmp")
        picSize = # TODO_MIGRATE: self.dm.GetPicSize(xiaolvren)
        # print(picSize, 'picSize')
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        xiaolvren_pos = # TODO_MIGRATE: self.dm.FindPicEx(
            int(x),
            int(y),
            int(w),
            int(h),
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren.bmp"),
            "",
            0.9,
            find_dir,
        )
        # print(xiaolvren_pos, 'xiaolvren_pos')
        if xiaolvren_pos:
            xiaolvren_pos = xiaolvren_pos.split("|")
            # print(xiaolvren_pos, 'xiaolvren_pos')
            xiaolvren_pos = self.sort_array_by_second_value(xiaolvren_pos,order)
            xiaolvren_pos_color = "07d307"
            for item in xiaolvren_pos:
                if self.overed:
                    return
                new_item = item.split(",")
                # print(new_item[1], new_item[2], base_image, 'new_item[1]')
                if npc_posx != 0 and int(new_item[1]) in npc_posx and int(
                        new_item[2]) in npc_possy:
                    continue
                item_x = int(new_item[1]) + int(int(picW) * 0.5)
                item_y = int(new_item[2]) + int(int(picH) * 0.5)
                if # TODO_MIGRATE: self.dm.CmpColor(item_x, item_y, xiaolvren_pos_color,
                                    0.7) == 1:
                    self.hasZhengDianCount -= 1
                    continue
                hasZhengDian = False
                change_color_time = 0
                find_zhengdian_time = time.time()
                engine.move_to(item_x, item_y)
                time.sleep(0.001)
                engine.left_click(role="main")
                time.sleep(0.001)
                engine.move_to(int(item_x - 200), item_y)
                time.sleep(0.1)
                self.color_format = "b@ffff00-000000|fff200-000000"
                is_zhengdian = None
                while True:
                    if time.time() - find_zhengdian_time > 10:
                        print("超时10s")
                        break
                    # if not self.find_str(base_image, self.dituLocation, 0):
                    # 	break
                    if change_color_time == 0 and # TODO_MIGRATE: self.dm.CmpColor(item_x,
                                                                   item_y,
                                                                   xiaolvren_pos_color,
                                                                   0.7) == 1:
                        change_color_time = time.time()
                    time.sleep(0.01)
                    self.confidenceNum = 0.8
                    time.sleep(0.001)
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/dianwei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dianwei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        print("npc")
                        self.confidenceNum = 0.9
                        break'''

new_zd_by_xl = '''    # 在地图通过小绿人打整点
    def zhengdian_by_xiaolvren(self, base_image, find_dir, npc_posx=[],
                               npc_possy=[], order=1):
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 3)
        if not base_image_res:
            return f"不在{base_image}"
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren.bmp")
        xiaolvren_results = engine.find_pic_all(
            xiaolvren,
            (int(x), int(y), int(w - x), int(h - y)),
            0.9,
            "main",
        )
        if xiaolvren_results:
            xiaolvren_pos = [f"0,{r.x},{r.y}" for r in xiaolvren_results]
            xiaolvren_pos = self.sort_array_by_second_value(xiaolvren_pos, order)
            xiaolvren_pos_color = "07d307"
            for item in xiaolvren_pos:
                if self.overed:
                    return
                new_item = item.split(",")
                if npc_posx != 0 and int(new_item[1]) in npc_posx and int(
                        new_item[2]) in npc_possy:
                    continue
                item_x = int(new_item[1])
                item_y = int(new_item[2])
                if engine._cmp_color(item_x, item_y, xiaolvren_pos_color,
                                    0.7) == 1:
                    self.hasZhengDianCount -= 1
                    continue
                hasZhengDian = False
                change_color_time = 0
                find_zhengdian_time = time.time()
                engine.move_to(item_x, item_y)
                time.sleep(0.001)
                engine.left_click(role="main")
                time.sleep(0.001)
                engine.move_to(int(item_x - 200), item_y)
                time.sleep(0.1)
                self.color_format = "b@ffff00-000000|fff200-000000"
                is_zhengdian = None
                while True:
                    if time.time() - find_zhengdian_time > 10:
                        print("超时10s")
                        break
                    # if not self.find_str(base_image, self.dituLocation, 0):
                    # 	break
                    if change_color_time == 0 and engine._cmp_color(item_x,
                                                                   item_y,
                                                                   xiaolvren_pos_color,
                                                                   0.7) == 1:
                        change_color_time = time.time()
                    time.sleep(0.01)
                    self.confidenceNum = 0.8
                    time.sleep(0.001)
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/dianwei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dianwei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        print("npc")
                        self.confidenceNum = 0.9
                        break'''

if old_zd_by_xl in content:
    content = content.replace(old_zd_by_xl, new_zd_by_xl)
    replacement_count += 1
    print("Replaced zhengdian_by_xiaolvren method")
else:
    print("WARNING: Could not find zhengdian_by_xiaolvren pattern")


# ============================================================
# Step 9: Replace FindPicEx in _find_dots_by_xiaolvren (V3) - the while loop section
# ============================================================
# The function starts at zhengdian_by_xiaolvren_v3_ditu. Let me handle the FindPicEx within it.
old_v3_findex = '''            green_result = # TODO_MIGRATE: self.dm.FindPicEx(
                int(x), int(y), int(w), int(h), xiaolvren, "", 0.9, 0
            )
            target_dots = []
            if green_result:
                all_dots = green_result.split("|")
                for item in all_dots:
                    parts = item.split(",")
                    tl_x = int(parts[1])
                    tl_y = int(parts[2])
                    if self._is_near_npc_zone(tl_x, tl_y, npc_zones, threshold=10):
                        continue
                    skip = False
                    for ax, ay in attacked_set:
                        if abs(tl_x - ax) <= 20 and abs(tl_y - ay) <= 20:
                            skip = True
                            break
                    if skip:
                        continue
                    click_x = tl_x + pic_w // 2
                    click_y = tl_y + pic_h // 2
                    target_dots.append((click_x, click_y, tl_x, tl_y))'''

new_v3_findex = '''            green_results = engine.find_pic_all(xiaolvren, (int(x), int(y), int(w - x), int(h - y)), 0.9, "main")
            target_dots = []
            if green_results:
                for r in green_results:
                    tl_x = r.x
                    tl_y = r.y
                    if self._is_near_npc_zone(tl_x, tl_y, npc_zones, threshold=10):
                        continue
                    skip = False
                    for ax, ay in attacked_set:
                        if abs(tl_x - ax) <= 20 and abs(tl_y - ay) <= 20:
                            skip = True
                            break
                    if skip:
                        continue
                    click_x = tl_x + pic_w // 2
                    click_y = tl_y + pic_h // 2
                    target_dots.append((click_x, click_y, tl_x, tl_y))'''

if old_v3_findex in content:
    content = content.replace(old_v3_findex, new_v3_findex)
    replacement_count += 1
    print("Replaced V3 FindPicEx pattern")
else:
    print("WARNING: Could not find V3 FindPicEx pattern")


# ============================================================
# Step 10: Replace GetPicSize in V3 _find_dots_by_xiaolvren
# ============================================================
old_v3_picsize = '''        pic_size = # TODO_MIGRATE: self.dm.GetPicSize(xiaolvren).split(",")
        pic_w, pic_h = int(pic_size[0]), int(pic_size[1])'''

new_v3_picsize = '''        pic_size = engine.find_pic(xiaolvren, self.dituLocation, 0.9, "main")
        if pic_size:
            pic_w, pic_h = pic_size.width, pic_size.height
        else:
            pic_w, pic_h = 10, 10'''

if old_v3_picsize in content:
    content = content.replace(old_v3_picsize, new_v3_picsize)
    replacement_count += 1
    print("Replaced V3 GetPicSize pattern")
else:
    print("WARNING: Could not find V3 GetPicSize pattern")


# ============================================================
# Step 11: Replace CmpColor calls in _find_dots_by_xiaolvren (V3) _filter_valid_dots
# ============================================================
old_cmpcolor_v3 = '''            if # TODO_MIGRATE: self.dm.CmpColor(cx, cy, green_color, 0.7) == 1:
                continue'''
new_cmpcolor_v3 = '''            if engine._cmp_color(cx, cy, green_color, 0.7) == 1:
                continue'''

if old_cmpcolor_v3 in content:
    content = content.replace(old_cmpcolor_v3, new_cmpcolor_v3)
    replacement_count += 1
    print("Replaced V3 CmpColor pattern")
else:
    print("WARNING: Could not find V3 CmpColor pattern")


# ============================================================
# Step 12: Replace zhengdian_by_xiaolvren_for_gongcheng
# ============================================================
old_zd_gc = '''    # 在地图通过小绿人打整点
    def zhengdian_by_xiaolvren_for_gongcheng(self, base_image, find_dir,
                                             npc_posx=[], npc_possy=[],
                                             order=1):
        if npc_posx is None:
            npc_posx = [0]
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 5)
        if not base_image_res:
            return f"不在{base_image}"
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren2.bmp")
        picSize = # TODO_MIGRATE: self.dm.GetPicSize(xiaolvren)
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        xiaolvren_pos = # TODO_MIGRATE: self.dm.FindPicEx(
            int(x),
            int(y),
            int(w),
            int(h),
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren2.bmp"),
            "",
            0.7,
            find_dir,
        )
        if xiaolvren_pos:
            xiaolvren_pos = xiaolvren_pos.split("|")
            # print(xiaolvren_pos, 'xiaolvren_pos')
            xiaolvren_pos = self.sort_array_by_second_value(xiaolvren_pos,
                                                            order)
            # print(xiaolvren_pos, 'xiaolvren_pos111')
            xiaolvren_pos_color = "07d307"
            # xiaolvren_pos_color = self.dm.GetColor(int(int(xiaolvren_pos[0].split(',')[1]) + int(int(picW) * 0.5)), int(int(xiaolvren_pos[0].split(',')[2]) + int(int(picH) * 0.5)))
            # print(xiaolvren_pos_color, 'xiaolvren_pos_color')
            for item in xiaolvren_pos:
                if self.overed:
                    return
                new_item = item.split(",")
                # print(new_item[1], new_item[2], base_image, 'new_item[1]')
                if npc_posx != 0 and int(new_item[1]) in npc_posx and int(
                        new_item[2]) in npc_possy:
                    continue
                item_x = int(new_item[1]) + int(int(picW) * 0.5)
                item_y = int(new_item[2]) + int(int(picH) * 0.5)
                if # TODO_MIGRATE: self.dm.CmpColor(item_x, item_y, xiaolvren_pos_color,
                                    0.7) == 1:
                    continue
                hasZhengDian = False
                change_color_time = 0
                find_zhengdian_time = time.time()
                engine.move_to(item_x, item_y)
                time.sleep(0.001)
                engine.left_click(role="main")
                time.sleep(0.001)
                engine.move_to(int(item_x - 200), item_y)
                time.sleep(0.1)
                while True:
                    if time.time() - find_zhengdian_time > 10:
                        print("超时10s")
                        if base_image == "野外北":
                            self.check_line()
                        break
                    # if not self.find_str(base_image, self.dituLocation, 0):
                    # 	break
                    if change_color_time == 0 and # TODO_MIGRATE: self.dm.CmpColor(item_x,
                                                                   item_y,
                                                                   xiaolvren_pos_color,
                                                                   0.7) == 1:
                        change_color_time = time.time()
                    time.sleep(0.01)
                    self.confidenceNum = 0.6
                    time.sleep(0.001)'''

new_zd_gc = '''    # 在地图通过小绿人打整点
    def zhengdian_by_xiaolvren_for_gongcheng(self, base_image, find_dir,
                                             npc_posx=[], npc_possy=[],
                                             order=1):
        if npc_posx is None:
            npc_posx = [0]
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 5)
        if not base_image_res:
            return f"不在{base_image}"
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren2.bmp")
        xiaolvren_results = engine.find_pic_all(
            xiaolvren,
            (int(x), int(y), int(w - x), int(h - y)),
            0.7,
            "main",
        )
        if xiaolvren_results:
            xiaolvren_pos = [f"0,{r.x},{r.y}" for r in xiaolvren_results]
            xiaolvren_pos = self.sort_array_by_second_value(xiaolvren_pos,
                                                            order)
            xiaolvren_pos_color = "07d307"
            for item in xiaolvren_pos:
                if self.overed:
                    return
                new_item = item.split(",")
                if npc_posx != 0 and int(new_item[1]) in npc_posx and int(
                        new_item[2]) in npc_possy:
                    continue
                item_x = int(new_item[1])
                item_y = int(new_item[2])
                if engine._cmp_color(item_x, item_y, xiaolvren_pos_color,
                                    0.7) == 1:
                    continue
                hasZhengDian = False
                change_color_time = 0
                find_zhengdian_time = time.time()
                engine.move_to(item_x, item_y)
                time.sleep(0.001)
                engine.left_click(role="main")
                time.sleep(0.001)
                engine.move_to(int(item_x - 200), item_y)
                time.sleep(0.1)
                while True:
                    if time.time() - find_zhengdian_time > 10:
                        print("超时10s")
                        if base_image == "野外北":
                            self.check_line()
                        break
                    # if not self.find_str(base_image, self.dituLocation, 0):
                    # 	break
                    if change_color_time == 0 and engine._cmp_color(item_x,
                                                                   item_y,
                                                                   xiaolvren_pos_color,
                                                                   0.7) == 1:
                        change_color_time = time.time()
                    time.sleep(0.01)
                    self.confidenceNum = 0.6
                    time.sleep(0.001)'''

if old_zd_gc in content:
    content = content.replace(old_zd_gc, new_zd_gc)
    replacement_count += 1
    print("Replaced zhengdian_by_xiaolvren_for_gongcheng method")
else:
    print("WARNING: Could not find zhengdian_by_xiaolvren_for_gongcheng pattern")


# ============================================================
# Step 13: Now handle remaining TODO_MIGRATE lines that couldn't be matched with full methods
# ============================================================

# Replace specific line patterns within findGame and find_and_bing_windows methods
# We need to handle these at the line level since they're mixed in with other code

lines = content.split("\n")
new_lines = []
migrate_count = 0

for i, line in enumerate(lines):
    modified = False
    
    # TODO_MIGRATE: self.dm.GetWindowText / GetClassName (standalone var assignments in callbacks)
    if "window_text = # TODO_MIGRATE:" in line and "GetWindowText" in line:
        line = line.replace("# TODO_MIGRATE: self.dm.GetWindowText(hwnd)", "win32gui.GetWindowText(hwnd)")
        modified = True
    elif "window_text = # TODO_MIGRATE:" in line and "self.win1_dm.GetWindowText" in line:
        line = line.replace("# TODO_MIGRATE: self.win1_dm.GetWindowText(hwnd)", "win32gui.GetWindowText(hwnd)")
        modified = True
    elif "window_text = # TODO_MIGRATE:" in line and "self.win2_dm.GetWindowText" in line:
        line = line.replace("# TODO_MIGRATE: self.win2_dm.GetWindowText(hwnd)", "win32gui.GetWindowText(hwnd)")
        modified = True
    
    if "class_name = # TODO_MIGRATE:" in line:
        line = line.replace("# TODO_MIGRATE: self.dm.GetClassName(hwnd)", "win32gui.GetClassName(hwnd)")
        line = line.replace("# TODO_MIGRATE: self.win1_dm.GetClassName(hwnd)", "win32gui.GetClassName(hwnd)")
        line = line.replace("# TODO_MIGRATE: self.win2_dm.GetClassName(hwnd)", "win32gui.GetClassName(hwnd)")
        modified = True
    
    if "class_name = # TODO_MIGRATE:" in line and "GetWindowClass" in line:
        line = line.replace("# TODO_MIGRATE: self.dm.GetWindowClass(hwnd)", "win32gui.GetClassName(hwnd)")
        line = line.replace("# TODO_MIGRATE: self.win1_dm.GetWindowClass(hwnd)", "win32gui.GetClassName(hwnd)")
        line = line.replace("# TODO_MIGRATE: self.win2_dm.GetWindowClass(hwnd)", "win32gui.GetClassName(hwnd)")
        modified = True
    
    # child_rect = ... GetWindowRect(hwnd)
    if "child_rect = # TODO_MIGRATE:" in line and "GetWindowRect" in line:
        line = line.replace("# TODO_MIGRATE: self.dm.GetWindowRect(hwnd)", "win32gui.GetWindowRect(hwnd)")
        line = line.replace("# TODO_MIGRATE: self.win1_dm.GetWindowRect(hwnd)", "win32gui.GetWindowRect(hwnd)")
        line = line.replace("# TODO_MIGRATE: self.win2_dm.GetWindowRect(hwnd)", "win32gui.GetWindowRect(hwnd)")
        modified = True
    
    # hwnds = ... EnumWindow(...)
    if "hwnds = # TODO_MIGRATE:" in line and "EnumWindow" in line:
        # EnumWindow(0, title, class, flags) -> we need to replace with engine.find_window or win32gui
        # For now, keep the pattern: use win32gui.FindWindow
        # The original: self.dm.EnumWindow(0, title, class, 1+2) returns comma-separated hwnds
        # We'll replace with win32gui.EnumWindows approach
        line = line.replace(
            "# TODO_MIGRATE: self.dm.EnumWindow(0, target_window_title, target_window_class,",
            "win32gui.EnumWindows(lambda h, t: True if not t else None, 0); hwnds = str(win32gui.FindWindow(None, target_window_title))"
        )
        line = line.replace(
            "# TODO_MIGRATE: self.win1_dm.EnumWindow(0, target_window_title,",
            "win32gui.EnumWindows(lambda h, t: True if not t else None, 0); hwnds = str(win32gui.FindWindow(None, target_window_title))"
        )
        line = line.replace(
            "# TODO_MIGRATE: self.win2_dm.EnumWindow(0, target_window_title,",
            "win32gui.EnumWindows(lambda h, t: True if not t else None, 0); hwnds = str(win32gui.FindWindow(None, target_window_title))"
        )
        modified = True
    
    # BindWindow calls
    if "bind_result = # TODO_MIGRATE:" in line and "BindWindow" in line:
        # BindWindow is used for dm backend binding. In ya_engine, this is handled
        # by the engine's window management. We'll replace with a simple assignment.
        line = line.replace(
            "# TODO_MIGRATE: self.dm.BindWindow(self.click_hwnd, \"dx2\", \"windows3\",",
            "1  # engine handles window binding; bind_result = 1"
        )
        line = line.replace(
            "# TODO_MIGRATE: self.dm.BindWindow(self.click_hwnd, \"gdi\", \"windows3\",",
            "1  # engine handles window binding; bind_result = 1"
        )
        line = line.replace(
            "# TODO_MIGRATE: self.win1_dm.BindWindow(self.win1_hwnd, \"gdi\", \"windows3\",",
            "1  # engine handles window binding; bind_result = 1"
        )
        line = line.replace(
            "# TODO_MIGRATE: self.win2_dm.BindWindow(self.win2_hwnd, \"gdi\", \"windows3\",",
            "1  # engine handles window binding; bind_result = 1"
        )
        modified = True
    
    # BindWindow for refresh views
    if "bind_result = # TODO_MIGRATE:" in line and "BindWindow(hwnd" in line:
        line = "        bind_result = 1  # engine handles window binding"
        modified = True
    
    # GetWindowTitle
    if "GetWindowTitle" in line and "# TODO_MIGRATE:" in line:
        line = line.replace("# TODO_MIGRATE: self.dm.GetWindowTitle(", "win32gui.GetWindowText(")
        line = line.replace("# TODO_MIGRATE: self.win1_dm.GetWindowTitle(", "win32gui.GetWindowText(")
        line = line.replace("# TODO_MIGRATE: self.win2_dm.GetWindowTitle(", "win32gui.GetWindowText(")
        modified = True
    
    # GetClientSize
    if "location = # TODO_MIGRATE:" in line and "GetClientSize" in line:
        line = "        left, top, right, bottom = win32gui.GetClientRect(self.click_hwnd); location = (right - left, bottom - top, 1)"
        modified = True
    
    # current_rect = ... GetWindowRect
    if "current_rect = # TODO_MIGRATE:" in line and "GetWindowRect" in line:
        line = line.replace("# TODO_MIGRATE: self.dm.GetWindowRect(self.click_hwnd)", "win32gui.GetWindowRect(self.click_hwnd)")
        modified = True
    
    # UnBindWindow calls
    if "# TODO_MIGRATE:" in line and "UnBindWindow" in line:
        line = "        # engine handles window unbinding"
        modified = True
    
    # KeyPress 116 (F5)
    if "# TODO_MIGRATE:" in line and "KeyPress(116)" in line:
        line = "        # engine.key_press(\"F5\")  # already handled above"
        modified = True
    
    # LeftDoubleClick
    if "# TODO_MIGRATE:" in line and "LeftDoubleClick" in line:
        line = "            engine.left_click(role=\"main\"); time.sleep(0.1); engine.left_click(role=\"main\")"
        modified = True
    
    # CapturePng -> cv2.imwrite
    if "# TODO_MIGRATE:" in line and "CapturePng" in line:
        # The capturePng is followed by coordinate lines, which are the parameters
        # We'll replace the whole CapturePng call with cv2.imwrite
        line = "                    # Engine screenshot (cv2.imwrite) for debugging"
        modified = True
    
    # MoveToEx calls
    if "# TODO_MIGRATE:" in line and "MoveToEx" in line:
        line = line.replace("# TODO_MIGRATE:", "# migrated:")
        # The MoveToEx parameters will be consumed by engine.move_to below
        # Actually, these are todo lines followed by the actual coordinates
        # The coordinate lines are not part of the TODO_MIGRATE line.
        # Since MoveToEx (2nd and 3rd params are move path) -> engine.move_to(x, y)
        # We'll just convert the TODO comment
        modified = True
    
    # FindColor calls
    if "dm_ret = # TODO_MIGRATE:" in line and "FindColor" in line:
        # Pattern: dm_ret = # TODO_MIGRATE: self.dm.FindColor(x1, y1, x2, y2, color, sim, 0)
        # Replace with engine.find_color
        line = line.replace("# TODO_MIGRATE: self.dm.FindColor", "engine.find_color")
        modified = True
    
    if modified:
        migrate_count += 1
    
    new_lines.append(line)

content = "\n".join(new_lines)
print(f"Line-level TODO_MIGRATE replacements: {migrate_count}")


# ============================================================
# Step 14: Handle remaining edge cases
# ============================================================

# The FindColor calls need special treatment because they return (x, y, r) tuple
# but engine.find_color returns MatchResult or None
# Let's find and fix the remaining FindColor usages

# First _click_color_button and _handle_continue_dialog have:
#   dm_ret = engine.find_color(x1, y1, x2, y2, color, sim, 0)
#   x, y, r = dm_ret
#   if r == 1:
# 
# engine.find_color(color, (x, y, w, h), tolerance, role) returns MatchResult or None
# So we need to change the pattern

old_findcolor_click = '''    def _click_color_button(self, x1, y1, x2, y2, color, sim,
                            double_click=False, timeout=3):
        """点击指定区域内的颜色按钮

        Args:
            x1, y1, x2, y2: 查找区域坐标
            color: 颜色值
            sim: 相似度
            double_click: 是否双击
            timeout: 等待颜色出现的超时时间（秒），默认3秒
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            dm_ret = engine.find_color(x1, y1, x2, y2, color, sim, 0)
            x, y, r = dm_ret
            if r == 1:
                engine.move_to(x, y)
                time.sleep(0.5)
                engine.left_click(role="main")
                if double_click:
                    time.sleep(0.5)
                    engine.left_click(role="main")
                return True
            time.sleep(0.1)  # 每次查找间隔0.1秒，避免CPU占用过高
        return False'''

new_findcolor_click = '''    def _click_color_button(self, x1, y1, x2, y2, color, sim,
                            double_click=False, timeout=3):
        """点击指定区域内的颜色按钮

        Args:
            x1, y1, x2, y2: 查找区域坐标
            color: 颜色值
            sim: 相似度
            double_click: 是否双击
            timeout: 等待颜色出现的超时时间（秒），默认3秒
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = engine.find_color(color, (x1, y1, x2 - x1, y2 - y1), int((1 - sim) * 255), "main")
            if result:
                engine.move_to(result.x, result.y)
                time.sleep(0.5)
                engine.left_click(role="main")
                if double_click:
                    time.sleep(0.5)
                    engine.left_click(role="main")
                return True
            time.sleep(0.1)  # 每次查找间隔0.1秒，避免CPU占用过高
        return False'''

if old_findcolor_click in content:
    content = content.replace(old_findcolor_click, new_findcolor_click)
    replacement_count += 1
    print("Replaced _click_color_button method")
else:
    print("WARNING: Could not find _click_color_button pattern")


# Fix _handle_continue_dialog FindColor
old_handle_continue = '''            dm_ret = # TODO_MIGRATE: self.dm.FindColor(249, 340, 291, 352, "ffff00-000000", 0.7,
                                       0)
            x, y, r = dm_ret
            if r == 1:
                return'''

new_handle_continue = '''            result = engine.find_color("ffff00-000000", (249, 340, 291 - 249, 352 - 340), int((1 - 0.7) * 255), "main")
            if result:
                return'''

if old_handle_continue in content:
    content = content.replace(old_handle_continue, new_handle_continue)
    replacement_count += 1
    print("Replaced _handle_continue_dialog FindColor")
else:
    # Try to find this pattern 
    if "# TODO_MIGRATE:" in content and "FindColor(249, 340, 291, 352" in content:
        print("WARNING: _handle_continue_dialog FindColor pattern not found exactly - searching...")
        # The line might have been partially modified. Let's check what it looks like now.
        for line in content.split("\n"):
            if "FindColor" in line and "249" in line:
                print(f"  Found: {line.strip()}")

# ============================================================
# Step 15: Handle findGame window management
# ============================================================

# The findGame method has get_window_rect that returns (left, top, right, bottom, isFind)
# but win32gui.GetWindowRect returns (left, top, right, bottom) without the isFind flag
# We need to adjust the code that unpacks child_rect

# Replace child_rect assignments that had isFind
old_child_rect = "left, top, right, bottom, isFind = child_rect"
new_child_rect = "left, top, right, bottom = child_rect; isFind = 1"
content = content.replace(old_child_rect, new_child_rect)
print("Fixed child_rect unpacking (removed isFind)")

# The same for current_rect unpacking
old_current_rect = "left, top, right, bottom, isFind = current_rect"
new_current_rect = "left, top, right, bottom = current_rect; isFind = 1"
content = content.replace(old_current_rect, new_current_rect)
print("Fixed current_rect unpacking")

# location = ... GetClientSize => (x, y, res) tuple
# win32gui.GetClientRect => (left, top, right, bottom) 
# The old pattern: x, y, res = location
# After our replacement, location is (width, height, 1), so:
old_location = "x, y, res = location"
new_location = "x, y, res = location[0], location[1], location[2]"
content = content.replace(old_location, new_location)
print("Fixed location unpacking for GetClientSize")


# ============================================================
# Step 16: Handle MoveToEx calls that still have TODO markers
# ============================================================

# The MoveToEx lines appear as:
#   # TODO_MIGRATE: self.dm.MoveToEx(int(d_pos[0]), int(d_pos[1]), 3, 2)
# We replaced the TODO_MIGRATE part but the actual line is still a comment.
# We need to uncomment and convert to engine.move_to

# These lines are commented out. Let's convert them to engine.move_to calls
lines = content.split("\n")
new_lines = []
for line in lines:
    if "# migrated:" in line and "MoveToEx" in line:
        # Extract the coordinates from the MoveToEx call and call engine.move_to
        # Example: # migrated: self.dm.MoveToEx(int(d_pos[0]), int(d_pos[1]), 3, 2)
        # -> engine.move_to(int(d_pos[0]), int(d_pos[1]))
        match = re.search(r'MoveToEx\(([^,]+),\s*([^,)]+)(?:,\s*\d+)?(?:,\s*\d+)?\)', line)
        if match:
            coords_x = match.group(1).strip()
            coords_y = match.group(2).strip()
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}engine.move_to({coords_x}, {coords_y})")
            migrate_count += 1
            continue
    # Also handle the Engine MoveToEx when it's a todo for dm but the actual line is a comment
    if "# TODO_MIGRATE:" in line and "MoveToEx" in line:
        match = re.search(r'MoveToEx\(([^,]+),\s*([^,)]+)(?:,\s*\d+)?(?:,\s*\d+)?\)', line)
        if match:
            coords_x = match.group(1).strip()
            coords_y = match.group(2).strip()
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}engine.move_to({coords_x}, {coords_y})")
            migrate_count += 1
            continue
        else:
            # The MoveToEx spans multiple lines. The TODO_MIGRATE line is just a comment
            # followed by the actual coordinate lines. We'll convert the comment.
            new_lines.append(f"{' ' * (len(line) - len(line.lstrip()))}engine.move_to(")
            migrate_count += 1
            continue
    new_lines.append(line)

content = "\n".join(new_lines)


# ============================================================
# Step 17: Handle the CapturePng multi-line call
# ============================================================
# The capturePng is:
#   # TODO_MIGRATE: self.dm.CapturePng(
#       0,
#       0,
#       self.locationWidth,
#       self.locationHeight,
#       f"wait_for_{C1}_more_than_22_seconds.png",
#   )
# We need to replace with cv2.imwrite using engine.screenshot()

old_capture = '''                    # TODO_MIGRATE: self.dm.CapturePng(
                        0,
                        0,
                        self.locationWidth,
                        self.locationHeight,
                        f"wait_for_{C1}_more_than_22_seconds.png",
                    )'''

new_capture = '''                    img = engine.screenshot()
                    if img is not None:
                        cv2.imwrite(f"wait_for_{C1}_more_than_22_seconds.png", img)'''

if old_capture in content:
    content = content.replace(old_capture, new_capture)
    replacement_count += 1
    print("Replaced CapturePng call")
else:
    print("WARNING: Could not find CapturePng pattern - will handle manually if needed")


# ============================================================
# Step 18: Handle commented FindPicEx in findGame (xian_pos)
# ============================================================
old_xian = '''        # xian_pos = # TODO_MIGRATE: self.dm.FindPicEx(left, top, right, bottom, self.get_resource_path("serveAssets/images/xian.bmp"), "", 0.8, 2)'''
if old_xian in content:
    content = content.replace(old_xian, "        # xian_pos = engine.find_pic(self.get_resource_path(\"serveAssets/images/xian.bmp\"), (left, top, right - left, bottom - top), 0.8, \"main\", 2)")
    replacement_count += 1
    print("Replaced commented xian_pos FindPicEx")


# ============================================================
# Step 19: Write back
# ============================================================
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal method-level replacements: {replacement_count}")
print("Done! Checking for remaining TODO markers...")

# Count remaining
remaining = content.count("TODO_MIGRATE") + content.count("TODO_DELETE")
print(f"Remaining TODO markers: {remaining}")
