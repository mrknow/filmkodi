import urllib
import urllib2
import os
import re
import xbmcplugin
import xbmcgui
import xbmcaddon
from BeautifulSoup import BeautifulSoup
try:
    import json
except:
    import simplejson as json

addon = xbmcaddon.Addon('plugin.video.ustream')

BASE_RESOURCE_PATH = os.path.join( addon.getAddonInfo('path'), "../script.common.plugin.cache/" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
print("MMMMM",sys.path)

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
from pyamf import remoting

addon = xbmcaddon.Addon('plugin.video.ustream')
addon_version = addon.getAddonInfo('version')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
home = addon.getAddonInfo('path')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
next_icon = xbmc.translatePath(os.path.join(home, 'resources', 'next.png'))
search_icon = xbmc.translatePath(os.path.join(home, 'resources', 'search.png'))
cache = StorageServer.StorageServer("ustream", 24)
pref_stream_type = addon.getSetting('stream_type')
base = 'http://www.ustream.tv'
#dev_key = 'D9B39696EF3F310EA840C3A8EFC8306D'
dev_key = '6A5FC1EFA64F5CA1F945DE9BAE3B2F44'


def addon_log(string):
    xbmc.log("[addon.ustream-%s]: %s" %(addon_version, string))


def make_request(url):
        try:
            headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
                       'Referer' : base+'/new'}
            req = urllib2.Request(url,None,headers)
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
            return data
        except urllib2.URLError, e:
            addon_log('We failed to open "%s".' % url)
            if hasattr(e, 'reason'):
                addon_log('We failed to reach a server.')
                addon_log('Reason: %s' %e.reason)
            if hasattr(e, 'code'):
                addon_log('We failed with error code - %s.' % e.code)
                xbmc.executebuiltin("XBMC.Notification(Ustream,HTTP ERROR: "+str(e.code)+",5000,"+icon+")")
                
                
def cache_categories():
        cat_list = []
        soup = BeautifulSoup(make_request(base+'/exlore/all'), convertEntities=BeautifulSoup.HTML_ENTITIES)
	print("MNMNSoup",soup)
        #for i in soup.find('li', attrs={'class':"mainmenu categories"})('li'):
        for i in soup.find('div', attrs={'class':"sub-menu-list categories"})('ul'):
            print("MarekIIII",i.a.string, i.a['data-requestpath'])
            cat_list.append((i.a.string, i.a['data-requestpath']))
        return cat_list
        
        
def categories():
        for i in cache.cacheFunction(cache_categories):
            addDir(i[0], base+i[1], 1, icon)
        addDir('User Search', '', 6, search_icon)


def index_category(url, page=None):
        if page is None:
            if not url.endswith('/all.json'):
                url = url.split('.json')[0]+'/all.json'
        data = json.loads(make_request(url))
        if data['success']:
            soup = BeautifulSoup(data['pageContent'], convertEntities=BeautifulSoup.HTML_ENTITIES)
            items = soup.findAll('li', attrs={'class' : "media-swap-wrap"})
            if len(items) < 1:
                addon_log('no items')
            else:
                for i in items:
                    title = i.a['title']
                    href = i.a['href']
                    # addon_log(href)
                    thumb = i.img['src']
                    if i.find('span', attrs={'class' : 'badge-live'}):
                        title += ' [Live]'
                        addLiveLink(title.encode('utf-8'), href, 2, thumb)
                    else:
                        if i.find('span', attrs={'class' : 'badge-featured'}):
                            title += ' [Highlight]'
                        addLiveLink(title.encode('utf-8'), href, 5, thumb)
                
                if page is None:
                    page = 2
                    url += '?page=2'
                else:
                    page += 1
                    url = url[:-1]+str(page)
                addDir('Next Page', url, 1, next_icon, page)
        else:
            addon_log('data[success] = False')
            
            
