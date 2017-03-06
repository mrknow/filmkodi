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
import sys, json
import xbmcgui
from binascii import hexlify, unhexlify, a2b_hex, a2b_base64
from resources.lib.crypto.keyedHash.evp import EVP_BytesToKey
from resources.lib.crypto.cipher.aes_cbc  import AES_CBC
from hashlib import md5
from __generic_host__ import GenericHost

mainurl='http://anime-odcinki.pl/'
animemovies = 'http://anime-odcinki.pl/filmy'
animelist = 'http://anime-odcinki.pl/anime'

class Animeodcinki(GenericHost):
    scriptname = 'Anime-odcinki'
    host = 'animeodcinki'
    MENU_TAB = [
        {'id': 1, 'title': 'Nowe odcinki emitowane', 'mod': 'ListNowe'},
        {'id': 2, 'title': 'Lista Anime', 'mod': 'ListAnime'},
        {'id': 3, 'title': 'Filmy Anime', 'mod': 'ListMovieseLeter', },
        {'id': 4, 'title': 'Szukaj', 'mod': 'find', }

    ]

    def ListNowe(self):
        result = self.request(mainurl)
        r = self.client.parseDOM(result, 'section', attrs={'id': 'block-views-new-emitowane-block'})[0]
        r = self.client.parseDOM(r, 'div', attrs={'id': 'issued-ep'})[0]
        r = self.client.parseDOM(r, 'div')
        r = [(self.client.parseDOM(i, 'img', ret='src'), self.client.parseDOM(i, 'a', ret='href'), self.client.parseDOM(i, 'a')) for i in r]
        r = [(i[0][0], i[1][0], i[2][0]) for i in r if len(i[1]) > 0 and len(i[2]) > 0]
        for i in r:
            try:
                meta = {'title':i[2].encode('utf8'), 'poster':i[0]}
                params = {'service':self.host, 'name':'playselectedmovie', 'category':'','isplayable':'true', 'url':i[1]}
                params.update(meta)
                self.add2(params)
            except:
                pass
        self.dirend(int(sys.argv[1]))

    def ListAnime(self, url):
        result = self.request(url)
        r = self.client.parseDOM(result, 'div', attrs={'id': 'letter-index'})[0]
        r = self.client.parseDOM(r, 'span')
        r = [(self.client.parseDOM(i, 'a', ret='href')[0], self.client.parseDOM(i, 'a', ret='data-index')[0].upper()) for i in r]
        for i in r:
            self.add(self.host, 'items-menu', 'ListAnimeLeter', i[1], 'None', i[0] ,  True, False)
        self.control.directory(int(sys.argv[1]))


    def ListAnimeLeter(self, url):
        result = self.request(url)
        letter= url.split('?')[-1]
        r = self.client.parseDOM(result, 'tbody')[0]
        r = [self.client.parseDOM(r, 'tr'),self.client.parseDOM(r, 'tr', ret='data-fl')]
        r = [(r[0][idx].strip(), r[1][idx]) for idx, val in enumerate(r[0])]
        r = [(i[0], i[1]) for i in r if i[1] == letter]
        r = [(self.client.parseDOM(i[0], 'a', ret='href')[0], self.client.parseDOM(i[0], 'a')[0]) for i in r]
        for i in r:
            # (self, service, name, category,               title, iconimage, url, desc, rating, folder = True, isPlayable = True):
            self.add(self.host, 'items-menu', 'ListAnimeEpisodes', i[1], 'None', i[0],  True, False)
        self.control.directory(int(sys.argv[1]))


    def ListAnimeEpisodes(self, url):
        result = self.request(url)

        try:
            img = self.client.parseDOM(result, 'section', attrs={'id': 'anime-header'})[0]
            img = self.client.parseDOM(img, 'img', ret='src')[0]
        except:
            img=''
        try:
            mydesc=''
            #self.control.log('AAA%s' % result)
            desc = self.client.parseDOM(result, 'div', attrs={'class':'field field-name-body field-type-text-with-summary field-label-hidden'})[0]
            desc = self.client.parseDOM(desc,'p')
            for i in desc:
                self.control.log('AAA%s' % i.encode('utf-8'))
                mydesc += self.control.cleanhtml(i.encode('utf-8'))
        except Exception as e:
            self.control.log('E %s' % e)
            mydesc=''

        r = self.client.parseDOM(result, 'li', attrs={'class':'lista_odc_tytul_pozycja'})
        r = [(self.client.parseDOM(i, 'a', ret='href')[0], self.client.parseDOM(i, 'a')[0]) for i in r]
        #for i in r:
        #    self.add(self.host, 'playselectedmovie', 'None', i[1], img, i[0], 'aaaa', 'None', False, True)
        #self.control.directory(int(sys.argv[1]))
        for i in r:
            try:
                meta = {'title':i[1].encode('utf8'), 'poster':img, 'plot':mydesc}
                params = {'service':self.host, 'name':'playselectedmovie', 'category':'','isplayable':'true', 'url':i[0]}
                params.update(meta)
                self.add2(params)
            except:
                pass
        self.dirend(int(sys.argv[1]))

    def listsSearchResults(self, key):
        url = 'http://anime-odcinki.pl/szukaj/%s' % key
        result = self.request(url)
        r = self.client.parseDOM(result, 'li', attrs={'class':'search-result'})
        r = [(self.client.parseDOM(i, 'a', ret='href')[0], self.client.parseDOM(i, 'a')[0]) for i in r]
        for i in r:
            # (self, service, name, category,               title, iconimage, url, desc, rating, folder = True, isPlayable = True):
            self.add(self.host, 'None', 'ListAnimeEpisodes', i[1], 'None', i[0], True, False)
        self.control.directory(int(sys.argv[1]))

    def getMovieLinkFromXML(self, url):
        try:
            result = self.request(url)
            r = self.client.parseDOM(result, 'div', attrs={'id': 'video-player-control'})[0]
            r = [self.client.parseDOM(r, 'div', attrs={'class': 'video-player-mode'}), self.client.parseDOM(r, 'div', attrs={'class': 'video-player-mode'}, ret='data-hash')]
            r = [(r[0][idx].strip(), r[1][idx]) for idx, val in enumerate(r[0])]
            r1 = [i[0] for i in r]
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór strony video", r1)
            if video_menu != "":
                mylink = self._encryptPlayerUrl(json.loads(r[video_menu][1]))
                self.control.log('PLAY Mylink menu %s' % mylink)
                return self.urlresolve(mylink)

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
        self.control.log('URL: ' + str(url))
        if category=='ListNowe':
            self.ListNowe()
        elif category == 'ListMovieseLeter':
            self.ListAnime(animemovies)
        elif category == 'ListAnime':
            self.ListAnime(animelist)
        elif category == 'ListAnimeLeter':
            self.ListAnimeLeter(url)
        elif category == 'ListAnimeEpisodes':
            self.ListAnimeEpisodes(url)


    #from samsamsam
    #https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/raw/master/IPTVPlayer/hosts/hostanimeodcinki.py

    def _encryptPlayerUrl(self, data):
        decrypted = ''
        try:
            salt = a2b_hex(data["v"])
            key, iv = EVP_BytesToKey(md5, "s05z9Gpd=syG^7{", salt, 32, 16, 1)

            if iv != a2b_hex(data.get('b', '')):
                self.control.log("_encryptPlayerUrl IV mismatched")

            if 0:
                from Crypto.Cipher import AES
                aes = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
                decrypted = aes.decrypt(a2b_base64(data["a"]))
                decrypted = decrypted[0:-ord(decrypted[-1])]
            else:
                kSize = len(key)
                alg = AES_CBC(key, keySize=kSize)
                decrypted = alg.decrypt(a2b_base64(data["a"]), iv=iv)
                decrypted = decrypted.split('\x00')[0]
            decrypted = "%s" % json.loads(decrypted).encode('utf-8')
        except Exception:
            decrypted = ''
        return decrypted