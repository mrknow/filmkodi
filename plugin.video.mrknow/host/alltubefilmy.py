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
from xbmcgui import ListItem
import urllib

from __generic_host__ import GenericHost
from search import Search


mainUrl = 'http://alltube.tv/'
catUrl = 'http://alltube.tv/filmy-online/'
lastUrl = 'http://alltube.tv/filmy-online/strona[0]+'
szukajUrl = 'http://alltube.tv/szukaj'

special_code = '''
ZGVmIGFiYyhpbl9hYmMpOg0KICAgIGRlZiByaGV4KGEpOg0KICAgICAgICBoZXhfY2hyID0gJzAxMjM0
NTY3ODlhYmNkZWYnDQogICAgICAgIHJldCA9ICcnDQogICAgICAgIGZvciBpIGluIHJhbmdlKDQpOg0K
ICAgICAgICAgICAgcmV0ICs9IGhleF9jaHJbKGEgPj4gKGkgKiA4ICsgNCkpICYgMHgwRl0gKyBoZXhf
Y2hyWyhhID4+IChpICogOCkpICYgMHgwRl0NCiAgICAgICAgcmV0dXJuIHJldA0KICAgIGRlZiBoZXgo
dGV4dCk6DQogICAgICAgIHJldCA9ICcnDQogICAgICAgIGZvciBpIGluIHJhbmdlKGxlbih0ZXh0KSk6
DQogICAgICAgICAgICByZXQgKz0gcmhleCh0ZXh0W2ldKQ0KICAgICAgICByZXR1cm4gcmV0DQogICAg
ZGVmIGFkZDMyKGEsIGIpOg0KICAgICAgICByZXR1cm4gKGEgKyBiKSAmIDB4RkZGRkZGRkYNCiAgICBk
ZWYgY21uKGEsIGIsIGMsIGQsIGUsIGYpOg0KICAgICAgICBiID0gYWRkMzIoYWRkMzIoYiwgYSksIGFk
ZDMyKGQsIGYpKTsNCiAgICAgICAgcmV0dXJuIGFkZDMyKChiIDw8IGUpIHwgKGIgPj4gKDMyIC0gZSkp
LCBjKQ0KICAgIGRlZiBmZihhLCBiLCBjLCBkLCBlLCBmLCBnKToNCiAgICAgICAgcmV0dXJuIGNtbigo
YiAmIGMpIHwgKCh+YikgJiBkKSwgYSwgYiwgZSwgZiwgZykNCiAgICBkZWYgZ2coYSwgYiwgYywgZCwg
ZSwgZiwgZyk6DQogICAgICAgIHJldHVybiBjbW4oKGIgJiBkKSB8IChjICYgKH5kKSksIGEsIGIsIGUs
IGYsIGcpDQogICAgZGVmIGhoKGEsIGIsIGMsIGQsIGUsIGYsIGcpOg0KICAgICAgICByZXR1cm4gY21u
KGIgXiBjIF4gZCwgYSwgYiwgZSwgZiwgZykNCiAgICBkZWYgaWkoYSwgYiwgYywgZCwgZSwgZiwgZyk6
DQogICAgICAgIHJldHVybiBjbW4oYyBeIChiIHwgKH5kKSksIGEsIGIsIGUsIGYsIGcpDQogICAgZGVm
IGNyeXB0Y3ljbGUodGFiQSwgdGFiQik6DQogICAgICAgIGEgPSB0YWJBWzBdDQogICAgICAgIGIgPSB0
YWJBWzFdDQogICAgICAgIGMgPSB0YWJBWzJdDQogICAgICAgIGQgPSB0YWJBWzNdDQogICAgICAgIGEg
PSBmZihhLCBiLCBjLCBkLCB0YWJCWzBdLCA3LCAtNjgwODc2OTM2KTsNCiAgICAgICAgZCA9IGZmKGQs
IGEsIGIsIGMsIHRhYkJbMV0sIDEyLCAtMzg5NTY0NTg2KTsNCiAgICAgICAgYyA9IGZmKGMsIGQsIGEs
IGIsIHRhYkJbMl0sIDE3LCA2MDYxMDU4MTkpOw0KICAgICAgICBiID0gZmYoYiwgYywgZCwgYSwgdGFi
QlszXSwgMjIsIC0xMDQ0NTI1MzMwKTsNCiAgICAgICAgYSA9IGZmKGEsIGIsIGMsIGQsIHRhYkJbNF0s
IDcsIC0xNzY0MTg4OTcpOw0KICAgICAgICBkID0gZmYoZCwgYSwgYiwgYywgdGFiQls1XSwgMTIsIDEy
MDAwODA0MjYpOw0KICAgICAgICBjID0gZmYoYywgZCwgYSwgYiwgdGFiQls2XSwgMTcsIC0xNDczMjMx
MzQxKTsNCiAgICAgICAgYiA9IGZmKGIsIGMsIGQsIGEsIHRhYkJbN10sIDIyLCAtNDU3MDU5ODMpOw0K
ICAgICAgICBhID0gZmYoYSwgYiwgYywgZCwgdGFiQls4XSwgNywgMTc3MDAzNTQxNik7DQogICAgICAg
IGQgPSBmZihkLCBhLCBiLCBjLCB0YWJCWzldLCAxMiwgLTE5NTg0MTQ0MTcpOw0KICAgICAgICBjID0g
ZmYoYywgZCwgYSwgYiwgdGFiQlsxMF0sIDE3LCAtNDIwNjMpOw0KICAgICAgICBiID0gZmYoYiwgYywg
ZCwgYSwgdGFiQlsxMV0sIDIyLCAtMTk5MDQwNDE2Mik7DQogICAgICAgIGEgPSBmZihhLCBiLCBjLCBk
LCB0YWJCWzEyXSwgNywgMTgwNDYwMzY4Mik7DQogICAgICAgIGQgPSBmZihkLCBhLCBiLCBjLCB0YWJC
WzEzXSwgMTIsIC00MDM0MTEwMSk7DQogICAgICAgIGMgPSBmZihjLCBkLCBhLCBiLCB0YWJCWzE0XSwg
MTcsIC0xNTAyMDAyMjkwKTsNCiAgICAgICAgYiA9IGZmKGIsIGMsIGQsIGEsIHRhYkJbMTVdLCAyMiwg
MTIzNjUzNTMyOSk7DQogICAgICAgIGEgPSBnZyhhLCBiLCBjLCBkLCB0YWJCWzFdLCA1LCAtMTY1Nzk2
NTEwKTsNCiAgICAgICAgZCA9IGdnKGQsIGEsIGIsIGMsIHRhYkJbNl0sIDksIC0xMDY5NTAxNjMyKTsN
CiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbMTFdLCAxNCwgNjQzNzE3NzEzKTsNCiAgICAg
ICAgYiA9IGdnKGIsIGMsIGQsIGEsIHRhYkJbMF0sIDIwLCAtMzczODk3MzAyKTsNCiAgICAgICAgYSA9
IGdnKGEsIGIsIGMsIGQsIHRhYkJbNV0sIDUsIC03MDE1NTg2OTEpOw0KICAgICAgICBkID0gZ2coZCwg
YSwgYiwgYywgdGFiQlsxMF0sIDksIDM4MDE2MDgzKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIs
IHRhYkJbMTVdLCAxNCwgLTY2MDQ3ODMzNSk7DQogICAgICAgIGIgPSBnZyhiLCBjLCBkLCBhLCB0YWJC
WzRdLCAyMCwgLTQwNTUzNzg0OCk7DQogICAgICAgIGEgPSBnZyhhLCBiLCBjLCBkLCB0YWJCWzldLCA1
LCA1Njg0NDY0MzgpOw0KICAgICAgICBkID0gZ2coZCwgYSwgYiwgYywgdGFiQlsxNF0sIDksIC0xMDE5
ODAzNjkwKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbM10sIDE0LCAtMTg3MzYzOTYx
KTsNCiAgICAgICAgYiA9IGdnKGIsIGMsIGQsIGEsIHRhYkJbOF0sIDIwLCAxMTYzNTMxNTAxKTsNCiAg
ICAgICAgYSA9IGdnKGEsIGIsIGMsIGQsIHRhYkJbMTNdLCA1LCAtMTQ0NDY4MTQ2Nyk7DQogICAgICAg
IGQgPSBnZyhkLCBhLCBiLCBjLCB0YWJCWzJdLCA5LCAtNTE0MDM3ODQpOw0KICAgICAgICBjID0gZ2co
YywgZCwgYSwgYiwgdGFiQls3XSwgMTQsIDE3MzUzMjg0NzMpOw0KICAgICAgICBiID0gZ2coYiwgYywg
ZCwgYSwgdGFiQlsxMl0sIDIwLCAtMTkyNjYwNzczNCk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBk
LCB0YWJCWzVdLCA0LCAtMzc4NTU4KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbOF0s
IDExLCAtMjAyMjU3NDQ2Myk7DQogICAgICAgIGMgPSBoaChjLCBkLCBhLCBiLCB0YWJCWzExXSwgMTYs
IDE4MzkwMzA1NjIpOw0KICAgICAgICBiID0gaGgoYiwgYywgZCwgYSwgdGFiQlsxNF0sIDIzLCAtMzUz
MDk1NTYpOw0KICAgICAgICBhID0gaGgoYSwgYiwgYywgZCwgdGFiQlsxXSwgNCwgLTE1MzA5OTIwNjAp
Ow0KICAgICAgICBkID0gaGgoZCwgYSwgYiwgYywgdGFiQls0XSwgMTEsIDEyNzI4OTMzNTMpOw0KICAg
ICAgICBjID0gaGgoYywgZCwgYSwgYiwgdGFiQls3XSwgMTYsIC0xNTU0OTc2MzIpOw0KICAgICAgICBi
ID0gaGgoYiwgYywgZCwgYSwgdGFiQlsxMF0sIDIzLCAtMTA5NDczMDY0MCk7DQogICAgICAgIGEgPSBo
aChhLCBiLCBjLCBkLCB0YWJCWzEzXSwgNCwgNjgxMjc5MTc0KTsNCiAgICAgICAgZCA9IGhoKGQsIGEs
IGIsIGMsIHRhYkJbMF0sIDExLCAtMzU4NTM3MjIyKTsNCiAgICAgICAgYyA9IGhoKGMsIGQsIGEsIGIs
IHRhYkJbM10sIDE2LCAtNzIyNTIxOTc5KTsNCiAgICAgICAgYiA9IGhoKGIsIGMsIGQsIGEsIHRhYkJb
Nl0sIDIzLCA3NjAyOTE4OSk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzldLCA0LCAt
NjQwMzY0NDg3KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbMTJdLCAxMSwgLTQyMTgx
NTgzNSk7DQogICAgICAgIGMgPSBoaChjLCBkLCBhLCBiLCB0YWJCWzE1XSwgMTYsIDUzMDc0MjUyMCk7
DQogICAgICAgIGIgPSBoaChiLCBjLCBkLCBhLCB0YWJCWzJdLCAyMywgLTk5NTMzODY1MSk7DQogICAg
ICAgIGEgPSBpaShhLCBiLCBjLCBkLCB0YWJCWzBdLCA2LCAtMTk4NjMwODQ0KTsNCiAgICAgICAgZCA9
IGlpKGQsIGEsIGIsIGMsIHRhYkJbN10sIDEwLCAxMTI2ODkxNDE1KTsNCiAgICAgICAgYyA9IGlpKGMs
IGQsIGEsIGIsIHRhYkJbMTRdLCAxNSwgLTE0MTYzNTQ5MDUpOw0KICAgICAgICBiID0gaWkoYiwgYywg
ZCwgYSwgdGFiQls1XSwgMjEsIC01NzQzNDA1NSk7DQogICAgICAgIGEgPSBpaShhLCBiLCBjLCBkLCB0
YWJCWzEyXSwgNiwgMTcwMDQ4NTU3MSk7DQogICAgICAgIGQgPSBpaShkLCBhLCBiLCBjLCB0YWJCWzNd
LCAxMCwgLTE4OTQ5ODY2MDYpOw0KICAgICAgICBjID0gaWkoYywgZCwgYSwgYiwgdGFiQlsxMF0sIDE1
LCAtMTA1MTUyMyk7DQogICAgICAgIGIgPSBpaShiLCBjLCBkLCBhLCB0YWJCWzFdLCAyMSwgLTIwNTQ5
MjI3OTkpOw0KICAgICAgICBhID0gaWkoYSwgYiwgYywgZCwgdGFiQls4XSwgNiwgMTg3MzMxMzM1OSk7
DQogICAgICAgIGQgPSBpaShkLCBhLCBiLCBjLCB0YWJCWzE1XSwgMTAsIC0zMDYxMTc0NCk7DQogICAg
ICAgIGMgPSBpaShjLCBkLCBhLCBiLCB0YWJCWzZdLCAxNSwgLTE1NjAxOTgzODApOw0KICAgICAgICBi
ID0gaWkoYiwgYywgZCwgYSwgdGFiQlsxM10sIDIxLCAxMzA5MTUxNjQ5KTsNCiAgICAgICAgYSA9IGlp
KGEsIGIsIGMsIGQsIHRhYkJbNF0sIDYsIC0xNDU1MjMwNzApOw0KICAgICAgICBkID0gaWkoZCwgYSwg
YiwgYywgdGFiQlsxMV0sIDEwLCAtMTEyMDIxMDM3OSk7DQogICAgICAgIGMgPSBpaShjLCBkLCBhLCBi
LCB0YWJCWzJdLCAxNSwgNzE4Nzg3MjU5KTsNCiAgICAgICAgYiA9IGlpKGIsIGMsIGQsIGEsIHRhYkJb
OV0sIDIxLCAtMzQzNDg1NTUxKTsNCiAgICAgICAgdGFiQVswXSA9IGFkZDMyKGEsIHRhYkFbMF0pOw0K
ICAgICAgICB0YWJBWzFdID0gYWRkMzIoYiwgdGFiQVsxXSk7DQogICAgICAgIHRhYkFbMl0gPSBhZGQz
MihjLCB0YWJBWzJdKTsNCiAgICAgICAgdGFiQVszXSA9IGFkZDMyKGQsIHRhYkFbM10pDQogICAgZGVm
IGNyeXB0YmxrKHRleHQpOg0KICAgICAgICByZXQgPSBbXQ0KICAgICAgICBmb3IgaSBpbiByYW5nZSgw
LCA2NCwgNCk6DQogICAgICAgICAgICByZXQuYXBwZW5kKG9yZCh0ZXh0W2ldKSArIChvcmQodGV4dFtp
KzFdKSA8PCA4KSArIChvcmQodGV4dFtpKzJdKSA8PCAxNikgKyAob3JkKHRleHRbaSszXSkgPDwgMjQp
KQ0KICAgICAgICByZXR1cm4gcmV0DQogICAgZGVmIGpjc3lzKHRleHQpOg0KICAgICAgICB0eHQgPSAn
JzsNCiAgICAgICAgdHh0TGVuID0gbGVuKHRleHQpDQogICAgICAgIHJldCA9IFsxNzMyNTg0MTkzLCAt
MjcxNzMzODc5LCAtMTczMjU4NDE5NCwgMjcxNzMzODc4XQ0KICAgICAgICBpID0gNjQNCiAgICAgICAg
d2hpbGUgaSA8PSBsZW4odGV4dCk6DQogICAgICAgICAgICBjcnlwdGN5Y2xlKHJldCwgY3J5cHRibGso
dGV4dFsnc3Vic3RyaW5nJ10oaSAtIDY0LCBpKSkpDQogICAgICAgICAgICBpICs9IDY0DQogICAgICAg
IHRleHQgPSB0ZXh0W2kgLSA2NDpdDQogICAgICAgIHRtcCA9IFswLCAwLCAwLCAwLCAwLCAwLCAwLCAw
LCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXQ0KICAgICAgICBpID0gMA0KICAgICAgICB3aGlsZSBpIDwg
bGVuKHRleHQpOg0KICAgICAgICAgICAgdG1wW2kgPj4gMl0gfD0gb3JkKHRleHRbaV0pIDw8ICgoaSAl
IDQpIDw8IDMpDQogICAgICAgICAgICBpICs9IDENCiAgICAgICAgdG1wW2kgPj4gMl0gfD0gMHg4MCA8
PCAoKGkgJSA0KSA8PCAzKQ0KICAgICAgICBpZiBpID4gNTU6DQogICAgICAgICAgICBjcnlwdGN5Y2xl
KHJldCwgdG1wKTsNCiAgICAgICAgICAgIGZvciBpIGluIHJhbmdlKDE2KToNCiAgICAgICAgICAgICAg
ICB0bXBbaV0gPSAwDQogICAgICAgIHRtcFsxNF0gPSB0eHRMZW4gKiA4Ow0KICAgICAgICBjcnlwdGN5
Y2xlKHJldCwgdG1wKTsNCiAgICAgICAgcmV0dXJuIHJldA0KICAgIGRlZiByZXplZG93YSh0ZXh0KToN
CiAgICAgICAgcmV0dXJuIGhleChqY3N5cyh0ZXh0KSkNCiAgICByZXR1cm4gcmV6ZWRvd2EoaW5fYWJj
KQ0K
'''


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

        tab = []
        re_site = re.compile(r'(?si)<tr>.*?<td>\s*<img.*?>\s*(.*?)</td>.*?<td.*?<a .*?href="(.*?[^/"]+)".*?<td.*?<td.*?>([^<]*).*?<div class="rate">([^<]*).*?</tr>')
        for r in re_site.finditer(link.text):
            name, site, variant, rate = r.groups()
            rate = rate.strip()
            self.control.log("Link ALL %s" % site)
            label = '{name} [COLOR dimgray]({rate})[/COLOR]'.format(name=name, rate=rate, variant=variant)
            li = ListItem(label, variant)
            li.setPath(site)
            if rate.endswith('%'):
                try:
                    li.setRating('alltube', float(rate[:-1]) / 10.0)
                except:
                    pass
            tab.append(li)
        if not tab:
            #d = xbmcgui.Dialog()
            #d.ok('Nie znaleziono streamingu', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return None

        # prefered site, TODO: use settings
        preselect = -1
        for i, e in enumerate(tab):
            if 'vidoza' in e.getLabel().lower():
                preselect = i
                break

        d = xbmcgui.Dialog()
        video_menu = d.select("Wybór strony video", tab, preselect=preselect)
        self.control.log('Alltube wybrales [%s]' % video_menu)

        if video_menu != -1:
            linkVideo = tab[video_menu].getPath()
            self.control.log('Alltube: wybrano [%s]' % linkVideo)
            if 'http://alltube.tv/special.php' in linkVideo:
                try:
                    tmp = base64.b64decode(special_code)
                    _myFun = compile(tmp, '', 'exec')
                    vGlobals = {"__builtins__": None, 'len': len, 'list': list, 'ord': ord, 'range': range}
                    vLocals = {'abc': ''}
                    exec _myFun in vGlobals, vLocals
                    myFun1 = vLocals['abc']
                except Exception as e:
                    self.control.log('Alltube err1 [%s]' % e)

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
                    self.control.log('Alltube err3 [%s]' % e)

                self.control.log("XXXXXXXXXXX %s" % mycookie)

                #http://alltube.tv/special.php?hosting=openload&id=oU9oQLz4F-U&width=673&height=471.09999999999997
                link = self.s.get(linkVideo+ '&width=673&height=471.09999999999997', cookies=mycookie,verify=False)
                self.control.log('Alltube  link [%s]' % link)
                match = re.search('<iframe src="(.+?)"', link.text)
                if match:
                    linkVideo = match.group(1)
            elif linkVideo.startswith('http://alltube.pl/link/'):
                page = self.request(linkVideo)
                for r in re.finditer(r'(?si)<section class="player".*?<iframe src="([^"]*)"', page):
                    url = r.group(1)
                    self.control.log('2.1 All pageparser   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s] -> [%s]' % (linkVideo, url))
                    return self.urlresolve(url)
            self.control.log('2 All pageparser   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
            #linkVideo = self.up.getVideoLink(tab2[video_menu], url)
            return self.urlresolve(linkVideo)

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



