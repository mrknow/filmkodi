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


mainUrl = 'http://alltube.tv/'
catUrl = 'http://alltube.tv/filmy-online/'
lastUrl = 'http://alltube.tv/filmy-online/strona[0]+'
szukajUrl = 'http://alltube.tv/szukaj'

def byteify(input):
    if isinstance(input, dict):
        return dict([(byteify(key), byteify(value)) for key, value in input.iteritems()])
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

class alltubefilmy(GenericHost):

    scriptname = 'alltubefilmy'
    host = 'alltubefilmy'
    MENU_TAB = [
        {'id': 1, 'title': 'Ostatnio dodane', 'mod': 'Ostatniododane'},
        {'id': 10, 'title': 'Kategorie', 'mod': 'Kategorie'},
         {'id': 4, 'title': 'Szukaj', 'mod': 'find', },
        {'id': 5, 'title': 'Historia wyszukiwania', 'mod': 'history'},
        # {'id': 3, 'title': 'Bajki', 'mod': 'ListBajki', },
        # {'id': 3, 'title': 'Bajki', 'mod': 'ListBajki', },


    ]

    #search = Search(url='%(quoted)s', service='alltubefilmy', listItemsFun=self.listsItemsOther)

    def listsCategoriesMenu(self):
        result = self.client.request(catUrl)
        r = self.client.parseDOM(result, 'ul', {"class": "filter-list filter-category"})[0]
        r = [(self.client.parseDOM(r, 'li'), self.client.parseDOM(r, 'li', ret='data-id'))]
        r = [(r[0][0][i],r[0][1][i]) for i,j in enumerate(r[0][0])]
        for i in r:
            self.control.log('%s' % str(i))
            myurl = catUrl + 'kategoria['+i[1]+']+strona[0]+'
            self.add('alltubefilmy', 'categories-menu', i[0],i[0],  'None', myurl, True, False)
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

    def listsItems(self, url):
        kategoria = ''
        myurl = ''
        #self.control.log('Strona1 %s' % url)

        try:
            temp = re.findall('kategoria\[(\d+)\]',url)[0]
            myurl = myurl + 'kategoria[' + str(temp) + ']+'
        except Exception as e:
            self.control.log('Exception  %s' % e)
            pass

        try:
            temp = re.findall('strona\[(\d+)\]',url)[0]
            nowastrona = int(temp) + 1
            myurl = myurl + 'strona[' + str(nowastrona) + ']+'
        except:
            pass

        myurl = catUrl + myurl
        self.control.log('Strona2 %s' % myurl)


        link = self.request(url)
        r = self.client.parseDOM(link,'div', {"class": "col-xs-12 col-sm-6 col-lg-4"})
        r = [(self.client.parseDOM(i, 'a', ret='href'),self.client.parseDOM(i, 'img', ret='src'),
              self.client.parseDOM(i, 'h3'),self.client.parseDOM(i, 'div', attrs={'class': 'second-title'}),
              self.client.parseDOM(i, 'p'),self.client.parseDOM(i, 'div', attrs={'class': 'item-details'})) for i in r]
        r = [(i[0],i[1],i[2],i[3],i[4], re.findall('(\d{4})',i[5][0])) for i in r]

        for i in r:
            try:
                meta = {'title': i[2][0], 'poster': i[1][0], 'year': i[5][0],'plot': i[4][0]}
                params = {'service': self.host, 'name': 'playselectedmovie', 'category': '','isplayable': 'true','url': i[0][0]}
                params.update(meta)
                self.add2(params)
            except Exception as e:
                self.control.log('ALLTUBE-1 ITEM ADD ERROR %s' % e)
                pass

        self.add('alltubefilmy', 'categories-menu', u'Następna strona',u'Następna strona',  'None', myurl, True, False)
        self.dirend(int(sys.argv[1]))

    def getMovieLinkFromXML(self, url):
        #autor: samsamsam
        #
        # skopiowane rozwiązanie dla alltube
        # url https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/commit/7cc90471eab3ea58f710d477a5189e650b5ae6e0


        import base64
        import json
        headers = {'Referer':url}
        link = self.s.get(url,verify=False)
        mycookie = link.cookies.get_dict()
        self.control.log("SSSSSSSSSSSSS %s" % mycookie)

        #s.cookies
        match1 = re.compile(
            '<td><img src="(.*?)"\s.*alt="(.*?)">(.*?)</td>\s.*<td style="width: 100px;">\s.*<a href="#!" class="watch"\s.*data-iframe="(.*?)">.*\s.*\s.*\s.*\s.*\s.*\s.*<td style="width: 80px;"\s.*class="text-center">(.*?)</td>'
        ).findall(link.text)
        self.control.log("Match1 %s"% match1)
        tab = []
        tab2 = []
        if match1:
            for i in range(len(match1)):
                self.control.log("Link ALL %s" % match1[i][3].decode('base64'))
                tab.append(match1[i][1] + ' - ' + match1[i][4])
                tab2.append(match1[i][3].decode('base64'))
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór strony video", tab)
            self.control.log('Altube wybrales [%s]' % video_menu)

            if video_menu != -1:
                linkVideo = tab2[video_menu]
                if 'http://alltube.tv/special.php' in linkVideo:
                    try:
                        tmp = 'ZGVmIGFiYyhpbl9hYmMpOg0KICAgIGRlZiByaGV4KGEpOg0KICAgICAgICBoZXhfY2hyID0gJzAxMjM0NTY3ODlhYmNkZWYnDQogICAgICAgIHJldCA9ICcnDQogICAgICAgIGZvciBpIGluIHJhbmdlKDQpOg0KICAgICAgICAgICAgcmV0ICs9IGhleF9jaHJbKGEgPj4gKGkgKiA4ICsgNCkpICYgMHgwRl0gKyBoZXhfY2hyWyhhID4+IChpICogOCkpICYgMHgwRl0NCiAgICAgICAgcmV0dXJuIHJldA0KICAgIGRlZiBoZXgodGV4dCk6DQogICAgICAgIHJldCA9ICcnDQogICAgICAgIGZvciBpIGluIHJhbmdlKGxlbih0ZXh0KSk6DQogICAgICAgICAgICByZXQgKz0gcmhleCh0ZXh0W2ldKQ0KICAgICAgICByZXR1cm4gcmV0DQogICAgZGVmIGFkZDMyKGEsIGIpOg0KICAgICAgICByZXR1cm4gKGEgKyBiKSAmIDB4RkZGRkZGRkYNCiAgICBkZWYgY21uKGEsIGIsIGMsIGQsIGUsIGYpOg0KICAgICAgICBiID0gYWRkMzIoYWRkMzIoYiwgYSksIGFkZDMyKGQsIGYpKTsNCiAgICAgICAgcmV0dXJuIGFkZDMyKChiIDw8IGUpIHwgKGIgPj4gKDMyIC0gZSkpLCBjKQ0KICAgIGRlZiBmZihhLCBiLCBjLCBkLCBlLCBmLCBnKToNCiAgICAgICAgcmV0dXJuIGNtbigoYiAmIGMpIHwgKCh+YikgJiBkKSwgYSwgYiwgZSwgZiwgZykNCiAgICBkZWYgZ2coYSwgYiwgYywgZCwgZSwgZiwgZyk6DQogICAgICAgIHJldHVybiBjbW4oKGIgJiBkKSB8IChjICYgKH5kKSksIGEsIGIsIGUsIGYsIGcpDQogICAgZGVmIGhoKGEsIGIsIGMsIGQsIGUsIGYsIGcpOg0KICAgICAgICByZXR1cm4gY21uKGIgXiBjIF4gZCwgYSwgYiwgZSwgZiwgZykNCiAgICBkZWYgaWkoYSwgYiwgYywgZCwgZSwgZiwgZyk6DQogICAgICAgIHJldHVybiBjbW4oYyBeIChiIHwgKH5kKSksIGEsIGIsIGUsIGYsIGcpDQogICAgZGVmIGNyeXB0Y3ljbGUodGFiQSwgdGFiQik6DQogICAgICAgIGEgPSB0YWJBWzBdDQogICAgICAgIGIgPSB0YWJBWzFdDQogICAgICAgIGMgPSB0YWJBWzJdDQogICAgICAgIGQgPSB0YWJBWzNdDQogICAgICAgIGEgPSBmZihhLCBiLCBjLCBkLCB0YWJCWzBdLCA3LCAtNjgwODc2OTM2KTsNCiAgICAgICAgZCA9IGZmKGQsIGEsIGIsIGMsIHRhYkJbMV0sIDEyLCAtMzg5NTY0NTg2KTsNCiAgICAgICAgYyA9IGZmKGMsIGQsIGEsIGIsIHRhYkJbMl0sIDE3LCA2MDYxMDU4MTkpOw0KICAgICAgICBiID0gZmYoYiwgYywgZCwgYSwgdGFiQlszXSwgMjIsIC0xMDQ0NTI1MzMwKTsNCiAgICAgICAgYSA9IGZmKGEsIGIsIGMsIGQsIHRhYkJbNF0sIDcsIC0xNzY0MTg4OTcpOw0KICAgICAgICBkID0gZmYoZCwgYSwgYiwgYywgdGFiQls1XSwgMTIsIDEyMDAwODA0MjYpOw0KICAgICAgICBjID0gZmYoYywgZCwgYSwgYiwgdGFiQls2XSwgMTcsIC0xNDczMjMxMzQxKTsNCiAgICAgICAgYiA9IGZmKGIsIGMsIGQsIGEsIHRhYkJbN10sIDIyLCAtNDU3MDU5ODMpOw0KICAgICAgICBhID0gZmYoYSwgYiwgYywgZCwgdGFiQls4XSwgNywgMTc3MDAzNTQxNik7DQogICAgICAgIGQgPSBmZihkLCBhLCBiLCBjLCB0YWJCWzldLCAxMiwgLTE5NTg0MTQ0MTcpOw0KICAgICAgICBjID0gZmYoYywgZCwgYSwgYiwgdGFiQlsxMF0sIDE3LCAtNDIwNjMpOw0KICAgICAgICBiID0gZmYoYiwgYywgZCwgYSwgdGFiQlsxMV0sIDIyLCAtMTk5MDQwNDE2Mik7DQogICAgICAgIGEgPSBmZihhLCBiLCBjLCBkLCB0YWJCWzEyXSwgNywgMTgwNDYwMzY4Mik7DQogICAgICAgIGQgPSBmZihkLCBhLCBiLCBjLCB0YWJCWzEzXSwgMTIsIC00MDM0MTEwMSk7DQogICAgICAgIGMgPSBmZihjLCBkLCBhLCBiLCB0YWJCWzE0XSwgMTcsIC0xNTAyMDAyMjkwKTsNCiAgICAgICAgYiA9IGZmKGIsIGMsIGQsIGEsIHRhYkJbMTVdLCAyMiwgMTIzNjUzNTMyOSk7DQogICAgICAgIGEgPSBnZyhhLCBiLCBjLCBkLCB0YWJCWzFdLCA1LCAtMTY1Nzk2NTEwKTsNCiAgICAgICAgZCA9IGdnKGQsIGEsIGIsIGMsIHRhYkJbNl0sIDksIC0xMDY5NTAxNjMyKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbMTFdLCAxNCwgNjQzNzE3NzEzKTsNCiAgICAgICAgYiA9IGdnKGIsIGMsIGQsIGEsIHRhYkJbMF0sIDIwLCAtMzczODk3MzAyKTsNCiAgICAgICAgYSA9IGdnKGEsIGIsIGMsIGQsIHRhYkJbNV0sIDUsIC03MDE1NTg2OTEpOw0KICAgICAgICBkID0gZ2coZCwgYSwgYiwgYywgdGFiQlsxMF0sIDksIDM4MDE2MDgzKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbMTVdLCAxNCwgLTY2MDQ3ODMzNSk7DQogICAgICAgIGIgPSBnZyhiLCBjLCBkLCBhLCB0YWJCWzRdLCAyMCwgLTQwNTUzNzg0OCk7DQogICAgICAgIGEgPSBnZyhhLCBiLCBjLCBkLCB0YWJCWzldLCA1LCA1Njg0NDY0MzgpOw0KICAgICAgICBkID0gZ2coZCwgYSwgYiwgYywgdGFiQlsxNF0sIDksIC0xMDE5ODAzNjkwKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbM10sIDE0LCAtMTg3MzYzOTYxKTsNCiAgICAgICAgYiA9IGdnKGIsIGMsIGQsIGEsIHRhYkJbOF0sIDIwLCAxMTYzNTMxNTAxKTsNCiAgICAgICAgYSA9IGdnKGEsIGIsIGMsIGQsIHRhYkJbMTNdLCA1LCAtMTQ0NDY4MTQ2Nyk7DQogICAgICAgIGQgPSBnZyhkLCBhLCBiLCBjLCB0YWJCWzJdLCA5LCAtNTE0MDM3ODQpOw0KICAgICAgICBjID0gZ2coYywgZCwgYSwgYiwgdGFiQls3XSwgMTQsIDE3MzUzMjg0NzMpOw0KICAgICAgICBiID0gZ2coYiwgYywgZCwgYSwgdGFiQlsxMl0sIDIwLCAtMTkyNjYwNzczNCk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzVdLCA0LCAtMzc4NTU4KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbOF0sIDExLCAtMjAyMjU3NDQ2Myk7DQogICAgICAgIGMgPSBoaChjLCBkLCBhLCBiLCB0YWJCWzExXSwgMTYsIDE4MzkwMzA1NjIpOw0KICAgICAgICBiID0gaGgoYiwgYywgZCwgYSwgdGFiQlsxNF0sIDIzLCAtMzUzMDk1NTYpOw0KICAgICAgICBhID0gaGgoYSwgYiwgYywgZCwgdGFiQlsxXSwgNCwgLTE1MzA5OTIwNjApOw0KICAgICAgICBkID0gaGgoZCwgYSwgYiwgYywgdGFiQls0XSwgMTEsIDEyNzI4OTMzNTMpOw0KICAgICAgICBjID0gaGgoYywgZCwgYSwgYiwgdGFiQls3XSwgMTYsIC0xNTU0OTc2MzIpOw0KICAgICAgICBiID0gaGgoYiwgYywgZCwgYSwgdGFiQlsxMF0sIDIzLCAtMTA5NDczMDY0MCk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzEzXSwgNCwgNjgxMjc5MTc0KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbMF0sIDExLCAtMzU4NTM3MjIyKTsNCiAgICAgICAgYyA9IGhoKGMsIGQsIGEsIGIsIHRhYkJbM10sIDE2LCAtNzIyNTIxOTc5KTsNCiAgICAgICAgYiA9IGhoKGIsIGMsIGQsIGEsIHRhYkJbNl0sIDIzLCA3NjAyOTE4OSk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzldLCA0LCAtNjQwMzY0NDg3KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbMTJdLCAxMSwgLTQyMTgxNTgzNSk7DQogICAgICAgIGMgPSBoaChjLCBkLCBhLCBiLCB0YWJCWzE1XSwgMTYsIDUzMDc0MjUyMCk7DQogICAgICAgIGIgPSBoaChiLCBjLCBkLCBhLCB0YWJCWzJdLCAyMywgLTk5NTMzODY1MSk7DQogICAgICAgIGEgPSBpaShhLCBiLCBjLCBkLCB0YWJCWzBdLCA2LCAtMTk4NjMwODQ0KTsNCiAgICAgICAgZCA9IGlpKGQsIGEsIGIsIGMsIHRhYkJbN10sIDEwLCAxMTI2ODkxNDE1KTsNCiAgICAgICAgYyA9IGlpKGMsIGQsIGEsIGIsIHRhYkJbMTRdLCAxNSwgLTE0MTYzNTQ5MDUpOw0KICAgICAgICBiID0gaWkoYiwgYywgZCwgYSwgdGFiQls1XSwgMjEsIC01NzQzNDA1NSk7DQogICAgICAgIGEgPSBpaShhLCBiLCBjLCBkLCB0YWJCWzEyXSwgNiwgMTcwMDQ4NTU3MSk7DQogICAgICAgIGQgPSBpaShkLCBhLCBiLCBjLCB0YWJCWzNdLCAxMCwgLTE4OTQ5ODY2MDYpOw0KICAgICAgICBjID0gaWkoYywgZCwgYSwgYiwgdGFiQlsxMF0sIDE1LCAtMTA1MTUyMyk7DQogICAgICAgIGIgPSBpaShiLCBjLCBkLCBhLCB0YWJCWzFdLCAyMSwgLTIwNTQ5MjI3OTkpOw0KICAgICAgICBhID0gaWkoYSwgYiwgYywgZCwgdGFiQls4XSwgNiwgMTg3MzMxMzM1OSk7DQogICAgICAgIGQgPSBpaShkLCBhLCBiLCBjLCB0YWJCWzE1XSwgMTAsIC0zMDYxMTc0NCk7DQogICAgICAgIGMgPSBpaShjLCBkLCBhLCBiLCB0YWJCWzZdLCAxNSwgLTE1NjAxOTgzODApOw0KICAgICAgICBiID0gaWkoYiwgYywgZCwgYSwgdGFiQlsxM10sIDIxLCAxMzA5MTUxNjQ5KTsNCiAgICAgICAgYSA9IGlpKGEsIGIsIGMsIGQsIHRhYkJbNF0sIDYsIC0xNDU1MjMwNzApOw0KICAgICAgICBkID0gaWkoZCwgYSwgYiwgYywgdGFiQlsxMV0sIDEwLCAtMTEyMDIxMDM3OSk7DQogICAgICAgIGMgPSBpaShjLCBkLCBhLCBiLCB0YWJCWzJdLCAxNSwgNzE4Nzg3MjU5KTsNCiAgICAgICAgYiA9IGlpKGIsIGMsIGQsIGEsIHRhYkJbOV0sIDIxLCAtMzQzNDg1NTUxKTsNCiAgICAgICAgdGFiQVswXSA9IGFkZDMyKGEsIHRhYkFbMF0pOw0KICAgICAgICB0YWJBWzFdID0gYWRkMzIoYiwgdGFiQVsxXSk7DQogICAgICAgIHRhYkFbMl0gPSBhZGQzMihjLCB0YWJBWzJdKTsNCiAgICAgICAgdGFiQVszXSA9IGFkZDMyKGQsIHRhYkFbM10pDQogICAgZGVmIGNyeXB0YmxrKHRleHQpOg0KICAgICAgICByZXQgPSBbXQ0KICAgICAgICBmb3IgaSBpbiByYW5nZSgwLCA2NCwgNCk6DQogICAgICAgICAgICByZXQuYXBwZW5kKG9yZCh0ZXh0W2ldKSArIChvcmQodGV4dFtpKzFdKSA8PCA4KSArIChvcmQodGV4dFtpKzJdKSA8PCAxNikgKyAob3JkKHRleHRbaSszXSkgPDwgMjQpKQ0KICAgICAgICByZXR1cm4gcmV0DQogICAgZGVmIGpjc3lzKHRleHQpOg0KICAgICAgICB0eHQgPSAnJzsNCiAgICAgICAgdHh0TGVuID0gbGVuKHRleHQpDQogICAgICAgIHJldCA9IFsxNzMyNTg0MTkzLCAtMjcxNzMzODc5LCAtMTczMjU4NDE5NCwgMjcxNzMzODc4XQ0KICAgICAgICBpID0gNjQNCiAgICAgICAgd2hpbGUgaSA8PSBsZW4odGV4dCk6DQogICAgICAgICAgICBjcnlwdGN5Y2xlKHJldCwgY3J5cHRibGsodGV4dFsnc3Vic3RyaW5nJ10oaSAtIDY0LCBpKSkpDQogICAgICAgICAgICBpICs9IDY0DQogICAgICAgIHRleHQgPSB0ZXh0W2kgLSA2NDpdDQogICAgICAgIHRtcCA9IFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXQ0KICAgICAgICBpID0gMA0KICAgICAgICB3aGlsZSBpIDwgbGVuKHRleHQpOg0KICAgICAgICAgICAgdG1wW2kgPj4gMl0gfD0gb3JkKHRleHRbaV0pIDw8ICgoaSAlIDQpIDw8IDMpDQogICAgICAgICAgICBpICs9IDENCiAgICAgICAgdG1wW2kgPj4gMl0gfD0gMHg4MCA8PCAoKGkgJSA0KSA8PCAzKQ0KICAgICAgICBpZiBpID4gNTU6DQogICAgICAgICAgICBjcnlwdGN5Y2xlKHJldCwgdG1wKTsNCiAgICAgICAgICAgIGZvciBpIGluIHJhbmdlKDE2KToNCiAgICAgICAgICAgICAgICB0bXBbaV0gPSAwDQogICAgICAgIHRtcFsxNF0gPSB0eHRMZW4gKiA4Ow0KICAgICAgICBjcnlwdGN5Y2xlKHJldCwgdG1wKTsNCiAgICAgICAgcmV0dXJuIHJldA0KICAgIGRlZiByZXplZG93YSh0ZXh0KToNCiAgICAgICAgcmV0dXJuIGhleChqY3N5cyh0ZXh0KSkNCiAgICByZXR1cm4gcmV6ZWRvd2EoaW5fYWJjKQ0K'
                        tmp = base64.b64decode(tmp)
                        _myFun = compile(tmp, '', 'exec')
                        vGlobals = {"__builtins__": None, 'len': len, 'list': list, 'ord': ord, 'range': range}
                        vLocals = {'abc': ''}
                        exec _myFun in vGlobals, vLocals
                        myFun1 = vLocals['abc']
                    except Exception as e:
                        self.control.log('Altube err1 [%s]' % e)

                    data = self.request(urlparse.urljoin(mainUrl,'/jsverify.php?op=tag'))
                    try:
                        data = byteify(json.loads(data))
                        d = {}
                        for i in range(len(data['key'])):
                            d[data['key'][i]] = data['hash'][i]
                        tmp = ''
                        for k in sorted(d.keys()):
                            tmp += d[k]
                        mycookie['tmvh'] ='%s' % myFun1(tmp)

                    except Exception as e:
                        self.control.log('Altube err3 [%s]' % e)

                    self.control.log("XXXXXXXXXXX %s" % mycookie)

                    #http://alltube.tv/special.php?hosting=openload&id=oU9oQLz4F-U&width=673&height=471.09999999999997
                    link = self.s.get(linkVideo+ '&width=673&height=471.09999999999997', cookies=mycookie,verify=False)
                    self.control.log('Altube  link [%s]' % link)
                    match = re.search('<iframe src="(.+?)"', link.text)
                    if match:
                        linkVideo = match.group(1)
                self.control.log('2 All pageparser   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
                #linkVideo = self.up.getVideoLink(tab2[video_menu], url)
                return self.urlresolve(linkVideo)
        else:
            return None

        try:
            tab=[]
            result = self.request(urlparse.urljoin(mainurl, url))
            result = self.control.encoding_fix(result)
            r = self.client.parseDOM(result, 'div', attrs={'class': 'url'}, ret='data-url')
            r = [(self.html_parser.unescape(i)) for i in r]
            r = [(self.client.parseDOM(i, 'iframe', ret='src')[0]) for i in r]
            r2 =[(self.control.getHostName(i)) for i in r]
            d = xbmcgui.Diaself.control.log()
            video_menu = d.select("Wybór strony video", r2)
            if video_menu != "":
                mylink = r[video_menu]
                self.control.self.control.log('PLAY Mylink menu %s' % mylink)
                return self.urlresolve(mylink)

            linkVideo = False
            return linkVideo
        except Exception as e:
            self.control.log('ERROR %s' % e)
            return None

    def sub_handleService(self, params):
        name = params["name"]
        category = params["category"]
        url = params["url"]

        if name == 'main-menu' and category == 'Ostatniododane':
            self.control.log('Jest Ostatnio dodane: ')
            self.listsItems(lastUrl)
        elif name == 'main-menu' and category == 'Kategorie':
            self.control.log('Jest Kategorie: ')
            self.listsCategoriesMenu()
        elif name == 'categories-menu':
            self.control.log('Jest categories-menu: ')
            self.listsItems(url)



        
  
