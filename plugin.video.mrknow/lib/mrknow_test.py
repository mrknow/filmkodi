# -*- coding: utf-8 -*-

import random, string, sys
sys.path.append('/home/mrknow/Dokumenty/praca/kodi/plugin.video.specto/mylib/')


def get(title):
    if title == None: return
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title


#src='http://dayt.se/forum/forum.php'
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import control

src='http://dayt.se/forum/forumdisplay.php?338-Limitless'

result = client.source(myurl)

control.log('############ DAYT res-1 %s' % result)

result = client.parseDOM(result, 'h3', attrs={'class': 'searchtitle'})
control.log('############ DAYT res-1 %s' % result)

#r = requests.get(src)

#result = re.compile('<span class="sectiontitle"><a href="([^"]+)">([^<]+)</a></span> <span class="rightrss">').findall(r.text)
#print('srcIklub: %s' % result)

#result = [(re.compile('(.+?)(?:&amp)').findall(i[0]), re.sub('&#\d*;', '', i[1])) for i in result]
#print('srcIklub: %s' % result)
#result = [('/' + i[0][0] , get(i[1])) for i in result if len(i[0]) > 0]
#print('srcIklub: %s' % result)



#import urlparse
#print urlparse.urljoin('http://dayt.se', '/forum/'+ '/search.php?do=process')
