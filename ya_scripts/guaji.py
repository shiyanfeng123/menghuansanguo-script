"""挂机脚本 - 逻辑对齐serveScript.py guajiAndzhengdianScript"""
import time

_e = None


def bishuishuxue(engine):
    global _e
    _e = engine
    engine.beginFun()
    engine.guajiAndzhengdianScript(
        "ya_assets/images/guaji/bishuishuxue.bmp|ya_assets/images/guaji/bishuishuxue1.bmp"
    )


def wokou(engine):
    global _e
    _e = engine
    engine.beginFun()
    engine.guajiAndzhengdianScript(
        "ya_assets/images/guaji/wokou.bmp|ya_assets/images/guaji/wokou1.bmp"
    )


def longchao(engine):
    global _e
    _e = engine
    engine.beginFun()
    engine.guajiAndzhengdianScript(
        "ya_assets/images/guaji/longchao.bmp|ya_assets/images/guaji/longchao1.bmp"
    )


def senluodian(engine):
    global _e
    _e = engine
    engine.beginFun()
    engine.guajiAndzhengdianScript(
        "ya_assets/images/guaji/senluodian.bmp|ya_assets/images/guaji/senluodian1.bmp"
    )
