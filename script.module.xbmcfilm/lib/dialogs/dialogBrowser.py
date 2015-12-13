# -*- coding: utf-8 -*-

import xbmcgui

class DialogBrowser:

    def __init__(self):
        self.dlg = xbmcgui.Dialog()

    def browseFolders(self, head):
        return self.dlg.browse(0, head,'files', '', False, False)
        
    def close(self):
        self.dlg.close()