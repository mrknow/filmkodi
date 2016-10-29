# -*- coding: utf-8 -*-

import random, string, sys
import json,re

'''
Encryption.Using your solution to the previous problem, and create a "rot13" translator.
"rot13" is an old and fairly simplistic encryption routine where by each letter of the alphabet is
rotated 13 characters. Letters in the first half of the alphabet will be rotated to the equivalent
letter in the second half and vice versa, retaining case. For example, 'a' goes to 'n' and 'X' goes
to 'K'. Obviously, numbers and symbols are immune from translation.
Created on 2012-11-7

@author: aihua.sun
'''
# initialize letters list

import urllib
import string

sourceString= "0%3B%7C%5Z%5B%3Z0%3B%7Z3%3Y%2Z%2Z0%2A%24%24%24%24%3Y%28%21%5Z%5B%2Z%22%22%29%5Z0%5B%2A2%24%3Y%2Z%2Z0%2A%241%241%3Y%28%21%5Z%5B%2Z%22%22%29%5Z0%5B%2A1%241%3Y%2Z%2Z0%2A%241%24%24%3Y%28%7Z%7B%2Z%22%22%29%5Z0%5B%2A%24%241%24%3Y%280%5Z0%5B%2Z%22%22%29%5Z0%5B%2A1%24%24%3Y%2Z%2Z0%2A%24%24%241%3Y%28%21%22%22%2Z%22%22%29%5Z0%5B%2A%242%3Y%2Z%2Z0%2A%241%24%3Y%2Z%2Z0%2A%24%242%3Y%28%7Z%7B%2Z%22%22%29%5Z0%5B%2A%24%241%3Y%2Z%2Z0%2A%24%24%24%3Y%2Z%2Z0%2A%243%3Y%2Z%2Z0%2A%242%24%3Y%2Z%2Z0%7B%3Z0.%241%3B%280.%241%3B0%2Z%22%22%29%5Z0.%241%24%5B%2Z%280.1%24%3B0.%241%5Z0.2%24%5B%29%2Z%280.%24%24%3B%280.%24%2Z%22%22%29%5Z0.2%24%5B%29%2Z%28%28%210%29%2Z%22%22%29%5Z0.1%24%24%5B%2Z%280.2%3B0.%241%5Z0.%24%241%5B%29%2Z%280.%24%3B%28%21%22%22%2Z%22%22%29%5Z0.2%24%5B%29%2Z%280.1%3B%28%21%22%22%2Z%22%22%29%5Z0.1%241%5B%29%2Z0.%241%5Z0.%241%24%5B%2Z0.2%2Z0.1%24%2Z0.%24%3Z0.%24%24%3B0.%24%2Z%28%21%22%22%2Z%22%22%29%5Z0.1%24%24%5B%2Z0.2%2Z0.1%2Z0.%24%2Z0.%24%24%3Z0.%24%3B%280.3%29%5Z0.%241%5B%5Z0.%241%5B%3Z0.%24%280.%24%280.%24%24%2Z%22%5A%22%22%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%24%241%2Z0.%24%24%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.2%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.%24%241%2Z0.%24%241%24%2Z0.1%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%24%241%2Z0.%24%24%24%2Z%22.%22%2Z0.2%2Z0.1%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.1%24%24%2Z0.%24%24%241%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.%24%241%2Z%22%3B%5A%5A%5A%22%22%2Z0.%24%24%24%24%2Z0.2%24%2Z0.%241%241%2Z0.%242%24%2Z0.%241%24%24%2Z0.%24%24%24%2Z0.%242%2Z0.%242%24%2Z0.%24%24%24%24%2Z0.1%24%24%2Z0.%24%241%2Z0.%24%24%241%2Z0.%242%2Z0.3%2Z0.%241%24%2Z0.%24%241%2Z%22%5A%5A%5A%22%3Z%22%2Z%22%5A%22%22%29%28%29%29%28%29%3Z";
print sourceString

sourceString = urllib.unquote(sourceString)
new_string = re.sub('[^a-zA-Z]', '', sourceString)
print sourceString
print new_string

rot_13_trans = string.maketrans(
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

)
def rot_13_decrypt(line):
    """Rotate 13 encryption"""
    line = line.translate(rot_13_trans)
    return line

print rot_13_decrypt(sourceString)

