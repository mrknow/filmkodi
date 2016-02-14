# -*- coding: utf-8 -*-

import xbmcgui

class DialogInfo:

    def __init__(self):
        self.dlg = xbmcgui.Dialog()
        self.head = 'SportsDevil Info'

    def show(self, message):
        self.dlg.ok(self.head, message)