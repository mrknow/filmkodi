# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys, math
import xbmcaddon, xbmc, xbmcgui
import urlparse
import httplib 

try:
    import simplejson as json
except ImportError:
    import json

scriptID = 'plugin.video.mrknow'
scriptname = "Polish Live TV"
ptv = xbmcaddon.Addon(scriptID)

import z_pLog, mrknow_Parser, settings, libCommon,xppod
#import maxvideo, anyfiles

log = z_pLog.pLog()
sets = settings.TVSettings()

CHARS = [
    [ 'F', 'a' ],
    [ 'a', 'F' ],
    [ 'A', 'f' ],
    [ 'k', 'B' ],
    [ 'K', 'b' ],
    [ 'b', 'K' ],
    [ 'B', 'k' ],
    [ 'm', 'I' ],
    [ 'M', 'i' ],
    [ 'i', 'M' ],
    [ 'I', 'm' ],
    [ 'D', 'x' ],
    [ 'x', 'D' ],
    [ 'O', 'y' ],
    [ 'y', 'O' ],
    [ 'C', 'z' ],
    [ 'z', 'C' ],   
]    

class urlparser:
  def __init__(self):
    self.cm = libCommon.common()


  def hostSelect(self, v):
    hostUrl = False
    d = xbmcgui.Dialog()
    if len(v) > 0:
      valTab = []
      for i in range(len(v)):
        valTab.append(str(i+1) + '. ' + self.getHostName(v[i], True))
      item = d.select("Wybor hostingu", valTab)
      if item >= 0: hostUrl = v[item]
    else: d.ok ('Brak linkow','Przykro nam, ale nie znalezlismy zadnego linku do video.', 'Sproboj ponownie za jakis czas')
    return hostUrl


  def getHostName(self, url, nameOnly = False):
    hostName = ''       
    match = re.search('http://(.+?)/',url)
    match1 = re.search('https://(.+?)/',url)
    
    if match:
      hostName = match.group(1)
      if (nameOnly):
        n = hostName.split('.')
        hostName = n[-2]
    elif match1:
      hostName = match1.group(1)
      if (nameOnly):
        n = hostName.split('.')
        hostName = n[-2]
        
    return hostName


  def getVideoLink(self, url,referer=''):
    nUrl=''
    host = self.getHostName(url)
    log.info("uvideo hosted by: " + host)
    log.info('URL: '+url + ' ' +referer)
    
    if host == 'www.putlocker.com':
        nUrl = self.parserPUTLOCKER(url)
    if host == 'www.sockshare.com':
        nUrl = self.parserSOCKSHARE(url)
    if host == 'megustavid.com' or host == 'www.megustavid.com':
        nUrl = self.parserMEGUSTAVID(url)
    if host == 'hd3d.cc':
        nUrl = self.parserHD3D(url)
    if host == 'sprocked.com':
        nUrl = self.parserSPROCKED(url)
    if host == 'odsiebie.pl':
        nUrl = self.parserODSIEBIE(url) 
    if host == 'www.wgrane.pl':
        nUrl = self.parserWGRANE(url)
    if host == 'www.cda.pl' or host == 'ebd.cda.pl' or host =='cda.pl':
        nUrl = self.parserCDA(url)
    if host == 'maxvideo.pl' or host == 'nextvideo.pl':
        nUrl = self.parserMAXVIDEO(url)
    if host == 'video.anyfiles.pl':
        nUrl = self.parserANYFILES(url)
    if host == 'www.videoweed.es' or host == 'www.videoweed.com' or host == 'videoweed.es' or host == 'videoweed.com':
        nUrl = self.parserVIDEOWEED(url)
    if host== 'www.novamov.com' or host == 'embed.novamov.com':
        nUrl = self.parserNOVAMOV(url)
    if host== 'www.nowvideo.eu':
        nUrl = self.parserNOWVIDEO(url)
    if host== 'www.rapidvideo.com':
        nUrl = self.parserRAPIDVIDEO(url)
    if host== 'www.videoslasher.com':
        nUrl = self.parserVIDEOSLASHER(url) 
    if host== 'www.youtube.com':
        nUrl = self.parserYOUTUBE(url)  
    if host== 'stream.streamo.tv':
        nUrl = self.parserSTREAMO(url)  
    if host== 'tosiewytnie.pl':
        nUrl = self.parsertosiewytnie(url)  
    if host== 'www.liveleak.com':
        nUrl = self.parserliveleak(url) 
    if host== 'vimeo.com':
        nUrl = self.parserVIMEO(url)    
    if host== 'yukons.net':
        nUrl = self.parserYUKONS(url)
    if host== 'www.reyhq.com':
        nUrl = self.parserREYHQ(url)      
    if host== 'www.sawlive.tv':
        nUrl = self.parserSAWLIVE(url,referer)  
    if host== 'www.ilive.to':
        nUrl = self.parserILIVE(url,referer)      
    if host== 'mips.tv':
        nUrl = self.parserMIPS(url,referer)      
    if host== 'www.ukcast.tv':
        nUrl = self.parserUKCAST(url,referer)              
    if host== 'castamp.com':
        nUrl = self.parserCASTAMP(url,referer)   
    if host== 'liveview365.tv':
        nUrl = self.parserLIVEVIEW365(url,referer)   
    if host== 'www.jokerupload.com':
        nUrl = self.parserjokerupload(url)   
    if host== 'www.topupload.tv':
        nUrl = self.parsertopupload(url)   
    if host== 'www.putlive.in':
        nUrl = self.parserputlive(url,referer)   
    if host== 'emb.aliez.tv':
        nUrl = self.parseraliez(url,referer)   
    if host== 'www.ucaster.eu':
        nUrl = self.parseucaster(url,referer)   
    if host== 'www.flashwiz.tv':
        nUrl = self.parseflashwiz(url,referer)   
    if host== 'goodcast.tv':
        nUrl = self.parsegoodcast(url)   
    if host== 'goodcast.org':
        nUrl = self.parsegoodcastorg(url,referer)   
    if host== 'sharecast.to':
        nUrl = self.sharecastto(url,referer)   
    if host== 'www.yycast.com':
        nUrl = self.parseyycast(url,referer)   
    if host== 'www.liveflash.tv':
        nUrl = self.parseliveflash(url,referer)           
    if host== 'ovcast.com':
        nUrl = self.parseovcast(url,referer)           
    if host== 'stream4.tv':
        nUrl = self.stream4(url,referer)           
    if host== 'jjcast.com':
        nUrl = self.jjcast(url,referer)           
    if host.find("wrzuta.pl") > -1:
        nUrl = self.wrzutapl(url)  
    if host== 'hqstream.tv':
        nUrl = self.hqstream(url,referer)           
    if host== 'maxupload.tv':
        nUrl = self.maxuploadtv(url,referer)           
            
    return nUrl


  def maxuploadtv(self,url,referer):
    query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)    

    #r = re.search('value="(.+?)" name="fuck_you"', link)
    #if r:
   
    #self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "maxuploadtv.cookie"
    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
    postdata = {'ok':'yes', 'Close Ad and Watch as Free User':'confirm', 'true': 'submited'}
    link = self.cm.getURLRequestData(query_data, postdata)
    match = re.compile("url: \'(.*?)\'\r\n").findall(link)
    #print("Link",match,link)
    if len(match) > 0:
    #    print ("PDATA",match)
    #    url = "http://www.putlocker.com" + match[0]
    #    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
    #    link = self.cm.getURLRequestData(query_data)
    #    match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
    #    print match
    #    if len(match) > 0:
    #      url = match[0].replace('&amp;','&')
    #      print url
    #      return url