sys.path.append('/home/mrknow/Dokumenty/praca/kodi/specto/plugin.video.specto/mylib/')
#sys.path.append('/home/mrknow/Dokumenty/praca/kodi/filmkodi/script.mrknow.urlresolver2/lib/')
sys.path.append('/home/mrknow/Dokumenty/praca/kodi/filmkodi/plugin.video.mrknow/lib/')

import mrknow_pCommon

cm = mrknow_pCommon.common()

url = 'http://zobaczmyto.tv/serial-online/1397-projekt-lady-2016/sezon-1,odcinek-1'

query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
link = cm.getURLRequestData(query_data)
match1 = re.compile('<div class="play-free" id="loading-(.*?)">Oglądaj na:<br />(.*?)</div>').findall(link)
print ('zobaczmyto.tv PLAYYYYYYERRRRRRRRRRRR [%s]',match1)
tab=[]
tab2=[]
if len(match1) > 0:
    for i in range(len(match1)):
        match2 = re.compile("\$\('#(.*?)-" + match1[i][0] + "'\).load\('(.*?)'\);").findall(link)
        if len(match2) > 0:
            tab.append('Strona - ' + match2[0][0])
            tab2.append(match2[0][1])
    #d = xbmcgui.Dialog()
    #video_menu = d.select("Wybór strony video", tab)
    #if video_menu != "":
    #    query_data = {'url': tab2[video_menu], 'use_host': False, 'use_cookie': False, 'use_post': False,
    #                  'return_data': True}
    #    link = self.cm.getURLRequestData(query_data)
    #    match = re.search("""<iframe src="(.*?)" (.*?)></iframe>""", link)
    #    if match:
    #        linkVideo = self.up.getVideoLink(match.group(1), url)
    #        return linkVideo
    #else:
    #    return ''

print (tab,tab2)
exit()


import urlresolver

url = 'http://openload.co/embed/7wlGOdWQnT4'

z = False
hmf = urlresolver.HostedMediaFile(url, include_disabled=True, include_universal=False)
if hmf:
    print 'yay! we can resolve this one'
    z = hmf.resolve()
else:
    print 'dupa'
print z

exit()


print ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(25))

from resources.lib.sources import sezonlukdizi_tv

from resources.lib.libraries import client
from resources.lib.libraries import cleantitle
from resources.lib.libraries import control
from resources.lib import resolvers

from resources.lib.resolvers import yadisk
from resources.lib.sources.movie25_mv import source


my = source()
a = my.get_movie('tt1431045','Deadpool','2016')
control.log('############ DAYT res-1 %s' % a)
#
b = my.get_sources(a,'','','')
control.log('############ DAYT res-2 %s' % b)
exit
#{'tmdb': '60948', 'tvdb': '272644', 'tvshowtitle': '12 Monkeys', 'imdb': 'tt3148266', 'year': '2015', 'action': 'seasons', 'tvrage': '36903'}
imdb = 'tt3148266'
tvdb = '272644'
title = '12 Monkeys'
year = '2015'
data = '2016-05-23'

#c=my.get_show('tt3148266',tvdb,'12 Monkeys','2015')
#control.log('############ DAYT res-1 %s' % c)
#PARAMS: {'tmdb': '60948', 'episode': '6', 'name': '12 Monkeys S02E06', 'title': 'Immortal', 'tvdb': '272644', 'season': '2', 'tvshowtitle': '12 Monkeys', 'date': '2016-05-23', 'meta': '{"rating": "8.0", "code": "tt3148266", "tmdb": "60948", "imdb": "tt3148266", "year": "2015", "duration": "2700", "plot": "Cole\'s partnership with Ramse is put to the test when they travel back to the 1970s to try to prevent the Twelve from murdering a disturbed Vietnam veteran with a connection to the Witness.", "votes": "47", "thumb": "http://thetvdb.com/banners/episodes/272644/5565074.jpg", "title": "Immortal", "tvdb": "272644", "mpaa": "TV-14", "fanart": "http://thetvdb.com/banners/fanart/original/272644-20.jpg", "season": "2", "status": "Continuing", "poster": "http://thetvdb.com/banners/posters/272644-12.jpg", "tvshowtitle": "12 Monkeys", "studio": "Syfy", "genre": "Mystery / Science-Fiction", "tvrage": "36903", "banner": "http://thetvdb.com/banners/graphical/272644-g5.jpg", "episode": "6", "name": "12 Monkeys S02E06", "premiered": "2016-05-23", "cast": [["Aaron Stanford", ""], ["Amanda Schull", ""], ["Kirk Acevedo", ""], ["Barbara Sukowa", ""], ["Todd Stashwick", ""], ["Emily Hampshire", ""], ["Noah Bean", ""], ["Tom Noonan", ""]], "trailer": "plugin://plugin.video.specto/?action=trailer&name=12+Monkeys"}', 'imdb': 'tt3148266', 'year': '2015', 'action': 'sources', 'tvrage': '36903', 'alter': '0'}
#d=my.get_episode(c,imdb,tvdb,title,data,'2','6')
#control.log('############ DAYT res-1 %s' % d)
#e=my.get_sources(d,'','','')

