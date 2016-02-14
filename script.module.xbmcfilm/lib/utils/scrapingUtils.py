# -*- coding: utf-8 -*-


import regexUtils
import re
import urllib
import urlparse


def findJS(data):
    idName = '(?:f*id|ch)'
    jsName = '([^\"\']+?\.js[^\"\']*?)'
    regex = "(?:java)?scr(?:'\+')?ipt.*?" + idName + "\s*=\s*[\"']([^\"']+)[\"'][^<]*</scr(?:'\+')?ipt\s*>[^<]*<scr(?:'\+')?ipt[^<]*src=[\"']" + jsName + "[\"']"
    
    jscript = regexUtils.findall(data, regex)
    if jscript:
        jscript = filter(lambda x: x[1].find('twitter') == -1, jscript)
        return jscript
    
    return None


def findPHP(data, streamId):
    regex = "document.write\('.*?src=['\"]*(.*?.(?:php|html)[^&\"]*).*?['\" ]*.*?\)"
    php = regexUtils.findall(data, regex)
    if php:
        return re.sub(r"\'\+\s*(?:[fc]*id|ch)\s*\+\'", "%s" % streamId,php[0])
    
    regex = "document.write\('.*?src=['\"]*(.*?(?:f*id|ch)\s*\+'\.html*).*?['\" ]*.*?\)"
    html = regexUtils.findall(data, regex)
    if html:
        return re.sub(r"\'\+\s*(?:f*id|ch)\s*\+\'", "%s" % streamId,html[0])
    
    return None

def findRTMP(url, data):
    #if data.lower().find('rtmp') == -1:
    #    return None
    try:
        text = str(data)
    except:
        text = data
    
    #method 1
    #["'=](http://[^'" ]*.swf[^'" ]*file=([^&"']+)[^'" ]*&streamer=([^"'&]+))
    #streamer=([^&"]+).*?file=([^&"]+).*?src="([^"]+.swf)"
    
    # method 2
    #"([^"]+.swf\?.*?file=(rtmp[^&]+)&.*?id=([^&"]+)[^"]*)"

    sep1 = '[\'"&\? ]'
    sep2 = '(?:[\'"]\s*(?:,|\:)\s*[\'"]|=)'
    value = '([^\'"&]+)'


    method1 = True
    method2 = False
    radius = 400

    playpath = ''
    swfUrl = ''

    rtmp = regexUtils.findall(text, sep1 + 'streamer' + sep2 + value)
    if not rtmp:
        tryMethod2 = regexUtils.findall(text, sep1 + 'file' + sep2 + value)
        if tryMethod2 and tryMethod2[0].startswith('rtmp'):
            method1 = False
            method2 = True
            rtmp = tryMethod2
            
    if rtmp:
        for r in rtmp:
            
            tmpRtmp = r.replace('/&','').replace('&','')
                        
            idx = text.find(tmpRtmp)
            
            min_idx = 0
            max_idx = len(text) - 1
            
            start = idx-radius
            if start < min_idx:
                start = min_idx
                
            end = idx+radius
            if end > max_idx:
                end = max_idx
            
            area = text[start:end]
            
            clipStart = idx+len(tmpRtmp)
            if clipStart < max_idx:
                text = text[clipStart:]
            if method1:
                playpath = regexUtils.findall(area, sep1 + 'file' + sep2 + value)
            if method2:
                playpath = regexUtils.findall(area, sep1 + 'id' + sep2 + value)
                if playpath:
                    tmpRtmp = tmpRtmp + '/' + playpath[0]
            
            if playpath:
                swfUrl = regexUtils.findall(area, 'SWFObject\([\'"]([^\'"]+)[\'"]')
                if not swfUrl:
                    swfUrl = regexUtils.findall(area, sep1 + '([^\'"& ]+\.swf)')
                    if not swfUrl:
                        swfUrl = regexUtils.findall(data, sep1 + '([^\'"& ]+\.swf)')

                if swfUrl:
                    finalSwfUrl = swfUrl[0]
                    if not finalSwfUrl.startswith('http'):
                        finalSwfUrl = urlparse.urljoin(url, finalSwfUrl)
                    
                    regex = '://(.*?)/'
                    server = regexUtils.findall(tmpRtmp, regex)
                    if server:
                        if server[0].find(':') == -1:
                            tmpRtmp = tmpRtmp.replace(server[0], server[0] + ':1935')
                    
                    return [tmpRtmp, playpath[0], finalSwfUrl]
    
    return None


