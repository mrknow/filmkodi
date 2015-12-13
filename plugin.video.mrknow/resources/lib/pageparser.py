# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys, math
import xbmcaddon, xbmc, xbmcgui
import urlparse, httplib, random, string

scriptID = 'plugin.video.mrknow'
scriptname = "Wtyczka XBMC www.mrknow.pl"
ptv = xbmcaddon.Addon(scriptID)

import z_pLog, Parser, settings, libCommon, urlparser


log = z_pLog.pLog()
sets = settings.TVSettings()

class pageparser:
  def __init__(self):
    self.cm = libCommon.common()
    self.up = urlparser.urlparser()
    self.settings = settings.TVSettings()
    


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
    if match:
      hostName = match.group(1)
      if (nameOnly):
	n = hostName.split('.')
	hostName = n[-2]
    return hostName


  def getVideoLink(self, url):
    nUrl=''
    host = self.getHostName(url)
    log.info("video hosted by: " + host)
    log.info(url)
    
    if host == 'livemecz.com':
        nUrl = self.livemecz(url)
        print "Self",nUrl
    if host == 'www.drhtv.com.pl':
        nUrl = self.drhtv(url)
    elif host == 'www.realtv.com.pl':
        nUrl = self.realtv(url)
    elif host == 'www.transmisje.info':
        nUrl = self.transmisjeinfo(url)
    elif host == '79.96.137.217' or host == 'http://178.216.200.26':
        nUrl = self.azap(url)
    elif host == 'bbpolska.webd.pl':
        nUrl = self.bbpolska(url)
    elif host == 'fotosend.pl':
        nUrl = self.azap(url)
    elif host == 'typertv.com':
        nUrl = self.typertv(url)
    elif host == 'streamon.pl':
        nUrl = self.streamon(url)
    elif host == 'goodcast.tv':
        nUrl = self.goodcasttv(url)
    elif host == 'mecz.tv':
        nUrl = self.mecztv(url)        
        
    elif nUrl  == '':
        print "Jedziemy na ELSE - "+  nUrl
        nUrl = self.pageanalyze(url,host)
    print ("Link:",nUrl)
    return nUrl

  def mecztv(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match1=re.compile('<iframe frameborder="0" height="480" marginheight="0px" marginwidth="0px" name="livemecz.com" scrolling="no" src="(.*?)" width="640"></iframe>').findall(link)
    print ("AAAAA",match1)
    if len(match1[0])>0:
        query_data = { 'url': match1[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("Link",link)
        match2=re.compile('<iframe marginheight="0" marginwidth="0" name="mecz.tv" src="(.*?)" frameborder="0" height="480" scrolling="no" width="640"></iframe>').findall(link)
        print ("Link",match2)
        if len(match2[0])>0:
            query_data = { 'url': match2[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link = self.cm.getURLRequestData(query_data)
            print ("Link",link)
            match3=re.compile('<iframe(.*?)src="(.*?)"(.*?)>').findall(link)
            if len(match3)>0:
                print ("Match3",match3)
                nUrl = self.pageanalyze(match3[0][1],url)
            else:
                nUrl = self.pageanalyze(match2[0],url)
        #nUrl = self.pageanalyze('http://goodcast.tv/' + match1[0][0], 'http://goodcast.tv/' + match1[0][0])
        
        #return nUrl
        return False

  def goodcasttv(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match1=re.compile('<iframe frameborder="0" width="630" height="360" margin="0px" name="goodcast.tv" scrolling="no" src="(.*?)"></iframe>').findall(link)
    query_data = { 'url': match1[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    print ("link-1",link)
    match2=re.compile('<iframe width="630px" height="350px" scrolling="no" frameborder="0" src="(.*?)"></iframe>').findall(link)
    match3=re.compile("file: '(.*?)',").findall(link)
    print ("AAAAA",match2,match3)
    if len(match2)>0:
        nUrl = self.up.getVideoLink(match2[0], url)
        return nUrl
    if len(match3)>0:
        nUrl = self.up.getVideoLink(match1[0], url)
        return nUrl
    
    
  def streamon(self,url):
    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "streamon.cookie"
    nUrl = self.pageanalyze(url,url)
    return nUrl    

    
  def typertv(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match1=re.compile('<iframe src=\'(.*?)\' width=\'(.*?)\' height=\'(.*?)\' frameborder=\'(.*?)\' scrolling=\'no\'></iframe>').findall(link)
    print ("AAAAA",match1,link)
    if len(match1)>0:
        print ("Mam Iframe",match1)
        nUrl = self.pageanalyze('http://'+self.getHostName(url)+'/'+match1[0][0],url)
        return nUrl    
    
    
    
    
  def azap(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    print link
    match1=re.compile('<meta http-equiv="Refresh" content="(.*?); url=(.*?)" />').findall(link)
    if len(match1)>0:
        url = match1[0][1]
        print ("m",match1)
        nUrl =  self.up.getVideoLink(url)
        print nUrl
        return nUrl
        
    else:
        return self.pageanalyze(match1[0])
    
  def bbpolska(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match=re.compile('<div id="player">(.*?)</div>').findall(link)
    print match
    if len(match)>0:
        match1=re.compile('src="(.*?)"').findall(match[0])
        print match1
        return self.pageanalyze(match1[0],match1[0])
    else:
        return False
    
    match=re.compile('<iframe width="(.*?)" height="(.*?)" src="(.*?)" scrolling="no" frameborder="0" style="border: 0px none transparent;">').findall(link)
    print ("Match",match)
    return self.pageanalyze('http://www.transmisje.info'+match[0][2],'http://www.transmisje.info')
  

  def transmisjeinfo(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match=re.compile('<iframe width="(.*?)" height="(.*?)" src="(.*?)" scrolling="no" frameborder="0" style="border: 0px none transparent;">').findall(link)
    print ("Match",match)
    return self.pageanalyze('http://www.transmisje.info'+match[0][2],'http://www.transmisje.info')

  def realtv(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match=re.compile('<iframe frameborder="0" height="420" marginheight="0px" marginwidth="0px" name="RealTV.com.pl" scrolling="no" src="(.*?)" width="650">').findall(link)
    print ("Match",match)
    return self.pageanalyze(match[0],'http://www.realtv.com.pl')

 
  def livemecz(self,url):
    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match=re.compile('<iframe frameborder="0" height="480" marginheight="0px" marginwidth="0px" name="livemecz.com" scrolling="no" src="(.+?)" width="640"></iframe>').findall(link)
    query_data = { 'url': match[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
    link = self.cm.getURLRequestData(query_data)
    match=re.compile('<iframe marginheight="0" marginwidth="0" name="livemecz.com" src="(.*?)" frameborder="0" height="480" scrolling="no" width="640">').findall(link)
    print ("Match livemecz",match)
    videolink =  self.pageanalyze(match[0],'http://livemecz.com/')
    print ("videolink  livemecz",videolink)
    return videolink

  def drhtv(self,url):
    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "streamon.cookie"
    return self.pageanalyze(url,url,'','Accept-Encoding: gzip, deflate')

  def pageanalyze(self,url,referer='',cookie='',headers=''):
    print ('DANE',url,referer,cookie,headers)
   
    if cookie != '':
        query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': cookie, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("LINK cookie",link)
    elif headers != '':
        query_data = { 'url': url, 'use_host': True, 'host': headers, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("LINK headers",link)
    
    else:
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("LINK",link)

        
    match=re.compile('<script type="text/javascript"> channel="(.*?)"; width="(.*?)"; height="(.*?)";</script><script type="text/javascript" src="http://yukons.net/share.js"></script>').findall(link)
    match1=re.compile("<script type='text/javascript'>fid='(.*?)'; v_width=(.*?); v_height=(.*?);</script><script type='text/javascript' src='http://www.reyhq.com/player.js'></script>").findall(link)
    match2=re.compile("<script type='text/javascript' src='http://www.sawlive.tv/embed/(.*?)'>").findall(link)
    match3=re.compile("<script type='text/javascript' src='http://sawlive.tv/embed/(.*?)'>").findall(link)
    match4=re.compile('<script type="text/javascript" src="http://www.ilive.to/embed/(.*?)">').findall(link)
    match5=re.compile("<script type='text/javascript'> channel='(.*?)'; user='(.*?)'; width='640'; height='400';</script><script type='text/javascript' src='http://jimey.tv/player/jimeytv_embed.js'>").findall(link)
    match6=re.compile("<script type='text/javascript'> width=(.*?), height=(.*?), channel='(.*?)', e='(.*?)';</script><script type='text/javascript' src='http://www.mips.tv/content/scripts/mipsEmbed.js'>").findall(link)
    match7=re.compile('<script type="text/javascript">fid="(.*?)"; v_width=(.*?); v_height=(.*?);</script><script type="text/javascript" src="http://www.ukcast.tv/embed.js"></script>').findall(link)
    match8=re.compile('<script type="text/javascript"> channel="(.*?)"; vwidth="(.*?)"; vheight="(.*?)";</script><script type="text/javascript" src="http://castamp.com/embed.js"></script>').findall(link)
    match9=re.compile("<script type='text/javascript'>id='(.*?)'; width='(.*?)'; height='(.*?)';</script><script type='text/javascript' src='http://liveview365.tv/js/player.js'></script>").findall(link)
    match10=re.compile('<script type="text/javascript"> channel="(.*?)"; width="(.*?)"; height="(.*?)";</script>\r\n<script type="text/javascript" src="http://yukons.net/share.js"></script>').findall(link)
    match11=re.compile('<iframe width="600px" height="400px" scrolling="no" frameborder="0" src="http://www.putlive.in/(.*?)"></iframe>').findall(link)
    match12=re.compile('<iframe frameborder=0 marginheight=0 marginwidth=0 scrolling=\'no\'src="(.*?)" width="(.*?)" height="(.*?)">').findall(link)
    match13=re.compile("<script type='text/javascript'> width=640, height=480, channel='(.*?)', g='(.*?)';</script><script type='text/javascript' src='http://www.ucaster.eu/static/scripts/ucaster.js'></script>").findall(link)
    match14=re.compile("<script type='text/javascript'>fid='(.*?)'; v_width=(.*?); v_height=(.*?);</script><script type='text/javascript' src='http://www.flashwiz.tv/player.js'></script>").findall(link)
    match15=re.compile('<script type="text/javascript"> fid="(.*?)"; v_width=(.*?); v_height=(.*?);</script><script type="text/javascript" src="http://www.yycast.com/javascript/embedPlayer.js"></script>').findall(link)
    match16=re.compile("<script type='text/javascript'> width=(.*?), height=(.*?), channel='(.*?)', g='(.*?)';</script><script type='text/javascript' src='http://www.liveflash.tv/resources/scripts/liveFlashEmbed.js'></script>").findall(link)
    match17=re.compile('<script type="text/javascript">ca="(.*?)";width="(.*?)"; height="(.*?)";</script><script type="text/javascript" src="https://ovcast.com/js/embed.js"></script>').findall(link)
    match18=re.compile("<script type=\'text/javascript\'>id=\'(.*?)\'; width=\'(.*?)\'; height=\'(.*?)\';</script><script type=\'text/javascript\' src=\'http://stream4.tv/player.js\'>").findall(link)
    match19=re.compile("<script type='text/javascript'>id='(.*?)'; width='(.*?)'; height='(.*?)';</script><script type='text/javascript' src='http://goodcast.org/player.js'></script>").findall(link)
    match20=re.compile('<script type="text/javascript" src="http://(.*?)jjcast.com/(.*?)">').findall(link)
    match21=re.compile('<script type="text/javascript" language="JavaScript" src="http://hqstream.tv/pl?(.*?)"></script>').findall(link)
    match22=re.compile("<script type='text/javascript'>(.*?)</script><script type='text/javascript' src='http://cdn.tiv.pw/stream(.*?).js'></script>").findall(link)
    
    #<script type="text/javascript" language="JavaScript" src="http://hqstream.tv/pl?streampage=dqewdfdewd&width=640&height=360"></script>
    print ("Match",match8,match2,match1,match,match3,match4,match5)
    if len(match) > 0:
        return self.up.getVideoLink('http://yukons.net/'+match[0][0])
    elif len(match1) > 0:
        return self.up.getVideoLink('http://www.reyhq.com/'+match1[0][0])
    elif len(match2) > 0:
        print ("Match2",match2)
        return self.up.getVideoLink('http://www.sawlive.tv/embed/'+match2[0],url)
    elif len(match3) > 0:
        return self.up.getVideoLink('http://www.sawlive.tv/embed/'+match3[0],url)
    elif len(match4) > 0:
        print ("Match4",match4)
        return self.up.getVideoLink('http://www.ilive.to/embed/'+match4[0],referer)
    elif len(match6) > 0:
        print ("Match6",match6[0])
        return self.up.getVideoLink('http://mips.tv/embedplayer/'+match6[0][2]+'/'+match6[0][3]+'/'+match6[0][0]+'/'+match6[0][1])
    elif len(match7) > 0:
        print ("Match7",match7)
        return self.up.getVideoLink('http://www.ukcast.tv/embed.php?u='+match7[0][0]+'&amp;vw='+match7[0][1]+'&amp;vh='+match7[0][2])
    elif len(match8) > 0:
        print ("Match8",match8)
        return self.up.getVideoLink('http://castamp.com/embed.php?c='+match8[0][0]+'&ch=1',referer)
    elif len(match9) > 0:
        print ("Match9",match9)
        return self.up.getVideoLink('http://liveview365.tv/embedded?id='+match9[0][0],referer)
    elif len(match10) > 0:
        print ("Match10",match10)
        return self.up.getVideoLink('http://yukons.net/'+match10[0][0])
    elif len(match11) > 0:
        print ("Match11",'http://www.putlive.in/'+match11[0])
        return self.up.getVideoLink('http://www.putlive.in/'+match11[0],referer)
    elif len(match12) > 0:
        print ("Match12",match12)
        return self.up.getVideoLink(match12[0][0],referer)
    elif len(match13) > 0:
        print ("Match13",match13)
        return self.up.getVideoLink('http://www.ucaster.eu/embedded/'+match13[0][0]+'/'+match13[0][1]+'/400/480',referer)
    elif len(match14) > 0:
        print ("Match14",match14)
        return self.up.getVideoLink('http://www.flashwiz.tv/embed.php?live='+match14[0][0]+'&vw='+match14[0][1]+'&vh='+match14[0][2],referer)
    elif len(match15) > 0:
        print ("Match15",match15)
        return self.up.getVideoLink('http://www.yycast.com/embed.php?fileid='+match15[0][0]+'&vw='+match15[0][1]+'&vh='+match15[0][2],referer)
    elif len(match16) > 0:
        print ("Match16",match16)
        return self.up.getVideoLink('http://www.liveflash.tv/embedplayer/'+match16[0][2]+'/'+match16[0][3]+'/'+match16[0][0]+'/'+match16[0][1],referer)
    elif len(match17) > 0:
        print ("Match17",match17)
        return self.up.getVideoLink('https://ovcast.com/gen.php?ch='+match17[0][0]+'&width='+match17[0][1]+'&height='+match17[0][2],referer)
    elif len(match18) > 0:
        print ("Match18",match18)
        return self.up.getVideoLink('http://stream4.tv/player.php?id='+match18[0][0]+'&width='+match18[0][1]+'&height='+match18[0][2],referer)
    elif len(match19) > 0:
        print ("Match19",match19)
        return self.up.getVideoLink('http://goodcast.org/stream.php?id='+match19[0][0]+'&width='+match19[0][1]+'&height='+match19[0][2],referer)
    elif len(match20) > 0:
        print ("Match20",match20)
        return self.up.getVideoLink('http://jjcast.com/'+match20[0][1].replace('embed','player'),referer)
    elif len(match21) > 0:
        print ("Match21",match21)
        return self.up.getVideoLink('http://hqstream.tv/player.php'+match21[0],referer)
    elif len(match22) > 0:
        print ("Match22",match22)
        return self.up.getVideoLink('http://cdn.tiv.pw/stream'++match22[0] +'.html',referer)
        #return self.up.getVideoLink('http://hqstream.tv/player.php'+match21[0],referer)


    else:
        return False





          
