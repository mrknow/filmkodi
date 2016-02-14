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


import json,urlparse,base64

from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import client

mytraktkey = 'd4161a7a106424551add171e5470112e4afdaf2438e6ef2fe0548edc75924868'

def getTrakt(url, post=None):
    try:
        trakt_base = 'http://api-v2launch.trakt.tv'
        #headers = {'Content-Type': 'application/json', 'trakt-api-key': base64.urlsafe_b64decode('ZWI0MWU5NTI0M2Q4Yzk1MTUyZWQ3MmExZmMwMzk0YzkzY2I3ODVjYjMzYWVkNjA5ZmRkZTFhMDc0NTQ1ODRiNA=='), 'trakt-api-version': '2'}
        headers = {'Content-Type': 'application/json', 'trakt-api-key': 'd4161a7a106424551add171e5470112e4afdaf2438e6ef2fe0548edc75924868', 'trakt-api-version': '2'}
        user, password = getTraktCredentials()
        token = cache.get(authTrakt, 24, urlparse.urljoin(trakt_base, '/auth/login'), json.dumps({'login': user, 'password': password}), headers, table='rel_trakt')
        headers.update({'trakt-user-login': user, 'trakt-user-token': token})
    except:
        pass
    try:
        if not post == None: post = json.dumps(post)
        result = client.request(urlparse.urljoin(trakt_base, url), post=post, headers=headers)
        return result
    except:
        pass


def authTrakt(url, post, headers):
    try:
        result = client.request(url, post=post, headers=headers)
        return json.loads(result)['token']
    except:
        pass


def getTraktCredentials():
    user = control.setting('trakt_user') 
    password = control.setting('trakt_password')
    if (user == '' or password == ''): return False
    return (user, password)


def getTraktAddonMovieInfo():
    try: scrobble = control.addon('script.trakt').getSetting('scrobble_movie')
    except: scrobble = ''
    try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
    except: ExcludeHTTP = ''
    try: authorization = control.addon('script.trakt').getSetting('authorization')
    except: authorization = ''
    if scrobble == 'true' and ExcludeHTTP == 'false' and not authorization == '': return True
    else: return False


def getTraktAddonEpisodeInfo():
    try: scrobble = control.addon('script.trakt').getSetting('scrobble_episode')
    except: scrobble = ''
    try: ExcludeHTTP = control.addon('script.trakt').getSetting('ExcludeHTTP')
    except: ExcludeHTTP = ''
    try: authorization = control.addon('script.trakt').getSetting('authorization')
    except: authorization = ''
    if scrobble == 'true' and ExcludeHTTP == 'false' and not authorization == '': return True
    else: return False


def manager(name, imdb, tvdb, content):
    try:
        user, password = getTraktCredentials()
        post = {"movies": [{"ids": {"imdb": imdb}}]} if content == 'movie' else {"shows": [{"ids": {"tvdb": tvdb}}]}

        items = [(control.lang(30472).encode('utf-8'), '/sync/collection')]
        items += [(control.lang(30473).encode('utf-8'), '/sync/collection/remove')]
        items += [(control.lang(30474).encode('utf-8'), '/sync/watchlist')]
        items += [(control.lang(30475).encode('utf-8'), '/sync/watchlist/remove')]
        items += [(control.lang(30476).encode('utf-8'), '/users/%s/lists/%s/items' % (user, '%s'))]

        result = getTrakt('/users/%s/lists' % user)
        result = json.loads(result)
        lists = [(i['name'], i['ids']['slug']) for i in result]
        lists = [lists[i//2] for i in range(len(lists)*2)]
        for i in range(0, len(lists), 2):
            lists[i] = ((control.lang(30477) + ' ' + lists[i][0]).encode('utf-8'), '/users/%s/lists/%s/items' % (user, lists[i][1]))
        for i in range(1, len(lists), 2):
            lists[i] = ((control.lang(30478) + ' ' + lists[i][0]).encode('utf-8'), '/users/%s/lists/%s/items/remove' % (user, lists[i][1]))
        items += lists

        select = control.selectDialog([i[0] for i in items], control.lang(30471).encode('utf-8'))

        if select == -1:
            return
        elif select == 4:
            t = control.lang(30476).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            new = k.getText() if k.isConfirmed() else None
            if (new == None or new == ''): return
            url = '/users/%s/lists' % user
            result = getTrakt('/users/%s/lists' % user, post={"name": new, "privacy": "private"})

            try: slug = json.loads(result)['ids']['slug']
            except: return control.infoDialog('Failed', heading=name)
            result = getTrakt(items[select][1] % slug, post=post)
        else:
            result = getTrakt(items[select][1], post=post)

        info = 'Successful' if not result == None else 'Failed'
        control.infoDialog(info, heading=name)
    except:
        return


def syncMovies(timeout=0):
    try:
        user, password = getTraktCredentials()
        return cache.get(getTrakt, timeout, '/users/%s/watched/movies' % user, table='rel_trakt')
    except:
        pass


def syncTVShows(timeout=0):
    try:
        user, password = getTraktCredentials()
        return cache.get(getTrakt, timeout, '/users/%s/watched/shows?extended=full' % user, table='rel_trakt')
    except:
        pass


def markMovieAsWatched(imdb):
    if not imdb.startswith('tt'): imdb = 'tt' + imdb
    return getTrakt('/sync/history', {"movies": [{"ids": {"imdb": imdb}}]})


def markMovieAsNotWatched(imdb):
    if not imdb.startswith('tt'): imdb = 'tt' + imdb
    return getTrakt('/sync/history/remove', {"movies": [{"ids": {"imdb": imdb}}]})


def markTVShowAsWatched(tvdb):
    return getTrakt('/sync/history', {"shows": [{"ids": {"tvdb": tvdb}}]})


def markTVShowAsNotWatched(tvdb):
    return getTrakt('/sync/history/remove', {"shows": [{"ids": {"tvdb": tvdb}}]})


def markEpisodeAsWatched(tvdb, season, episode):
    season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
    return getTrakt('/sync/history', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})


def markEpisodeAsNotWatched(tvdb, season, episode):
    season, episode = int('%01d' % int(season)), int('%01d' % int(episode))
    return getTrakt('/sync/history/remove', {"shows": [{"seasons": [{"episodes": [{"number": episode}], "number": season}], "ids": {"tvdb": tvdb}}]})


def getMovieSummary(id):
    return getTrakt('/movies/%s' % id)


def getTVShowSummary(id):
    return getTrakt('/shows/%s' % id)