#        else:
#          return False
#      else:
        return match[0]
    else:
      return ''
    
  def wrzutapl(self, url):
    HOST = "User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0"
    query = urlparse.urlparse(url)
    url1 = query.path.split("/")
    url = query.scheme + '://' + query.netloc+ '/xml/plik/' + url1[2] +'/wrzuta.pl/sa/963669'
    query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    print ("Link",link)
    match = re.compile('<fileH264Id><!\[CDATA\[(.*?)\]\]></fileH264Id>', re.DOTALL).findall(link)
    match1 = re.compile('<fileHQId><!\[CDATA\[(.*?)\]\]></fileHQId>', re.DOTALL).findall(link)
    match2 = re.compile('<fileMQId><!\[CDATA\[(.*?)\]\]></fileMQId>', re.DOTALL).findall(link)
    match3 = re.compile('<fileId><!\[CDATA\[(.*?)\]\]></fileId>', re.DOTALL).findall(link)
    
    #print ("AAAAAAAAAAAAAA",match)
    if len(match)>0:
        return match[0]
    elif len(match1)>0:
        return match1[0]
    elif len(match2)>0:
        return match2[0]
    elif len(match3)>0:
        return match3[0]
    else:
        return ''
  def hqstream(self,url,referer):
    req = urllib2.Request(url)
    req.add_header('Referer', 'http://jjcast.com/')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match1 = re.compile("<script language=\'javascript\'>\n    var a = (.*?);\nvar b = (.*?);\nvar c = (.*?);\nvar d = (.*?);\nvar f = (.*?);\nvar v_part = \'(.*?)\';\n</script>", re.DOTALL).findall(link)
    
    print("Matc",link)
    print("Matc",match1)
    if len(match1) > 0:
        ip0 = str(int(match1[0][0]) / int(match1[0][4]))
        ip1 = str(int(match1[0][1]) / int(match1[0][4]))
        ip2 = str(int(match1[0][2]) / int(match1[0][4]))
        ip3 = str(int(match1[0][3]) / int(match1[0][4]))
        nUrl = 'rtmp://' + ip0 + '.' + ip1 + '.' + ip2 + '.' + ip3 + match1[0][5] + ' live=true swfUrl=http://filo.hqstream.tv/jwp6/jwplayer.flash.swf pageUrl='+url
        print nUrl
        return nUrl
    
        
  def jjcast(self,url,referer):
    req = urllib2.Request(url)
    req.add_header('Referer', 'http://jjcast.com/')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match2 = re.compile("}}return p}\('(.*?)\(\);", re.DOTALL).findall(link)
    match = re.compile(match2[0][2]+".2\((.*?)\);", re.DOTALL).findall(link)
    match1 = re.compile(match2[0][2]+".5\((.*?)\);", re.DOTALL).findall(link)    
    match3 = re.compile(match2[0][2]+".6\((.*?)\);", re.DOTALL).findall(link)    
    file = ''
    if len(match) > 0:
            for i in range(len(match)):
                print match[i].replace('\\','').replace("'","")
                file += match[i].replace('\\','').replace("'","")
    elif len(match1) > 0:
            for i in range(len(match1)):
                print match1[i].replace('\\','').replace("'","")
                file += match1[i].replace('\\','').replace("'","")
    elif len(match3) > 0:
            for i in range(len(match3)):
                print match3[i].replace('\\','').replace("'","")
                file += match3[i].replace('\\','').replace("'","")
    #rtmpdump -r "rtmp://streamspot.jjcast.com/redirect" -a "redirect" -f "WIN 11,6,602,180" -W "http://jjcast.com/jplayer.swf" -p "http://jjcast.com/player.php?stream=4janpxr2hf634&width=640&height=360" -y "mjg8jqspviimvs3" -o mjg8jqspviimvs3.f
    link = 'rtmp://31.204.153.133:1935/live playpath='+file+' live=true swfUrl=http://jjcast.com/jplayer.swf pageUrl='+url
    return link
        
  def stream4(self,url,referer):
    query = urlparse.urlparse(url)
    p = urlparse.parse_qs(query.query)
    query_data = { 'url': 'http://xbmcfilm.com/stream4.tv.txt', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    plink = self.cm.getURLRequestData(query_data)
    plink = plink.replace('\n','')
    link = plink+' playpath='+p['id'][0]+' live=true swfUrl=http://static.stream4.tv/playerg.swf pageUrl=http://stream4.tv/player.php'
    return link
    
    
  def parseovcast(self,url,referer):
    query = urlparse.urlparse(url)
    p = urlparse.parse_qs(query.query)
    print p
    print ("LINK",url)
    link = 'rtmp://share.ovcast.com/live1 playpath='+p['ch'][0]+' token=chupem_me_a_pissa live=true'
#    print link
    return link
    
  def parseliveflash(self,url,referer):
    query_data = { 'url': 'http://www.liveflash.tv:1935/loadbalancer', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    rtmpsrv = link.replace('redirect=','')  
    req = urllib2.Request(url)
    req.add_header('Referer', 'http://'+referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = re.search("so.addParam\('FlashVars', '(.*?)'\);",link)
    match1 = re.search("'flashplayer': \"(.*?)\",",link)
    link = 'rtmp://'+rtmpsrv+':1935/stream/ playpath='+match.group(1)+' swfVfy=1 conn=S:OK live=true swfUrl=http://www.liveflash.tv/resources/scripts/eplayer.swf pageUrl='+url
    print link
    #C:\Users\domw\Downloads\rtmpdump-2.4-git-010913-windows>rtmpdump.exe -r rtmp://174.37.252.220:1935/stream/ --playpath="id=91677&s=x4537456754&g=1&a=1&l="  --swfUrl=http://www.liveflash.tv/resources/scripts/eplayer.swf --pageUrl=http://www.liveflash.tv/embedplayer/x4537456754/1/640/480 -z -v --conn=S:OK
    return link
    

  def sharecastto(self,url,referer):
    req = urllib2.Request(url)
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = re.search('file: "(.*?)",',link)
    match1 = re.search('flashplayer: "(.*?)",',link)
    print ("Link-3",referer,match1,link)
    link = match.group(1)+' swfUrl='+match1.group(1)+' pageUrl='+url

    return link
  
  
  def parseyycast(self,url,referer):

    

    req = urllib2.Request(url)
    req.add_header('Referer', 'http://'+referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = re.search("'file': '(.*?)',",link)
    match1 = re.search("'flashplayer': \"(.*?)\",",link)
    link = 'rtmp://212.7.206.66:1935/live/_definst_ playpath='+match.group(1)+' swfUrl='+match1.group(1)+' pageUrl='+url
    return link
    
  def parsegoodcastorg(self,url,referer):
    req = urllib2.Request(url)
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    print ('LINK',url,referer,link)
    match = re.compile('<embed id="player"\n\t\t\t\t\t\tsrc="(.*?)"\n\t\t\t\t\t\twidth="(.*?)"\n\t\t\t\t\t\theight="(.*?)"\n\t\t\t\t\t\tallowscriptaccess="always"\n\t\t\t\t\t\tallowfullscreen="true"\n\t\t\t\t\t\tflashvars="file=(.*?)&amp;streamer=(.*?)&amp;', re.DOTALL).findall(link)
    print ('MATCH',match)
    
    if len(match)>0:
        linkVideo = match[0][4] + '/'+match[0][3]
        linkVideo = linkVideo + ' pageUrl='+url+' swfUrl='+match[0][0]
        print ("linkVideo",linkVideo)
        return linkVideo
    else:
        return False
  def parsegoodcast(self,url):
  
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match1=re.compile("file: '(.*?)',").findall(link)
    if len(match1)>0:
        linkVideo =  match1[0] +' live=true pageUrl='+url+' swfUrl=http://goodcast.tv/jwplayer/player.swf'
        #linkVideo = "rtmp://95.211.186.67:1936/live/tvn24?token=ezf129U0OsDwPnbdrRAmAg pageUrl=http://goodcast.tv/tvn24.php swfUrl=http://goodcast.tv/jwplayer/player.swf"
        # rtmpdump -r "rtmp://95.211.186.67:1936/live/" -a "live/" -f "LNX 11,2,202,297" -W "http://goodcast.tv/jwplayer/player.swf" -p "http://goodcast.tv" -y "tvn24?token=ezf129U0OsDwPnbdrRAmAg"
        print ("LinkVideo", linkVideo)
        return linkVideo
    else:
        return False
    
    
  def parserSTREAMO(self,url):
    return url
    
  def parseflashwiz(self,url,referer):
    print ("Zaa",url,referer)
    req = urllib2.Request(url)
    req.add_header('Referer', 'http://'+referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    print link
    #rtmpdump -r "rtmpe://46.19.140.18/live" -a "live" -f "WIN 11,6,602,180" -W "http://www.flashwiz.tv/player/player-licensed.swf" -p "http://www.flashwiz.tv/embed.php?live=gregrehherh&vw=600&vh=400" -y "gregrehherh" -o gregrehherh.flv
    query = urlparse.urlparse(url)
    p = urlparse.parse_qs(query.query)
    print p['live']
    link = 'rtmpe://46.19.140.18/live playpath='+p['live'][0]+' pageUrl=http://www.flashwiz.tv/player/player-licensed.swf swfUrl=http://www.flashwiz.tv/player/player-licensed.swf' 
    return link
    
    
  def parseucaster(self,url,referer):
    print ("a",url,referer)
    req = urllib2.Request(url)
    req.add_header('Referer', 'http://'+referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = re.search('"file":      "(.*?)"',link)
    print ("ZZZZzzzz",link)
    
    if match:   
       link = urllib.unquote(match.group(1)) + ' pageUrl=http://aliez.tv/live/mlb/ swfUrl=http://player.longtailvideo.com/player.swf app=aliezlive-live live=true tcUrl=rtmp://play.aliez.com/aliezlive-live'
       return link
    else: 
      return False

  def parseraliez(self,url,referer):
    req = urllib2.Request(url)
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = re.search('"file":(.*?)"(.*?)"',link)
    print ("ZZZZzzzz",match,link)
    print match.group(2)
    if match:   
       link = urllib.unquote(match.group(2)) + ' pageUrl=http://aliez.tv/live/mlb/ swfUrl=http://player.longtailvideo.com/player.swf app=aliezlive-live live=true tcUrl=rtmp://play.aliez.com/aliezlive-live'
       return link
    else: 
      return False

  def parserputlive(self,url,referer):
    print ("a",url,referer)
    req = urllib2.Request(url)
    req.add_header('Referer', 'http://'+referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    print ("Link",link)
    match = re.compile('html\(unescape\("(.*?)"\)\);').findall(link)
    if len(match)>0:
        print urllib.unquote(match[0])
        match1 = re.compile('src="(.*?)"').findall(urllib.unquote(match[0]))
        match2 = re.compile('streamer=(.*?)&amp;').findall(urllib.unquote(match[0]))
        match3 = re.compile('file=(.*?)&amp;').findall(urllib.unquote(match[0]))
        print ("Link",match1)
        print ("Link",match2)
        print ("Link",match3)
        return match2[0] + match3[0] + ' pageUrl='+ match1[0]+' swfUrl='+ match1[0]
#parsertopupload
        
  def parsertopupload(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    print ("Url parser Link",url,link)
    match = re.search("'file': '(.*?)'",link)

    if match:   
      return match.group(1)
    else: 
      return False
  def parserjokerupload(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.search("'file': '(.*?)'",link)
    if match:   
      return match.group(1)
    else: 
      return False
    
  def parserLIVEVIEW365(self,url,referer):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link22 = self.cm.getURLRequestData(query_data)
    match22=re.compile("var so = new SWFObject\('(.*?)', 'player'").findall(link22)
    print match22
    match23=re.compile("so.addVariable\('file', '(.*?)'\);").findall(link22)
    print match23
    #match24=re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link22)
    videolink = 'rtmp://93.114.44.30:1935/cdn2/liveview365 playpath=' +match23[0] + ' swfUrl=' + match22[0] + ' pageUrl='+url+' live=true swfVfy=true'
    print ("Link",videolink)
    return videolink

  def parserCASTAMP(self,url,referer):
    print url,referer
    req = urllib2.Request(url)
    req.add_header('Referer', referer)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link22=response.read()
    response.close()
    query = urlparse.urlparse(url)
    p = urlparse.parse_qs(query.query)
    print p['c']
    match22=re.compile("'flashplayer': \"(.*?)\",").findall(link22)
    match23=re.compile("'streamer': '(.*?)',").findall(link22)
    match24=re.compile("'file': '(.*)',").findall(link22)
    #rtmpdump -r "rtmpe://204.45.157.74/live" -a "live" -f "WIN 11,6,602,171" -W "http://www.udemy.com/static/flash/player5.9.swf" -p "http://www.castamp.com/embed.php?c=ilmecz&tk=1dGwTOdu&vwidth=640&vheight=480" -y "ilmecz" -o ilmecz.flv
    videolink = match23[0] + ' playpath=' +p['c'][0] + ' swfUrl=' + match22[0] + ' pageUrl=http://castamp.com/embed.php'
    print ("Link",videolink)
    return videolink

  def parserUKCAST(self,url,referer):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link22 = self.cm.getURLRequestData(query_data)
    match22=re.compile("SWFObject\('(.*?)','mpl','','','9'\);").findall(link22)
    match23=re.compile("so.addVariable\('file', '(.*?)'\);").findall(link22)
    match24=re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link22)
    videolink = match24[0] + ' playpath=' +match23[0] + ' swfUrl=' + match22[0] + ' pageUrl=http://www.ukcast.tv live=true swfVfy=true'
    print ("Link",videolink)
    return videolink

  def parserMIPS(self,url,referer):
    query = urlparse.urlparse(url)
    channel = query.path
    channel=channel.replace("/embed/","")
    params = query.path.split("/")
    print ("Query",query,params)
    return False

    
    print ("AAAA",match22)
    print ("BBBB",link22)
    if len(match22[1]) > 0:
        videolink = match22[1]
        print ("videolink", match22[1])
        return match22[1]
    else:
        return False
    
  def parserILIVE(self,url,referer):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link21 = self.cm.getURLRequestData(query_data)
    print link21,
    match21=re.compile("<iframe src='(.*?)'").findall(link21)
    print match21
    req = urllib2.Request(match21[0])
    req.add_header('Referer', 'http://'+referer)
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link22=response.read()
    response.close()
    #query_data = { 'url': match21[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    #link22 = self.cm.getURLRequestData(query_data)
    
    print ("ZZZ",link22)
    match22=re.compile("file: \"(.*?)\",").findall(link22)
    match23=re.compile('streamer: "(.*?)",').findall(link22)
    match24=re.compile("'flash', src: '(.*?)'").findall(link22)
    print match22,match23,match24
    if len(match22) > 0:
        videolink = match23[0] + ' playpath=' +match22[0].replace('.flv','') + ' swfUrl=' + match24[0] + ' pageUrl='+ match21[0] +' live=true swfVfy=true live=true'
        return videolink
    else:
        return False

    
  def parserSAWLIVE(self,url,referer):
    def decode(tmpurl):
        host = self.getHostName(tmpurl)
        result = ''
        for i in host:
            result += hex(ord(i)).split('x')[1]
        return result
 
    query = urlparse.urlparse(url)
    channel = query.path
    channel=channel.replace("/embed/","")
    query_data = { 'url': 'http://www.sawlive.tv/embed/' + channel, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link21 = self.cm.getURLRequestData(query_data)
    match21=re.compile("var escapa = unescape\('(.*?)'\);").findall(link21)
    start= urllib.unquote(match21[0]).find('src="')
    end = len(urllib.unquote(match21[0]))
#    print("SAW:",link21,match21)
    url =  urllib.unquote(match21[0])[start+5:end] + '/' + decode(referer)
#        url =  urllib.unquote(match21[0])[start+5:end] +'/7777772e64726874762e636f6d2e706c'
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link22 = self.cm.getURLRequestData(query_data)
    match22=re.compile("SWFObject\('(.*?)','mpl','100%','100%','9'\);").findall(link22)
    match23=re.compile("so.addVariable\('file', '(.*?)'\);").findall(link22)
    match24=re.compile("so.addVariable\('streamer', '(.*?)'\);").findall(link22)
    print ("Match",match22,match23,match24,link22)
    videolink = match24[0] + ' playpath=' +match23[0] + ' swfUrl=' + match22[0] + ' pageUrl=http://sawlive.tv/embed/' +channel + ' live=true swfVfy=true'
    return videolink

  def parserREYHQ(self,url):
    query = urlparse.urlparse(url)
    channel = query.path
    channel=channel.replace("/","")
    videolink = 'rtmp://' + '89.248.172.239:1935/live' 
    videolink += ' pageUrl=http://www.reyhq.com live=true playpath='+channel
    videolink += ' swfVfy=http://www.reyhq.com/player/player-licensed.swf'
    print ("videolink", videolink)
    return videolink

  def parserYUKONS(self,url):
    query = urlparse.urlparse(url)
    channel = query.path
    channel=channel.replace("/","")
    query_data = { 'url': 'http://yukons.net/lb.php', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link1 = self.cm.getURLRequestData(query_data)
    link1 = link1.replace("srv=", "");
    #"rtmp://198.144.158.83:443/kuyo" --app "kuyo" --flashVer "LNX 11,2,202,273" --swfVfy "http://yukons.net/yukplay.swf" 
    #--pageUrl  "http://yukons.net" --playpath "drhtvvekko" -o drhtvvekko.flv
    videolink = 'rtmp://198.144.158.83:443/kuyo app=kuyo playpath=' + channel 
    videolink += ' pageUrl=http://yukons.net live=true'
    videolink += ' swfVfy=http://yukons.net/yukplay.swf'
    #print ("videolink", videolink)
    return videolink


  def parserVIMEO(self,url):
    query = urlparse.urlparse(url)
    p = urlparse.parse_qs(query.query)
    print p
    if len(p) > 0:
        link = "plugin://plugin.video.vimeo/?action=play_video&videoid=" + p['clip_id'][0]
    else:
        tmp = query.path.split("/")
        link = link = "plugin://plugin.video.vimeo/?action=play_video&videoid=" +tmp[1]
    return link

  def parserliveleak(self,url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('file: "(.+?)",').findall(link)
    print match
    for url in match:
      return url
          
        
  def check_url(self,url):
    def _head(url):
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
        #print ("URL:", scheme, netloc, path, params, query, fragment)
        connection = httplib.HTTPConnection(netloc)
        connection.request('HEAD',  path  +'?'+ query ) 
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

    
  def parsertosiewytnie(self,url):
    movlink = url
    movlink = movlink.replace('/m3', '/h')
    if (self.check_url(movlink)):
        return movlink
    else:
        movlink = movlink.replace('mp4', 'mov')
        return movlink
 

  def parserYOUTUBE(self,url):
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
            print p
            if len(p) > 0:
		return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + p['v'][0]
	    else:
		return ''
        if query.path[:7] == '/embed/':
            print query
            print query.path.split('/')[2]
            return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + query.path.split('/')[2]
    # fail?
    return None        

    

  def parserPUTLOCKER(self,url):
    query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)    

    r = re.search('value="(.+?)" name="fuck_you"', link)
    if r:
      self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
      self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "putlocker.cookie"
      query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
      postdata = {'fuck_you' : r.group(1), 'confirm' : 'Close Ad and Watch as Free User'}
      link = self.cm.getURLRequestData(query_data, postdata)
      match = re.compile("playlist: '(.+?)'").findall(link)

      if len(match) > 0:
        print ("PDATA",match)
        url = "http://www.putlocker.com" + match[0]
        query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
        print match
        if len(match) > 0:
          url = match[0].replace('&amp;','&')
          print url
          return url
#        else:
#          return False
#      else:
#        return False
    else:
      return ''

  def parserMEGUSTAVID(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)    
    match = re.compile('value="config=(.+?)">').findall(link)
    if len(match) > 0:
      p = match[0].split('=')
      url = "http://megustavid.com/media/nuevo/player/playlist.php?id=" + p[1]
      query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
      link = self.cm.getURLRequestData(query_data)      
      match = re.compile('<file>(.+?)</file>').findall(link)
      if len(match) > 0:
        return match[0]
      else:
        return False
    else: 
      return False


  def parserHD3D(self,url):
    username = ptv.getSetting('hd3d_login')
    password = ptv.getSetting('hd3d_password')
    urlL = 'http://hd3d.cc/login.html'
    self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "hd3d.cookie"
    query_dataL = { 'url': urlL, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
    postdata = {'user_login': username, 'user_password': password}
    data = self.cm.getURLRequestData(query_dataL, postdata)
    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.compile("""url: ["'](.+?)["'],.+?provider:""").findall(link)
    if len(match) > 0:
      ret = match[0]
    else:
     ret = False
    return ret


  def parserSPROCKED(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.search("""url: ['"](.+?)['"],.*\nprovider""",link)
    if match:    
      return match.group(1)
    else: 
      return False


  def parserODSIEBIE(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    try:
      (v_ext, v_file, v_dir, v_port, v_host) = re.search("\|\|.*SWFObject",link).group().split('|')[40:45]
      url = "http://%s.odsiebie.pl:%s/d/%s/%s.%s" % (v_host, v_port, v_dir, v_file, v_ext);
    except:
      url = False
    return url


  def parserWGRANE(self,url):
    hostUrl = 'http://www.wgrane.pl'            
    playlist = hostUrl + '/html/player_hd/xml/playlist.php?file='
    key = url[-32:]
    nUrl = playlist + key
    query_data = { 'url': nUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.search("""<mainvideo url=["'](.+?)["']""",link)
    if match:
      ret = match.group(1).replace('&amp;','&')
      return ret
    else: 
      return False

  def parserCDA(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.search("""file: ['"](.+?)['"],""",link)
    if match:   
      linkVideo = match.group(1) + '|Cookie="PHPSESSID=1&Referer=http://static.cda.pl/player5.9/player.swf'
      print linkVideo
      return linkVideo
    else: 
      return False

  def parserDWN(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.search("""<iframe src="(.+?)&""",link)
    if match:
      query_data = { 'url': match.group(1), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
      link = self.cm.getURLRequestData(query_data)
    else: 
      return False


  def parserANYFILES(self,url):
    COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "anyfiles.cookie"
    self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
    self.cm.addCookieItem(COOKIEFILE, {'name': 'AnyF18', 'value': 'mam18', 'domain': 'video.anyfiles.pl'}, False)
    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': True, 'use_post': False, 'return_data': True }
    data = self.cm.getURLRequestData(query_data)
    #var flashvars = {"uid":"player-vid-8552","m":"video","st":"c:1LdwWeVs3kVhWex2PysGP45Ld4abN7s0v4wV"};
    match = re.search("""var flashvars = {.+?"st":"(.+?)"}""",data)
    if match:
        nUrl = xppod.Decode(match.group(1)[2:]).encode('utf-8').strip()
        if 'http://' in nUrl: url2 = nUrl
        else: url2 = 'http://video.anyfiles.pl' + nUrl
                
        query_data = { 'url': url2+ "&ref=" +urllib.quote_plus(url), 'use_host': False, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': False, 'use_post': False, 'return_data': True }
        data = self.cm.getURLRequestData(query_data)
        data = xppod.Decode(data).encode('utf-8').strip()

        #json cleanup
        while data[-2:] != '"}': data = data[:-1]
        result = json.loads(data)
        if (result['ytube']=='0'):
            vUrl = result['file'].split("or")
            print ("Dasta",vUrl[0])
            vUrl = vUrl[0].encode('utf-8').split(' ')
            return vUrl[0]
        else:
            p = result['file'].split("/")
            if 'watch' in p[3]: videoid = p[3][8:19]
            else: videoid = p[3]
            plugin = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + videoid
            return plugin
            return False 

  
  
  def parserWOOTLY(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    c = re.search("""c.value="(.+?)";""",link)
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
      query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
      link = self.cm.getURLRequestData(query_data, postdata)
      match = re.search("""<video.*\n.*src=['"](.+?)['"]""",link)
      if match:
        return match.group(1)
      else: 
        return False
    else: 
      return False


  def parserMAXVIDEO(self, url):
    mainUrl = 'http://maxvideo.pl'
    apiVideoUrl = mainUrl + '/api/get_link.php?key=8d00321f70b85a4fb0203a63d8c94f97&v='
    videoHash = url.split('/')[-1]
    print ("ZAW",videoHash)
    
    query_data = { 'url': apiVideoUrl + videoHash, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    data = self.cm.getURLRequestData(query_data, {'v' : videoHash})
    result = json.loads(data)
    print result
    result = dict([(str(k), v) for k, v in result.items()])
    if 'error' in result: 
        videoUrl = ''
    else:
        videoUrl = result['ok'].encode('UTF-8')
    return videoUrl+'|Referer=http://maxvideo.pl/mediaplayer/player.swf'
    
      
  def parserVIDEOWEED(self, url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match_domain = re.compile('flashvars.domain="(.+?)"').findall(link)
    match_file = re.compile('flashvars.file="(.+?)"').findall(link)
    match_filekey = re.compile('flashvars.filekey="(.+?)"').findall(link)
    if len(match_domain) > 0 and len(match_file) > 0 and len(match_filekey) > 0:
        get_api_url = ('%s/api/player.api.php?user=undefined&codes=1&file=%s&pass=undefined&key=%s') % (match_domain[0], match_file[0], match_filekey[0])
        link_api = { 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        if 'url' in link_api:
            parser = Parser.Parser()
            params = parser.getParams(link_api)
            return parser.getParam(params, "url")
        else:
            return False
    else:
        return False
    
      
  def parserNOVAMOV(self, url):
      query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
      link = self.cm.getURLRequestData(query_data)
      match_file = re.compile('flashvars.file="(.+?)";').findall(link)
      match_key = re.compile('flashvars.filekey="(.+?)";').findall(link)
      print "match_key",match_key,match_file
      if len(match_file) > 0 and len(match_key) > 0:
          get_api_url = ('http://www.novamov.com/api/player.api.php?key=%s&user=undefined&codes=1&pass=undefined&file=%s') % (match_key[0], match_file[0])
          link_api = self.cm.getURLRequestData({ 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
          match_url = re.compile('url=(.+?)&title').findall(link_api)
          if len(match_url) > 0:
              return match_url[0]
          else:
              return False


  def parserNOWVIDEO(self, url):
      query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
      link = self.cm.getURLRequestData(query_data)
      match_file = re.compile('flashvars.file="(.+?)";').findall(link)
      match_key = re.compile('flashvars.filekey="(.+?)";').findall(link)
      if len(match_file) > 0 and len(match_key) > 0:
          get_api_url = ('http://www.nowvideo.eu/api/player.api.php?codes=1&key=%s&user=undefined&pass=undefined&file=%s') % (match_key[0], match_file[0])
          query_data = { 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
          link_api = self.cm.getURLRequestData(query_data)
          match_url = re.compile('url=(.+?)&title').findall(link_api)
          if len(match_url) > 0:
              return match_url[0]
          else:
              return False


  def parserSOCKSHARE(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data) 
    r = re.search('value="(.+?)" name="fuck_you"', link)
    if r:
      self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
      self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "sockshare.cookie"
      postdata = {'fuck_you' : r.group(1), 'confirm' : 'Close Ad and Watch as Free User'}
      query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
      link = self.cm.getURLRequestData(query_data, postdata) 
      match = re.compile("playlist: '(.+?)'").findall(link)
      if len(match) > 0:
        url = "http://www.sockshare.com" + match[0]
        query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data) 
        match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
        if len(match) > 0:
          url = match[0].replace('&amp;','&')
          return url
        else:
          return False
      else:
        return False
    else:
      return False


  def parserRAPIDVIDEO(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match = re.search("""'(.+?)','720p'""",link)
    if match:    
      return match.group(1)
    else: 
      return False


  def parserVIDEOSLASHER(self, url):
    self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "videoslasher.cookie"
    query_data = { 'url': url.replace('embed', 'video'), 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
    postdata = {'confirm': 'Close Ad and Watch as Free User', 'foo': 'bar'}
    data = self.cm.getURLRequestData(query_data, postdata)
    
    match = re.compile("playlist: '/playlist/(.+?)'").findall(data)
    if len(match)>0:
        query_data = { 'url': 'http://www.videoslasher.com//playlist/' + match[0], 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE,  'use_post': True, 'return_data': True }
        data = self.cm.getURLRequestData(query_data)
        match = re.compile('<title>Video</title><media:content url="(.+?)"').findall(data)
        if len(match)>0:
            sid = self.cm.getCookieItem(self.COOKIEFILE,'authsid')
            if sid != '':
                streamUrl = match[0] + '|Cookie="authsid=' + sid + '"'
                return streamUrl  
            else:
                return False
        else:
            return False
    else:
      return False



  def checklnt(self,AString):
    #{var TMPResult="";
    for i in range(len(AString)):
    #for(i=0;i<AString.length;i++){
        #TMPResult=TMPResult+parseStign(AString.charAt(i));}
        a=a
    return TMPResult
  def parseStign(self, string):
    out = string
    for i in range(len(CHARS)):
        out = string.replace(CHARS[i][0], CHARS[i][1])
        string = out
    return out 
          