def getHostName(url):
    scheme = urlparse.urlparse(url)
    if scheme:
        return scheme.netloc.replace('www.','')
    return None


def findFrames(data):
    if data.lower().find('frame') == -1:
        return None
    return regexUtils.findall(data, "(frame[^>]*)>")


def findContentRefreshLink(page, data):
    
    regex = '0;\s*url=([^\'" ]+)'
    links = regexUtils.findall(data, regex)
    if links:
        return links[0]
    
    regex = 'window.location\s*=\s*[\'"]([^\'"]+)[\'"]'
    links = regexUtils.findall(data, regex)
    if links:
        return links[0]
    
    regex = 'frame\s*scrolling=\"auto\"\s*noresize\s*src\s*=\s*[\'"]([^\'"]+)[\'"]'
    links = regexUtils.findall(data, regex)
    if links:
        return links[0]
    
    #hd**ee.fv/cr**hd.fv/sp**ts4u.tv
    regex = '<a\s*href="([^"]+)"\s*target="_blank"><img\s*(?:src="[^"]+"\s*height="\d+"\s*width="\d+"\s*longdesc="[^"]+"|class="alignnone"\s*src="[^"]*"\s*alt="[^"]*"\s*width="\d\d\d"\s*height="\d\d\d")'
    links = regexUtils.findall(data, regex)
    if links:
        return urlparse.urljoin(urllib.unquote(page), links[0]).strip()

    return None


def findEmbedPHPLink(data):
    regex = '<script type="text/javascript" src="((?![^"]+localtimes)(?![^"]+adcash)[^"]+\.php\?[^"]+)"\s*>\s*</script>'

    links = regexUtils.findall(data, regex)
    if links:
        return links[0]
    
   
    return None

def findVideoFrameLink(page, data):
    
    minheight=300
    minwidth=300
    
    frames = findFrames(data)
    if not frames:
        return None
    
    iframes = regexUtils.findall(data, "(frame(?![^>]*cbox\.ws)(?![^>]*Publi)(?![^>]*dailymotion)(?![^>]*blacktvlive\.)(?![^>]*chat\d*\.\w+)(?![^>]*ad122m)(?![^>]*adshell)(?![^>]*capacanal)(?![^>]*waframedia)(?![^>]*Beba.tv/embed)(?![^>]*maxtags)(?![^>]*s/a1\.php)(?![^>]*right-sidebar)[^>]*\sheight\s*=\s*[\"']*([\%\d]+)(?:px)?[\"']*[^>]*>)")

    if iframes:
        for iframe in iframes:
            if iframe[1] == '100%':
                height = minheight+1
            else:
                height = int(iframe[1])
            if height > minheight:
                m = regexUtils.findall(iframe[0], "[\"' ]width\s*=\s*[\"']*(\d+[%]*)(?:px)?[\"']*")
                if m:
                    if m[0] == '100%':
                        width = minwidth+1
                    else:
                        width = int(m[0])
                    if width > minwidth:
                        m = regexUtils.findall(iframe[0], '[\'"\s]+(?:src|SRC)\s*=\s*["\']*\s*([^>"\' ]+)\s*[>"\']*')
                        if m:
                            if 'premiertv' in page:
                                page = page+'/'
                            return urlparse.urljoin(urllib.unquote(page), m[0]).strip()


    # Alternative 1
    iframes = regexUtils.findall(data, "(frame(?![^>]*cbox\.ws)(?![^>]*capacanal)(?![^>]*dailymotion)[^>]*[\"; ]height:\s*(\d+)[^>]*>)")
    if iframes:
        for iframe in iframes:
            height = int(iframe[1])
            if height > minheight:
                m = regexUtils.findall(iframe[0], "[\"; ]width:\s*(\d+)")
                if m:
                    width = int(m[0])
                    if width > minwidth:
                        m = regexUtils.findall(iframe[0], '[\"; ](?:src|SRC)=["\']*\s*([^>"\' ]+)\s*[>"\']*')
                        if m:
                            return urlparse.urljoin(urllib.unquote(page), m[0]).strip()

    # Alternative 2 (Frameset)
    m = regexUtils.findall(data, '<(?:FRAMESET|frameset)[^>]+100%[^>]+>\s*<(?:FRAME|frame)[^>]+src="([^"]+)"')
    if m:
        return urlparse.urljoin(urllib.unquote(page), m[0]).strip()
    
    m = regexUtils.findall(data, r'playStream\(\'iframe\', \'[^\']*(https*:[^\']+)\'\)')
    if m:
        return urlparse.urljoin(urllib.unquote(page), m[0]).strip()

    return None
