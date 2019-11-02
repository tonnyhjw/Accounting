# -*- coding:utf-8 -*-
# Author: 黄景文

import pyautogui as pag

def mouse_position():
    return pag.position()

# (x=1057, y=32)
def run_experiment():
    pag.click(x=818, y=63)
    pag.tripleClick(x=818, y=63)
    pag.hotkey("ctrl", "c")

def double_hotkey(hotkey_1=None, hotkey_2=None):
    if not hotkey_1 or not hotkey_2:
        print("Hot key missing!!!")
    pag.hotkey(hotkey_1, hotkey_2, interval=0.1)
    return
