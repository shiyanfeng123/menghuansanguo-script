# -*- coding: utf-8 -*-
import os
import sys
import json
import time


class ScriptEngine:
    def __init__(self, thread, config):
        self.thread = thread
        self.cfg = config
        self.name = config.get("name", "未命名")
        self.dm = thread.dm

    def run(self):
        script_type = self.cfg.get("type", "dungeon_run")
        if script_type == "dungeon_run":
            self._run_dungeon()
        elif script_type == "daily_chain":
            self._run_daily_chain()
        else:
            print(f"[ScriptEngine] 未知脚本类型: {script_type}")

    # ==================== dungeon_run ====================

    def _run_dungeon(self):
        entry = self.cfg.get("entry", {})
        loop = self.cfg.get("loop", {})
        fallback = self.cfg.get("fallback", "官渡")

        self._exit_residual_dungeon()

        city = entry.get("city", "")
        if city:
            if not self._confirm_map(city):
                sub_maps = self._get_sub_maps()
                if sub_maps and self._is_in_any_map(sub_maps):
                    self._exit_dungeon_custom()
                    time.sleep(2)
                else:
                    self._go_to_city(entry)

        if city and not self._confirm_map(city):
            fb_name = entry.get("fb_name", "")
            if fb_name:
                self.thread.feiFb(fb_name, entry.get("is_elite", False))
                time.sleep(1)

        mode = loop.get("mode", "infinite")
        count = loop.get("count", 1)
        clear_every = loop.get("clear_bag_every", 0)
        run_count = 0

        while True:
            if self.thread.check_stop_or_over():
                return
            result = self._dungeon_single_run()
            if not result:
                break
            run_count += 1
            if mode != "infinite" and run_count >= count:
                break
            if clear_every and run_count % clear_every == 0:
                self.thread.clearBag()

        self.thread.scriptName = fallback
        fallback_map = self._get_fallback_map(fallback)
        if fallback_map:
            self._navigate_to_map(fallback, fallback_map)
        if fallback == "官渡" and hasattr(self.thread, "guanduWhile"):
            self.thread.guanduWhile()
        elif fallback == "魔镜" and hasattr(self.thread, "mojingWhile"):
            self.thread.mojingWhile()
        elif fallback == "黑风" and hasattr(self.thread, "heifengWhile"):
            self.thread.heifengWhile()
        else:
            fallback_config = self._load_sub_script(fallback)
            if fallback_config:
                fallback_engine = ScriptEngine(self.thread, fallback_config)
                fallback_engine.run()

    def _dungeon_single_run(self):
        entry = self.cfg.get("entry", {})

        fb_name = entry.get("fb_name", "")
        npc_image = entry.get("npc_image", "")

        if fb_name:
            self.thread.feiFb(fb_name, entry.get("is_elite", False))
        elif npc_image:
            self._enter_via_npc(entry)

        confirm_map = self.cfg.get("confirm_map", "")
        if confirm_map:
            result = self.thread.waitFor(confirm_map, self.thread.dituLocation, 8)
            if not result:
                print(f"[{self.name}] 没次数了")
                return False

        stages = self.cfg.get("stages", [])
        for i, stage in enumerate(stages):
            if self.thread.check_stop_or_over():
                return False

            map_name = stage.get("map_name", "")
            for fight in stage.get("monsters", []):
                repeat = max(1, int(fight.get("repeat", 1)))
                for _ in range(repeat):
                    if self.thread.check_stop_or_over():
                        return False
                    self._execute_fight(fight, map_name)

            transition = stage.get("transition", {})
            click_map = transition.get("click_map_name", "")
            if click_map and i < len(stages) - 1:
                self._execute_transition(transition, map_name)

        self._exit_dungeon_custom()
        time.sleep(1)
        return True

    # ==================== daily_chain ====================

    def _run_daily_chain(self):
        tasks = self.cfg.get("tasks", [])
        fallback = self.cfg.get("fallback", "官渡")

        for task in tasks:
            if self.thread.check_stop_or_over():
                return

            script_name = task.get("script", "")
            count = max(1, int(task.get("count", 1)))

            sub_config = self._load_sub_script(script_name)
            if not sub_config:
                print(f"[ScriptEngine] 子脚本不存在: {script_name}")
                continue

            sub_entry = sub_config.get("entry", {})
            city = sub_entry.get("city", "")
            if city and not self._confirm_map(city):
                self._go_to_city(sub_entry)

            for _ in range(count):
                if self.thread.check_stop_or_over():
                    return
                sub_engine = ScriptEngine(self.thread, sub_config)
                if sub_config.get("type", "dungeon_run") == "dungeon_run":
                    sub_engine._dungeon_single_run()

        self.thread.scriptName = fallback

    # ==================== 辅助方法 ====================

    def _exit_residual_dungeon(self):
        out_fb = (
            f"{self.thread.get_resource_path('serveAssets/images/outFb.bmp')}"
            f"|{self.thread.get_resource_path('serveAssets/images/outFb1.bmp')}"
        )
        out_pos = self.thread.find_pic_or_str(out_fb, self.thread.gameLocation, 0)
        if out_pos:
            self.dm.MoveTo(out_pos.x, out_pos.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)

    def _exit_dungeon_custom(self):
        exit_map = self.cfg.get("exit_map", "")
        city = self.cfg.get("entry", {}).get("city", "")

        out_fb = (
            f"{self.thread.get_resource_path('serveAssets/images/outFb.bmp')}"
            f"|{self.thread.get_resource_path('serveAssets/images/outFb1.bmp')}"
        )

        start_time = time.time()
        location_queding = None

        while True:
            if self.thread.check_stop_or_over():
                return

            check_map = exit_map or city
            if check_map and self.thread.find_pic_or_str(check_map, self.thread.dituLocation, 0):
                break

            if time.time() - start_time > 30:
                break

            outX = getattr(self.thread, "locationX", 0) + 514
            outY = getattr(self.thread, "locationY", 0) + 50
            self.dm.MoveTo(int(outX), int(outY))
            time.sleep(0.1)
            self.dm.LeftClick()

            location_queding = self.thread.waitFor(out_fb, self.thread.gameLocation, 3)
            if location_queding:
                break

        if location_queding:
            while True:
                if not self.thread.find_pic_or_str(out_fb, self.thread.gameLocation, 0):
                    break
                self.dm.MoveTo(location_queding.x, location_queding.y)
                time.sleep(0.1)
                self.dm.LeftClick()
                time.sleep(0.1)
                self.dm.LeftClick()

        huodetongbi = self.thread.waitFor("获得铜币", self.thread.gameLeftLocation, 1)
        if huodetongbi:
            self.dm.MoveTo(huodetongbi.x, huodetongbi.y)
            time.sleep(0.001)
            self.dm.LeftClick()

    def _confirm_map(self, map_name):
        result = self.thread.waitFor(map_name, self.thread.dituLocation, 3)
        return result is not None and result is not False

    def _is_in_any_map(self, map_names):
        if not map_names:
            return False
        text_names = [n for n in map_names if "serveAssets" not in n]
        image_names = [n for n in map_names if "serveAssets" in n]
        if text_names:
            combined = "|".join(text_names)
            result = self.thread.find_pic_or_str(combined, self.thread.dituLocation, 0)
            if result is not None and result is not False:
                return True
        for name in image_names:
            result = self.thread.find_pic_or_str(name, self.thread.dituLocation, 0)
            if result is not None and result is not False:
                return True
        return False

    def _get_sub_maps(self):
        sub_maps = self.cfg.get("sub_maps", [])
        if sub_maps:
            return sub_maps
        stages = self.cfg.get("stages", [])
        return list(dict.fromkeys(s.get("map_name", "") for s in stages if s.get("map_name")))

    def _go_to_city(self, entry):
        city = entry.get("city", "")
        city_mode = entry.get("city_mode", "text")
        yizhan = entry.get("yizhan", "")
        is_fei = entry.get("is_fei", True)

        if city_mode == "image" and city:
            city_image = city
            city_name = self._guess_city_name_from_image(city)
            if not city_name:
                city_name = city
        else:
            city_image = entry.get("city_image", "")
            if not city_image:
                city_image = self._guess_city_image(city)
            city_name = city

        if city_image:
            if city_name and city_name != city_image:
                find_address = f"地图{city_name}"
            else:
                find_address = city_image
            address_pos_city = self.thread.get_resource_path(city_image) if "serveAssets" in city_image else city_image
            self.thread.go_in_ditu(
                find_address,
                address_pos_city,
                city_name,
                yizhan,
                "",
                is_fei,
            )

    def _guess_city_name_from_image(self, image_path):
        reverse_map = {
            "luoyang": "洛阳", "zhuojun": "涿郡", "xiangyang": "襄阳",
            "xuchang": "许昌", "xuzhou": "徐州", "chengxi": "城西",
            "guandu": "官渡", "wuceng": "五层",
        }
        basename = os.path.basename(image_path).lower().replace(".bmp", "").replace(".png", "").replace(".jpg", "")
        return reverse_map.get(basename, "")

    def _guess_city_image(self, city):
        city_map = {
            "洛阳": "serveAssets/images/zhengdian/luoyang.bmp",
            "涿郡": "serveAssets/images/zhengdian/zhuojun.bmp",
            "襄阳": "serveAssets/images/zhengdian/xiangyang.bmp",
            "许昌": "serveAssets/images/zhengdian/xuchang.bmp",
            "徐州": "serveAssets/images/zhengdian/xuzhou.bmp",
            "城西": "serveAssets/images/zhengdian/chengxi.bmp",
        }
        return city_map.get(city, "")

    def _enter_via_npc(self, entry):
        city = entry.get("city", "")
        city_mode = entry.get("city_mode", "text")
        npc_image = entry.get("npc_image", "")
        npc_mode = entry.get("npc_image_mode", "image")
        npc_name = entry.get("npc_name", city)

        if city_mode == "image" and city:
            city_for_find = self._guess_city_name_from_image(city) or city
        else:
            city_for_find = city

        if npc_image:
            if npc_mode == "text":
                npc_path = npc_image
            else:
                npc_path = self._resolve_image_path(npc_image)
            self.thread.findAndClickPic(
                city_for_find,
                npc_name,
                npc_path,
                self.thread.gameBottomLocation,
                "进入",
                self.thread.gameBottomLocation,
                "0.1,0.1",
                "tab",
            )

    def _execute_fight(self, fight, map_name):
        detect_mode = fight.get("detect_mode", "text")
        target_name = fight.get("name", "")
        target_image = fight.get("images", "")
        search_region = self._resolve_region(fight.get("region", "gameBottomLocation"))
        battle_end_image = fight.get(
            "battle_end",
            "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
        )
        battle_end_region = self.thread.gameBottomLocation
        move_key = fight.get("move_key", "tab")
        move_region = fight.get("move_region", "0.1,0.12")

        battle_end_path = self._resolve_image_path(battle_end_image)

        if detect_mode == "image" and target_image:
            parts = [p.strip() for p in target_image.split("|") if p.strip()]
            if len(parts) >= 2:
                B = self._resolve_image_path(parts[0])
                B1 = self._resolve_image_path(parts[1])
            elif len(parts) == 1:
                B = self._resolve_image_path(parts[0])
                B1 = self._resolve_image_path(parts[0])
            else:
                B = ""
                B1 = ""
        elif detect_mode == "text" and target_name:
            B = target_name
            B1 = target_name
        elif target_name:
            B = target_name
            B1 = target_name
        elif target_image:
            B = self._resolve_image_path(target_image)
            B1 = ""
        else:
            B = ""
            B1 = ""

        self.thread.findAndClickPic(
            map_name,
            B,
            B1,
            search_region,
            battle_end_path,
            battle_end_region,
            move_region,
            move_key,
        )

    def _execute_transition(self, transition, current_map_name):
        click_map_name = transition.get("click_map_name", "")
        click_region = transition.get("click_region_proportion", "")

        if not click_map_name:
            return

        if click_region:
            result = self.thread.waitFor(click_map_name, self.thread.dituLocation, 10)
            if result:
                try:
                    parts = click_region.split(",")
                    rx = float(parts[0])
                    ry = float(parts[1])
                    loc_x = getattr(self.thread, "locationX", 0)
                    loc_y = getattr(self.thread, "locationY", 0)
                    loc_w = getattr(self.thread, "locationWidth", 900)
                    loc_h = getattr(self.thread, "locationHeight", 580)
                    click_x = int((1000 - int(rx * 1000)) / 1000 * loc_w + loc_x)
                    click_y = int(int(ry * 1000) / 1000 * loc_h + loc_y)
                    self.dm.MoveTo(click_x, click_y)
                    time.sleep(0.1)
                    self.dm.LeftClick()
                    time.sleep(0.5)
                except (ValueError, IndexError):
                    self.thread.waitForAAndClickB1(
                        click_map_name,
                        click_map_name,
                        self.thread.dituLocation,
                        self.thread.gameLeftLocation,
                    )
            else:
                self.thread.waitForAAndClickB1(
                    click_map_name,
                    click_map_name,
                    self.thread.dituLocation,
                    self.thread.gameLeftLocation,
                )
        else:
            self.thread.waitForAAndClickB1(
                click_map_name,
                click_map_name,
                self.thread.dituLocation,
                self.thread.gameLeftLocation,
            )

    def _navigate_to_map(self, map_name, city_image):
        if not city_image:
            return
        if not self._confirm_map(map_name):
            self.thread.go_in_ditu(
                f"地图{map_name}",
                self.thread.get_resource_path(city_image),
                map_name,
                "",
                "",
                True,
            )

    def _get_fallback_map(self, fallback):
        fallback_maps = {
            "官渡": "serveAssets/images/zhengdian/guandu.bmp",
            "城西": "serveAssets/images/zhengdian/chengxi.bmp",
            "五层": "serveAssets/images/zhengdian/wuceng.bmp",
        }
        return fallback_maps.get(fallback, self._guess_city_image(fallback))

    def _resolve_region(self, region_name):
        if isinstance(region_name, (list, tuple)):
            return tuple(region_name)
        return getattr(self.thread, region_name, self.thread.gameBottomLocation)

    def _resolve_image_path(self, image_path):
        if not image_path:
            return ""
        parts = [p.strip() for p in image_path.split("|") if p.strip()]
        if len(parts) <= 1:
            return self.thread.get_resource_path(image_path)
        return "|".join(self.thread.get_resource_path(p) for p in parts)

    def _load_sub_script(self, name):
        scripts_dir = self._get_scripts_dir()
        config_path = os.path.join(scripts_dir, name, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    @staticmethod
    def _get_scripts_dir():
        if hasattr(sys, "_MEIPASS"):
            external = os.path.join(os.path.dirname(sys.executable), "user_scripts")
            if os.path.exists(external):
                return external
            return os.path.join(sys._MEIPASS, "user_scripts")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_scripts")

    @staticmethod
    def load_config(script_name):
        scripts_dir = ScriptEngine._get_scripts_dir()
        config_path = os.path.join(scripts_dir, script_name, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
