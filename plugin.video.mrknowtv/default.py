# -*- coding: utf-8 -*-

'''
    mrknowtv Add-on
    Copyright (C) 2016 mrknow

'''




import urlparse,sys
from resources.lib.lib import control

import xbmcaddon, os, xbmc
scriptID = 'plugin.video.mrknowtv'
ptv = xbmcaddon.Addon(scriptID)
datapath = xbmc.translatePath(ptv.getAddonInfo('profile'))

#BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "mylib" )
#sys.path.append( os.path.join( ptv.getAddonInfo('path'), "mylib" ) )

#import pydevd
#pydevd.settrace('localhost', port=34099, stdoutToServer=True, stderrToServer=True)


params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
#control.log("->----------                PARAMS: %s" % params)
#control.log("->----------                PARAMS2: %s" % sys.argv[2])
#control.log("->----------                PARAMS2: %s" % sys.argv[0])



try:
    action = params['action']
except:
    action = None
try:
    name = params['name']
except:
    name = None
try:
    title = params['title']
except:
    title = None
try:
    year = params['year']
except:
    year = None
try:
    imdb = params['imdb']
except:
    imdb = '0'
try:
    tmdb = params['tmdb']
except:
    tmdb = '0'
try:
    tvdb = params['tvdb']
except:
    tvdb = '0'
try:
    service = params['service']
except:
    service = '0'

try:
    id = params['id']
except:
    id = '0'
try:
    alter = params['genre']
except:
    pass
try:
    date = params['date']
except:
    date = None
try:
    url = params['url']
except:
    url = None
try:
    image = params['image']
except:
    image = None
try:
    meta = params['meta']
except:
    meta = None
try:
    query = params['query']
except:
    query = None
try:
    source = params['source']
except:
    source = None
try:
    content = params['content']
except:
    content = None
try:
    provider = params['provider']
except:
    provider = None



if action == None:
    from resources.lib.indexers import navigator
    navigator.navigator().root()


elif action == 'tv':
    from resources.lib.indexers import tv
    tv.tv().get(url)

elif action == 'movieNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().movies()

elif action == 'tvNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tvshows()

elif action == 'myNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().milenium()

elif action == 'downloadNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().downloads()

elif action == 'toolNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tools()

elif action == 'libtoolNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().library()

elif action == 'searchNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().search()

elif action == 'movies':
    from resources.lib.indexers import movies
    movies.movies().get(url)

elif action == 'movieWidget':
    from resources.lib.indexers import movies
    movies.movies().widget()

elif action == 'movieFavourites':
    from resources.lib.indexers import movies
    movies.movies().favourites()

elif action == 'movieSearch':
    from resources.lib.indexers import movies
    movies.movies().search(query)

elif action == 'movieGenres':
    from resources.lib.indexers import movies
    movies.movies().genres()

elif action == 'movieUserlists':
    from resources.lib.indexers import movies
    movies.movies().userlists()


elif action == 'tvFavourites':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().favourites()

elif action == 'tvSearch':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().search(query)

elif action == 'tvPerson':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().person(query)

elif action == 'tvGenres':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().genres()

elif action == 'tvNetworks':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().networks()

elif action == 'tvYears':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().years()

elif action == 'tvUserlists':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().userlists()


elif action == 'tvWidget':
    from resources.lib.indexers import episodes
    episodes.episodes().widget()


elif action == 'openSettings':
    from resources.lib.lib import control
    control.openSettings(query)

elif action == 'moviePlaycount':
    from resources.lib.libraries import playcount
    playcount.movies(title, year, imdb, query)

elif action == 'episodePlaycount':
    from resources.lib.libraries import playcount
    playcount.episodes(imdb, tvdb, season, episode, query)

elif action == 'tvPlaycount':
    from resources.lib.libraries import playcount
    playcount.tvshows(name, year, imdb, tvdb, season, query)

elif action == 'clearCache':
    from resources.lib.lib import cache
    cache.clear()

elif action == 'addFavourite':
    from resources.lib.libraries import favourites
    favourites.addFavourite(meta, content, query)

elif action == 'deleteFavourite':
    from resources.lib.libraries import favourites
    favourites.deleteFavourite(meta, content)

elif action == 'addView':
    from resources.lib.libraries import views
    views.addView(content)

elif action == 'movieToLibrary':
    from resources.lib.libraries import libtools
    libtools.libmovies().add(name, title, year, imdb, tmdb)

elif action == 'moviesToLibrary':
    from resources.lib.libraries import libtools
    libtools.libmovies().range(url)

elif action == 'tvshowToLibrary':
    from resources.lib.libraries import libtools
    libtools.libtvshows().add(tvshowtitle, year, imdb, tmdb, tvdb, service)

elif action == 'tvshowsToLibrary':
    from resources.lib.libraries import libtools
    libtools.libtvshows().range(url)

elif action == 'updateLibrary':
    from resources.lib.libraries import libtools
    libtools.libepisodes().update(query)

elif action == 'resolve':
    from resources.lib.sources import sources
    from resources.lib.libraries import control
    url = sources().sourcesResolve(url, provider)
    control.addItem(handle=int(sys.argv[1]), url=url, listitem=control.item(name))
    control.directory(int(sys.argv[1]))

elif action == 'download':
    from resources.lib.sources import sources
    from resources.lib.libraries import simpledownloader
    url = sources().sourcesResolve(url, provider)
    simpledownloader.download(name, image, url)

elif action == 'play':
    from resources.lib.sources import sources
    sources().play(name, title, service, meta, url)

elif action == 'sources':
    from resources.lib.sources import sources
    sources().addItem(name, title, year, imdb, tmdb, tvdb, service, season, episode, tvshowtitle, alter, date, meta)

elif action == 'playItem':
    from resources.lib.sources import sources
    sources().playItem(content, name, year, imdb, tvdb, source)

elif action == 'alterSources':
    from resources.lib.sources import sources
    sources().alterSources(url, meta)

elif action == 'clearSources':
    from resources.lib.sources import sources
    sources().clearSources()


