# -*- coding: utf-8 -*-

'''
    plugin.video.mrknow XBMC Addon
    Copyright (C) 2017 mrknow

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import sys, urlparse
import re
from __generic_host__ import GenericHost

mainurl='http://segos.es/'
lastadded = '/?page=filmy'
bajki = '/bajki.php'
szukaj = '/szukaj.php?title=%s'

class Segos(GenericHost):
    scriptname = 'Segos'
    host = 'segos'
    MENU_TAB = [
        {'id': 1, 'title': 'Ostatnio dodane', 'mod': 'ListNowe'},
        {'id': 2, 'title': 'Gatunki', 'mod': 'ListGatunki'},
        {'id': 3, 'title': 'Bajki', 'mod': 'ListBajki', },
        {'id': 4, 'title': 'Szukaj', 'mod': 'find', },
        {'id': 5, 'title': 'Historia wyszukiwania', 'mod': 'history'},

    ]

    def ListMovies(self, url):
        result = self.client.request(urlparse.urljoin(mainurl, url))
        r = self.client.parseDOM(result, 'div', attrs={'class': 'well'})[0]
        r = self.client.parseDOM(r, 'div', attrs={'class': 'col-lg-12 col-md-12 col-xs-12'})
        for i in r:
            self.control.log('a %s' % i.encode('ascii', 'ignore'))
        r = [(self.client.parseDOM(i, 'div', attrs={'Style':'text-align: center;margin-top: 5px;'}),
              self.client.parseDOM(i, 'img', attrs={'class':'img-responsive img-home-portfolio img-glowna'}, ret='src')) for i in r]
        r = [(self.client.parseDOM(i[0], 'a', ret='href'),self.client.parseDOM(i[0], 'a'),i[1]) for i in r]
        r = [(i[0][0], i[1][0].encode('utf-8'), i[2][0]) for i in r if len(i[1]) > 0 and len(i[2]) > 0]

        for i in r:
            img = i[2]
            if not img.startswith('http'):
                img = urlparse.urljoin(mainurl, img)
            meta = {'title': i[1], 'poster': img, 'originaltitle': i[1]}
            params = {'service': self.host, 'name': 'playselectedmovie', 'category': '', 'isplayable': 'true','url':  i[0]}
            params.update(meta)
            self.add2(params)

        r2 = re.findall('<li class="active"><a href=".*?">.*?</a></li><li><a href="(.*?)">.*?</a>',result)
        if r2:
            self.control.log('XXXX' + str(r2))
            self.add(self.host, 'items-menu', 'ListMovies', 'Następna', 'None', r2[0], True, False)

        self.dirend(int(sys.argv[1]))

    def ListMovies1(self, url):
        result = self.client.request(urlparse.urljoin(mainurl, url))
        r = self.client.parseDOM(result, 'div', attrs={'class': 'well'})[0]
        r = self.client.parseDOM(r, 'div', attrs={'class': 'col-lg-3 col-md-3 col-sm-6 segos'})
        r = [(self.client.parseDOM(i, 'a', ret='href'),
              self.client.parseDOM(i, 'div', attrs={'style':'text-align:center;padding-top:7px;'}),
              self.client.parseDOM(i, 'img', attrs={'class':'img-responsive img-home-portfolio img-glowna'}, ret='src')) for i in r]
        for i in r:
            self.control.log('aaa'+str(i))

        r = [(i[0],i[1],i[2]) for i in r]
        r = [(i[0][0], i[1][0].encode('utf-8'), i[2][0]) for i in r if len(i[1]) > 0 and len(i[2]) > 0]

        for i in r:
            img = i[2]
            if not img.startswith('http'):
                img = urlparse.urljoin(mainurl, img)
            meta = {'title': i[1], 'poster': img, 'originaltitle': i[1]}
            params = {'service': self.host, 'name': 'playselectedmovie', 'category': '', 'isplayable': 'true','url':  i[0]}
            params.update(meta)
            self.add2(params)


        r2 = re.findall('<li class="active"><a href=".*?">.*?</a></li><li><a href="(.*?)">.*?</a>',result)
        if r2:
            self.control.log('XXXX' + str(r2))
            self.add(self.host, 'items-menu', 'ListMovies1', 'Następna', 'None', r2[0], True, False)

        self.dirend(int(sys.argv[1]))

    def listsSearchResults(self, key):
        url = szukaj % key
        result = self.client.request(urlparse.urljoin(mainurl, url))
        r = self.client.parseDOM(result, 'p', attrs={'style':'padding-top.+?'})
        r = [(self.client.parseDOM(i, 'a', ret='href')[0], self.client.parseDOM(i, 'a')[0]) for i in r]
        for i in r:
            title = i[1].encode('utf-8').replace('<img src="/img/hd.png">','')
            # (self, service, name, category,               title, iconimage, url, desc, rating, folder = True, isPlayable = True):
            self.add(self.host,  'playselectedmovie', 'None', title, 'None', i[0], False, True)
        self.dirend(int(sys.argv[1]))

    def ListGatunki(self):
        result = self.client.request(urlparse.urljoin(mainurl, lastadded))
        r2 = re.findall('<li><a href="(/filmy/gatunek.php\?gatunek=.*?)">(.*?)</a></li>', result)
        self.control.log('ZXZX' + str(r2))

        if r2:
            self.control.log('ZXZX'+str(r2))
            for i in enumerate(r2):
                self.control.log('ZXZX' + str(i[1][0]))
                self.add(self.host, 'items-menu', 'ListMovies1', i[1][1], 'None', i[1][0], True, False)
            self.control.directory(int(sys.argv[1]))



    def getMovieLinkFromXML(self, url):
        try:
            result = self.client.request(urlparse.urljoin(mainurl, url))
            r = self.client.parseDOM(result, 'a', attrs={'target': '_blank'}, ret='href')[0]
            self.control.log(str(r))
            return self.urlresolve(r)
            linkVideo = False
            return linkVideo
        except:
            return None

    def sub_handleService(self, params):
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        if category=='ListNowe':
            self.ListMovies(lastadded)
        elif category == 'ListMovies':
            self.ListMovies(url)
        elif category == 'ListMovies1':
            self.ListMovies1(url)
        elif category == 'ListBajki':
            self.ListMovies(bajki)
        elif category == 'ListGatunki':
            self.ListGatunki()

        else:
            self.control.log('AAAAAAAAAAAA')

