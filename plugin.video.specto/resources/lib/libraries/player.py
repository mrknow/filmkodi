# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,sys,json,time,xbmc

from resources.lib.libraries import control
from resources.lib.libraries import subtitles
from resources.lib.libraries import bookmarks
from resources.lib.libraries import trakt


class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)


    def run(self, content, name, url, year, imdb, tvdb, meta):

        if control.window.getProperty('PseudoTVRunning') == 'True':
            return control.player.play(url, control.item(path=url))

        self.getVideoInfo(content, name, year, imdb, tvdb)

        if self.folderPath.startswith('plugin://') and not meta == None:
            poster, thumb, meta = self.getMeta(meta)
        else:
            poster, thumb, meta = self.getLibraryMeta()

        item = control.item(path=url, iconImage='DefaultVideo.png', thumbnailImage=thumb)
        item.setInfo(type='Video', infoLabels = meta)
        try: item.setArt({'poster': poster, 'tvshow.poster': poster, 'season.poster': poster})
        except: pass
        item.setProperty('Video', 'true')
        item.setProperty('IsPlayable', 'true')
        control.player.play(url, item)

        for i in range(0, 240):
            if self.isPlayingVideo(): break
            xbmc.sleep(1000)
        while self.isPlayingVideo():
            try: self.totalTime = self.getTotalTime()
            except: pass
            try: self.currentTime = self.getTime()
            except: pass
            xbmc.sleep(1000)
        control.window.clearProperty('script.trakt.ids')
        time.sleep(5)


    def getVideoInfo(self, content, name, year, imdb, tvdb):
        try:
            self.loadingTime = time.time()
            self.totalTime = 0 ; self.currentTime = 0
            self.folderPath = control.infoLabel('Container.FolderPath')
            self.name = name ; self.year = year ; self.content = content
            self.file = self.name + '.strm'
            self.file = self.file.translate(None, '\/:*?"<>|').strip('.')
            self.imdb = 'tt' + imdb if imdb.isdigit() else imdb
            self.tvdb = tvdb if not tvdb == None else '0'
        except:
            pass

        try:
            if self.content == 'movie':
                self.title = re.compile('(.+?) [(]\d{4}[)]$').findall(self.name)[0]
            elif self.content == 'episode':
                self.tvshowtitle, self.season, self.episode = re.compile('(.+?) S(\d*)E(\d*)$').findall(self.name)[0]
                self.season, self.episode = '%01d' % int(self.season), '%01d' % int(self.episode)
                self.file2 = '%s (%s) S%02dE%02d.strm' % (self.tvshowtitle.translate(None, '\/:*?"<>|'), self.year, int(self.season), int(self.episode))
        except:
            pass

        try:
            if control.setting('resume_playback') == 'true':
                self.offset = bookmarks.getBookmark(self.name, self.imdb)
                if self.offset == '0': raise Exception()

                minutes, seconds = divmod(float(self.offset), 60) ; hours, minutes = divmod(minutes, 60)
                yes = control.yesnoDialog('%s %02d:%02d:%02d' % (control.lang(30461).encode('utf-8'), hours, minutes, seconds), '', '', self.name, control.lang(30463).encode('utf-8'), control.lang(30462).encode('utf-8'))

                if yes: self.offset = '0'
        except:
            pass

        try:
            if self.content == 'movie':
                control.window.setProperty('script.trakt.ids', json.dumps({'imdb': self.imdb}))
            elif self.content == 'episode':
                control.window.setProperty('script.trakt.ids', json.dumps({'tvdb': self.tvdb}))
        except:
            pass


    def getMeta(self, meta):
        try:
            meta = json.loads(meta)

            poster = meta['poster'] if 'poster' in meta else '0'
            thumb = meta['thumb'] if 'thumb' in meta else poster

            if poster == '0': poster = control.addonPoster()

            return (poster, thumb, meta)
        except:
            poster, thumb, meta = '', '', {'title': self.name}
            return (poster, thumb, meta)


    def getLibraryMeta(self):
        try:
            if self.content == 'movie':
                meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "originaltitle", "year", "genre", "studio", "country", "runtime", "rating", "votes", "mpaa", "director", "writer", "plot", "plotoutline", "tagline", "thumbnail", "file"]}, "id": 1}' % (self.year, str(int(self.year)+1), str(int(self.year)-1)))
                meta = unicode(meta, 'utf-8', errors='ignore')
                meta = json.loads(meta)['result']['movies']
                meta = [i for i in meta if i['file'].endswith(self.file)][0]

                for k, v in meta.iteritems():
                    if type(v) == list:
                        try: meta[k] = str(' / '.join([i.encode('utf-8') for i in v]))
                        except: meta[k] = ''
                    else:
                        try: meta[k] = str(v.encode('utf-8'))
                        except: meta[k] = str(v)

                self.DBID = meta['movieid'] ; poster = thumb = meta['thumbnail']

                meta = {'title': meta['title'], 'originaltitle': meta['originaltitle'], 'year': meta['year'], 'genre': meta['genre'], 'studio' : meta['studio'], 'country' : meta['country'], 'duration' : meta['runtime'], 'rating': meta['rating'], 'votes': meta['votes'], 'mpaa': meta['mpaa'], 'director': meta['director'], 'writer': meta['writer'], 'plot': meta['plot'], 'plotoutline': meta['plotoutline'], 'tagline': meta['tagline']}


            elif self.content == 'episode':
                meta = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "season", "episode", "showtitle", "firstaired", "runtime", "rating", "director", "writer", "plot", "thumbnail", "file"]}, "id": 1}' % (self.season, self.episode))
                meta = unicode(meta, 'utf-8', errors='ignore')
                meta = json.loads(meta)['result']['episodes']
                match = [i for i in meta if i['file'].endswith(self.file2)]
                match += [i for i in meta if i['file'].endswith(self.file)]
                meta = match[0]

                for k, v in meta.iteritems():
                    if type(v) == list:
                        try: meta[k] = str(' / '.join([i.encode('utf-8') for i in v]))
                        except: meta[k] = ''
                    else:
                        try: meta[k] = str(v.encode('utf-8'))
                        except: meta[k] = str(v)

                self.DBID = meta['episodeid'] ; thumb = meta['thumbnail'] ; showtitle = meta['showtitle']

                meta = {'title': meta['title'], 'season' : meta['season'], 'episode': meta['episode'], 'tvshowtitle': meta['showtitle'], 'premiered' : meta['firstaired'], 'duration' : meta['runtime'], 'rating': meta['rating'], 'director': meta['director'], 'writer': meta['writer'], 'plot': meta['plot']}

                poster = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"filter": {"field": "title", "operator": "is", "value": "%s"}, "properties": ["thumbnail"]}, "id": 1}' % showtitle)
                poster = unicode(poster, 'utf-8', errors='ignore')
                poster = json.loads(poster)['result']['tvshows'][0]['thumbnail']


            return (poster, thumb, meta)
        except:
            poster, thumb, meta = '', '', {'title': self.name}
            return (poster, thumb, meta)


    def setWatchedStatus(self):
        if self.content == 'movie':
            try:
                control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID))
                if not self.folderPath.startswith('plugin://'): control.refresh()
            except:
                pass

            try:
                from metahandler import metahandlers
                metaget = metahandlers.MetaData(preparezip=False)
                metaget.get_meta('movie', self.title ,year=self.year)
                metaget.change_watched(self.content, '', self.imdb, season='', episode='', year='', watched=7)
            except:
                pass

            try:
                if trakt.getTraktAddonMovieInfo() == False: trakt.markMovieAsWatched(self.imdb)
                trakt.syncMovies()
            except:
                pass


        elif self.content == 'episode':
            try:
                control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.DBID))
                if not self.folderPath.startswith('plugin://'): control.refresh()
            except:
                pass

            try:
                from metahandler import metahandlers
                metaget = metahandlers.MetaData(preparezip=False)
                metaget.get_meta('tvshow', self.tvshowtitle, imdb_id=self.imdb)
                metaget.get_episode_meta(self.tvshowtitle, self.imdb, self.season, self.episode)
                metaget.change_watched(self.content, '', self.imdb, season=self.season, episode=self.episode, year='', watched=7)
            except:
                pass

            try:
                if trakt.getTraktAddonEpisodeInfo() == False: trakt.markEpisodeAsWatched(self.tvdb, self.season, self.episode)
                trakt.syncTVShows()
            except:
                pass


    def onPlayBackStarted(self):
        for i in range(0, 200):
            if control.condVisibility('Window.IsActive(busydialog)') == 1: control.idle()
            else: break
            control.sleep(100)

        if control.setting('playback_info') == 'true':
            elapsedTime = '%s %s %s' % (control.lang(30464).encode('utf-8'), int((time.time() - self.loadingTime)), control.lang(30465).encode('utf-8'))
            control.infoDialog(elapsedTime, heading=self.name)

        try:
            if self.offset == '0': raise Exception()
            self.seekTime(float(self.offset))
        except:
            pass
        try:
            if not control.setting('subtitles') == 'true': raise Exception()
            try: subtitle = subtitles.get(self.name, self.imdb, self.season, self.episode)
            except: subtitle = subtitles.get(self.name, self.imdb, '', '')
        except:
            pass


    def onPlayBackStopped(self):
        try:
            bookmarks.deleteBookmark(self.name, self.imdb)
            ok = int(self.currentTime) > 180 and (self.currentTime / self.totalTime) <= .92
            if ok: bookmarks.addBookmark(self.currentTime, self.name, self.imdb)
        except:
            pass
        try:
            ok = self.currentTime / self.totalTime >= .9
            if ok: self.setWatchedStatus()
        except:
            pass


    def onPlayBackEnded(self):
        self.onPlayBackStopped()