#url = 'http://ok.ru/video/86215559923'
#print resolvers.request(url)



"""
src='http://dayt.se/forum/search.php?do=process'

post={'titleonly':1,'securitytoken':'guest','do':'process','q':'London + Has Fallen','B1':''}
result = client.source(src, post=post)
result = client.parseDOM(result, 'h3', attrs={'class': 'searchtitle'})
result = [(client.parseDOM(i, 'a', attrs={'class': 'title'}, ret='href')[0],client.parseDOM(i, 'a', attrs={'class': 'title'})[0]) for i in result]
control.log('############ DAYT res-1 %s' % result)
result = [i for i in result if title in cleantitle.movie(i[1])]
result = [i[0] for i in result if any(x in i[1] for x in years)][0]
result = re.compile('(.+?)(?:&amp)').findall(result)[0]

control.log('############ DAYT res-1 %s' % result)



exit()
result = client.parseDOM(result, 'iframe', ret='src')
result = [i for i in result if 'pasep' in i][0]

control.log('############ DAYT res-1 %s' % result)
result = client.source(result)
result = client.parseDOM(result, 'iframe', ret='src')[0]
result = client.source(result)
result = client.parseDOM(result, 'iframe', ret='src')[0]
control.log('############ DAYT res-2 %s' % result)
#control.log('############ DAYT res-2 %s' % resolvers.request(result))


result10 = client.parseDOM(result2, 'div', attrs = {'id': '5throw'})[0]
result10 = client.parseDOM(result10, 'a', attrs = {'rel': 'nofollow'}, ret='href')
for i in result10:
    print resolvers.request(i)


control.log('############ DAYT res-2 %s' % result10)
https://cloclo9.cldmail.ru/2dfVwUu76bo9TkKgZDPE/G/GT9F/FoCczQknq?key=9170c586eac96c6fbe53d3b77bf5d59b1ac4538a


src='https://cloud.mail.ru/public/GT9F/FoCczQknq'
src='https://cloud.mail.ru/public/6i3K/8aL4QRjZU'
#print resolvers.request(src)

result20 = client.source(src)
title= client.parseDOM(result20, 'title')
print title

vid = src.split('public')[-1]
token  = re.compile('"tokens":{"download":"([^"]+)"}').findall(result20)[0]
weblink = re.compile('"weblink_get":\[{"count":\d+,"url":"([^"]+)"}\]').findall(result20)[0]
print("Dane",token,weblink,vid)


if len(token)>0 and len(weblink)>0:
    url = weblink + vid + '?key='+token

    #result20 = json.loads(result20)
    control.log('############ DAYT res-2 %s' % url)
    #https://cloclo9.cldmail.ru/2dfVwUu76bo9TkKgZDPE/G/GT9F/FoCczQknq?key=9170c586eac96c6fbe53d3b77bf5d59b1ac4538a






src=' http://dayt.se/forum/forumdisplay.php?356-The-Flash'
mytitile = cleantitle.tv('S%02dE%02d' % (2,19)).lower()
control.log('############ DAYT mytitle %s' % mytitile)


result = client.source(src)
result = client.parseDOM(result, 'h3', attrs={'class': 'threadtitle'})
result = [(client.parseDOM(i, 'a', attrs={'class': 'title'}, ret='href')[0],client.parseDOM(i, 'a', attrs={'class': 'title'})[0]) for i in result]
result = [i for i in result if mytitile in i[1].lower()]
result = [(re.compile('(.+?)(?:&amp)').findall(i[0]), i[1]) for i in result][0][0]
control.log('############ DAYT res-2 %s' % result[0])

    #a = client.parseDOM(i, 'a', attrs={'class': 'title'})[0]
    #a1 = client.parseDOM(i, 'a', attrs={'class': 'title'},ret='href')[0]

    #control.log('############ DAYT res-20 %s' % a)
    #control.log('############ DAYT res-21 %s' % a1)
"""