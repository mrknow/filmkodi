# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys, xbmcplugin, xbmcgui
import cookielib, os, string, cookielib, StringIO
import os, time, base64, logging, calendar
import xbmcaddon, string, xbmc



ptv = xbmcaddon.Addon()
scriptID = ptv.getAddonInfo('id')
scriptname = ptv.getAddonInfo('name')
#dbg = ptv.getSetting('default_debug') in ('true')
ptv = xbmcaddon.Addon(scriptID)


#BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( ptv.getAddonInfo('path'), "lib" ) )

import mrknow_pLog, settings, mrknow_Parser, xbmcfilmapi, mrknow_urlparser, mrknow_Player, mrknow_pCommon
import json

#my_hello_string = ptv.getLocalizedString(30300)

#mainUrl = 'http://xbmcfilm.com/'
mainUrl = 'http://127.0.0.1:5000/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {0: ptv.getLocalizedString(30400),
            1: ptv.getLocalizedString(30403),
            2: ptv.getLocalizedString(30402),
            5: ptv.getLocalizedString(30401),
            6: ptv.getLocalizedString(30404),
            7: ptv.getLocalizedString(30000),

            }


STRPATH =  os.path.join( xbmc.translatePath( "special://home" ),'xbmcfilm_files')
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

class xbmcfilm:

    def __init__(self):
        self.log = mrknow_pLog.pLog()
        self.log.info('Starting xbmcfilm.pl')
        self.p = mrknow_Player.mrknow_Player()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.settings = settings.TVSettings()


        self.api = xbmcfilmapi.XbmcFilmAPI()
        self.cm = mrknow_pCommon.common()
        self.level = 1
        self.mytree = {}

    def chkdict(self,dict,item):
        if item not in dict.keys():
            dict[item] = ''
        if item in dict.keys() and dict[item] == None:
            dict[item] = ''
        return dict[item]

    def traverse(self, data):
        #print("Directory", "-"*self.level, data['title'], self.level)
        self.mytree[self.level] = data['title']
        mypath = ''
        for o in range(0, self.level):
            mypath = mypath + os.path.sep + self.mytree[o+1]
        self.cm.checkDir(STRPATH + mypath)
        dane = {'id': str(data["id"])}
        files = json.dumps(self.api.getfiles(dane))
        filesobj = json.loads(files)
        for i in filesobj["data"]:
            print("File",i)
            filename = i['title'] + '.strm'
            filename1 = self.cm.encoded_item(''.join(c for c in filename if c in valid_chars))
            file = open(STRPATH + mypath + os.path.sep + filename1 , "w")
            params = {'service': 'cda', 'name': 'playSelectedMovie', 'category': None, 'title': i['title'].encode('utf-8','ignore'),
                  'iconimage': '', 'url':i['url'].encode('utf-8','ignore'), 'desc':'', 'myid':i['id']}
            u=sys.argv[0] + self.parser.setParam(params)
            file.write(u)
            file.close()

        for kid in data['children']:
            self.level += 1
            self.traverse(kid)
            self.level -= 1

    def listsMain(self, table):
        for num, val in table.items():
            self.add('cdapl', 'main'+str(num), val, val, 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listStrm(self):
        #check if directory exist
        self.cm.checkDir(STRPATH)
        #Get self home data
        data = {'id': '0'}
        marek = json.dumps(self.api.getcatalogs(data))
        objs = json.loads(marek)
        #delete old files
        folder = STRPATH + os.path.sep + self.cm.encoded_item(objs['data'][0]['title'])
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except Exception, e:
                    print e
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception, e:
                    print e

        self.traverse(objs["data"][0])
        xbmc.executebuiltin('XBMC.UpdateLibrary(video)')

    def listsMainMenu(self, id):
        data = {'id': id}
        self.log.info('XXX TagID: id %s' % data)
        #marek = json.dumps(self.api.getcatalogs(data))
        #self.log.info('XXX: marek %s' % marek)

        #objs = json.loads(marek)

        #if "status" in objs.keys() and objs["status"] == 'fail_authenticated':
        #    d = xbmcgui.Dialog()
        #    d.ok(ptv.getLocalizedString(30010),ptv.getLocalizedString(30405))
        #    return False
        #if id=="0":
        #    for o in objs["data"][0]["children"]:
        #        poster = self.chkdict(o,'poster')
        #        self.add('cdapl', 'main-menu', '[COLOR white]'+ o['title'] + '[/COLOR]', poster, 'None', 'None', 'None', True, False,str(o['id']))
        #else:
        #    for o in objs["data"]:
        #        poster = self.chkdict(o,'poster')
        #        self.add('cdapl', 'main-menu', '[COLOR white]'+ o['title'] + '[/COLOR]', poster, 'None', 'None', 'None', True, False,str(o['id']))

        files = json.dumps(self.api.getfiles(data))
        filesobj = json.loads(files)

        self.log.info('ZZZZZZZZZZZZZZZXXX: files %s' % files)
        if "status" in filesobj.keys() and filesobj["status"] == 'fail_authenticated':
            d = xbmcgui.Dialog()
            d.ok(ptv.getLocalizedString(30010),ptv.getLocalizedString(30405))
            return False



        for i in filesobj["data"]:
            print("I",i)
            poster = self.chkdict(i,'poster')
            plot = self.chkdict(i,'plot')
            self.add('cdapl', 'playSelectedMovie','None',i['title'] ,poster, i['url'], plot, False, True,str(i['id']))

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
    def listsItems(self, type, dane=''):
        if dane != '':
            data = {'type': type, 'dane':dane}
        else:
            data = {'type': type}
        files = json.dumps(self.api.getfilestype(data))
        filesobj = json.loads(files)
        if "status" in filesobj.keys() and filesobj["status"] == 'fail_authenticated':
            d = xbmcgui.Dialog()
            d.ok(ptv.getLocalizedString(30010),ptv.getLocalizedString(30405))
            return False
        print ("Marel",files)
        print ("objs", filesobj["data"])
        for i in filesobj["data"]:
            poster = self.chkdict(i,'poster')
            plot = self.chkdict(i,'plot')
            self.add('cdapl', 'playSelectedMovie','None',i['title'], poster, i['url'], plot, False, True,str(i['id']))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
    def listsItemsTags(self):
        data = {'id': '0'}
        marek = json.dumps(self.api.getcatalogs(data))
        self.log.info('XXX: marek %s' % marek)
        filesobj = json.loads(marek)
        if "status" in filesobj.keys() and filesobj["status"] == 'fail_authenticated':
            d = xbmcgui.Dialog()
            d.ok(ptv.getLocalizedString(30010),ptv.getLocalizedString(30405))
            return False
        for o in filesobj["data"]:
            self.add('cdapl', 'tags', 'Tags', '[COLOR white]'+ o['title'] + '[/COLOR]', 'None', 'None', 'None', True, False,str(o['id']))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsinTags(self, id):
        data = {'id': id}
        marek = json.dumps(self.api.gettags(data))
        objs = json.loads(marek)
        print ("objs",objs)
        for i in objs["data"]:
            print("I",i)
            poster = self.chkdict(i,'poster')
            plot = self.chkdict(i,'plot')
            self.add('cdapl', 'playSelectedMovie','None',i['title'] ,poster, i['url'], plot, False, True,str(i['id']))


        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def add(self, service, name, category, title, iconimage, url, desc='', folder = True, isPlayable = True,myid = "0"):
        params = {'service': service, 'name': name, 'category': category, 'title':title.encode('utf-8','ignore'),
                  'iconimage': iconimage, 'url':url.encode('utf-8','ignore'), 'desc':'', 'myid':myid}
        u=sys.argv[0] + self.parser.setParam(params)
        if name == 'main-menu' or name == 'categories-menu':
            title = category 
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if folder:
            liz.addContextMenuItems([ ('Refresh', 'Container.Refresh'),('Go up', 'Action(ParentDir)') ])
            print("Folder dsaadsads")
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title, "Plot": desc} )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)

    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text


    def LOAD_AND_PLAY_VIDEO(self, url, title, icon,year='',plot='', id=''):
        data = {'id': id}
        options = ""
        if ptv.getSetting('cda_show_rate') == 'true':
            options = 'bitrate'

        mojadata = self.api.getplay(data)
        self.log.info(mojadata)

        progress = xbmcgui.DialogProgress()
        progress.create('Postęp', '')
        message = ptv.getLocalizedString(30406)
        progress.update( 10, "", message, "" )
        xbmc.sleep( 1000 )
        progress.update( 30, "", message, "" )
        progress.update( 50, "", message, "" )
        VideoLink = ''
        subs=''
        VideoLink = self.up.getVideoLink(url, "", options)
        if isinstance(VideoLink, basestring):
            videoUrl = VideoLink
        else:
            videoUrl = VideoLink[0]
            subs = VideoLink[1]
        if 'subs' in mojadata:
            print("mojadata2", mojadata['subs'])
            subs = mojadata['subs']
        progress.update( 70, "", message, "" )
        pluginhandle = int(sys.argv[1])
        if videoUrl == '':
            progress.close()
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Mo�e to chwilowa awaria.', 'Spr�buj ponownie za jaki� czas')
            return False
        if icon == '' or  icon == 'None':
            icon = "DefaultVideo.png"
        if plot == '' or plot == 'None':
            plot = ''
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl )
        liz.setInfo( type="video", infoLabels={ "Title": title} )
        xbmcPlayer = xbmc.Player()

        if subs != '':
            subsdir = os.path.join(ptv.getAddonInfo('path'), "subs")
            if not os.path.isdir(subsdir):
                os.mkdir(subsdir)
            query_data = { 'url': subs, 'use_host': False, 'use_header': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            progress.update( 80, "", message, "" )
            data = self.cm.getURLRequestData(query_data)
            output = open((os.path.join(subsdir, "napisy.txt" )),"w+")
            progress.update( 90, "", message, "" )
            output.write(data)
            output.close()
            progress.update( 100, "", message, "" )
            progress.close()
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

            for _ in xrange(30):
                if xbmcPlayer.isPlaying():
                    break
                time.sleep(1)
            else:
                raise Exception('No video playing. Aborted after 30 seconds.')
            xbmcPlayer.setSubtitles((os.path.join(subsdir, "napisy.txt" )))
            xbmcPlayer.showSubtitles(True)

        else:
            progress.update( 90, "", message, "" )
            progress.close()
            #listitem = xbmcgui.ListItem(path=videoUrl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)


    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        myid = self.parser.getParam(params, "myid")
        desc = self.parser.getParam(params, "desc")

        self.log.info('name:%s,' %(name))

        if name == None:
            self.listsMain(MENU_TAB)
        elif name == 'main0':
            self.listsMainMenu("0")
        elif name == 'main2':
            self.listsMainMenu("2")
        elif name == 'main1':
            self.listsMainMenu("100")
        elif name == 'main4':
             self.listsItemsFollow('users')
        elif name == 'main5':
             self.listsItemsTags()
        elif name == 'main7':
            self.log.info('Wyświetlam ustawienia')
            self.settings.showSettings()

        elif name == 'main6':
            key = self.searchInputText()
            if key != None:
                self.listsItems('search', key)

        elif name == 'tags':
            self.listsItemsinTags(myid)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(url, title, icon, '',desc,myid)


init = xbmcfilm()
init.handleService()