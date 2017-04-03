# -*- coding: utf-8 -*-
#

import xbmc,sys
import xbmcaddon
import xbmcgui
import time, socket
import math
import urllib2
import base64

from utilities import Debug, notification, getSetting, getSettingAsBool, getSettingAsInt, getString, setSetting
from urllib2 import Request, urlopen, HTTPError, URLError
from httplib import HTTPException, BadStatusLine

try:
    import simplejson as json
except ImportError:
    import json

try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

# read settings
scriptID = sys.modules[ "__main__" ].scriptID

class XbmcFilmsError(Exception):
    def __init__(self, value, code=None):
        self.value = value
        if code:
            self.code = code
    def __str__(self):
        return repr(self.value)

class XbmcFilmsAuthProblem(XbmcFilmsError): pass
class XbmcFilmsServerBusy(XbmcFilmsError): pass
class XbmcFilmsUnknownError(XbmcFilmsError): pass
class XbmcFilmsNotFoundError(XbmcFilmsError): pass
class XbmcFilmsNetworkError(XbmcFilmsError):
    def __init__(self, value, timeout):
        super(XbmcFilmsNetworkError, self).__init__(value)
        self.timeout = timeout

class XbmcFilmAPI(object):

    __apikey = "a22023e223248f2390873"
    #__baseURL = "http://0.0.0.0:5000/api2"
    __baseURL = "http://api.xbmcfilm.com/api2"
    __username = ""
    __password = ""

    def __init__(self, loadSettings=False):
        Debug("[XbmcFilm] Initializing.")

        self.__username = getSetting('xbmcfilm_user')
        self.__password = sha1(getSetting('xbmcfilm_pass')).hexdigest()

        self.settings = None
        if loadSettings and self.testAccount():
            self.getAccountSettings()

    def __getData(self, url, args, timeout=60):
        data = None
        try:
            Debug("[XbmcFilm] __getData(): urllib2.Request(%s)" % url)

            if args == None:
                req = Request(url)
            else:
                req = Request(url, args)

            Debug("[XbmcFilm] __getData(): urllib2.urlopen()")
            t1 = time.time()
            req.add_header('Content-Type', 'application/json')
            response = urlopen(req, timeout=timeout)
            t2 = time.time()

            Debug("[XbmcFilm] __getData(): response.read()")
            data = response.read()
            Debug("[XbmcFilm] __getData(): Response Code: %i" % response.getcode())
            Debug("[XbmcFilm] __getData(): Response Time: %0.2f ms" % ((t2 - t1) * 1000))
            Debug("[XbmcFilm] __getData(): Response Headers: %s" % str(response.info().dict))

        except BadStatusLine, e:
            raise XbmcFilmsUnknownError("BadStatusLine: '%s' from URL: '%s'" % (e.line, url))
        except IOError, e:
            if hasattr(e, 'code'): # error 401 or 503, possibly others
                # read the error document, strip newlines, this will make an html page 1 line
                error_data = e.read().replace("\n", "").replace("\r", "")

                if e.code == 401: # authentication problem
                    raise XbmcFilmsAuthProblem(error_data)
                elif e.code == 503: # server busy problem
                    raise XbmcFilmsServerBusy(error_data)
                else:
                    try:
                        _data = json.loads(error_data)
                        if 'status' in _data:
                            data = error_data
                    except ValueError:
                        raise XbmcFilmsUnknownError(error_data, e.code)

            elif hasattr(e, 'reason'): # usually a read timeout, or unable to reach host
                raise XbmcFilmsNetworkError(str(e.reason), isinstance(e.reason, socket.timeout))

            else:
                raise XbmcFilmsUnknownError(e.message)

        return data
    
    # make a JSON api request to xbmcfilm
    # method: http method (GET or POST)
    # req: REST request (ie '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
    # args: arguments to be passed by POST JSON (only applicable to POST requests), default:{}
    # returnStatus: when unset or set to false the function returns None upon error and shows a notification,
    #    when set to true the function returns the status and errors in ['error'] as given to it and doesn't show the notification,
    #    use to customise error notifications
    # silent: default is True, when true it disable any error notifications (but not debug messages)
    # passVersions: default is False, when true it passes extra version information to xbmcfilm to help debug problems
    # hideResponse: used to not output the json response to the log
    def XbmcFilmsRequest(self, method, url, args=None, returnStatus=False, returnOnFailure=False, silent=True, passVersions=False, hideResponse=False):
        raw = None
        data = None
        jdata = {}
        retries = getSettingAsInt('retries')

        if args is None:
            args = {}

        if not (method == 'POST' or method == 'GET'):
            Debug("[XbmcFilm] xbmcfilmRequest(): Unknown method '%s'." % method)
            return None
        
        if method == 'POST':
            # debug log before username and sha1hash are injected
            Debug("[XbmcFilm] xbmcfilmRequest(): Request data: '%s'." % str(json.dumps(args)))
            
            # inject username/pass into json data
            args['username'] = self.__username
            args['password'] = self.__password
            
            # check if plugin version needs to be passed
            if passVersions:
                args['plugin_version'] = scriptID
                args['media_center_version'] = xbmc.getInfoLabel('system.buildversion')
                args['media_center_date'] = xbmc.getInfoLabel('system.builddate')
            
            # convert to json data
            jdata = json.dumps(args)

        Debug("[XbmcFilm] xbmcfilmRequest(): Starting retry loop, maximum %i retries." % retries)
        
        # start retry loop
        for i in range(retries):    
            Debug("[XbmcFilm] xbmcfilmRequest(): (%i) Request URL '%s'" % (i, url))

            # check if we are closing
            if xbmc.abortRequested:
                Debug("[XbmcFilm] xbmcfilmRequest(): (%i) xbmc.abortRequested" % i)
                break

            try:
                # get data from xbmcfilm.tv
                raw = self.__getData(url, jdata)                
            except XbmcFilmsError, e:
                if isinstance(e, XbmcFilmsServerBusy):
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) Server Busy (%s)" % (i, e.value))
                    xbmc.sleep(5000)
                elif isinstance(e, XbmcFilmsAuthProblem):
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) Authentication Failure (%s)" % (i, e.value))
                    setSetting('account_valid', False)
                    notification('xbmcfilm', getString(1110))
                    return
                elif isinstance(e, XbmcFilmsNetworkError):
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) Network error: %s" % (i, e.value))
                    if e.timeout:
                        notification('xbmcfilm', getString(1108) + " (timeout)") # can't connect to xbmcfilm
                    xbmc.sleep(5000)
                elif isinstance(e, XbmcFilmsUnknownError):
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) Other problem (%s)" % (i, e.value))
                else:
                    pass

                xbmc.sleep(1000)
                continue

            # check if we are closing
            if xbmc.abortRequested:
                Debug("[XbmcFilm] xbmcfilmRequest(): (%i) xbmc.abortRequested" % i)
                break

            # check that returned data is not empty
            if not raw:
                Debug("[XbmcFilm] xbmcfilmRequest(): (%i) JSON Response empty" % i)
                xbmc.sleep(1000)
                continue

            try:
                # get json formatted data    
                data = json.loads(raw)
                if hideResponse:
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) JSON response recieved, response not logged" % i)
                else:
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) JSON response: '%s'" % (i, str(data)))
            except ValueError:
                # malformed json response
                Debug("[XbmcFilm] xbmcfilmRequest(): (%i) Bad JSON response: '%s'" % (i, raw))
                if not silent:
                    notification('xbmcfilm', getString(1109) + ": Bad response from xbmcfilm") # Error
                
            # check for the status variable in JSON data
            if data and 'status' in data:
                if data['status'] == 'success':
                    break
                elif returnOnFailure and data['status'] == 'failure':
                    Debug("[XbmcFilm] xbmcfilmRequest(): Return on error set, breaking retry.")
                    break
                elif 'error' in data and data['status'] == 'failure':
                    Debug("[XbmcFilm] xbmcfilmRequest(): (%i) JSON Error '%s' -> '%s'" % (i, data['status'], data['error']))
                    xbmc.sleep(1000)
                    continue
                else:
                    pass

            # check to see if we have data, an empty array is still valid data, so check for None only
            if not data is None:
                Debug("[XbmcFilm] xbmcfilmRequest(): Have JSON data, breaking retry.")
                break

            xbmc.sleep(500)
        
        # handle scenario where all retries fail
        if data is None:
            Debug("[XbmcFilm] xbmcfilmRequest(): JSON Request failed, data is still empty after retries.")
            return None
        
        if 'status' in data:
            if data['status'] == 'failure':
                Debug("[XbmcFilm] xbmcfilmRequest(): Error: %s" % str(data['error']))
                if returnStatus or returnOnFailure:
                    return data
                if not silent:
                    notification('xbmcfilm', getString(1109) + ": " + str(data['error'])) # Error
                return None
            elif data['status'] == 'success':
                Debug("[XbmcFilm] xbmcfilmRequest(): JSON request was successful.")

        return data

    # helper for onSettingsChanged
    def updateSettings(self):
    
        _username = getSetting('username')
        _password = sha1(getSetting('password')).hexdigest()
        
        if not ((self.__username == _username) and (self.__password == _password)):
            self.__username = _username
            self.__password = _password
            self.testAccount(force=True)

    # http://api.xbmcfilm.tv/account/test/<apikey>
    # returns: {"status": "success","message": "all good!"}
    def testAccount(self, force=False):
        
        if self.__username == "":
            notification('xbmcfilm', getString(1106)) # please enter your Username and Password in settings
            setSetting('account_valid', False)
            return False
        elif self.__password == "":
            notification("xbmcfilm", getString(1107)) # please enter your Password in settings
            setSetting('account_valid', False)
            return False

        if not getSettingAsBool('account_valid') or force:
            Debug("[XbmcFilm] Testing account '%s'." % self.__username)

            url = "%s/account/test/%s" % (self.__baseURL, self.__apikey)
            Debug("[XbmcFilm] testAccount(url: %s)" % url)
            
            args = json.dumps({'username': self.__username, 'password': self.__password})
            response = None
            
            try:
                # get data from xbmcfilm.tv
                response = self.__getData(url, args)
            except XbmcFilmsError, e:
                if isinstance(e, XbmcFilmsError):
                    Debug("[XbmcFilm] testAccount(): Account '%s' failed authentication. (%s)" % (self.__username, e.value))
                elif isinstance(e, XbmcFilmsServerBusy):
                    Debug("[XbmcFilm] testAccount(): Server Busy (%s)" % e.value)
                elif isinstance(e, XbmcFilmsNetworkError):
                    Debug("[XbmcFilm] testAccount(): Network error: %s" % e.value)
                elif isinstance(e, XbmcFilmsUnknownError):
                    Debug("[XbmcFilm] testAccount(): Other problem (%s)" % e.value)
                else:
                    pass
            
            if response:
                data = None
                try:
                    data = json.loads(response)
                except ValueError:
                    pass

                if 'status' in data:
                    if data['status'] == 'success':
                        setSetting('account_valid', True)
                        Debug("[XbmcFilm] testAccount(): Account '%s' is valid." % self.__username)
                        return True

        else:
            return True

        notification('xbmcfilm', getString(1110)) # please enter your Password in settings
        setSetting('account_valid', False)
        return False

    # url: http://api.xbmcfilm.tv/account/settings/<apikey>
    # returns: all settings for authenticated user
    def getAccountSettings(self, force):
        _interval = (60 * 60 * 24 * 7) - (60 * 60) # one week less one hour

        _next = getSettingAsInt('xbmcfilm_settings_last') + _interval
        stale = force

        if force:
            Debug("[XbmcFilm] Forcing a reload of settings from xbmcfilm.tv.")

        if not stale and time.time() >= _next:
            Debug("[XbmcFilm] xbmcfilm.tv account settings are stale, reloading.")
            stale = True

        if stale:
            if self.testAccount():
                Debug("[XbmcFilm] Getting account settings for '%s'." % self.__username)
                url = "%s/account/settings/%s" % (self.__baseURL, self.__apikey)
                Debug("[XbmcFilm] getAccountSettings(url: %s)" % url)
                response = self.xbmcfilmRequest('POST', url, hideResponse=True)
                if response and 'status' in response:
                    if response['status'] == 'success':
                        del response['status']
                        setSetting('xbmcfilm_settings', json.dumps(response))
                        setSetting('xbmcfilm_settings_last', int(time.time()))
                        self.settings = response

        else:
            Debug("[XbmcFilm] Loaded cached account settings for '%s'." % self.__username)
            s = getSetting('xbmcfilm_settings')
            self.settings = json.loads(s)

    # helper to get rating mode, returns the setting from xbmcfilm.tv, or 'advanced' if there were problems getting them
    def getRatingMode(self):
        if not self.settings:
            self.getAccountSettings()
        rating_mode = "advanced"
        if self.settings and 'viewing' in self.settings:
            rating_mode = self.settings['viewing']['ratings']['mode']
        return rating_mode

        

    def watching(self, type, data):
        if self.testAccount():
            url = "%s/%s/watching/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] watching(url: %s, data: %s)" % (url, str(data)))
            if getSettingAsBool('simulate_scrobbling'):
                return {'status': 'success'}
            else:
                return self.xbmcfilmRequest('POST', url, data, passVersions=True)
    
    def watchingEpisode(self, info, duration, percent):
        data = {'tvdb_id': info['tvdb_id'], 'title': info['showtitle'], 'year': info['year'], 'season': info['season'], 'episode': info['episode'], 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        if 'uniqueid' in info:
            data['episode_tvdb_id'] = info['uniqueid']['unknown']
        return self.watching('show', data)
    def watchingMovie(self, info, duration, percent):
        data = {'imdb_id': info['imdbnumber'], 'title': info['title'], 'year': info['year'], 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        return self.watching('movie', data)

    # url: http://api.xbmcfilm.tv/<show|movie>/scrobble/<apikey>
    # returns: {"status": "success","message": "scrobbled The Walking Dead 1x01"}
    def scrobble(self, type, data):
        if self.testAccount():
            url = "%s/%s/scrobble/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] scrobble(url: %s, data: %s)" % (url, str(data)))
            if getSettingAsBool('simulate_scrobbling'):
                return {'status': 'success'}
            else:
                return self.xbmcfilmRequest('POST', url, data, returnOnFailure=True, passVersions=True)

    def scrobbleEpisode(self, info, duration, percent):
        data = {'tvdb_id': info['tvdb_id'], 'title': info['showtitle'], 'year': info['year'], 'season': info['season'], 'episode': info['episode'], 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        if 'uniqueid' in info:
            data['episode_tvdb_id'] = info['uniqueid']['unknown']
        return self.scrobble('show', data)
    def scrobbleMovie(self, info, duration, percent):
        data = {'imdb_id': info['imdbnumber'], 'title': info['title'], 'year': info['year'], 'duration': math.ceil(duration), 'progress': math.ceil(percent)}
        return self.scrobble('movie', data)

    # url: http://api.xbmcfilm.tv/<show|movie>/cancelwatching/<apikey>
    # returns: {"status":"success","message":"cancelled watching"}
    def cancelWatching(self, type):
        if self.testAccount():
            url = "%s/%s/cancelwatching/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] cancelWatching(url: %s)" % url)
            if getSettingAsBool('simulate_scrobbling'):
                return {'status': 'success'}
            else:
                return self.xbmcfilmRequest('POST', url)
        
    def cancelWatchingEpisode(self):
        return self.cancelWatching('show')
    def cancelWatchingMovie(self):
        return self.cancelWatching('movie')

    # url: http://api.xbmcfilm.tv/user/library/<shows|movies>/collection.json/<apikey>/<username>/min
    # response: [{"title":"Archer (2009)","year":2009,"imdb_id":"tt1486217","tvdb_id":110381,"seasons":[{"season":2,"episodes":[1,2,3,4,5]},{"season":1,"episodes":[1,2,3,4,5,6,7,8,9,10]}]}]
    # note: if user has nothing in collection, response is then []
    def getLibrary(self, type):
        if self.testAccount():
            url = "%s/user/library/%s/collection.json/%s/%s/min" % (self.__baseURL, type, self.__apikey, self.__username)
            Debug("[XbmcFilm] getLibrary(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)

    def getShowLibrary(self):
        return self.getLibrary('shows')
    def getMovieLibrary(self):
        return self.getLibrary('movies')

    # url: http://api.xbmcfilm.tv/user/library/<shows|movies>/watched.json/<apikey>/<username>/min
    # returns: [{"title":"Archer (2009)","year":2009,"imdb_id":"tt1486217","tvdb_id":110381,"seasons":[{"season":2,"episodes":[1,2,3,4,5]},{"season":1,"episodes":[1,2,3,4,5,6,7,8,9,10]}]}]
    # note: if nothing watched in collection, returns []
    def getWatchedLibrary(self, type):
        if self.testAccount():
            url = "%s/user/library/%s/watched.json/%s/%s/min" % (self.__baseURL, type, self.__apikey, self.__username)
            Debug("[XbmcFilm] getWatchedLibrary(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)

    def getWatchedEpisodeLibrary(self,):
        return self.getWatchedLibrary('shows')
    def getWatchedMovieLibrary(self):
        return self.getWatchedLibrary('movies')

    # url: http://api.xbmcfilm.tv/<show|show/episode|movie>/library/<apikey>
    # returns: {u'status': u'success', u'message': u'27 episodes added to your library'}
    def addToLibrary(self, type, data):
        if self.testAccount():
            url = "%s/%s/library/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] addToLibrary(url: %s, data: %s)" % (url, str(data)))
            return self.xbmcfilmRequest('POST', url, data)

    def addEpisode(self, data):
        return self.addToLibrary('show/episode', data)
    def addShow(self, data):
        return self.addToLibrary('show', data)
    def addMovie(self, data):
        return self.addToLibrary('movie', data)

    # url: http://api.xbmcfilm.tv/<show|show/episode|movie>/unlibrary/<apikey>
    # returns:
    def removeFromLibrary(self, type, data):
        if self.testAccount():
            url = "%s/%s/unlibrary/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] removeFromLibrary(url: %s, data: %s)" % (url, str(data)))
            return self.xbmcfilmRequest('POST', url, data)

    def removeEpisode(self, data):
        return self.removeFromLibrary('show/episode', data)
    def removeShow(self, data):
        return self.removeFromLibrary('show', data)
    def removeMovie(self, data):
        return self.removeFromLibrary('movie', data)

    # url: http://api.xbmcfilm.tv/<show|show/episode|movie>/seen/<apikey>
    # returns: {u'status': u'success', u'message': u'2 episodes marked as seen'}
    def updateSeenInLibrary(self, type, data):
        if self.testAccount():
            url = "%s/%s/seen/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] updateSeenInLibrary(url: %s, data: %s)" % (url, str(data)))
            return self.xbmcfilmRequest('POST', url, data)

    def updateSeenEpisode(self, data):
        return self.updateSeenInLibrary('show/episode', data)
    def updateSeenShow(self, data):
        return self.updateSeenInLibrary('show', data)
    def updateSeenMovie(self, data):
        return self.updateSeenInLibrary('movie', data)

    # url: http://api.xbmcfilm.tv/<show|show/episode|movie>/summary.format/apikey/title[/season/episode]
    # returns: returns information for a movie, show or episode
    def getSummary(self, type, data):
        if self.testAccount():
            url = "%s/%s/summary.json/%s/%s" % (self.__baseURL, type, self.__apikey, data)
            Debug("[XbmcFilm] getSummary(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)

    def getShowSummary(self, id, extended=False):
        data = str(id)
        if extended:
            data = "%s/extended" % data
        return self.getSummary('show', data)
    def getEpisodeSummary(self, id, season, episode):
        data = "%s/%s/%s" % (id, season, episode)
        return self.getSummary('show/episode', data)
    def getMovieSummary(self, id):
        data = str(id)
        return self.getSummary('movie', data)

    # url: http://api.xbmcfilm.tv/show/season.format/apikey/title/season
    # returns: returns detailed episode info for a specific season of a show.
    def getSeasonInfo(self, id, season):
        if self.testAccount():
            url = "%s/show/season.json/%s/%s/%d" % (self.__baseURL, self.__apikey, id, season)
            Debug("[XbmcFilm] getSeasonInfo(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)
    
    # url: http://api.xbmcfilm.tv/rate/<show|episode|movie>/apikey
    # returns: {"status":"success","message":"rated Portlandia 1x01","type":"episode","rating":"love","ratings":{"percentage":100,"votes":2,"loved":2,"hated":0},"facebook":true,"twitter":true,"tumblr":false}
    def rate(self, type, data):
        if self.testAccount():
            url = "%s/rate/%s/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] rate(url: %s, data: %s)" % (url, str(data)))
            return self.xbmcfilmRequest('POST', url, data, passVersions=True)

    def rateShow(self, data):
        return self.rate('show', data)
    def rateEpisode(self, data):
        return self.rate('episode', data)
    def rateMovie(self, data):
        return self.rate('movie', data)

    # url: http://api.xbmcfilm.tv/user/lists.json/apikey/<username>
    # returns: Returns all custom lists for a user.
    def getUserLists(self):
        if self.testAccount():
            url = "%s/user/lists.json/%s/%s" % (self.__baseURL, self.__apikey, self.__username)
            Debug("[XbmcFilm] getUserLists(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)

    # url: http://api.xbmcfilm.tv/user/list.json/apikey/<username>/<slug>
    # returns: Returns list details and all items it contains.
    def getUserList(self, data):
        if self.testAccount():
            url = "%s/user/list.json/%s/%s/%s" % (self.__baseURL, self.__apikey, self.__username, data)
            Debug("[XbmcFilm] getUserList(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url, passVersions=True)

    # url: http://api.xbmcfilm.tv/lists/<add|delete|items/add|items/delete>/apikey
    # returns: {"status": "success","message": ... }
    # note: return data varies based on method, but all include status/message
    def userList(self, method, data):
        if self.testAccount():
            url = "%s/lists/%s/%s" % (self.__baseURL, method, self.__apikey)
            Debug("[XbmcFilm] userList(url: %s, data: %s)" % (url, str(data)))
            return self.xbmcfilmRequest('POST', url, data, passVersions=True)
    
    def userListAdd(self, list_name, privacy, description=None, allow_shouts=False, show_numbers=False):
        data = {'name': list_name, 'show_numbers': show_numbers, 'allow_shouts': allow_shouts, 'privacy': privacy}
        if description:
            data['description'] = description
        return self.userList('add', data)
    def userListDelete(self, slug_name):
        data = {'slug': slug_name}
        return self.userList('delete', data)
    def userListItemAdd(self, data):
        return self.userList('items/add', data)
    def userListItemDelete(self, data):
        return self.userList('items/delete', data)
    def userListUpdate(self, data):
        return self.userList('update', data)

    # url: http://api.xbmcfilm.tv/user/watchlist/<movies|shows>.json/<apikey>/<username>
    # returns: [{"title":"GasLand","year":2010,"released":1264320000,"url":"http://xbmcfilm.tv/movie/gasland-2010","runtime":107,"tagline":"Can you light your water on fire? ","overview":"It is happening all across America-rural landowners wake up one day to find a lucrative offer from an energy company wanting to lease their property. Reason? The company hopes to tap into a reservoir dubbed the \"Saudi Arabia of natural gas.\" Halliburton developed a way to get the gas out of the ground-a hydraulic drilling process called \"fracking\"-and suddenly America finds itself on the precipice of becoming an energy superpower.","certification":"","imdb_id":"tt1558250","tmdb_id":"40663","inserted":1301130302,"images":{"poster":"http://xbmcfilm.us/images/posters_movies/1683.jpg","fanart":"http://xbmcfilm.us/images/fanart_movies/1683.jpg"},"genres":["Action","Comedy"]},{"title":"The King's Speech","year":2010,"released":1291968000,"url":"http://xbmcfilm.tv/movie/the-kings-speech-2010","runtime":118,"tagline":"God save the king.","overview":"Tells the story of the man who became King George VI, the father of Queen Elizabeth II. After his brother abdicates, George ('Bertie') reluctantly assumes the throne. Plagued by a dreaded stutter and considered unfit to be king, Bertie engages the help of an unorthodox speech therapist named Lionel Logue. Through a set of unexpected techniques, and as a result of an unlikely friendship, Bertie is able to find his voice and boldly lead the country into war.","certification":"R","imdb_id":"tt1504320","tmdb_id":"45269","inserted":1301130174,"images":{"poster":"http://xbmcfilm.us/images/posters_movies/8096.jpg","fanart":"http://xbmcfilm.us/images/fanart_movies/8096.jpg"},"genres":["Action","Comedy"]}]
    # note: if nothing in list, returns []
    def getWatchlist(self, type):
        if self.testAccount():
            url = "%s/user/watchlist/%s.json/%s/%s" % (self.__baseURL, type, self.__apikey, self.__username)
            Debug("[XbmcFilm] getWatchlist(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)

    def getWatchlistShows(self):
        return self.getWatchlist('shows')
    def getWatchlistMovies(self):
        return self.getWatchlist('movies')

    # url: http://api.xbmcfilm.tv/<movie|show>/watchlist/<apikey>
    # returns: 
    def watchlistAddItems(self, type, data):
        if self.testAccount():
            url = "%s/%s/watchlist/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] watchlistAddItem(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url, data, passVersions=True)

    def watchlistAddShows(self, data):
        return self.watchlistAddItems('show', data)
    def watchlistAddMovies(self, data):
        return self.watchlistAddItems('movie', data)

    # url: http://api.xbmcfilm.tv/<movie|show>/unwatchlist/<apikey>
    # returns: 
    def watchlistRemoveItems(self, type, data):
        if self.testAccount():
            url = "%s/%s/unwatchlist/%s" % (self.__baseURL, type, self.__apikey)
            Debug("[XbmcFilm] watchlistRemoveItems(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url, data, passVersions=True)

    def watchlistRemoveShows(self, data):
        return self.watchlistRemoveItems('show', data)
    def watchlistRemoveMovies(self, data):
        return self.watchlistRemoveItems('movie', data)

    # url: http://api.xbmcfilm.tv/user/ratings/<movies|shows>.json/<apikey>/<username>/<rating>
    # returns:
    # note: if no items, returns []
    def getRatedItems(self, type):
        if self.testAccount():
            url = "%s/user/ratings/%s.json/%s/%s/all" % (self.__baseURL, type, self.__apikey, self.__username)
            Debug("[XbmcFilm] getRatedItems(url: %s)" % url)
            return self.xbmcfilmRequest('POST', url)

    def getRatedMovies(self):
        return self.getRatedItems('movies')
    def getRatedShows(self):
        return self.getRatedItems('shows')

    def getcatalogs(self,data):
        if self.testAccount():
            url = "%s/%s/get/%s" % (self.__baseURL, 'catalogs', self.__apikey)
            Debug("[XbmcFilm] getcatalogs(url: %s, data: %s)" % (url, str(data)))
            return self.XbmcFilmsRequest('POST', url, data, passVersions=True)
    def getfiles(self,data):
        if self.testAccount():
            url = "%s/%s/get/%s" % (self.__baseURL, 'files', self.__apikey)
            Debug("[XbmcFilm] getcatalogs(url: %s, data: %s)" % (url, str(data)))
            return self.XbmcFilmsRequest('POST', url, data, passVersions=True)
    def getfilestype(self,data):
        if self.testAccount():
            url = "%s/%s/get/%s" % (self.__baseURL, 'filestype', self.__apikey)
            Debug("[XbmcFilm] getfilestype(url: %s, data: %s)" % (url, str(data)))
            return self.XbmcFilmsRequest('POST', url, data, passVersions=True)
    def gettags(self,data):
        if self.testAccount():
            url = "%s/%s/get/%s" % (self.__baseURL, 'tags', self.__apikey)
            Debug("[XbmcFilm] getfilestype(url: %s, data: %s)" % (url, str(data)))
            return self.XbmcFilmsRequest('POST', url, data, passVersions=True)

    def getplay(self,data):
        if self.testAccount():
            url = "%s/%s/set/%s" % (self.__baseURL, 'play', self.__apikey)
            Debug("[XbmcFilm] getfilestype(url: %s, data: %s)" % (url, str(data)))
            return self.XbmcFilmsRequest('POST', url, data, passVersions=True)
