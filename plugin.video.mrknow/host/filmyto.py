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
import HTMLParser
import xbmcgui

mainurl='http://filmy.to'
lastadded = '/filmy/1'
litera = 'http://filmy.to/filmy/1?litera=%s'
#bajki = '/bajki.php'
szukajUrl = '/szukaj?q=%s'

class Filmyto(GenericHost):
    scriptname = 'Filmyto'
    host = 'filmyto'
    MENU_TAB = [
        {'id': 1, 'title': 'Ostatnio dodane', 'mod': 'ListNowe'},
        {'id': 10, 'title': 'Alfabetycznie', 'mod': 'ListLitera'},
        {'id': 4, 'title': 'Szukaj', 'mod': 'find', },
        {'id': 5, 'title': 'Historia wyszukiwania', 'mod': 'history'},

    ]
    html_parser = HTMLParser.HTMLParser()

    def listsSearchResults(self,key):
        myurl = urlparse.urljoin(mainurl, szukajUrl % key)
        result = self.request(myurl)
        #movie clearfix
        r = self.client.parseDOM(result, 'div', attrs={'class': 'movie clearfix'})
        r = [(self.client.parseDOM(i, 'a', ret='href'),
              self.client.parseDOM(i, 'span', attrs={'class': 'title-pl'}),
              self.client.parseDOM(i, 'span', attrs={'class': 'title-en'}),

             self.client.parseDOM(i, 'img', ret='src'),
              self.client.parseDOM(i, 'p'),
              self.client.parseDOM(i, 'p', attrs={'class': 'plot'})) for i in r]
        r = [(i[0][0],i[1],i[2],i[3],
              re.findall('\((\d{4})\)', i[4][0]),i[5]) for i in r]

        for i in r:
            try:
                self.control.log('aaa %s' % str(i))

                meta = {'title': i[1][0], 'poster': urlparse.urljoin(mainurl, i[3][0]), 'year': i[4][0],
                        'plot': i[5][0].strip()}
                try:
                    meta['originaltitle'] = i[2][0]
                except:
                    meta['originaltitle'] = i[1][0]
                    pass
                params = {'service': self.host, 'name': 'playselectedmovie', 'category': '', 'isplayable': 'true',
                          'url': urlparse.urljoin(mainurl,i[0])}
                params.update(meta)
                self.add2(params)
            except Exception as e:
                self.control.log('Error %s, %s' % (e, str(i)))
                pass

        self.dirend(int(sys.argv[1]))

    def ListMovies(self, url):
        #try:
            myurl = urlparse.urljoin(mainurl, url)
            if '?' in myurl:
                myurl = myurl+ '&widok=galeria'
            else: myurl = myurl+ '?widok=galeria'
            result = self.request(myurl)

            r = self.client.parseDOM(result, 'div', attrs={'class':'movie clearfix'})
            r = [(self.client.parseDOM(i, 'a', attrs={'class':'pic'}, ret='href'),
                  self.client.parseDOM(i, 'div', attrs={'class': 'cover pull-left'}),
                  self.client.parseDOM(i, 'div', attrs={'class': 'movie-details'}),
                  self.client.parseDOM(i, 'div', attrs={'class': 'description'})) for i in r]
            #for i in r:
            #    self.control.log('IIII >>>>>>'+str(i))
            r = [(i[0],
                  self.client.parseDOM(i[1], 'img', ret='src'),
                  self.client.parseDOM(i[2], 'h3'),
                  self.client.parseDOM(i[2], 'span', attrs={'class': 'title-en'}),
                  re.findall('(\d{4}) \((.*?)\)',i[2][0]),
                  i[3]) for i in r]

            #for i in r:
            #    self.control.log('>>>>>>'+str(i))

            for i in r:
                meta = {'title': i[2][0], 'poster': urlparse.urljoin(mainurl, i[1][0]), 'year':i[4][0][0],
                        'plot':i[5][0], 'originaltitle': i[2][0]}
                try:
                    meta['originaltitle'] = i[3][0]
                except:
                    pass

                params = {'service': self.host, 'name': 'playselectedmovie', 'category': '','isplayable': 'true',
                          'url': i[0][0]}
                params.update(meta)
                self.add2(params)

            r2 = re.findall('<a title="Nast.*?pna strona" class="ttip" href="(.*?)">&rarr;</a>',result)
            if r2:
                self.control.log('XXXX' + str(r2))
                self.add(self.host, 'items-menu', 'ListMovies', 'Następna', 'None', r2[0] , True, False)

            self.dirend(int(sys.argv[1]))


    def ListLitera(self):
        result = self.client.request(urlparse.urljoin(mainurl, lastadded))
        r = self.client.parseDOM(result, 'button', attrs={'name':'litera'}, ret='value')
        for i in r:
            self.control.log('>>> ' + str(i))
            # (self, service, name, category,               title, iconimage, url, desc, rating, folder = True, isPlayable = True):
            self.add(self.host, 'None', 'ListMovies', i.upper() , 'None', litera % i, True, False)
        self.control.directory(int(sys.argv[1]))

    def ListMovies1(self, url):
        result = self.client.request(urlparse.urljoin(mainurl, url), utf=False)
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
            self.add(self.host, 'playselectedmovie', 'None', i[1], img, i[0], 'aaaa', 'None', False, True)

        r2 = re.findall('<li class="active"><a href=".*?">.*?</a></li><li><a href="(.*?)">.*?</a>',result)
        if r2:
            self.control.log('XXXX' + str(r2))
            self.add(self.host, 'items-menu', 'ListMovies1', 'Następna', 'None', r2[0], 'aaaa', 'None', True, False)

        self.control.directory(int(sys.argv[1]))

    def ListMoviesSzukaj(self, url):
        result = self.client.request(urlparse.urljoin(mainurl, url),utf=False)
        r = self.client.parseDOM(result, 'p', attrs={'style':'padding-top.+?'})
        r = [(self.client.parseDOM(i, 'a', ret='href')[0], self.client.parseDOM(i, 'a')[0]) for i in r]
        for i in r:
            title = i[1].encode('utf-8').replace('<img src="/img/hd.png">','')
            # (self, service, name, category,               title, iconimage, url, desc, rating, folder = True, isPlayable = True):
            self.add(self.host,  'playselectedmovie', 'None', title, 'None', i[0], 'aaaa', 'None', False, True)
        self.dirend(int(sys.argv[1]))

    def ListGatunki(self):
        result = self.client.request(urlparse.urljoin(mainurl, lastadded))
        r2 = re.findall('<li><a href="(/filmy/gatunek.php\?gatunek=.*?)">(.*?)</a></li>', result)
        self.control.log('ZXZX' + str(r2))

        if r2:
            self.control.log('ZXZX'+str(r2))
            for i in enumerate(r2):
                self.control.log('ZXZX' + str(i[1][0]))
                self.add(self.host, 'None', 'ListMovies1', i[1][1], 'None', i[1][0], 'aaaa', 'None', True, False)
            self.control.directory(int(sys.argv[1]))

    def getMovieLinkFromXML(self, url):
        try:
            tab=[]
            result = self.request(urlparse.urljoin(mainurl, url))
            result = self.control.encoding_fix(result)
            r = self.client.parseDOM(result, 'div', attrs={'class': 'url'}, ret='data-url')
            r = [(self.html_parser.unescape(i)) for i in r]
            r = [(self.client.parseDOM(i, 'iframe', ret='src')[0]) for i in r]
            r2 =[(self.control.getHostName(i)) for i in r]
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór strony video", r2)
            if video_menu != "":
                mylink = r[video_menu]
                self.control.log('PLAY Mylink menu %s' % mylink)
                return self.urlresolve(mylink)

            linkVideo = False
            return linkVideo
        except Exception as e:
            self.control.log('ERROR %s' % e)
            return None

    def sub_handleService(self, params):
    	name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        self.control.log('URL: ' + str(url))
        if category=='ListNowe':
            self.ListMovies(lastadded)
        elif category == 'ListMovies':
            self.ListMovies(url)
        elif category == 'ListLitera':
            self.ListLitera()
        elif category == 'ListBajki':
            self.ListMovies(bajki)
        elif category == 'ListGatunki':
            self.ListGatunki()


