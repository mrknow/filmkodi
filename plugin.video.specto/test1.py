# -*- coding: utf-8 -*-

import random, string, sys
import json,re
sys.path.append('/home/mrknow/Dokumenty/praca/kodi/plugin.video.specto/mylib/')

print ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(25))

from resources.lib.sources import sezonlukdizi_tv

from resources.lib.libraries import client
from resources.lib.libraries import cleantitle
from resources.lib.libraries import control
from resources.lib import resolvers

from resources.lib.resolvers import yadisk
from resources.lib.sources.fmovies_mv_tv import source


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