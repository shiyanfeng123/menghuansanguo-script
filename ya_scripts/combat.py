"""自动战斗脚本 - 逻辑对齐serveScript.py"""
import time
import threading

_e = None
_combat_thread = None
_combat_running = False


def zidongzhandou(engine):
    global _e, _combat_running
    _e = engine
    _combat_running = True
    engine.beginFun()
    while not engine.overed:
        if engine.check_stop():
            continue
        if not _combat_running:
            break
        _combat_step()
        time.sleep(1.0)


def _combat_step():
    if _e.overed:
        return
    if _e.find_pic("ya_assets/images/zhaohuan.bmp", _e.gameLocation, _e.confidenceNum):
        _e.click_image("ya_assets/images/zhaohuan.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.3)
    if _e.find_pic("ya_assets/images/fangyu.bmp", _e.gameLocation, _e.confidenceNum):
        _e.click_image("ya_assets/images/fangyu.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.3)
    if _e.addBloudFlag:
        _e.click_image("ya_assets/images/addBloud.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.1)
        _e.click_image("ya_assets/images/addBloud1.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.1)
        _e.click_image("ya_assets/images/addBloud2.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.1)
    if _e.find_pic("ya_assets/images/zhanhun/liubei.bmp", _e.gameLocation, _e.confidenceNum):
        _e.click_image("ya_assets/images/zhanhun/liubei.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.3)
    zdzd = _e.find_pic("ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp", _e.gameLocation, _e.confidenceNum)
    if zdzd:
        _e.click_image("ya_assets/images/closeJJ.bmp", _e.gameLocation, _e.confidenceNum)
        time.sleep(0.3)


def stop_combat():
    global _combat_running
    _combat_running = False
