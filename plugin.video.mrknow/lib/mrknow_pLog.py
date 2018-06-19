# -*- coding: utf-8 -*-

try:
    import xbmc
    from xbmc import LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO, LOGNONE, LOGNOTICE, LOGSEVERE, LOGWARNING
except ImportError:
    xbmc = None


class pLog:
    def __call__(self, msg):
        self.log(msg)

    def _log(self, msg='', level=None, args=None):
        plugin = "plugin.video.mrknow"
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        else:
            msg = str(msg)
        if args:
            msg += ' ' + ' '.join(args)
        if xbmc:
            if level is None:
                level = LOGINFO
            xbmc.log("[%s] %s" % (plugin, msg), level)
        else:
            print("[%s] %s" % (plugin, msg))

    def log(self, msg='', level=None):
        self._log(msg, level=level)

    def debug(self, msg, *args):
        self._log(msg, args=args, level=LOGDEBUG)

    def info(self, msg, *args):
        self._log(msg, args=args, level=LOGINFO)

    def notice(self, msg, *args):
        self._log(msg, args=args, level=LOGNOTICE)

    def warn(self, msg, *args):
        self._log(msg, args=args, level=LOGWARNING)

    def error(self, msg, *args):
        self._log(msg, args=args, level=LOGERROR)

