# -*- coding: utf-8 -*-
'''
method getURLRequestData(params):
	params['use_host'] - True or False. If false the method can use global HOST
	params['host'] -  Use when params['outside_host'] is setting on True. Enter a own host
	params['use_cookie'] - True, or False. Enable using cookie
	params['cookiefile'] - Set cookie file
	params['save_cookie'] - True, or False. Save cookie to file
	params['load_cookie'] - True, or False. Load cookie
	params['url'] - Url address
	params['use_post'] - True, or False. Use post method.
	post_data - Post data
	params['return_data'] - True, or False. Return response read data.
	params['read_data'] - True, or False. Use when params['return_data'] is False.
	
	If you want to get data from url use this method (for default host):
	data = { 'url': <your url>, 'use_host': False, use_cookie': False, 'use_post': False, 'return_data': True }
	response = self.getURLRequestData(data)
	
	If you want to get XML, or JSON data then:
	data = { 'url': <your url>, 'use_host': False, use_cookie': False, 'use_post': False, 'return_data': False }
	response = self.getURLRequestData(data)

	If you want to get data with different user-agent then:
	data = { 'url': <your url>, 'use_host': True, 'host': <your own user-agent define>, use_cookie': False, 'use_post': False, 'return_data': True }
	response = self.getURLRequestData(data)

	If you want to save cookie file:
	data = { 'url': <your url>, 'use_host': True, 'host': <your own user-agent define>, 'use_cookie': True, 'load_cookie': False, 'save_cookie': True, 'cookiefile': <path to cookie file>, 'use_post': True, 'return_data': True }
	response = self.getURLRequestData(data, post_data)

	If you want to load cookie file:
	data = { 'url': <your url>, 'use_host': True, 'host': <your own user-agent define>, 'use_cookie': True, 'load_cookie': True, 'save_cookie': False, 'cookiefile': <path to cookie file>, 'use_post': True, 'return_data': True }
	response = self.getURLRequestData(data, post_data)

	If you want to load cookie file without post:
	data = { 'url': <your url>, 'use_host': True, 'host': <your own user-agent define>, 'use_cookie': True, 'load_cookie': True, 'save_cookie': False, 'cookiefile': <path to cookie file>, 'use_post': False, 'return_data': True }
	response = self.getURLRequestData(data)
	
	and etc...
'''

import re, os, sys, cookielib, random
import urllib, urllib2, re, sys, math
#import elementtree.ElementTree as ET
import xbmcaddon, xbmc, xbmcgui
try:
    import simplejson as json
except ImportError:
    import json

import gzip, StringIO

import z_pLog

log = z_pLog.pLog()

scriptID = sys.modules[ "__main__" ].scriptID
scriptname = "Polish Live TV"
ptv = xbmcaddon.Addon(scriptID)

dbg = ptv.getSetting('default_debug')

HOST_TABLE = { 100: 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0',
	       101: 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11',
	       102: 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.11',
	       103: 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
	       104: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20121213 Firefox/19.0',
	       105: 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:17.0) Gecko/20100101 Firefox/17.0',
	       106: 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11',
	       107: 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	       108: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17',
	       109: 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
	       110: 'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01',
	       111: 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
	       112: 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
	       113: 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
	    }

HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
HISTORYFILE = xbmc.translatePath(ptv.getAddonInfo('profile') + "history.xml")