def get_video_info(href):
        if 'highlight/' in href:
            url = '%s/content/highlight/%s/title-bar.json' %(base, href.split('/')[-1])
            data = json.loads(make_request(url))
            pattern = 'data-content-type="channel" data-content-id="(.+?)"'
            content_id = re.findall(pattern, str(data['data']))[0]
            amf_data = get_amf(content_id)
            if amf_data['offairContent'].has_key('videos'):
                addon_log("len(amf_data['offairContent']['videos']: %s" %len(amf_data['offairContent']['videos']))
                # need to add a method for selecting the correct video
                video_id = amf_data['offairContent']['videos'][0]
            else: video_id = href.split('/')[1] #this should be the full video_id not the highlight
        else:
            video_id = href.split('/')[-1]
        url = 'http://api.ustream.tv/json/video/%s/getInfo?key=%s' %(video_id, dev_key)
        addon_log('getInfo: '+url)
        data = json.loads(make_request(url))
        play_url = ''
        succeeded = False
        if data['results'] is not None:
            play_url = data['results']['liveHttpUrl']
            if play_url is not None:
                succeeded = True
                addon_log('play_url: '+play_url)
            else: xbmc.executebuiltin("XBMC.Notification(Ustream,Unable to resolve URL,5000,"+icon+")")
                ## rtmplib seems to fail for these streams
                # rtmp = 'rtmp://74.217.100.130:1935/ustream/%s' %video_id
                # app = rtmp.split('/', 3)[-1]
                # playpath = re.findall('id=".+?" name="(.+?)"', data['results']['embedTag'])[0]
                # pageurl = re.findall("'title': u'.+?', u'url': u'(.+?)'", str(data))[0]
                # swfurl = getSwf()
                # play_url = '%s app=%s pageUrl=%s playpath=%s swfUrl=%s swfVfy=1 timeout=30' %(rtmp, app, pageurl, playpath, swfurl)
                # succeeded = True
                # addon_log('----- succeeded ------')
                # addon_log('---- play_url: '+play_url)
        else:
            addon_log('No Reasults')
            # for i in data.keys():
                # addon_log(i+': '+str(data[i]))
            xbmc.executebuiltin("XBMC.Notification(Ustream,Unable to resolve URL,5000,"+icon+")")
        item = xbmcgui.ListItem(path=play_url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded, item)
            
            
def get_channel_id_from_html(url):
        pattern=('ustream.vars.contentId=(.+?);ustream.vars.contentType="channel"')
        channel_id = re.findall(pattern, make_request(base+url))[0]
        resolve_url(channel_id)
            
            
def list_all_channels(user, stream_title=None):
        addon_log('list_all_channels: '+user)
        url = 'http://api.ustream.tv/json/user/%s/listAllChannels?key=%s' %(user, dev_key)
        data = json.loads(make_request(url))
        if data['results'] is not None:
            for i in data['results']:
                title = i['title']
                if not stream_title is None:
                    if stream_title in title:
                        addon_log('status key == %s' %i['status'])
                        if i['status'] == 'live':
                            return resolve_url(i['id'])
                        else : xbmc.executebuiltin("XBMC.Notification(Ustream,Channel Status: Offline,5000,"+icon+")")
                    else: continue
                else: addLiveLink('%s [%s]' %(title, i['status']), i['id'], 4, icon, False)
        else:
            try:
                addon_log('Error: '+data['error'])
                addon_log('MSG: '+data['msg'])
            except: pass
            
            
def user_search(user=None):
        if user is None:
            keyboard = xbmc.Keyboard('','User Search')
            keyboard.doModal()
            if (keyboard.isConfirmed() == False):
                return
            user = keyboard.getText()
            if len(user) < 1:
                return        
        url = 'http://api.ustream.tv/json/user/recent/search/username:like:%s?key=%s' %(user, dev_key)
        data = json.loads(make_request(url))
        if data['results'] is None:
            xbmc.executebuiltin("XBMC.Notification(Ustream,No Results Found,5000,"+icon+")")
        else:
            for i in data['results']:
                addDir(i['name'], i['id'], 3, icon)
                
                
def get_amf(content_id):
        amf_url = 'http://cgw.ustream.tv/Viewer/getStream/1/%s.amf' % content_id
        addon_log("amf_url: "+amf_url)
        amf_data = remoting.decode(make_request(amf_url)).bodies[0][1].body
        return amf_data
        
        
def getSwf():
        req = urllib2.Request(base+'/flash/viewer.swf')
        response = urllib2.urlopen(req)
        return response.geturl()
                
                
