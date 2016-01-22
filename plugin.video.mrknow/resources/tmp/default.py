# -*- coding: utf-8 -*-
import xbmcaddon

import urllib,urllib2,re,xbmcplugin,xbmcgui
import socket
if sys.version_info >=  (2, 7):
    import json as _json
else:
    import simplejson as _json 

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]
base_url = 'http://tvnplayer.pl/api/?platform=ConnectedTV&terminal=Samsung&format=json&v=2.0&authKey=ba786b315508f0920eca1c34d65534cd'
scale_url = 'http://redir.atmcdn.pl/scale/o2/tvn/web-content/m/'

__settings__ = xbmcaddon.Addon(id='plugin.video.tvnplayer.pl')

socket.setdefaulttimeout(10)

def TVNPlayerAPI(m,type,id,season):
    if m == 'mainInfo':
        GeoIP = urllib2.urlopen(base_url + '&m=checkClientip')
        GeoIPjson = _json.loads(GeoIP.read())
        GeoIP.close()
        __settings__.setSetting(id='checkClientip', value=str(GeoIPjson['result']))
        url = base_url + '&m=%s'% (m)
        print ("Url",url)
        response = urllib2.urlopen(url)
        njson = _json.loads(response.read())
        response.close()
        categories = njson['categories']
        for item in categories:
            name = item.get('name','')
            type = item.get('type','')
            id = item['id']
            if type != 'titles_of_day' and type != 'favorites' and type != 'pauses':
                addDir(name,'getItems',type,id,'DefaultVideoPlaylists.png','','')
    else:
        urlQuery = '&m=%s&type=%s&id=%s&limit=500&page=1&sort=newest' % (m, type, id)
        if season > 0:
            urlQuery = urlQuery + '&season=' + str(season)
        response = urllib2.urlopen(base_url + urlQuery)
        njson = _json.loads(response.read())
        response.close()
        if type == "series":
            if njson['items'][0]['season'] == str(season):
                return TVNPlayerItems(njson)
            else:
                seasons = njson['seasons']
                for item in seasons:
                    name = item.get('name','')
                    season = item.get('id','')
                    xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
                    addDir(name,'getItems',type,id,'DefaultTVShows.png','',season)
                if not seasons:
                    return TVNPlayerItems(njson)
        else:
            return TVNPlayerItems(njson)

def TVNPlayerItems(njson):
        items = njson['items']
        for item in items:
            name = item.get('title','')
            type = item.get('type','')
            type_episode = item.get('type_episode','')
            clickable = item['clickable']
            id = item['id']
            thumbnail = item['thumbnail'][0]['url']
            gets = {'type': 1,
                    'quality': 95,
                    'srcmode': 0,
                    'srcx': item['thumbnail'][0]['srcx'],
                    'srcy': item['thumbnail'][0]['srcy'],
                    'srcw': item['thumbnail'][0]['srcw'],
                    'srch': item['thumbnail'][0]['srch'],
                    'dstw': 256,
                    'dsth': 292}
            if type == 'episode':
                if clickable == 1 :                
                #if type_episode == 'normal' or type_episode == 'catchup':
                    tvshowtitle = item.get('title','')
                    episode = item.get('episode','')
                    sub_title = item.get('sub_title','')
                    lead = item.get('lead','')
                    season = item.get('season','')
                    start_date = item.get('start_date','')
                    url = pluginUrl+'?m=getItem&id='+str(id)+'&type='+type
                    name = tvshowtitle + ' - ' + sub_title
                    if not sub_title or tvshowtitle == sub_title:
                        name = tvshowtitle
                    if type_episode == 'catchup' :
                        if str(episode) == '0' :
                            name = name
                        elif str(season) == '0' :
                            name = name + ', odcinek '+ str(episode)
                        else:
                            name = name + ', sezon ' + str(season)+', odcinek '+ str(episode)
                    addLink(name,url,thumbnail,gets,tvshowtitle,lead,episode,season,start_date)
            else:
                addDir(name,'getItems',type,id,thumbnail,gets,'')

