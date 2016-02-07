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


import sys,xbmc

from resources.lib.libraries import control
from resources.lib.libraries import trakt


def movies(title, year, imdb, watched):
    traktMode = False if trakt.getTraktCredentials() == False else True

    watched = int(watched)

    try:
        if traktMode == True: raise Exception()
        from metahandler import metahandlers
        metaget = metahandlers.MetaData(preparezip=False)
        metaget.get_meta('movie', title ,year=year)
        metaget.change_watched('movie', '', imdb, season='', episode='', year='', watched=watched)
    except:
        pass

    try:
        if traktMode == False: raise Exception()
        if watched == 7: trakt.markMovieAsWatched(imdb)
        else: trakt.markMovieAsNotWatched(imdb)
        trakt.syncMovies()
    except:
        pass

    control.refresh()


def episodes(imdb, tvdb, season, episode, watched):
    traktMode = False if trakt.getTraktCredentials() == False else True

    watched = int(watched)

    try:
        if traktMode == True: raise Exception()
        from metahandler import metahandlers
        metaget = metahandlers.MetaData(preparezip=False)
        metaget.get_meta('tvshow', '', imdb_id=imdb)
        metaget.get_episode_meta('', imdb, season, episode)
        metaget.change_watched('episode', '', imdb, season=season, episode=episode, year='', watched=watched)
    except:
        pass

    try:
        if traktMode == False: raise Exception()
        if watched == 7: trakt.markEpisodeAsWatched(tvdb, season, episode)
        else: trakt.markEpisodeAsNotWatched(tvdb, season, episode)
        trakt.syncTVShows()
    except:
        pass

    control.refresh()


def tvshows(tvshowtitle, year, imdb, tvdb, season, watched):
    traktMode = False if trakt.getTraktCredentials() == False else True

    watched = int(watched)


    try:
        if traktMode == True: raise Exception()

        from metahandler import metahandlers
        from resources.lib.indexers import episodes

        metaget = metahandlers.MetaData(preparezip=False)

        dialog = control.progressDialog
        dialog.create(control.addonInfo('name'), str(tvshowtitle))
        dialog.update(0, str(tvshowtitle), control.lang(30451).encode('utf-8') + '...')

        metaget.get_meta('tvshow', '', imdb_id=imdb)

        items = episodes.episodes().get(tvshowtitle, year, imdb, '0', tvdb, '0', idx=False)
        try: items = [i for i in items if int('%01d' % int(season)) == int('%01d' % int(i['season']))]
        except: pass
        items = [{'name': i['name'], 'season': int('%01d' % int(i['season'])), 'episode': int('%01d' % int(i['episode']))} for i in items]

        for i in range(len(items)):
            if xbmc.abortRequested == True: return sys.exit()
            if dialog.iscanceled(): return dialog.close()

            dialog.update(int((100 / float(len(items))) * i), str(tvshowtitle), str(items[i]['name']))

            season, episode = items[i]['season'], items[i]['episode']
            metaget.get_episode_meta('', imdb, season, episode)
            metaget.change_watched('episode', '', imdb, season=season, episode=episode, year='', watched=watched)

        try: dialog.close()
        except: pass
    except:
        try: dialog.close()
        except: pass

    try:
        if traktMode == False: raise Exception()
        if watched == 7: trakt.markTVShowAsWatched(tvdb)
        else: trakt.markTVShowAsNotWatched(tvdb)
        trakt.syncTVShows()
    except:
        pass

    control.refresh()


