import xbmc
import xbmcaddon

addon = xbmcaddon.Addon('script.module.urlresolver')
name = addon.getAddonInfo('name')

LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR
LOGFATAL = xbmc.LOGFATAL
LOGINFO = xbmc.LOGINFO
LOGNONE = xbmc.LOGNONE
LOGNOTICE = xbmc.LOGNOTICE
LOGSEVERE = xbmc.LOGSEVERE
LOGWARNING = xbmc.LOGWARNING

def log_debug(msg):
    log(msg, level=LOGDEBUG)

def log_notice(msg):
    log(msg, level=LOGNOTICE)

def log_warning(msg):
    log(msg, level=LOGWARNING)

def log_error(msg):
    log(msg, level=LOGERROR)

def log(msg, level=LOGDEBUG):
    # override message level to force logging when addon logging turned on
    if addon.getSetting('addon_debug') == 'true' and level == LOGDEBUG:
        level = LOGNOTICE

    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('%s: %s' % (name, msg), level)
    except Exception as e:
        try: xbmc.log('Logging Failure: %s' % (e), level)
        except: pass  # just give up