def resolve_url(stream_id):
        amf_data = get_amf(stream_id)
        streams = []
        if not amf_data['status'] == 'offline':
            if 'streamVersions' in amf_data.keys():
                addon_log('streamVersions: '+str(len(amf_data['streamVersions'])))
                for i in amf_data['streamVersions'].keys():
                    if 'streamVersionCdn' in amf_data['streamVersions'][i].keys():
                        addon_log('streamVersionsCdn: '+str(len(amf_data['streamVersions'][i]['streamVersionCdn'])))
                        for cdn in amf_data['streamVersions'][i]['streamVersionCdn']:
                            # addon_log(amf_data['streamVersions'][i]['streamVersionCdn'][cdn])
                            cdn_url = amf_data['streamVersions'][i]['streamVersionCdn'][cdn]['cdnStreamUrl']
                            cdn_path = amf_data['streamVersions'][i]['streamVersionCdn'][cdn]['cdnStreamName']
                            streams.append((cdn_url, cdn_path))
                    else:
                        addon_log('No streamVersionCdn key!')
            else:
                addon_log('No streamVersions key!')
            if 'fmsUrl' in amf_data.keys():
                fms_url = amf_data['fmsUrl']
                # there may be issues with this path ???
                fms_path = amf_data['streamName']
                # if fms_path == 'streams/live':
                    # fms_path += '_1_'+stream_id
                streams.append((fms_url, fms_path))
            if 'cdnUrl' in amf_data.keys():
                cdn_url = amf_data['cdnUrl']
                cdn_path = amf_data['streamName']
                stream = (cdn_url, cdn_path)
                if not stream in streams:
                    streams.append((cdn_url, cdn_path))
            if 'liveHttpUrl' in amf_data.keys():
                streams.append((amf_data['liveHttpUrl'], None))
        else:
            addon_log('status key == offline')
            xbmc.executebuiltin("XBMC.Notification(Ustream,Channel is Offline,5000,"+icon+")")
            
        addon_log('streams %s' %str(len(streams)))
        addon_log(str(streams))
        play_url = False
        if len(streams) > 0:
            swf = ' swfUrl='+getSwf()
            stream_urls = {}
            for i in streams:
                if i[0].endswith('.m3u8'):
                    stream_urls['hls'] = i[0]
                else:
                    rtmp = i[0]
                    playpath = ' playpath=' + i[1]
                    app = ' app='+rtmp.split('/', 3)[-1]
                    try:
                        pageUrl = ' pageUrl='+amf_data['ads']['info']['url']
                    except:
                        try:
                            pageUrl = ' pageUrl='+amf_data['moduleConfig']['meta']['url']
                        except:
                            addon_log('pageUrl Exception')
                            continue
                    flash = rtmp + playpath + swf + pageUrl + app + ' swfVfy=1 live=true timeout=30'
                    if 'ustreamlivefs' in i[0]:
                        stream_urls['ustreamlivefs'] = flash
                    else:
                        stream_urls['other'] = flash
            if pref_stream_type == '0':
                if stream_urls.has_key('hls'):
                    play_url = get_hls(stream_urls['hls'])
            if pref_stream_type == '1':
                if stream_urls.has_key('ustreamlivefs'):
                    play_url = i
            if pref_stream_type == '2':
                if stream_urls.has_key('other'):
                    play_url = i
                            
            if not play_url:
                dialog = xbmcgui.Dialog()
                ret = dialog.select('Choose a stream type.', stream_urls.keys())
                play_url = stream_urls.values()[ret]
                if '.m3u8' in play_url:
                    play_url = get_hls(play_url)
        else:
            addon_log('No Streams')
                
        if play_url:
            print play_url
            addon_log('Play URL: '+play_url)
            succeeded = True
        else:
            succeeded = False
            play_url = ''
        item = xbmcgui.ListItem(path=play_url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded, item)
        
        
def get_hls(url):
        data = make_request(url)
        pattern = '#EXT-X-STREAM-INF:.+?,BANDWIDTH=(.+?),.+?\\n(.+?)\\n'
        streams = re.findall(pattern, data)
        if streams:
            best = 0
            for bandwidth, stream_url in streams:
                if int(bandwidth) > best:
                    best = int(bandwidth)
                    playurl = stream_url
            return playurl
        else:
            addon_log('hls resolved url: %s' %url)
            return url
            

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

        
def addDir(name,url,mode,iconimage,page=None):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        if page is not None:
            u += "&page="+str(page)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

        
def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name })
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addLiveLink(name,url,mode,iconimage,showcontext=True):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        if showcontext:
            contextMenu = [('List all channels from this user','XBMC.Container.Update(%s?url=%s&mode=3)' %(sys.argv[0], urllib.quote_plus(url)))]
            liz.addContextMenuItems(contextMenu)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok


params=get_params()

try:
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
except:
    pass

url=None
name=None
mode=None
page=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    catId=urllib.unquote_plus(params["catId"])
except:
    pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    page=int(params["page"])
except:
    pass

addon_log("Mode: "+str(mode))
addon_log("URL: "+str(url))
addon_log("Name: "+str(name))

if mode==None:
    categories()

elif mode==1:
    index_category(url, page)
    
elif mode==2:
    # stream_title = name.split(' [')[0]
    # list_all_channels(url, stream_title)
    get_channel_id_from_html(url)
    
elif mode==3:
    list_all_channels(url)
    
elif mode==4:
    resolve_url(url)
    
elif mode==5:
   get_video_info(url)
   
elif mode==6:
    user_search()
    
elif mode==7:
    pass
   
xbmcplugin.endOfDirectory(int(sys.argv[1]))
