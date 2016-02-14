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


import os,sys,urlparse
import time


from resources.lib.libraries import control
from resources.lib.libraries import trakt_api2
from resources.lib.libraries import gui_utils



artPath = control.artPath()

addonFanart = control.addonFanart()

try: action = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))['action']
except: action = None

traktMode = False if control.setting('trakt_user') == '' else True

imdbMode = False if control.setting('imdb_user') == '' else True

sysaddon = sys.argv[0]


class navigator:

    def __init__(self):
        movie_library = os.path.join(control.transPath(control.setting('movie_library')),'')
        tv_library = os.path.join(control.transPath(control.setting('tv_library')),'')
        tv_downloads = os.path.join(control.transPath(control.setting('tv_downloads')),'')
        movie_downloads = os.path.join(control.transPath(control.setting('movie_downloads')),'')
        if not os.path.exists(movie_library):
            os.makedirs(movie_library)
        if not os.path.exists(tv_library):
            os.makedirs(tv_library)
        if not os.path.exists(tv_downloads):
            os.makedirs(tv_downloads)
        if not os.path.exists(movie_downloads):
            os.makedirs(movie_downloads)

        #if not control.TOKEN:
        #    last_reminder = control.setting('last_reminder')
        #    if last_reminder !='':
        #        last_reminder = int(last_reminder)
        #    else:
        #        last_reminder = 0
        #    print("--- TRAKT ---, last reminder",last_reminder)
        #    now = int(time.time())
        #    if last_reminder >= 0 and last_reminder < now - (24 * 60 * 60):
        #        gui_utils.get_pin()
        #else:
        #    profile = control.traktapi.get_user_profile()
        #    control.set_setting('trakt_user', '%s (%s)' % (profile['username'], profile['name']))

    def trakt_pin_auth(self):
        gui_utils.get_pin()

    def root(self):
        self.addDirectoryItem(30001, 'movieNavigator', 'movies.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30002, 'tvNavigator', 'tvshows.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30003, 'channels', 'channels.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30004, 'myNavigator', 'myspecto.jpg', 'DefaultVideoPlaylists.png')

        if not control.setting('movie_widget') == '0':
            self.addDirectoryItem(30005, 'movieWidget', 'moviesAdded.jpg', 'DefaultRecentlyAddedMovies.png')

        if (traktMode == True and not control.setting('tv_alt_widget') == '0') or (traktMode == False and not control.setting('tv_widget') == '0'):
            self.addDirectoryItem(30006, 'tvWidget', 'calendarsAdded.jpg', 'DefaultRecentlyAddedEpisodes.png')

        if not control.setting('calendar_widget') == '0':
            self.addDirectoryItem(30007, 'calendars', 'calendar.jpg', 'DefaultRecentlyAddedEpisodes.png')

        self.addDirectoryItem(30008, 'toolNavigator', 'tools.jpg', 'DefaultAddonProgram.png')

        self.addDirectoryItem(30009, 'searchNavigator', 'search.jpg', 'DefaultFolder.png')

        self.endDirectory()

        from resources.lib.libraries import cache
        from resources.lib.libraries import changelog
        cache.get(changelog.get, 600000000, control.addonInfo('version'), table='changelog')


    def movies(self):
        self.addDirectoryItem(30021, 'movieGenres', 'movieGenres.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30022, 'movieYears', 'movieYears.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30023, 'moviePersons', 'movies.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30024, 'movieCertificates', 'movieCertificates.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30025, 'movies&url=featured', 'movies.jpg', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30026, 'movies&url=trending', 'moviesTrending.jpg', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30027, 'movies&url=popular', 'moviesPopular.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30028, 'movies&url=views', 'moviesViews.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30029, 'movies&url=boxoffice', 'moviesBoxoffice.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30030, 'movies&url=oscars', 'moviesOscars.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30031, 'movies&url=theaters', 'moviesTheaters.jpg', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30032, 'movies&url=added', 'moviesAdded.jpg', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(30033, 'movieFavourites', 'movieFavourites.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30034, 'moviePerson', 'moviePerson.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30035, 'movieSearch', 'movieSearch.jpg', 'DefaultMovies.png')

        self.endDirectory()


    def tvshows(self):
        self.addDirectoryItem(30051, 'tvGenres', 'tvGenres.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30052, 'tvYears', 'tvshows.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30053, 'tvNetworks', 'tvshows.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30054, 'tvshows&url=trending', 'tvshowsTrending.jpg', 'DefaultRecentlyAddedEpisodes.png')
        self.addDirectoryItem(30055, 'tvshows&url=popular', 'tvshowsPopular.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30056, 'tvshows&url=airing', 'tvshows.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30057, 'tvshows&url=active', 'tvshowsActive.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30058, 'tvshows&url=premiere', 'tvshows.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30059, 'tvshows&url=rating', 'tvshowsRating.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30060, 'tvshows&url=views', 'tvshowsViews.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30061, 'calendars', 'calendar.jpg', 'DefaultRecentlyAddedEpisodes.png')
        self.addDirectoryItem(30062, 'calendar&url=added', 'calendarsAdded.jpg', 'DefaultRecentlyAddedEpisodes.png')
        self.addDirectoryItem(30063, 'episodeFavourites', 'tvFavourites.jpg', 'DefaultRecentlyAddedEpisodes.png')
        self.addDirectoryItem(30064, 'tvFavourites', 'tvFavourites.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30065, 'tvPerson', 'tvPerson.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30066, 'tvSearch', 'tvSearch.jpg', 'DefaultTVShows.png')

        self.endDirectory()


    def specto(self):
        if traktMode == True:
            self.addDirectoryItem(30081, 'movies&url=traktcollection', 'moviesTraktcollection.jpg', 'DefaultMovies.png', context=(30191, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(30082, 'movies&url=traktwatchlist', 'moviesTraktwatchlist.jpg', 'DefaultMovies.png', context=(30191, 'moviesToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(30083, 'movies&url=traktfeatured', 'movies.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30084, 'movies&url=traktratings', 'movies.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30085, 'tvshows&url=traktcollection', 'tvshowsTraktcollection.jpg', 'DefaultTVShows.png', context=(30191, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(30086, 'tvshows&url=traktwatchlist', 'tvshowsTraktwatchlist.jpg', 'DefaultTVShows.png', context=(30191, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(30087, 'tvshows&url=traktfeatured', 'tvshows.jpg', 'DefaultTVShows.png')
            self.addDirectoryItem(30088, 'tvshows&url=traktratings', 'tvshows.jpg', 'DefaultTVShows.png')
            self.addDirectoryItem(30089, 'calendar&url=progress', 'calendarsProgress.jpg', 'DefaultRecentlyAddedEpisodes.png')
            self.addDirectoryItem(30090, 'calendar&url=mycalendar', 'calendarsMycalendar.jpg', 'DefaultRecentlyAddedEpisodes.png')

        if imdbMode == True:
            self.addDirectoryItem(30091, 'movies&url=imdbwatchlist', 'moviesImdbwatchlist.jpg', 'DefaultMovies.png', context=(30191, 'moviesToLibrary&url=imdbwatchlist'))
            self.addDirectoryItem(30092, 'tvshows&url=imdbwatchlist', 'tvshowsImdbwatchlist.jpg', 'DefaultTVShows.png', context=(30191, 'tvshowsToLibrary&url=imdbwatchlist'))

        if traktMode == True or imdbMode == True:
            self.addDirectoryItem(30093, 'movieUserlists', 'movieUserlists.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30094, 'tvUserlists', 'tvUserlists.jpg', 'DefaultTVShows.png')

        self.addDirectoryItem(30095, 'movieFavourites', 'movieFavourites.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30096, 'episodeFavourites', 'tvFavourites.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30097, 'tvFavourites', 'tvFavourites.jpg', 'DefaultTVShows.png')

        movie_downloads = control.setting('movie_downloads')
        tv_downloads = control.setting('tv_downloads')
        if len(control.listDir(movie_downloads)[0]) > 0 or len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(30098, 'downloadNavigator', 'downloads.jpg', 'DefaultFolder.png')

        self.endDirectory()


    def downloads(self):
        movie_downloads = control.setting('movie_downloads')
        tv_downloads = control.setting('tv_downloads')

        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(30099, movie_downloads, 'movies.jpg', 'DefaultMovies.png', isAction=False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(30100, tv_downloads, 'tvshows.jpg', 'DefaultTVShows.png', isAction=False)

        self.endDirectory()


    def tools(self):
        self.addDirectoryItem(30111, 'openSettings&query=0.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30112, 'openSettings&query=6.1', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30113, 'openSettings&query=1.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30114, 'openSettings&query=9.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30115, 'openSettings&query=2.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30116, 'openSettings&query=3.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30117, 'openSettings&query=4.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30118, 'openSettings&query=5.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30119, 'clearSources', 'cache.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30120, 'clearCache', 'cache.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30122, 'openSettings&query=8.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30121, 'libtoolNavigator', 'tools.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30141, 'openSettings&query=10.0', 'tools.jpg', 'DefaultAddonProgram.png')

        self.endDirectory()


    def library(self):
        self.addDirectoryItem(30131, 'openSettings&query=7.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30132, 'updateLibrary&query=tool', 'update.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30133, control.setting('movie_library'), 'movies.jpg', 'DefaultMovies.png', isAction=False)
        self.addDirectoryItem(30134, control.setting('tv_library'), 'tvshows.jpg', 'DefaultTVShows.png', isAction=False)

        if traktMode == True:
            self.addDirectoryItem(30135, 'moviesToLibrary&url=traktcollection', 'moviesTraktcollection.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30136, 'moviesToLibrary&url=traktwatchlist', 'moviesTraktwatchlist.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30137, 'tvshowsToLibrary&url=traktcollection', 'tvshowsTraktcollection.jpg', 'DefaultTVShows.png')
            self.addDirectoryItem(30138, 'tvshowsToLibrary&url=traktwatchlist', 'tvshowsTraktwatchlist.jpg', 'DefaultTVShows.png')

        if imdbMode == True:
            self.addDirectoryItem(30139, 'moviesToLibrary&url=imdbwatchlist', 'moviesImdbwatchlist.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30140, 'tvshowsToLibrary&url=imdbwatchlist', 'tvshowsImdbwatchlist.jpg', 'DefaultTVShows.png')

        self.endDirectory()


    def search(self):
        self.addDirectoryItem(30151, 'movieSearch', 'movieSearch.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30152, 'tvSearch', 'tvSearch.jpg', 'DefaultTVShows.png')
        self.addDirectoryItem(30153, 'moviePerson', 'moviePerson.jpg', 'DefaultMovies.png')
        self.addDirectoryItem(30154, 'tvPerson', 'tvPerson.jpg', 'DefaultTVShows.png')

        self.endDirectory()


    def addDirectoryItem(self, name, query, thumb, icon, context=None, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        thumb = os.path.join(artPath, thumb) if not artPath == None else icon
        cm = []
        if not context == None: cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = control.item(label=name, iconImage=thumb, thumbnailImage=thumb)
        item.addContextMenuItems(cm, replaceItems=False)
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self, cacheToDisc=True):
        control.directory(int(sys.argv[1]), cacheToDisc=cacheToDisc)


