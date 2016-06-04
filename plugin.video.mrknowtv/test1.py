# -*- coding: utf-8 -*-

import random, string, sys
import json,re
#sys.path.append('/home/mrknow/Dokumenty/praca/kodi/plugin.video.mrknowtv/mylib/')
sys.path.append('/home/mrknow/.kodi/addons/plugin.video.mrknowtv/mylib/')

#print ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(25))

#from resources.lib.sources import sezonlukdizi_tv

from resources.lib.lib import client
from resources.lib.lib import control
from resources.lib.lib import player

print(client.mystat('http://pierwsza.tv'))
import datetime
a = datetime.datetime.now()
b = datetime.timedelta(seconds=60)

print int(a.strftime('%s'))
c = a+b
print int(c.strftime('%s'))

print("a",a,b)
print(int(''),'a')
#from resources.lib import resolvers

#from resources.lib.resolvers import yadisk
#from resources.lib.sources.iwatchonline_mv_tv import source


#my = source()
#a = my.get_movie('tt1431045','Deadpool','2016')
#control.log('############ DAYT res-1 %s' % a)

#b = my.get_sources('/movie/54555-deadpool-2016','','','')
#control.log('############ DAYT res-1 %s' % b)


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