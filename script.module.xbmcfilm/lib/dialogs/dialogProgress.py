# -*- coding: utf-8 -*-

import xbmcgui

class DialogProgress:

    def __init__(self):
        self.dlg = xbmcgui.DialogProgress()
        self.__reset__()

    def __reset__(self):
        self.head = ''
        self.firstline = ''
        self.secondline = None
        self.thirdline = None
        self.percent = 0

    def isCanceled(self):
        return self.dlg.iscanceled()

    def update(self, percent=None, firstline=None, secondline=None, thirdline=None):
        if firstline:
            self.firstline = firstline
        if secondline:
            self.secondline = secondline
        if thirdline:
            self.thirdline = thirdline
        if percent:
            self.percent = percent

        if self.secondline and self.thirdline:
            self.dlg.update(self.percent, self.firstline, self.secondline, self.thirdline)
        elif self.secondline:
            self.dlg.update(self.percent, self.firstline, self.secondline)
        else:
            self.dlg.update(self.percent, self.firstline)



    def create(self, head, firstline = None, secondline=None, thirdline=None):
        if firstline:
            self.firstline = firstline
        if secondline:
            self.secondline = secondline
        if thirdline:
            self.thirdline = thirdline

        if self.secondline and self.thirdline:
            self.dlg.create(head, self.firstline, self.secondline, self.thirdline)
        elif self.secondline:
            self.dlg.create(head, self.firstline, self.secondline)
        else:
            self.dlg.create(head, self.firstline)


    def close(self):
        self.dlg.close()
        self.__reset__()