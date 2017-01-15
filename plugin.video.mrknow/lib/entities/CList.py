# -*- coding: utf-8 -*-

class CList(object):
    
    def __init__(self):
        self.start = ''
        self.section = ''
        self.sort = ''
        self.cfg = ''
        self.skill = ''
        self.catcher = ''
        self.items = []
        self.rules = []

    def getVideos(self):
        return filter(lambda x: x['type'] == 'video', self.items)