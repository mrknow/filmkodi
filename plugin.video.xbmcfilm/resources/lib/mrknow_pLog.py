# -*- coding: utf-8 -*-
import xbmc

class pLog:
    def __call__(self, msg):
        self.log(msg)

    def log(self,msg, level=xbmc.LOGNOTICE):
        plugin = "plugin.video.xbmcfilm"
        try:
          msg = msg.encode('utf-8')
        except:
          pass
        xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
        print("[%s] %s" % (plugin, msg.__str__()))
    def info(self,msg):
        self.log(msg)
