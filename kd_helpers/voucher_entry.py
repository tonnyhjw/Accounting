# -*- coding:utf-8 -*-
# Author: 黄景文


from utils.guiuitl import *

class voucherEntry():
    def __init__(self):
        pass

    def open_entrance(self):
        """打开《凭证录入》界面"""
        double_hotkey(hotkey_1="ctrl", hotkey_2="v")
        double_hotkey(hotkey_1="alt", hotkey_2="v")
        double_hotkey(hotkey_1="alt", hotkey_2="b")
        double_hotkey(hotkey_1="alt", hotkey_2="a")
        return


