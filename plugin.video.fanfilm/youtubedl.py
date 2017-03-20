# -*- coding: utf-8 -*-
from resources.lib.libraries import control
import xbmc,xbmcgui
import threading
import heapq

try:
    from YDStreamExtractor import getVideoInfo
    from YDStreamExtractor import mightHaveVideo

except Exception:
    print 'importing Error. You need youtubedl module which is in official xbmc.org'
    xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Please [COLOR yellow]install Youtube-dl[/COLOR] module ,10000,"")")


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._count = 0
        self._cv = threading.Condition()
    def put(self, item, priority):
        with self._cv:
            heapq.heappush(self._queue, (-priority, self._count, item))
            self._count += 1
            self._cv.notify()

    def get(self):
        with self._cv:
            while len(self._queue) == 0:
                self._cv.wait()
            return heapq.heappop(self._queue)[-1]


def queueItems(items):
    q = PriorityQueue()
    items.reverse()

    def submitItem(items):
        t = threading.Thread(target=resolve, args=(q, items.pop()['url'], len(items),))
        t.start()

    submitItem(items)

    while len(items) > 0:
        try:
            url = q.get()
            control.log('[YOUTUBE.DL] SUCCESS: %s' % url)
        except UserWarning as e:
            control.log('[YOUTUBE.DL] ERROR: %s' % e)
            url = None
        yield url
        submitItem(items)

def resolve(q, url, priority):
    q.put(resolveUrl(url), priority)

def resolveUrl(url):
    info = getVideoInfo(url.encode('utf-8','ignore'),quality=3,resolve_redirects=True)
    if info is None:
        raise UserWarning("Missing video info")
    stream_url = None
    for s in info.streams():
        try:
            stream_url = s['xbmc_url']
        except KeyError:
            continue

        if stream_url:
            return stream_url.encode('utf-8','ignore')

    raise UserWarning("Missing stream url")