#cj = cookielib.LWPCookieJar()
cj = cookielib.MozillaCookieJar()

 
class common:
    def __init__(self):
        pass

    def html_special_chars(self,txt):
        txt = txt.replace('#038;','')
        txt = txt.replace('&#34;','"')
        txt = txt.replace('&#39;','\'')
        txt = txt.replace('&#8221;','"')
        txt = txt.replace('&#8222;','"')
        txt = txt.replace('&#8211;','-')
        txt = txt.replace('&quot;','"')
        txt = txt.replace('&oacute;','ó')
        txt = txt.replace('&amp;','&')
        txt = txt.replace('\u0105','ą').replace('\u0104','Ą')
        txt = txt.replace('\u0107','ć').replace('\u0106','Ć')
        txt = txt.replace('\u0119','ę').replace('\u0118','Ę')
        txt = txt.replace('\u0142','ł').replace('\u0141','Ł')
        txt = txt.replace('\u0144','ń').replace('\u0144','Ń')
        txt = txt.replace('\u00f3','ó').replace('\u00d3','Ó')
        txt = txt.replace('\u015b','ś').replace('\u015a','Ś')
        txt = txt.replace('\u017a','ź').replace('\u0179','Ź')
        txt = txt.replace('\u017c','ż').replace('\u017b','Ż')
        return txt
    
    def getCookieItem(self, cookiefile, item):
	ret = ''
	cj = cookielib.MozillaCookieJar()
	cj.load(cookiefile, ignore_discard = True)
	for cookie in cj:
	    if cookie.name == item: ret = cookie.value
	return ret
    
    #item = {'name': 'xxx', 'value': 'yyy', 'domain': 'zzz'}
    def addCookieItem(self, cookiefile, item, load_cookie=True):
	if load_cookie==True and os.path.isfile(cookiefile):
	    cj.load(cookiefile, ignore_discard = True)
	c = cookielib.Cookie(0, item['name'], item['value'], None, False, item['domain'], False, False, '/', True, False, None, True, None, None, {})
	cj.set_cookie(c)
	cj.save(cookiefile, ignore_discard = True)

    def getURLRequestData(self, params = {}, post_data = {}):
    	host = HOST
    	response = None
    	req = None
    	out_data = None
    	opener = None
    	headers = { 'User-Agent' : host }
        if 'use_xml' in params:
            headers = { 'User-Agent' : host, 'Content-Type': 'text/xml' }
    	if dbg == 'true':
    		log.info('pCommon - getURLRequestData() -> params: ' + str(params))
        if params['use_host']:
        	host = params['host']
        if params['use_cookie']:
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			if params['load_cookie']:
				cj.load(params['cookiefile'], ignore_discard = True)
        if params['use_post']:
            #headers = {'User-Agent' : host}
            #log.info('pCommon - getURLRequestData() -> post data: ' + str(post_data))
            if 'use_xml' in params:
                dataPost = post_data
            else:
                dataPost = urllib.urlencode(post_data)
            req = urllib2.Request(params['url'], dataPost, headers)
        if not params['use_post']:
            req = urllib2.Request(params['url'])
            req.add_header('User-Agent', host)
        if params['use_cookie']:
            response = opener.open(req)
        else:
            response = urllib2.urlopen(req)
        if not params['return_data']:
        	try:
	            if params['read_data']:
	            	out_data = response.read()
	            else:
	            	out_data = response
	        except:
	        	out_data = response
        if params['return_data']:
            #
            if params['use_cookie'] == False:
                #print ("ENC",response.headers.get('content-encoding', ''),params)
                if response.info().get('Content-Encoding') == 'gzip':
                    buf = StringIO.StringIO( response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    out_data = f.read()
                else:
                    out_data = response.read()
            else:
                out_data = response.read()
            
            response.close()
        if params['use_cookie'] and params['save_cookie']:
        	cj.save(params['cookiefile'], ignore_discard = True)
        return out_data 
               
    def makeABCList(self):
        strTab = []
        strTab.append('0 - 9');
        for i in range(65,91):
            strTab.append(str(unichr(i)))	
        return strTab
    
    def getItemByChar(self, char, tab):
        strTab = []
        char = char[0]
        for i in range(len(tab)):
            if ord(char) >= 65:
                if tab[i][0].upper() == char:
                    strTab.append(tab[i])
            else:
                if ord(tab[i][0]) >= 48 and ord(tab[i][0]) <= 57:
                    strTab.append(tab[i])
        return strTab       
    
    def isNumeric(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False


    def checkDir(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)
            
    
    def getRandomHost(self):
	host_id = random.choice(HOST_TABLE.keys())
	log.info("host ID: " + str(host_id))
	host = HOST_TABLE[host_id]
	return host


    def LOAD_AND_PLAY_VIDEO(self, url, title, player = True):
        if url == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Moşe to chwilowa awaria.', 'Spróbuj ponownie za jaki�? czas')
            return False
        thumbnail = xbmc.getInfoImage("ListItem.Thumb")
        liz=xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        try:
	    if player != True:
		print "custom player pCommon"
		xbmcPlayer = player
	    else:
		print "default player pCommon"
		xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(url, liz)
        except:
            d = xbmcgui.Dialog()
	    d.ok('B�?�?d przy przetwarzaniu, lub wyczerpany limit czasowy ogl�?dania.', 'Zarejestruj si�? i op�?a�? abonament.', 'Aby ogl�?da�? za darmo spróbuj ponownie za jaki�? czas')        
	    return False
	return True
	    

    def formatDialogMsg(self, msg):
	valTab = []
	LENGTH = 56
	item = msg.split(' ');
	valTab.append('')
	valTab.append('')
	valTab.append('')

	if len(msg) <= LENGTH or len(item)==1:
	    valTab[0] = msg
	else:
	    isFull  = [False, False]
	    for i in item:
		if isFull[0] == False and isFull[1] == False:
		    if len(valTab[0] + ' ' + i) <= LENGTH:
			s = valTab[0] + ' ' + i
			valTab[0] = s.strip()
		    else:
			isFull[0] = True
		if isFull[0]:
		    if len(valTab[1] + ' ' + i) <= LENGTH:
			s = valTab[1] + ' ' + i
			valTab[1] = s.strip()
		    else:
			isFull[1] = True
		if isFull[1]:
		    if len(valTab[2] + ' ' + i) <= LENGTH:
			s = valTab[2] + ' ' + i
			valTab[2] = s.strip()
		    else:
			break
	return valTab	    




class history:
    def __init__(self):
        pass
    
    def readHistoryFile(self):
	file = open(HISTORYFILE, 'r')
	root = ET.parse(file).getroot()
	file.close()
	return root


    def writeHistoryFile(self, root):
	file = open(HISTORYFILE, 'w')
	ET.ElementTree(root).write(file)
	file.close() 


    def loadHistoryFile(self, service):
	if not os.path.isfile(HISTORYFILE):
	    self.makeHistoryFile(service)
	history = self.parseHistoryFile(service)
	return history
    

    def addHistoryItem(self, service, item):
	if not os.path.isfile(HISTORYFILE):
	    self.makeHistoryFile(service)
	strTab = []
	root = self.readHistoryFile()
	#check if item already exists
	exists = False
	for node in root.getiterator(service):
	    for child in node.getchildren():
		if child.text != None:
		    strTab.append(child.text)
		else:
		    strTab.append('')
		if child.text == item:
		    exists = True
	    if not exists:
		print "tab: " + str(strTab)
		i=0
		for node in root.getiterator(service):
		    for child in node.getchildren():
			if i==0: child.text = item
			else: child.text = strTab[i-1]
			i = i + 1
		self.writeHistoryFile(root)
		
		
    def clearHistoryItems(self, service):
	root = self.readHistoryFile()
	for node in root.getiterator(service):
	    for child in node.getchildren():
		child.text = ''
	self.writeHistoryFile(root)


    def parseHistoryFile(self, service):
	strTab = []
	root = self.readHistoryFile()
	serviceList = root.findall(service)
	if len(serviceList) == 0:
	    child = ET.Element(service)
	    root.append(child)   
	    for i in range(5):
		item = ET.Element('search')
		child.append(item)
	    self.writeHistoryFile(root)
	    
	for node in root.getiterator(service):
	    for child in node.getchildren():
		if child.text != None:
		    strTab.append(child.text)
		else:
		    strTab.append('')
	return strTab

    
    def makeHistoryFile(self, service):
	root = ET.Element('history')
	child = ET.Element(service)
	root.append(child)   
	for i in range(5):
	    item = ET.Element('search')
	    child.append(item)
	self.writeHistoryFile(root)




class Chars:
    def __init__(self):
        pass
    
    def setCHARS(self):
        return CHARS
    
    def replaceString(self, array, string):
        out = string
        for i in range(len(array)):
            out = string.replace(array[i][0], array[i][1])
            string = out
        return out    
    
    def replaceChars(self, string):
        out = string
        for i in range(len(CHARS)):
            out = string.replace(CHARS[i][0], CHARS[i][1])
            string = out
        return out        
    
