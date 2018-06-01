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
import sys, urlparse, os
import re
from __generic_host__ import GenericHost
import HTMLParser
import xbmcgui
import urllib

from __generic_host__ import GenericHost
from search import Search


mainUrl = 'https://cdax.tv/'
seriesUrl = 'https://cdax.tv/seriale-online/'
catUrl = 'https://cdax.tv/filmy-online/category:%s/?page=1'
lastUrl = 'https://cdax.tv/filmy-online/?page=1'
szukajUrl = 'http://alltube.tv/szukaj'

class cdaxseriale(GenericHost):

    scriptname = 'cdaxseriale'
    host = 'cdaxseriale'
    MENU_TAB = [
        {'id': 1, 'title': 'Ostatnio dodane', 'mod': 'Ostatniododane'},
        {'id': 10, 'title': 'Alfabetycznie', 'mod': 'Alfabetycznie'},
         #{'id': 4, 'title': 'Szukaj', 'mod': 'find', },
        #{'id': 5, 'title': 'Historia wyszukiwania', 'mod': 'history'},
        # {'id': 3, 'title': 'Bajki', 'mod': 'ListBajki', },
        # {'id': 3, 'title': 'Bajki', 'mod': 'ListBajki', },


    ]

    #search = Search(url='%(quoted)s', service='alltubefilmy', listItemsFun=self.listsItemsOther)

    def ListSeries(self):
        result = self.client.request(seriesUrl)
        r = self.client.parseDOM(result, 'ul', {"id": "series-list"})[0]
        r = self.client.parseDOM(r, 'li')
        r = [(self.client.parseDOM(i, 'a'), self.client.parseDOM(i,'a', ret='href')) for i in r]

        #r = [(r[0][0][i],r[0][1][i]) for i,j in enumerate(r[0])]
        for i in r:
            self.control.log('%s' % str(i))
            self.control.log('%s' % str(i[1][0]))

            #    myurl = catUrl  % i[1]
            self.add(self.host, 'categories-menu', i[0][0],i[0][0],  'None', i[1][0], True, False)
        #xbmcplugin.endOfDirectory(int(sys.argv[1]))
        self.control.directory(int(sys.argv[1]))

    def listsSearchResults(self, key):
        self.control.log(key)
        post_data = {'search': key}
        result = self.s.post(szukajUrl, data=post_data).text
        #self.control.log('ALA %s' % result.encode('utf-8'))
        try:
            result = re.findall('<h2 class="headline">Filmy</h2>(.*)<h2 class="headline">Seriale</h2>', result, re.DOTALL)[0]
            r = self.client.parseDOM(result, 'div', attrs={'class':'item-block clearfix'})
            r = [(self.client.parseDOM(i, 'a', ret='href'),
                  self.client.parseDOM(i, 'img', ret='src'),
                  self.client.parseDOM(i, 'h3'),
                  self.client.parseDOM(i, 'p')) for i in r]
            for i in r:
                self.control.log('ALA %s' % str(i))
                 # self.control.log('%s' % str(i) )
                try:
                    # self.control.log('AAA %s' % str(i))
                    meta = {'title': i[2][0], 'poster': i[1][0], 'year': '','plot': i[3][0]}
                    meta['originaltitle'] = i[2][0].encode('utf-8')
                    params = {'service': self.host, 'name': 'playselectedmovie', 'category': '', 'isplayable': 'true',
                              'url': i[0][0]}
                    params.update(meta)
                    self.add2(params)
                except Exception as e:
                    self.control.log('EEEEEEEEERRRTOO %s' % e)
                    pass
        except:
            pass
        self.dirend(int(sys.argv[1]))

    def listsEpisodes(self, url):
        self.control.log('[]1 %s' % url)
        result = self.request(url, utf=False)
        img = self.client.parseDOM(result, 'div', {"id": "single-poster"})[0]
        img = self.client.parseDOM(img, 'img', {"id": "item-image"}, ret='src')[0]
        plot = self.client.parseDOM(result, 'p', {"id": "item-description"})[0]
        year = self.client.parseDOM(result, 'sup')[0]
        title = self.client.parseDOM(result, 'h2')[0]
        title = title.split('<sup>')[0].strip()
        r = self.client.parseDOM(result, 'div', {"id": "accordion"})[0]
        r = self.client.parseDOM(r, 'li')

        r = [(self.client.parseDOM(i, 'a', ret='href'),self.client.parseDOM(i, 'a')) for i in r]

        for i in r:
            #self.control.log('AAA %s' % str(i))
            mytitle = '%s - %s' %(title,i[1][0])
            mytitle = " ".join(mytitle.splitlines()).strip().replace('&nbsp;','')

            try:
                meta = {'title': mytitle, 'poster': img,'plot': plot, 'year':year}
                params = {'service': self.host, 'name': 'playselectedmovie', 'category': 'None',
                          'isplayable': 'true','url': i[0][0]}
                params.update(meta)
                self.add2(params)
            except Exception as e:
                self.control.log('cdaxf-1 ITEM ADD ERROR %s' % e)
                pass
        self.dirend(int(sys.argv[1]))

    def listsItems(self, url):
        try:
            mypagenumber = re.findall('=(\d+)',url)[0]
            page = int(mypagenumber)
        except:
            page = 1
        self.control.log('[]1 %s' % url)
        self.control.log('[]1 %s' % page)
        mynext = url.replace('='+str(page), '='+str(page+1))
        self.control.log('[]2 %s' % mynext)

        #link = self.client.request(url)
        result = self.request(url, utf=False)
        r = self.client.parseDOM(result,'div', {"class": "col-xs-6 col-sm-3"})
        r = [(self.client.parseDOM(i, 'a', ret='href'),self.client.parseDOM(i, 'img', ret='src'),
              self.client.parseDOM(i, 'a', ret='data-content'),self.client.parseDOM(i, 'div', attrs={'class': 'year'}),
              self.client.parseDOM(i, 'div', attrs={'class': 'title'})) for i in r]

        for i in r:
            #self.control.log('%s' % str(i))
            try:
                tite = i[4][0].split('/')[1]
                titp = i[4][0].split('/')[0]
            except:
                tite = i[4][0]
                titp = i[4][0]
            try:
                meta = {'title': titp, 'poster': i[1][0],'plot': i[2][0], 'orginaltitle':tite}
                params = {'service': self.host, 'name': 'categories-menu', 'category': 'None','isplayable': 'false','url': i[0][0]}
                params.update(meta)
                self.add2(params)
            except Exception as e:
                self.control.log('cdaxf-1 ITEM ADD ERROR %s' % e)
                pass

        #self.add(self.host, 'categories-menu', u'Następna strona',u'Następna strona',  'None', mynext, True, False)
        self.dirend(int(sys.argv[1]))

    def getMovieLinkFromXML(self, url):
        link = self.client.request(url)
        r = self.client.parseDOM(link, 'tr')

        r = [(self.client.parseDOM(i, 'a', ret='href'),
              self.client.parseDOM(i, 'img', ret='alt'),
              self.client.parseDOM(i, 'td')
              ) for i in r]

        r = [(i[0][0], i[1][0], i[2][0], i[2][1]) for i in r if len(i[0]) > 0]

        for i in r:
            self.control.log('%s' % str(i))

        tab = []
        tab2 = []
        for i in r:
            self.control.log("Link ALL %s" % str(i))
            tab.append(i[1] + ' - ' + i[2]+ ' - ' + i[3])
            tab2.append(i[0])
        d = xbmcgui.Dialog()
        video_menu = d.select("Wybór strony video", tab)
        self.control.log('Altube wybrales [%s]' % video_menu)

        if video_menu != -1:
            linkVideo = tab2[video_menu]
            if 'cdax.tv/link/redirect' in linkVideo:
                link = self.request(linkVideo)
                match = re.search('<a href="(.*?)" class="btn btn-primary">Link do strony z video</a>', link)
                if match:
                    linkVideo = match.group(1).split('http')[-1]
                    linkVideo = 'http' + linkVideo
                    self.control.log('GRR  [%s]' % str(linkVideo))
            self.control.log('2 All pageparser   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
            #linkVideo = self.up.getVideoLink(tab2[video_menu], url)
            return self.urlresolve(linkVideo)
        else:
            return None

    def sub_handleService(self, params):
        name = params["name"]
        category = params["category"]
        url = params["url"]

        if name == 'main-menu' and category == 'Ostatniododane':
            self.control.log('Jest Ostatnio dodane: ')
            self.listsItems(seriesUrl)
        elif name == 'main-menu' and category == 'Alfabetycznie':
            self.control.log('Jest Kategorie: ')
            self.ListSeries()
        elif name == 'categories-menu':
            self.control.log('Jest categories-menu: ')
            self.listsEpisodes(url)





