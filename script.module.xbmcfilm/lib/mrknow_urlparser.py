# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys, math
import xbmcaddon, xbmc, xbmcgui

try:
    import simplejson as json
except ImportError:
    import json

import urlparse
import httplib

ptv = xbmcaddon.Addon()
scriptID = ptv.getAddonInfo('id')
scriptname = ptv.getAddonInfo('name')
# dbg = ptv.getSetting('default_debug') in ('true')
ptv = xbmcaddon.Addon(scriptID)

import mrknow_Parser, mrknow_pCommon, mrknow_pLog, mrknow_Pageparser
from mrknow_utils_js import WiseUnpacker
from jsbeautifier import beautify




HOST = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
HOST_CHROME = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'

CHARS = [
    ['F', 'a'],
    ['a', 'F'],
    ['A', 'f'],
    ['k', 'B'],
    ['K', 'b'],
    ['b', 'K'],
    ['B', 'k'],
    ['m', 'I'],
    ['M', 'i'],
    ['i', 'M'],
    ['I', 'm'],
    ['D', 'x'],
    ['x', 'D'],
    ['O', 'y'],
    ['y', 'O'],
    ['C', 'z'],
    ['z', 'C'],
]


class mrknow_urlparser:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.log = mrknow_pLog.pLog()

    def hostSelect(self, v):
        hostUrl = False
        d = xbmcgui.Dialog()
        if len(v) > 0:
            valTab = []
            for i in range(len(v)):
                valTab.append(str(i + 1) + '. ' + self.getHostName(v[i], True))
            item = d.select("Wybor hostingu", valTab)
        if item >= 0:
            hostUrl = v[item]
        else:
            d.ok('Brak linkow', 'Przykro nam, ale nie znalezlismy zadnego linku do video.',
                 'Sproboj ponownie za jakis czas')
        return hostUrl


    def getHostName(self, url):
        self.log.info('URL: '+url )
        hostName = urlparse.urlparse(url)[1].split('.')
        return hostName[-2] + '.' + hostName[-1]


    def getVideoLink(self, url, referer='', options=''):
        nUrl = url
        host = self.getHostName(url)
        self.log.info("URLPARSER uvideo hosted by: " + host + " link: " + url+" referer: " + referer)
        hostMap = {

        'erstream.com':             self.parsererstream             ,
        'sockshare.com':            self.parserSOCKSHARE            ,
        'megustavid.com':           self.parserMEGUSTAVID           ,
        'hd3d.cc':                  self.parserHD3D                 ,
        'sprocked.com':             self.parserSPROCKED             ,
        'odsiebie.pl':              self.parserODSIEBIE             ,
        'wgrane.pl':                self.parserWGRANE               ,
        'cda.pl':                   self.parserCDA                  ,
        'maxvideo.pl':              self.parserMAXVIDEO             ,
        'nextvideo.pl':             self.parserMAXVIDEO             ,
        'anyfiles.pl':              self.parserANYFILES             ,
        'videoweed.es':             self.parserVIDEOWEED            ,
        'videoweed.com':            self.parserVIDEOWEED            ,
        'novamov.com':              self.parserNOVAMOV              ,
        'nowvideo.eu':              self.parserNOWVIDEO             ,
        'rapidvideo.com':           self.parserRAPIDVIDEO           ,
        'videoslasher.com':         self.parserVIDEOSLASHER         ,
        'youtube.com':              self.parserYOUTUBE              ,
        'stream.streamo.tv':        self.parserSTREAMO              ,
        'tosiewytnie.pl':           self.parsertosiewytnie          ,
        'liveleak.com':             self.parserliveleak             ,
        'vimeo.com':                self.parserVIMEO                ,
        'yukons.net':               self.parserYUKONS               ,
        'reyhq.com':                self.parserREYHQ                ,
        'sawlive.tv':               self.parserSAWLIVE              ,
        'ilive.to':                 self.parserILIVE                ,
        'mips.tv':                  self.parserMIPS                 ,
        'ukcast.tv':                self.parserUKCAST               ,
        'castamp.com':              self.parserCASTAMP              ,
        'liveview365.tv':           self.parserLIVEVIEW365          ,
        'jokerupload.com':          self.parserjokerupload          ,
        'topupload.tv':             self.parsertopupload            ,
        'putlive.in':               self.parserputlive              ,
        'emb.aliez.tv':             self.parseraliez                ,
        'ucaster.eu':               self.parseucaster               ,
        'flashwiz.tv':              self.parseflashwiz              ,
        'goodcast.tv':              self.parsegoodcast              ,
        'goodcast.me':              self.parsegoodcastme            ,
        'goodcast.co':              self.parsegoodcastorg           ,
        'sharecast.to':             self.sharecastto                ,
        'yycast.com':               self.parseyycast                ,
        'liveflash.tv':             self.parseliveflash             ,
        'ovcast.com':               self.parseovcast                ,
        'stream4.tv':               self.stream4                    ,
        'jjcast.com':               self.jjcast                     ,
        "wrzuta.pl":                self.wrzutapl                   ,
        'hqstream.tv':              self.hqstream                   ,
        'maxupload.tv':             self.maxuploadtv                ,
        'fupptv.pl':                self.fupptvpl                   ,
        '7cast.net':                self.sevencastnet               ,
        'abcast.net':               self.abcastbiz                  ,
        'flexstream.net':           self.flexstreamnet              ,
        'npage.de':                 self.file1npagede,
        'freelivestream.tv':        self.freelivestreamtv,
        'shidurlive.com':           self.shidurlive,
        'castalba.tv':              self.castalbatv,
        'firedrive.com':            self.firedrivecom,
        'streamin.to':              self.streaminto,
        'played.to':                self.standard_file,
        'vidzer.net':               self.parserVIDZER,
        'nowvideo.sx':              self.parserNOWVIDEO,
        'vidto.me':                 self.parserVIDTO,
        'thevideo.me':              self.parserthevideome,
        'embed.up4free.com':        self.up4freecom,
        'static.castto.me':         self.casttome,
        'byetv.org':                self.byetv,
        'hdcast.me':                self.hdcastme,
        'pxstream.tv':              self.pxstream,
        'deltatv.pw':               self.deltatvpw,
        'ultracast.me':             self.ultracast,
        'biggestplayer.me':         self.biggestplayerme,
        'p2pcast.tv':               self.p2pcasttv,
        'videomega.tv':             self.parserVIDEOMEGA      ,
        'videowood.tv':             self.parservideowood,
        'vshare.io':                self.parsevshareio,
        'openload.co':              self.parseopenload,
        'tutelehd.com':             self.parsertutelehd,
        'streamplay.cc':            self.streamplay

        }
        #(url, options)
        if host in hostMap:
            nUrl = hostMap[host](url,referer, options)

        return nUrl

    def streamplay(self,url,referer,options):
        HEADER = {'Referer': referer,'User-Agent': HOST}
        query_data = { 'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        linkvideo = ''
        myfile = re.compile('<iframe src="(.*?)" id="(.*?)" scrolling="no" allowfullscreen></iframe>').findall(link)
        if len(myfile)>0:
            #print("Dane",rtmp,myfile,url)
            query_data = { 'url': myfile[0][0], 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link2 = self.cm.getURLRequestData(query_data)
            print("Dane",link2)
            mylink = re.compile('<div id="hideOnClick"></div>\r\n                                <a  \r\n                    href="(.*?)"').findall(link2)
            print("co", mylink)
            if len(mylink)>0:
                linkvideo = mylink[0]
        return linkvideo

    def parsertutelehd(self,url,referer,options):
        HEADER = {'Referer': referer,'User-Agent': HOST}
        query_data = { 'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #print("link",link)
        rtmp = re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link)
        myfile = re.compile("so.addVariable\('file', '(.*?)'\);").findall(link)

        #print("Dane",rtmp,myfile,url)
        url2 = 'http://filmkodi.com/mntest.php?file='+myfile[0]+'&search=' + rtmp[0]
        query_data = { 'url': url2, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link2 = self.cm.getURLRequestData(query_data)
        linkvideo = ''
        if len(myfile)>0:
            linkvideo = link2+' playpath=' + myfile[0] + ' swfUrl=http://tutelehd.com/player.swf swfVfy=1 flashver=WIN\\2017,0,0,169 live=true token=0fea41113b03061a pageUrl=' + url
            linkvideo = linkvideo.replace('live.tutelehd.com/redirect','198.144.159.127:1935/live')
        return linkvideo


    def parseopenload(self,url,referer,options):
        #print("link", urlparse.urlparse(url))
        myparts = urlparse.urlparse(url)
        media_id = myparts.path
        media_id = media_id.replace('/video/','').replace('/embed/','')
        url_new = 'https://openload.co/embed/' + media_id

        ticket_url = 'https://api.openload.io/1/file/dlticket?file=%s' % (media_id)
        query_data = { 'url': ticket_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        result = self.cm.getURLRequestData(query_data)
        js_result = json.loads(result)
        print("re",js_result,result)
        if js_result['status'] == 200:
            img = xbmcgui.ControlImage(450, 0, 400, 130, js_result['result']['captcha_url'])
            wdlg = xbmcgui.WindowDialog()
            wdlg.addControl(img)
            wdlg.show()
            kb = xbmc.Keyboard('', 'Type the letters in the image', False)
            kb.doModal()
            if (kb.isConfirmed()):
                solution = kb.getText()
                if solution == '':
                    raise Exception('You must enter text in the image to access video')
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Problem"," Nie wprowadzono kodu Captcha")
                return ''
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok(" Problem",js_result['msg'])
            return ''
        xbmc.sleep(js_result['result']['wait_time'] * 1000)
        video_url = 'https://api.openload.io/1/file/dl?file=%s&ticket=%s&captcha_response=%s' % (media_id, js_result['result']['ticket'],solution)
        query_data = { 'url': video_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        result = self.cm.getURLRequestData(query_data)
        js_result = json.loads(result)
        print("JSRES", js_result)
        if js_result['status'] == 200:
            #czy mamy napisy
            query_data = { 'url': url_new, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            result = self.cm.getURLRequestData(query_data)
            match2 = re.compile('var suburl = "(.*?)";').findall(result)
            print("res",result)
            print("match",match2)
            if len(match2)>0:
                #mamy napisy
                mylink = {}
                mylink[0] = js_result['result']['url'] + '?mime=true'
                mylink[1] = "https://openload.io" + match2[0].replace('\\','')
                print("mylink",mylink)
                return mylink
            else:
                return js_result['result']['url'] + '?mime=true'
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok(" Problem",js_result['msg'])
            return ''

    def parserthevideome(self,url,referer,options):
        if not 'embed' in url:
            myparts = urlparse.urlparse(url)
            url = myparts.scheme +'://'+ myparts.netloc  + myparts.path.replace('/','/embed-') + '-640x360.html'
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        linkvideo = ''
        match2 = re.compile('\{ label: \'(.*?)\', file: \'(.*?)\' \}').findall(link)
        if len(match2)>0:
            for i in range(len(match2)):
                linkvideo = match2[i][1]
            return linkvideo
        else:
            return linkvideo


    def parsevshareio(self,url, referer, options):
        HEADER = {'Referer': referer,'User-Agent': HOST}
        query_data = { 'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #print("Link",link)
        linkvideo = ''
        match1 = re.compile("url: '(.*?)',").findall(link)
        match2 = re.compile('<iframe src="(.*?)" (.*?)></iframe>').findall(link)
        if len(match1)>0:
            linkvideo = match1[0]
        if len(match2)>0:
            print("Mamy",match2[0])
            query_data = { 'url': 'http:'+match2[0][0], 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link = self.cm.getURLRequestData(query_data)
            #print("Link",link)
            match3 = re.compile("url: '(.*?)',").findall(link)
            if len(match3)>0:
                linkvideo = match3[0]

        return linkvideo

    def parservideowood(self,url, referer, options):
        HEADER = {'Referer': referer,'User-Agent': HOST}
        query_data = { 'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        linkvideo = ''
        match = re.compile('<iframe(.*?)src="http://videowood.tv/(.*?)" scrolling="no"></iframe>').findall(link)
        if len(match)>0:
            query_data = { 'url': 'http://videowood.tv/' + match[0][1], 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link2 = self.cm.getURLRequestData(query_data)
            match1 = re.compile('eval\((.*?)\)\n\n').findall(link2)
            print("link2",match1)
            moje = beautify("eval(" + match1[0]+")")
            print ("Moje",moje)
            print ("Moje2","eval(" + match1[0]+")")



            #match2 = re.compile('\{label:"(.*?)",file:"(.*?)"\}').findall(moje)
            #match3 = re.compile('hd_default:"(.*?)"').findall(moje)



    def parserVIDEOMEGA(self,url, referer,options):
        url = url.replace('?ref','iframe.php?ref')
        HEADER = {'Referer': referer,'User-Agent': HOST_CHROME}
        query_data = { 'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match1= re.compile('eval\((.*?)\n\n\n\t</script>').findall(link)
        if len(match1) > 0:
            match2 = re.compile('attr\("src", "(.*?)"\)').findall(beautify("eval(" + match1[0]))
            linkVideo= match2[0]
            self.log.info ('linkVideo ' + linkVideo)
            return linkVideo
        else:
            return False

    def p2pcasttv(self,url, referer,options):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        match = re.search('file: "(.*?)"',data)
        mylink = ''
        if match:
            mylink = match.group(1)
        return mylink

    def biggestplayerme(self,url, referer,options):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        match = re.search('file: "(.*?)"',data)
        mylink = ''
        if match:
            mylink = match.group(1)
            #mylink = match.group(1) + ' token=Fo5_n0w?U.rA6l3-70w47ch live=true timeout=30 pageUrl=http://deltatv.pw playpath='+match.group(1)
        return mylink

    def ultracast(self,url, referer,options):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        scripts_text = self.cm.getURLRequestData(query_data)
        rgx = WiseUnpacker.param_regex
        unpacked_script = None
        if re.search(rgx, scripts_text):
            w = re.search(rgx, scripts_text).group('param_w')
            i = re.search(rgx, scripts_text).group('param_i')
            s = re.search(rgx, scripts_text).group('param_s')
            e = re.search(rgx, scripts_text).group('param_e')
            unpacked_script = WiseUnpacker.unpack(w, i, s, e)
        match = re.search('{file:"(.*?)"}',unpacked_script)
        #return match.group(1)+'|Referer=http://ultracast.me/js/jwplayer.flash.swf'
        #return 'rtmp://rtmp.ultracast.me:1935/live?55e244dd8ada8/fhdfhdhhfdgqnHG8 token=#ed%%h0#w@%1  swfUrl=http://p.jwpcdn.com/6/12/jwplayer.flash.swf live=true timeout=30 swfVfy=true pageUrl=http://ultracast.me'
        return match.group(1)
        #+"|Referer=http://p.jwpcdn.com/6/12/jwplayer.flash.swf"

    def deltatvpw(self,url, referer,options):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        match = re.search('flashvars="file=(.*?)&amp;streamer=(.*?)&amp;',data)
        mylink = ''
        if match:
            mylink = match.group(2) + ' token=Fo5_n0w?U.rA6l3-70w47ch live=true timeout=60 pageUrl=http://deltatv.pw playpath='+match.group(1) + ' swfVfy=http://cdn.deltatv.pw/players.swf'
        return mylink

    def pxstream(self,url,referer,options):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        match = re.search("file: '(.*?)'",data)
        mylink = ''
        if match:
            match2 = re.search("streamer: '(.*?)'",data)
            from urlparse import urlparse
            myparts = urlparse(match2.group(1))
            myurl2 = myparts.scheme +'://'+ myparts.netloc  + ':443' + myparts.path  + '?' +myparts.query
            mylink= myurl2 + ' playpath=' +match.group(1)+ ' swfUrl=http://pxstream.tv/player510.swf pageUrl=http://pxstream.tv/ live=true timeout=30'
        return mylink

    def hdcastme(self,url,referer, options):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        mylink = ''
        match2 = re.search('getJSON\("(.*?)",', data)
        match = re.findall("file: '(.*?)',",data)
        if match2:
            query_data = {'url': match2.group(1), 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
            data2 = self.cm.getURLRequestData(query_data)
            mytoken = re.search('{"token":"(.*?)"}',data2)
            mylink = match[1] + ' live=true timeout=30 pageUrl=http://hdcast.me/ token='+ mytoken.group(1)


        return mylink

    def up4freecom(self,url,referer, options):
        mylink = mrknow_Pageparser.mrknow_Pageparser()
        mylink2 = mylink.pageanalyze(url,referer)
        print mylink2
        return mylink2

    def casttome(self, url, referer,options):
        query_data = { 'url': 'http://filmkodi.com/rtmp_casto.me.txt', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        mylink = self.cm.getURLRequestData(query_data)
        req = urllib2.Request(url)
        req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        print("Linik", link)
        match = re.search('\(\'file\',\'(.*?)\'\);', link)
        match1 = re.search('\(\'streamer\',\'(.*?)\'\);', link)
        mylink2 = mylink + ' playpath=' + match.group(1) + ' swfUrl=http://www.castto.me/_.swf token=#ed%h0#w@1 live=true timeout=30 swfVfy=true pageUrl=' + url
        #rtmp://cdn.castto.me:80/lb playpath=p01Mo9s5t9HTA6F5GdoH swfUrl=http://www.castto.me/_.swf live=true token=#ed%h0#w@1 pageUrl=http://static.castto.me
        print ("Link-3", mylink2, match1, match)
        return mylink2

    def parserVIDTO(self,url,referer,options):
        #url = url.replace('v/','/')
        if not 'embed' in url:
            myparts = urlparse.urlparse(url)
            media_id = myparts.path.split('/')[-1].replace('.html','')
            url = myparts.scheme +'://'+ myparts.netloc  + '/embed-' + media_id + '.html'
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print("Link",link)
        linkvideo = ''
        match = re.compile("<script type=\'text/javascript\'>eval\(function\(p,a,c,k,e,d\)(.*?)\n</script>").findall(link)
        if len(match)>0:
            moje = beautify("eval(function(p,a,c,k,e,d)" + match[0])
            match2 = re.compile('\{label:"(.*?)",file:"(.*?)"\}').findall(moje)
            match3 = re.compile('hd_default:"(.*?)"').findall(moje)
            if len(match2)>0:
                for i in range(len(match2)):
                    if match2[i][0] == match3[0]:
                        linkvideo = match2[i][1]
            return linkvideo
        else:
            return linkvideo

    def parserNOWVIDEO(self, url,referer, options):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match_file = re.compile('flashvars.file="(.+?)";').findall(link)
        match_key = re.compile('var fkzd="(.+?)";').findall(link)           #zmiana detoyy
        if len(match_file) > 0 and len(match_key) > 0:
            get_api_url = ('http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=kino.pecetowiec.pl&file=%s&numOfErrors=0&cid2=undefined&key=%s&cid=undefined') % (match_file[0],match_key[0])  #zmina detoyy
            query_data = { 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link_api = self.cm.getURLRequestData(query_data)
            match_url = re.compile('url=(.+?)&title').findall(link_api)
            if len(match_url) > 0:
                return match_url[0]
            else:
                return ''
        else:
            return ''

    def parserVIDZER(self,url,referer, options):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)

        match = re.search('href="(http[^"]+?getlink[^"]+?)"', link)
        if match:
            url = urllib.unquote( match.group(1) )
            return url


        r = re.search('value="(.+?)" name="fuck_you"', link)
        r2 = re.search('name="confirm" type="submit" value="(.+?)"', link)
        r3 = re.search('<a href="/file/([^"]+?)" target', link)
        if r:
            query_data = { 'url': 'http://www.vidzer.net/e/'+r3.group(1)+'?w=631&h=425', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
            postdata = {'confirm' : r2.group(1), 'fuck_you' : r.group(1)}
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.search("url: '([^']+?)'", link)
            if match:
                url = match.group(1) #+ '|Referer=http://www.vidzer.net/media/flowplayer/flowplayer.commercial-3.2.18.swf'
                return url
            else:
                return ''
        else:
            return ''

    def standard_file(self,url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match2 = re.compile('file: "(.*?)",', re.DOTALL).findall(link)
        if len(match2)>0:
            return match2[0]
        return ''

    def streaminto(self,url,referer, options):
        url = url.replace('video/','')
        if not 'embed' in url:
            myparts = urlparse.urlparse(url)
            url = myparts.scheme +'://'+ myparts.netloc  + myparts.path.replace('/','/embed-') + '-640x360.html'
        print("url",url)
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('streamer: "(.*?)",', re.DOTALL).findall(link)
        match2 = re.compile('file: "(.*?)",', re.DOTALL).findall(link)
        #print("Match",match,link)
        if len(match)>0:
            myvideo = match[0] + ' playpath='+match2[0]+' pageUrl='+url+' swfUrl=http://streamin.to/player/player.swf'
            print("link",myvideo)
            return myvideo
        return ''

    def parsegoodcastme(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://' + referer + '/')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match1 = re.compile('<object type="application/x-shockwave-flash" \n\t\t\t\tdata="(.*?)"').findall(link)
        match2 = re.compile('<param name="flashvars" value="file=(.*?)\&amp\;streamer=(.*?)\&amp\;').findall(link)
        if len(match1) > 0:
            linkVideo = match2[0][1] + ' playpath=' + match2[0][0] + ' live=true timeout=30 swfVfy=true swfUrl=' + \
                        match1[0] + ' token=Fo5_n0w?U.rA6l3-70w47ch pageUrl=' + url
            return linkVideo
        else:
            return False

    def castalbatv(self, url, referer,options):
        myhost = "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0"
        req = urllib2.Request(url)
        req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.compile("'file': (.*?),").findall(link)
        match1 = re.compile("'flashplayer': \"(.*?)\"", ).findall(link)
        match2 = re.compile("'streamer': (.*?),").findall(link)
        linkVideo=''
        if len(match) > 0:
            plik = beautify(match[0])
            plik1 = re.compile("unescape\('(.*?)'\n").findall(plik)
            plik2 = re.compile("unescape\(unescape\('(.*?)'\)").findall(plik)
            plik4 = beautify('unescape(' + plik2[0]+ ')')
            plik5 = plik4.replace('unescape(','').replace(')','')

            if len(plik1) > 0:
                if len(match2)>0:
                    malina2 = re.compile("unescape\('(.*?)'\)").findall(beautify(match2[0]))
                    linkVideo = malina2[0].replace(' ','') + ' playpath=' + plik1[0] + '?'+ plik5 + ' swfUrl=' + match1[0] + ' live=true timeout=30 swfVfy=true pageUrl=' + url

                    return linkVideo
        else:
            return linkVideo

    def shidurlive(self, url, referer,options):
        myhost = "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0"
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': myhost}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('src="(.*?)"').findall(link)
        if len(match) > 0:
            url1 = match[0].replace("'+kol+'", "")
            host = self.getHostName(referer)
            result = ''
            query_data = {'url': match[0], 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False,'return_data': True}
            link = self.cm.getURLRequestData(query_data)
            match1 = re.compile("so.addVariable\(\'file\', \'(.*?)\'\);").findall(link)
            match2 = re.compile("so.addVariable\(\'streamer\', \'(.*?)\'\);").findall(link)
            match3 = re.compile("so.addVariable\('file', unescape\('(.*?)'\)\);").findall(link)
            if match3:
                txtjs = "unescape('" + match3[0] + "');"
                txtjs = match3[0]
                link2 = beautify(txtjs)
                return match2[0] + ' playpath=' + link2.replace(' ','') + ' swfVfy=1 swfUrl=http://cdn.shidurlive.com/player.swf live=true pageUrl=' + url
        return ''

    def firedrivecom(self, url, referer,options):
        myhost = "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0"
        query_data = {'url': url, 'use_host': True, 'host': myhost, 'use_cookie': False, 'use_post': False,
                      'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<input type="hidden" name="confirm" value="(.*?)"/>').findall(link)
        time.sleep(5)
        COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "firedrivecom.cookie"
        query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False,
                      'cookiefile': COOKIEFILE, 'use_post': True, 'return_data': True}
        postdata = {'confirm': match[0]}
        link = self.cm.getURLRequestData(query_data, postdata)
        match1 = re.compile('file: loadURL\(\'(.*?)\'\),').findall(link)
        if len(match1) > 0:
            return match1[0]
        else:
            return ''

    def bixcom(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<source src="(.*?).m3u8">').findall(link)
        if len(match) > 0:
            #return match[0]+ ' playpath='+p['file'][0]+' swfUrl=http://www.freelivestream.tv/swfs/player.swf live=true timeout=30 swfVfy=true pageUrl=http://www.freelivestream.tv/'
            #return match[0]+'.m3u8'
            return "http://live.polwizjer.com/pl/2014tvaxn/playlist.m3u8/key=SFbctmb31JV9q0V11mfPGyB2JuexO5PMINxkAYozw73uKr8glKswx6OhFbU7V7ZnowO1g2LAoQHdTEymclv842GG8zzTikBOIbz4jbc="

        else:
            return ''

    def freelivestreamtv(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('var streamer="(.*?)";').findall(link)
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        if len(match) > 0:
            return match[0] + ' playpath=' + p['file'][
                0] + ' swfUrl=http://www.freelivestream.tv/swfs/player.swf live=true timeout=30 swfVfy=true pageUrl=http://www.freelivestream.tv/'
        else:
            return ''

    def file1npagede(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('file: "(.*?)"').findall(link)
        if len(match) > 0:
            link = match[0]
            return link
        else:
            return ''

    def flexstreamnet(self, url, referer,options):
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        link = 'rtmpe://94.242.228.143:443/loadbalance playpath=' + p['file'][
            0] + ' swfUrl=http://p.jwpcdn.com/6/8/jwplayer.flash.swf live=true timeout=30 swfVfy=true pageUrl=http://flexstream.net/'
        return link

    def abcastbiz(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link2 = self.cm.getURLRequestData(query_data)
        print("Link2222", link2)
        match = re.compile('flashvars=\'file=(.*?)&streamer=rtmp://live.abcast.net/redirect\?(.*?)&amp;displayclick').findall(link2)
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        link = 'rtmp://94.176.148.234:1935/live?'+ match[0][1]+' playpath=' + match[0][0] + ' swfUrl=http://abcast.net/juva.swf live=true timeout=30 swfVfy=true pageUrl=http://abcast.net'
        return link

    def parsererstream(self, url, referer,options):
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        finalurl = res.geturl()
        if finalurl:
            return finalurl
        else:
            return False

    def sevencastnet(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<script type="text/javascript">eval\(function\(p,a,c,k,e,d\)(.*?)\n</script>').findall(link)
        txtjs = "eval(function(p,a,c,k,e,d)" + match[0]
        link2 = beautify(txtjs)
        match_myScrT = re.compile('myScrT.push\(\\\\\'(.*?)\\\\\'\);').findall(link2)
        match_myRtk = re.compile('myRtk.push\(\\\\\'(.*?)\\\\\'\);').findall(link2)
        myScrT = beautify('unescape(\'' + ''.join(match_myScrT) + '\');')
        myRtk = beautify('unescape(\'' + ''.join(match_myRtk) + '\');')
        match_file = re.compile('unescape\(\'(.*?)\'\);').findall(myScrT)
        match_server = re.compile('unescape\(\'(.*?)\'\);').findall(myRtk)
        nUrl = match_server[0] + ' playpath=' + match_file[
            0] + '  live=true timeout=12 swfVfy=true swfUrl=http://7cast.net/jplayer.swf timeout=30 pageUrl=' + referer
        return nUrl

    def fupptvpl(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('file: "(.*?)"').findall(link)
        match1 = re.compile('streamer: "(.*?)"').findall(link)
        #print("Link",match,match1,link)
        if len(match) > 0:
            nUrl = match1[0] + match[
                1] + ' live=true timeout=30 swfVfy=true  swfUrl=http://www.fupptv.pl/media/flash/player510.swf pageUrl=' + referer
            return nUrl
        else:
            return ''

    def maxuploadtv(self, url, referer,options):
        query_data = {'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': False, 'use_post': False,
                      'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "maxuploadtv.cookie"
        query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False,
                      'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
        postdata = {'ok': 'yes', 'Close Ad and Watch as Free User': 'confirm', 'true': 'submited'}
        link = self.cm.getURLRequestData(query_data, postdata)
        match = re.compile("url: \'(.*?)\'\r\n").findall(link)
        #print("Link",match,link)
        if len(match) > 0:

            return match[0]
        else:
            return ''

    def wrzutapl(self, url, referer, options):
        HOST = "User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0"
        query = urlparse.urlparse(url)
        url1 = query.path.split("/")
        url = query.scheme + '://' + query.netloc + '/xml/plik/' + url1[2] + '/wrzuta.pl/sa/963669'
        query_data = {'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False,
                      'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<fileH264Id><!\[CDATA\[(.*?)\]\]></fileH264Id>', re.DOTALL).findall(link)
        match1 = re.compile('<fileHQId><!\[CDATA\[(.*?)\]\]></fileHQId>', re.DOTALL).findall(link)
        match2 = re.compile('<fileMQId><!\[CDATA\[(.*?)\]\]></fileMQId>', re.DOTALL).findall(link)
        match3 = re.compile('<fileId><!\[CDATA\[(.*?)\]\]></fileId>', re.DOTALL).findall(link)

        #print ("AAAAAAAAAAAAAA",match)
        if len(match) > 0:
            return match[0]
        elif len(match1) > 0:
            return match1[0]
        elif len(match2) > 0:
            return match2[0]
        elif len(match3) > 0:
            return match3[0]
        else:
            return ''

    def hqstream(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://jjcast.com/')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match1 = re.compile(
            "<script language=\'javascript\'>\n    var a = (.*?);\nvar b = (.*?);\nvar c = (.*?);\nvar d = (.*?);\nvar f = (.*?);\nvar v_part = \'(.*?)\';\n</script>",
            re.DOTALL).findall(link)

        if len(match1) > 0:
            ip0 = str(int(match1[0][0]) / int(match1[0][4]))
            ip1 = str(int(match1[0][1]) / int(match1[0][4]))
            ip2 = str(int(match1[0][2]) / int(match1[0][4]))
            ip3 = str(int(match1[0][3]) / int(match1[0][4]))
            nUrl = 'rtmp://' + ip0 + '.' + ip1 + '.' + ip2 + '.' + ip3 + match1[0][
                5] + ' live=true swfUrl=http://filo.hqstream.tv/jwp6/jwplayer.flash.swf pageUrl=' + url
            return nUrl

    def jjcast(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://jjcast.com/')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match2 = re.compile("}}return p}\('(.*?)\(\);", re.DOTALL).findall(link)
        match = re.compile(match2[0][2] + ".2\((.*?)\);", re.DOTALL).findall(link)
        match1 = re.compile(match2[0][2] + ".5\((.*?)\);", re.DOTALL).findall(link)
        match3 = re.compile(match2[0][2] + ".6\((.*?)\);", re.DOTALL).findall(link)
        file = ''
        if len(match) > 0:
            for i in range(len(match)):
                file += match[i].replace('\\', '').replace("'", "")
        elif len(match1) > 0:
            for i in range(len(match1)):
                file += match1[i].replace('\\', '').replace("'", "")
        elif len(match3) > 0:
            for i in range(len(match3)):
                file += match3[i].replace('\\', '').replace("'", "")
        #rtmpdump -r "rtmp://streamspot.jjcast.com/redirect" -a "redirect" -f "WIN 11,6,602,180" -W "http://jjcast.com/jplayer.swf" -p "http://jjcast.com/player.php?stream=4janpxr2hf634&width=640&height=360" -y "mjg8jqspviimvs3" -o mjg8jqspviimvs3.f
        link = 'rtmp://31.204.153.133:1935/live playpath=' + file + ' live=true swfUrl=http://jjcast.com/jplayer.swf pageUrl=' + url
        return link

    def stream4(self, url, referer,options):
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        query_data = {'url': 'http://xbmcfilm.com/stream4.tv.txt', 'use_host': False, 'use_cookie': False,
                      'use_post': False, 'return_data': True}
        plink = self.cm.getURLRequestData(query_data)
        plink = plink.replace('\n', '')
        link = plink + ' playpath=' + p['id'][
            0] + ' live=true swfUrl=http://static.stream4.tv/playerg.swf pageUrl=http://stream4.tv/player.php'
        return link

    def byetv(self, url, referer,options):
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        query_data = {'url': 'http://filmkodi.com/rtmp_byetv.org.txt', 'use_host': False, 'use_cookie': False,
                      'use_post': False, 'return_data': True}
        plink = self.cm.getURLRequestData(query_data)

        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': referer, 'User-Agent': HOST}
        query_data = {'url': url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        match = re.search("so.addVariable\('token', '(.*?)'\);",data)
        match1 = re.search("so.addVariable\('file', '(.*?)'\);",data)
        mylink = ''
        if match:
            mylink = plink +match.group(1) + ' playpath=' + match1.group(1) + ' live=true timeout=60 pageUrl=http://www.byetv.org/'
        return mylink

    def parseovcast(self, url, referer,options):
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        link = 'rtmp://share.ovcast.com/live1 playpath=' + p['ch'][0] + ' token=chupem_me_a_pissa live=true'
        return link

    def parseliveflash(self, url, referer,options):
        query_data = {'url': 'http://www.liveflash.tv:1935/loadbalancer', 'use_host': False, 'use_cookie': False,
                      'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        rtmpsrv = link.replace('redirect=', '')
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://' + referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.search("so.addParam\('FlashVars', '(.*?)'\);", link)
        match1 = re.search("'flashplayer': \"(.*?)\",", link)
        link = 'rtmp://' + rtmpsrv + ':1935/stream/ playpath=' + match.group(
            1) + ' swfVfy=1 conn=S:OK live=true swfUrl=http://www.liveflash.tv/resources/scripts/eplayer.swf pageUrl=' + url
        return link

    def sharecastto(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.search('file: "(.*?)",', link)
        match1 = re.search('flashplayer: "(.*?)",', link)
        link = match.group(1) + ' swfUrl=' + match1.group(1) + ' pageUrl=' + url

        return link

    def parseyycast(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://' + referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.search("'file': '(.*?)',", link)
        match1 = re.search("'flashplayer': \"(.*?)\",", link)
        link = 'rtmp://212.7.206.66:1935/live/_definst_ playpath=' + match.group(1) + ' swfUrl=' + match1.group(
            1) + ' pageUrl=' + url
        return link

    def parsegoodcastorg(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.compile(
            '<embed id="player"\n\t\t\t\t\t\tsrc="(.*?)"\n\t\t\t\t\t\twidth="(.*?)"\n\t\t\t\t\t\theight="(.*?)"\n\t\t\t\t\t\tallowscriptaccess="always"\n\t\t\t\t\t\tallowfullscreen="true"\n\t\t\t\t\t\tflashvars="file=(.*?)&amp;streamer=(.*?)&amp;',
            re.DOTALL).findall(link)

        if len(match) > 0:
            linkVideo = match[0][4] + '/' + match[0][3]
            linkVideo = linkVideo + ' pageUrl=' + url + ' swfUrl=' + match[0][0] + ' token=Fo5_n0w?U.rA6l3-70w47ch'
            return linkVideo
        else:
            return False

    def parsegoodcast(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile("file: '(.*?)',").findall(link)
        if len(match1) > 0:
            linkVideo = match1[0] + ' live=true pageUrl=' + url + ' swfUrl=http://goodcast.tv/jwplayer/player.swf'
            #linkVideo = "rtmp://95.211.186.67:1936/live/tvn24?token=ezf129U0OsDwPnbdrRAmAg pageUrl=http://goodcast.tv/tvn24.php swfUrl=http://goodcast.tv/jwplayer/player.swf"
            # rtmpdump -r "rtmp://95.211.186.67:1936/live/" -a "live/" -f "LNX 11,2,202,297" -W "http://goodcast.tv/jwplayer/player.swf" -p "http://goodcast.tv" -y "tvn24?token=ezf129U0OsDwPnbdrRAmAg"
            return linkVideo
        else:
            return False

    def parserSTREAMO(self, url, referer, options):
        return url

    def parseflashwiz(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://' + referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        link = 'rtmpe://46.19.140.18/live playpath=' + p['live'][
            0] + ' pageUrl=http://www.flashwiz.tv/player/player-licensed.swf swfUrl=http://www.flashwiz.tv/player/player-licensed.swf'
        return link


    def parseucaster(self, url, referer,options):
        print ("a", url, referer,options)
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://' + referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.search('"file":      "(.*?)"', link)
        print ("ZZZZzzzz", link)

        if match:
            link = urllib.unquote(match.group(
                1)) + ' pageUrl=http://aliez.tv/live/mlb/ swfUrl=http://player.longtailvideo.com/player.swf app=aliezlive-live live=true tcUrl=rtmp://play.aliez.com/aliezlive-live'
            return link
        else:
            return False

    def parseraliez(self, url, referer,options):
        req = urllib2.Request(url)
        req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.search('"file":(.*?)"(.*?)"', link)
        print ("ZZZZzzzz", match, link)
        print match.group(2)
        if match:
            link = urllib.unquote(match.group(
                2)) + ' pageUrl=http://aliez.tv/live/mlb/ swfUrl=http://player.longtailvideo.com/player.swf app=aliezlive-live live=true tcUrl=rtmp://play.aliez.com/aliezlive-live'
            return link
        else:
            return False

    def parserputlive(self, url, referer,options):
        print ("a", url, referer,options)
        req = urllib2.Request(url)
        req.add_header('Referer', 'http://' + referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        print ("Link", link)
        match = re.compile('html\(unescape\("(.*?)"\)\);').findall(link)
        if len(match) > 0:
            print urllib.unquote(match[0])
            match1 = re.compile('src="(.*?)"').findall(urllib.unquote(match[0]))
            match2 = re.compile('streamer=(.*?)&amp;').findall(urllib.unquote(match[0]))
            match3 = re.compile('file=(.*?)&amp;').findall(urllib.unquote(match[0]))
            print ("Link", match1)
            print ("Link", match2)
            print ("Link", match3)
            return match2[0] + match3[0] + ' pageUrl=' + match1[0] + ' swfUrl=' + match1[0]
            #parsertopupload

    def parsertopupload(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        print ("Url parser Link", url, link)
        match = re.search("'file': '(.*?)'", link)

        if match:
            return match.group(1)
        else:
            return False

    def parserjokerupload(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.search("'file': '(.*?)'", link)
        if match:
            return match.group(1)
        else:
            return False

    def parserLIVEVIEW365(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link22 = self.cm.getURLRequestData(query_data)
        match22 = re.compile("var so = new SWFObject\('(.*?)', 'player'").findall(link22)
        print match22
        match23 = re.compile("so.addVariable\('file', '(.*?)'\);").findall(link22)
        print match23
        #match24=re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link22)
        videolink = 'rtmp://93.114.44.30:1935/cdn2/liveview365 playpath=' + match23[0] + ' swfUrl=' + match22[
            0] + ' pageUrl=' + url + ' live=true swfVfy=true'
        print ("Link", videolink)
        return videolink

    def parserCASTAMP(self, url, referer,options):
        print ("parserCASTAMP", url, referer,options)
        req = urllib2.Request(url)
        req.add_header('Referer', referer)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0')
        response = urllib2.urlopen(req)
        link22 = response.read()
        response.close()
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        print (p['c'])
        match22 = re.compile("'flashplayer': \"(.*?)\",").findall(link22)
        match23 = re.compile("'streamer': '(.*?)',").findall(link22)
        match24 = re.compile("'file': '(.*)',").findall(link22)
        videolink = match23[0] + ' playpath=' + match24[0] + ' swfUrl=' + match22[0] + ' timeout=30 live=true swfVfy=true pageUrl=' + url
        print ("Link", videolink)
        return videolink

    def parserUKCAST(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link22 = self.cm.getURLRequestData(query_data)
        match22 = re.compile("SWFObject\('(.*?)','mpl','','','9'\);").findall(link22)
        match23 = re.compile("so.addVariable\('file', '(.*?)'\);").findall(link22)
        match24 = re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link22)
        videolink = match24[0] + ' playpath=' + match23[0] + ' swfUrl=' + match22[
            0] + ' pageUrl=http://www.ukcast.tv live=true swfVfy=true'
        print ("Link", videolink)
        return videolink

    def parserMIPS(self, url, referer,options):
        query = urlparse.urlparse(url)
        channel = query.path
        channel = channel.replace("/embed/", "")
        params = query.path.split("/")
        print ("Query", query, params)
        return False

        print ("AAAA", match22)
        print ("BBBB", link22)
        if len(match22[1]) > 0:
            videolink = match22[1]
            print ("videolink", match22[1])
            return match22[1]
        else:
            return False

    def parserILIVE(self, url, referer,options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link21 = self.cm.getURLRequestData(query_data)
        print link21,
        match21 = re.compile("<iframe src='(.*?)'").findall(link21)
        print match21
        req = urllib2.Request(match21[0])
        req.add_header('Referer', 'http://' + referer)
        #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link22 = response.read()
        response.close()
        #query_data = { 'url': match21[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        #link22 = self.cm.getURLRequestData(query_data)

        print ("ZZZ", link22)
        match22 = re.compile("file: \"(.*?)\",").findall(link22)
        match23 = re.compile('streamer: "(.*?)",').findall(link22)
        match24 = re.compile("'flash', src: '(.*?)'").findall(link22)
        print match22, match23, match24
        if len(match22) > 0:
            videolink = match23[0] + ' playpath=' + match22[0].replace('.flv', '') + ' swfUrl=' + match24[
                0] + ' pageUrl=' + match21[0] + ' live=true swfVfy=true live=true'
            return videolink
        else:
            return False


    def parserSAWLIVE(self, url, referer,options):
        def decode(tmpurl):
            host = self.getHostName(tmpurl)
            result = ''
            for i in host:
                result += hex(ord(i)).split('x')[1]
            return result

        query = urlparse.urlparse(url)
        channel = query.path
        channel = channel.replace("/embed/", "")
        print("chanel",channel)
        query_data = {'url': 'http://www.sawlive.tv/embed/' + channel, 'use_host': False, 'use_cookie': False,
                      'use_post': False, 'return_data': True, 'header' : {'Referer':  referer, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}}
        link21 = self.cm.getURLRequestData(query_data)

        match = re.compile('eval\(function\(p,a,c,k,e,d\)(.*?)split\(\'\|\'\),0,{}\)\)').findall(link21)

        txtjs = "eval(function(p,a,c,k,e,d)" + match[-1] +"split('|'),0,{}))"
        link2 = beautify(txtjs)
        match21 = re.compile("var escapa = unescape\('(.*?)'\);").findall(link21)
        start = urllib.unquote(match21[0]).find('src="')
        end = len(urllib.unquote(match21[0]))
        url = urllib.unquote(match21[0])[start + 5:end] + '/' + decode(referer)
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link22 = self.cm.getURLRequestData(query_data)
        match22 = re.compile("SWFObject\('(.*?)','mpl','100%','100%','9'\);").findall(link22)
        match23 = re.compile("so.addVariable\('file', '(.*?)'\);").findall(link22)
        match24 = re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link22)
        print ("Match", match22, match23, match24, link22)
        videolink = match24[0] + ' playpath=' + match23[0] + ' swfUrl=' + match22[
            0] + ' pageUrl=http://sawlive.tv/embed/' + channel + ' live=true swfVfy=true'
        return videolink

    def parserREYHQ(self, url, referer, options):
        query = urlparse.urlparse(url)
        channel = query.path
        channel = channel.replace("/", "")
        videolink = 'rtmp://' + '89.248.172.239:1935/live'
        videolink += ' pageUrl=http://www.reyhq.com live=true playpath=' + channel
        videolink += ' swfVfy=http://www.reyhq.com/player/player-licensed.swf'
        print ("videolink", videolink)
        return videolink

    def parserYUKONS(self, url, referer,options):
        query = urlparse.urlparse(url)
        channel = query.path
        channel = channel.replace("/", "")
        decode = ''
        decode2 = ''
        videolink = ''
        tmpheader = {}
        for i in range(len(channel)):
            decode += channel[i].encode("hex")
        for i in range(len(decode)):
            decode2 += decode[i].encode("hex")
        url2 = 'http://yukons.net/yaem/' + decode2
        COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "yukons.cookie"
        tmpheader['Referer'] = 'http://' + referer
        tmpheader['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
        query_data = {'url': url2, 'use_host': True, 'use_header': True, 'header': tmpheader, 'use_cookie': True,
                      'cookiefile': COOKIEFILE, 'save_cookie': True, 'use_post': False, 'return_data': True}
        link1 = self.cm.getURLRequestData(query_data)
        chanell_id = link1.replace("function kunja() { return '", "").replace("'; }", "")
        url3 = 'http://yukons.net/embed/' + decode2 + '/' + chanell_id + '/640/400'
        query_data = {'url': url3, 'use_host': True, 'use_header': True, 'header': tmpheader, 'use_cookie': True,
                      'cookiefile': COOKIEFILE, 'load_cookie': True, 'use_post': False, 'return_data': True}
        link2 = self.cm.getURLRequestData(query_data)
        match = re.compile(
            '<script type="text/javascript">\r\n\t\t\t  \t\t\r\n\t        \t(.*?)\r\n\t        \t\t\t  \t\t  \r\n\t\t\t  \r\n                </script>\n</span>').findall(
            link2)
        if len(match) > 0:
            dane = beautify(match[0])
            match1 = re.compile('so.addParam\((.*?)\)').findall(dane)
            if len(match1) > 0:
                query = urlparse.urlparse(match1[-1].replace("\\'", "").replace('FlashVars,', ''))
                p = urlparse.parse_qs(query.path)
                url4 = 'http://yukons.net/srvload/' + p['id'][0]
                query_data = {'url': url4, 'use_host': False, 'use_cookie': False, 'use_post': False,
                              'return_data': True}
                link3 = self.cm.getURLRequestData(query_data)
                videolink = 'rtmp://' + link3.replace('srv=', '') + ':443/kuyo playpath=' + p['s'][0] + '?id=' + \
                            p['id'][0] + '&pid=' + p['pid'][
                                0] + '  live=true timeout=30 swfUrl=http://yukons.net/yplay2.swf pageUrl=http://yukons.net/'
        #videolink = 'rtmp://173.192.200.79:443/kuyo playpath=jsdhjfsjdaf?id=845e96a40c4d38b379cb05c0b6bc86f6&pid=38392e3233312e3132342e313034 swfUrl=http://yukons.net/yplay2.swf pageUrl=http://yukons.net/'
        return videolink


    def parserVIMEO(self, url, referer, options):
        query = urlparse.urlparse(url)
        p = urlparse.parse_qs(query.query)
        print p
        if len(p) > 0:
            link = "plugin://plugin.video.vimeo/?action=play_video&videoid=" + p['clip_id'][0]
        else:
            tmp = query.path.split("/")
            link = link = "plugin://plugin.video.vimeo/?action=play_video&videoid=" + tmp[1]
        return link

    def parserliveleak(self, url, referer, options):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        match = re.compile('file: "(.+?)",').findall(link)
        print match
        for url in match:
            return url

    def check_url(self, url, referer, options):
        def _head(url):
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
            #print ("URL:", scheme, netloc, path, params, query, fragment)
            connection = httplib.HTTPConnection(netloc)
            connection.request('HEAD', path + '?' + query)
            return connection.getresponse()

        # redirection limit, default of 10
        redirect = 10
        # Perform HEAD
        resp = _head(url)

        while (resp.status >= 300) and (resp.status <= 399):
            # tick the redirect
            redirect -= 1
            # if redirect is 0, we tried :-(
            if redirect == 0:
                # we hit our redirection limit, raise exception
                return False
            # Perform HEAD
            url = resp.getheader('location')
            resp = _head(url)
        if resp.status >= 200 and resp.status <= 299:
            # horray!  We found what we were looking for.
            return True
        else:
            # Status unsure, might be, 404, 500, 401, 403, raise error with actual status code.
            return False


    def parsertosiewytnie(self, url, referer, options):
        movlink = url
        movlink = movlink.replace('/m3', '/h')
        if (self.check_url(movlink)):
            return movlink
        else:
            movlink = movlink.replace('mp4', 'mov')
            return movlink


    def parserYOUTUBE(self, url, referer, options):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        query = urlparse.urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                if len(p) > 0:
                    return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + p['v'][0]
                else:
                    return False
            if query.path[:7] == '/embed/':
                print query
                print query.path.split('/')[2]
                return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + query.path.split('/')[2]
        # fail?
        return None


    def parserPUTLOCKER(self, url, referer, options):
        query_data = {'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': False, 'use_post': False,
                      'return_data': True}
        link = self.cm.getURLRequestData(query_data)

        r = re.search('value="(.+?)" name="fuck_you"', link)
        if r:
            self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
            self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "putlocker.cookie"
            query_data = {'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': True,
                          'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True,
                          'return_data': True}
            postdata = {'fuck_you': r.group(1), 'confirm': 'Close Ad and Watch as Free User'}
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile("playlist: '(.+?)'").findall(link)

            if len(match) > 0:
                print ("PDATA", match)
                url = "http://www.putlocker.com" + match[0]
                query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False,
                              'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False,
                              'return_data': True}
                link = self.cm.getURLRequestData(query_data)
                match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
                print match
                if len(match) > 0:
                    url = match[0].replace('&amp;', '&')
                    print url
                    return url
                    #        else:
                    #          return False
                    #      else:
                    #        return False
        else:
            return ''

    def parserMEGUSTAVID(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('value="config=(.+?)">').findall(link)
        if len(match) > 0:
            p = match[0].split('=')
            url = "http://megustavid.com/media/nuevo/player/playlist.php?id=" + p[1]
            query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('<file>(.+?)</file>').findall(link)
            if len(match) > 0:
                return match[0]
            else:
                return False
        else:
            return False


    def parserHD3D(self, url, referer, options):
        username = ptv.getSetting('hd3d_login')
        password = ptv.getSetting('hd3d_password')
        urlL = 'http://hd3d.cc/login.html'
        self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "hd3d.cookie"
        query_dataL = {'url': urlL, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False,
                       'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
        postdata = {'user_login': username, 'user_password': password}
        data = self.cm.getURLRequestData(query_dataL, postdata)
        query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True,
                      'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile("""url: ["'](.+?)["'],.+?provider:""").findall(link)
        if len(match) > 0:
            ret = match[0]
        else:
            ret = False
        return ret


    def parserSPROCKED(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.search("""url: ['"](.+?)['"],.*\nprovider""", link)
        if match:
            return match.group(1)
        else:
            return False


    def parserODSIEBIE(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        try:
            (v_ext, v_file, v_dir, v_port, v_host) = re.search("\|\|.*SWFObject", link).group().split('|')[40:45]
            url = "http://%s.odsiebie.pl:%s/d/%s/%s.%s" % (v_host, v_port, v_dir, v_file, v_ext);
        except:
            url = False
        return url

    def parserWGRANE(self, url, referer, options):
        hostUrl = 'http://www.wgrane.pl'
        playlist = hostUrl + '/html/player_hd/xml/playlist.php?file='
        key = url[-32:]
        nUrl = playlist + key
        query_data = {'url': nUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.search("""<mainvideo url=["'](.+?)["']""", link)
        if match:
            ret = match.group(1).replace('&amp;', '&')
            return ret
        else:
            return False

    def parserCDA(self, url , referer, showwindow=''):
        query_data = {'url': url.replace('m.cda.pl', 'www.cda.pl'), 'use_host': True, 'host': HOST, 'use_cookie': False,
                      'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.search("""file: ['"](.+?)['"],""", link)
        match2 = re.compile('<a data-quality="(.*?)" (.*?)>(.*?)</a>', re.DOTALL).findall(link)
        match3 = re.search("url: '(.*?)'", link)
        if match2 and showwindow == 'bitrate':
            tab = []
            tab2 = []
            for i in range(len(match2)):
                match3 = re.compile('href="(.*?)"', re.DOTALL).findall(match2[i][1])
                if match3:
                    tab.append('Wideo bitrate - ' + match2[i][2] )
                    tab2.append(match3[0])
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór jakości video", tab)

            if video_menu != "":
                #print("AMAMAMA ",video_menu)
                #print("TABBBBBBBBBBBBBBBBBBBBBBBBB",tab,tab2[video_menu])
                url = match2[video_menu][0]
                query_data = {'url': 'http://www.cda.pl'+tab2[video_menu], 'use_host': True, 'host': HOST, 'use_cookie': False,                       'use_post': False, 'return_data': True}
                link = self.cm.getURLRequestData(query_data)
                match = re.search("""file: ['"](.+?)['"],""", link)
                match3 = re.search("url: '(.*?)'", link)
        if match:
            linkVideo = match.group(1) + '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
        elif match3:
            linkVideo = match3.group(1) + '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
        else:
            linkVideo =  ''
        return linkVideo

    def parserDWN(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.search("""<iframe src="(.+?)&""", link)
        if match:
            query_data = {'url': match.group(1), 'use_host': False, 'use_cookie': False, 'use_post': False,
                          'return_data': True}
            link = self.cm.getURLRequestData(query_data)
        else:
            return False

    def parserANYFILES(self, url, referer, options):
        HOST = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0"
        MAINURL = 'http://video.anyfiles.pl'
        COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "anyfiles.cookie"
        print("COOK",COOKIEFILE)
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': MAINURL, 'User-Agent': HOST}

        u = url.split('/')
        f1Url = MAINURL + "/videos.jsp?id=%s" % (u[-1])
        query_data = {'url': f1Url, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': True,
                      'cookiefile': COOKIEFILE, 'load_cookie': False, 'save_cookie': True, 'use_post': False,
                      'return_data': True}
        data = self.cm.getURLRequestData(query_data)


        fUrl = MAINURL + "/w.jsp?id=%s&width=620&height=349&pos=&skin=0" % (u[-1])
        HEADER = {'Referer' : f1Url,'User-Agent': HOST}
        query_data = { 'url': fUrl, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': True, 'use_post': False, 'return_data': True }
        data = self.cm.getURLRequestData(query_data)

        #add extra cookie
        HEADER['Referer'] = fUrl
        match = re.search("""var flashvars = {[^"]+?config: "([^"]+?)" }""",data)
        if not match:
            match = re.search('src="/?(pcs\?code=[^"]+?)"', data)
        if match:
            query_data = { 'url': MAINURL + '/' + match.group(1), 'use_host': False, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': False, 'use_post': False, 'use_header': True, 'header': HEADER, 'return_data': True }
            data = self.cm.getURLRequestData(query_data)
            print("data",data)
            #match = re.search("""'url':'(http[^']+?mp4)'""",data)
            match = re.search("var source = '(http[^']+?mp4)'",data)

            if match:
                return match.group(1)
            else:
                match = re.search("""'url':'api:([^']+?)'""",data)
                if match:
                    plugin = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + match.group(1)
                    return plugin
        return ''

    def parserWOOTLY(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        c = re.search("""c.value="(.+?)";""", link)
        if c:
            cval = c.group(1)
        else:
            return False
        match = re.compile("""<input type=['"]hidden['"] value=['"](.+?)['"].+?name=['"](.+?)['"]""").findall(link)
        if len(match) > 0:
            postdata = {};
            for i in range(len(match)):
                if (len(match[i][0])) > len(cval):
                    postdata[cval] = match[i][1]
                else:
                    postdata[match[i][0]] = match[i][1]
            self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
            self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "wootly.cookie"
            query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False,
                          'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.search("""<video.*\n.*src=['"](.+?)['"]""", link)
            if match:
                return match.group(1)
            else:
                return False
        else:
            return False

    def parserMAXVIDEO(self, url, referer, options):
        mainUrl = 'http://maxvideo.pl'
        apiVideoUrl = mainUrl + '/api/get_link.php?key=8d00321f70b85a4fb0203a63d8c94f97&v='
        videoHash = url.split('/')[-1]
        print ("ZAW", videoHash)

        query_data = {'url': apiVideoUrl + videoHash, 'use_host': False, 'use_cookie': False, 'use_post': False,
                      'return_data': True}
        data = self.cm.getURLRequestData(query_data, {'v': videoHash})
        result = simplejson.loads(data)
        print result
        result = dict([(str(k), v) for k, v in result.items()])
        if 'error' in result:
            videoUrl = ''
        else:
            videoUrl = result['ok'].encode('UTF-8')
        return videoUrl + '|Referer=http://maxvideo.pl/mediaplayer/player.swf'

    def parserVIDEOWEED(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match_domain = re.compile('flashvars.domain="(.+?)"').findall(link)
        match_file = re.compile('flashvars.file="(.+?)"').findall(link)
        match_filekey = re.compile('flashvars.filekey="(.+?)"').findall(link)
        if len(match_domain) > 0 and len(match_file) > 0 and len(match_filekey) > 0:
            get_api_url = ('%s/api/player.api.php?user=undefined&codes=1&file=%s&pass=undefined&key=%s') % (
            match_domain[0], match_file[0], match_filekey[0])
            link_api = {'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False,
                        'return_data': True}
            if 'url' in link_api:
                parser = Parser.Parser()
                params = parser.getParams(link_api)
                return parser.getParam(params, "url")
            else:
                return False
        else:
            return False

    def parserNOVAMOV(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match_file = re.compile('flashvars.file="(.+?)";').findall(link)
        match_key = re.compile('flashvars.filekey="(.+?)";').findall(link)
        print "match_key", match_key, match_file
        if len(match_file) > 0 and len(match_key) > 0:
            get_api_url = (
                          'http://www.novamov.com/api/player.api.php?key=%s&user=undefined&codes=1&pass=undefined&file=%s') % (
                          match_key[0], match_file[0])
            link_api = self.cm.getURLRequestData(
                {'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
            match_url = re.compile('url=(.+?)&title').findall(link_api)
            if len(match_url) > 0:
                return match_url[0]
            else:
                return False

    def parserSOCKSHARE(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        r = re.search('value="(.+?)" name="fuck_you"', link)
        if r:
            self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
            self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "sockshare.cookie"
            postdata = {'fuck_you': r.group(1), 'confirm': 'Close Ad and Watch as Free User'}
            query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False,
                          'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
            link = self.cm.getURLRequestData(query_data, postdata)
            match = re.compile("playlist: '(.+?)'").findall(link)
            if len(match) > 0:
                url = "http://www.sockshare.com" + match[0]
                query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False,
                              'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False,
                              'return_data': True}
                link = self.cm.getURLRequestData(query_data)
                match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
                if len(match) > 0:
                    url = match[0].replace('&amp;', '&')
                    return url
                else:
                    return False
            else:
                return False
        else:
            return False

    def parserRAPIDVIDEO(self, url, referer, options):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.search("""'(.+?)','720p'""", link)
        if match:
            return match.group(1)
        else:
            return False

    def parserVIDEOSLASHER(self, url, referer, options):
        self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "videoslasher.cookie"
        query_data = {'url': url.replace('embed', 'video'), 'use_host': False, 'use_cookie': True, 'save_cookie': True,
                      'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
        postdata = {'confirm': 'Close Ad and Watch as Free User', 'foo': 'bar'}
        data = self.cm.getURLRequestData(query_data, postdata)

        match = re.compile("playlist: '/playlist/(.+?)'").findall(data)
        if len(match) > 0:
            query_data = {'url': 'http://www.videoslasher.com//playlist/' + match[0], 'use_host': False,
                          'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE,
                          'use_post': True, 'return_data': True}
            data = self.cm.getURLRequestData(query_data)
            match = re.compile('<title>Video</title><media:content url="(.+?)"').findall(data)
            if len(match) > 0:
                sid = self.cm.getCookieItem(self.COOKIEFILE, 'authsid')
                if sid != '':
                    streamUrl = match[0] + '|Cookie="authsid=' + sid + '"'
                    return streamUrl
                else:
                    return False
            else:
                return False
        else:
            return False


    def parseStign(self, string):
        out = string
        for i in range(len(CHARS)):
            out = string.replace(CHARS[i][0], CHARS[i][1])
            string = out
        return out

