# -*- coding: utf-8 -*-

try:
    import xbmc
except:
    pass


class pLog:
    def __call__(self, msg):
        self.log(msg)

    #def log(self,msg, level=xbmc.LOGNOTICE):
    def log(self,msg='', level=2):
        plugin = "plugin.video.mrknow"
        try:
          msg = msg.encode('utf-8')
        except:
          pass
        try:
            xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
            #print("[%s] %s" % (plugin, msg.__str__()))
        except:
            #print("[%s] %s" % (plugin, msg.__str__()))
            pass
    def info(self,msg):
        self.log(msg)