def TVNPlayerItem(type, id):
        if __settings__.getSetting('checkClientip') == 'False' and __settings__.getSetting('pl_proxy') == '':
            __settings__.openSettings()
        else:
            if __settings__.getSetting('checkClientip') == 'False':
                pl_proxy = 'http://' + __settings__.getSetting('pl_proxy') + ':' + __settings__.getSetting('pl_proxy_port')
                proxy_handler = urllib2.ProxyHandler({'http':pl_proxy})
                if __settings__.getSetting('pl_proxy_pass') <> '' and __settings__.getSetting('pl_proxy_user') <> '':
                    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    password_mgr.add_password(None, pl_proxy, __settings__.getSetting('pl_proxy_user'), __settings__.getSetting('pl_proxy_pass'))
                    proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
                    opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
                else:
                    opener = urllib2.build_opener(proxy_handler)
            urlQuery = '&type=%s&id=%s&sort=newest&m=getItem&deviceScreenHeight=1080&deviceScreenWidth=1920' % (type, id)
            if __settings__.getSetting('checkClientip') == 'False':
                try:
                    getItem = opener.open(base_url + urlQuery)
                except Exception, ex:
                    ok = xbmcgui.Dialog().ok('TVNPlayer', 'Coś nie tak z Twoim proxy', 'error message', str(ex))
                    return ok
            else:
                getItem = urllib2.urlopen(base_url + urlQuery)
            njson = _json.loads(getItem.read())
            getItem.close()
            video_content = njson['item']['videos']['main']['video_content']
            if not video_content:
                ok = xbmcgui.Dialog().ok('TVNPlayer', 'Jak używasz proxy', 'to właśnie przestało działać')
                return ok
            else:
                profile_name_list = []
                for item in video_content:
                    profile_name = item['profile_name']
                    profile_name_list.append(profile_name)
                if __settings__.getSetting('auto_quality') == 'true' :
                    if 'HD' in profile_name_list:
                        select = profile_name_list.index('HD')
                    elif 'Bardzo Wysoka' in profile_name_list:
                        select = profile_name_list.index('Bardzo Wysoka')
                    elif 'Wysoka' in profile_name_list:
                        select = profile_name_list.index('Wysoka')
                    else:
                        select = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)
                else:
                    select = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)
                stream_url = njson['item']['videos']['main']['video_content'][select]['url']
                if __settings__.getSetting('checkClientip') == 'False':
                    new_stream_url = opener.open(stream_url)
                else:
                    new_stream_url = urllib2.urlopen(stream_url)
                stream_url = new_stream_url.read()
                new_stream_url.close()
                xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path=stream_url))

def htmlToText(html):
    html = re.sub('<.*?>','',html)
    return html .replace("&lt;", "<")\
                .replace("&gt;", ">")\
                .replace("&amp;", "&")\
                .replace("&quot;",'"')\
                .replace("&apos;","'")

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param


def addDir(name,m,type,id,thumbnail,gets,season):
        u=sys.argv[0]+"?m="+urllib.quote_plus(m)+"&type="+urllib.quote_plus(type)+"&id="+str(id)+"&season="+str(season)
        if not gets:
            thumbnailimage=''
        else:
            thumbnailimage='%s%s?%s' % (scale_url, thumbnail, urllib.urlencode(gets))
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=urllib.unquote(thumbnailimage))
        liz.setInfo( type="video",  infoLabels = {'title' : name })
        ok=xbmcplugin.addDirectoryItem(handle=pluginHandle,url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,thumbnail,gets,serie_title,lead,episode,season,start_date):
        ok=True
        if not gets:
            thumbnailimage=''
        else:
            thumbnailimage='%s%s?%s' % (scale_url, thumbnail, urllib.urlencode(gets))
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=urllib.unquote(thumbnailimage))
        liz.setInfo( type="video",  infoLabels = {
                'tvshowtitle' : serie_title ,
                'title' : name ,
                'plot': htmlToText(lead) ,
                'episode': int(episode) ,
                'season' : int(season) ,
                'aired' : start_date
        })
        if __settings__.getSetting('checkClientip') == 'False' and __settings__.getSetting('pl_proxy') == '':
            liz.setProperty("IsPlayable","false");
        else:
            liz.setProperty("IsPlayable","true");
        liz.setProperty('Fanart_Image', 'http://redir.atmcdn.pl/http/o2/tvn/web-content/m/' + thumbnail)
        ok=xbmcplugin.addDirectoryItem(handle=pluginHandle,url=url,listitem=liz,isFolder=False)
        return ok

params=get_params()

type=None
id=None

limit=None
page=None

try:
        m=urllib.unquote_plus(params["m"])
except:
        m="mainInfo"
        pass
try:
        type=urllib.unquote_plus(params["type"])
except:
        pass
try:
        id=int(params["id"])
except:
        pass
try:
        season=int(params["season"])
except:
        season="0"
        pass

print "Tryb: "+str(m)
print "Typ: "+str(type)
print "ID: "+str(id)
print "Sezon: "+str(season)

if m == "mainInfo":
        TVNPlayerAPI(m,type,id,season)
       
elif m == "getItems":
        TVNPlayerAPI(m,type,id,season)
        
elif m == "getItem":
        TVNPlayerItem(type,id)

if type == "series":
        xbmcplugin.setContent(pluginHandle, 'episodes')
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_EPISODE)
elif type == "catalog":
        xbmcplugin.addSortMethod( pluginHandle, xbmcplugin.SORT_METHOD_UNSORTED )
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        if id == 3:
            xbmcplugin.setContent(pluginHandle, 'movies')
xbmcplugin.endOfDirectory(pluginHandle)
