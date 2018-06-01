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
import re,os
from __generic_host__ import GenericHost
import HTMLParser
import xbmcgui,xbmc
import random
mainUrl = 'http://efilmy.tv/'
catUrl = '/filmy.html'

from lib.utils import unpackstd

#lastadded = '/filmy/1'
#litera = 'http://filmy.to/filmy/1?litera=%s'
#bajki = '/bajki.php'
#szukaj = '/szukaj.php?title=%s'

class efilmy(GenericHost):

    scriptname = "Filmy online www.mrknow.pl - efilmy"
    host = 'efilmy'
    MENU_TAB = [
        {'id': 1, 'title': 'Ostatnio dodane', 'mod': 'OstatnioDodane'},
        #{'id': 10, 'title': 'Alfabetycznie', 'mod': 'Alfabetycznie'},
        {'id': 11, 'title': "Kategorie", 'mod': 'listsCategoriesMenu'},
        {'id': 12, 'title': "Popularne - 7 dni", 'mod': 'Popularne7'},
        {'id': 13, 'title': "Popularne - 14 dni", 'mod': 'Popularne14'},
        {'id': 14, 'title': "Popularne - 31 dni", 'mod': 'Popularne31'},
        {'id': 15, 'title': "Wszystkie", 'mod': 'Wszystkie'},
        {'id': 16, 'title': "Szukaj", 'mod': 'find'},
        {'id': 5, 'title': 'Historia wyszukiwania', 'mod': 'history'},

    ]

    def listsCategoriesMenu(self):
        result = self.request(urlparse.urljoin(mainUrl, catUrl))
        r = self.client.parseDOM(result, 'ul', attrs={"class": "movie-cat"})[0]
        #self.control.log("m %s " % (r))

        r = self.client.parseDOM(r, 'li')
        r = [(self.client.parseDOM(i, 'a', ret='href'), self.client.parseDOM(i, 'a')) for i in r]

        for i in r:
            self.control.log("m %s %s " % (i[0], i[1]))
            self.add('efilmy', 'categories-menu', i[1][0].encode('utf-8'),i[1][0].encode('utf-8'), 'None', urlparse.urljoin(mainUrl, i[0][0]).replace('.html',',p0.html'), True, False)
        self.control.directory(int(sys.argv[1]))

    def listsItems(self,url):
        #obliczamy stronę

        mypagenumber = re.findall('(\d+).html',url)[0]
        page = int(mypagenumber)
        self.control.log('[]1 %s' % page)
        mynext = url.replace(str(page)+'.html', str(page+1)+'.html')
        self.control.log('[]2 %s' % mynext)
        #except:
        #    mynext = ''
        self.control.log('[]3 %s' % mynext)
        result = self.request(url)
        result = self.client.parseDOM(result, 'div', attrs={'class':'holder'})[0]
        self.MyAddItems1(result,'list-item')
        self.add('efilmy', 'categories-menu', 'Następna >>>', 'Następna >>>', "None", mynext,  True, False)
        self.dirend(int(sys.argv[1]))

    def listsItems3(self, url, myclass2):
        result = self.request(url)
        self.MyAddItems(result,myclass2, 'cat')
        self.dirend(int(sys.argv[1]))

    def listsItems4(self, url, myclass1, myclass2):
        result = self.request(mainUrl)
        r = self.client.parseDOM(result, 'div', attrs={'id': myclass1})[0]
        self.MyAddItems(r,myclass2)
        self.dirend(int(sys.argv[1]))

    def MyAddItems(self, data, myclass, other='dsc'):
        r = self.client.parseDOM(data,'div', {"class": myclass})
        try:
            r = [(self.client.parseDOM(i,'a', {'class': 'pl'}, ret='href'),
                  self.client.parseDOM(i, 'a', {'class': 'pl'}),
                  self.client.parseDOM(i, 'a', {'class': 'en'}),
                  self.client.parseDOM(i,'img', ret='src'),
                  self.client.parseDOM(i,'span', attrs={'class':other})
                  ) for i in r]
        except:
            pass
        #for i in r:
        #    self.control.log('AAA %s' % str(i))
        r =[(i[0], i[1], i[2], i[3],re.findall('(\d{4})',i[4][0]),self.client.parseDOM(i[4][0], 'a')) for i in r]
        for i in r:
            try:
                #self.control.log('AAA %s' % str(i))
                meta = {'title': i[1][0], 'poster': urlparse.urljoin(mainUrl, i[3][0]), 'year': i[4][0],
                        'plot': i[5][0], 'genre': i[5][0] }
                try:
                    meta['originaltitle'] = i[2][0]
                except:
                    meta['originaltitle'] = i[1][0]
                    pass
                params = {'service': self.host, 'name': 'playselectedmovie', 'category': '', 'isplayable': 'true',
                          'url': i[0][0]}
                params.update(meta)
                self.add2(params)
            except:
                pass

    def MyAddItems1(self, data, myclass, other='dsc'):
        r = self.client.parseDOM(data,'div', {"class": myclass})
        try:
            r = [(self.client.parseDOM(i,'a', {'class': 'title_pl'}, ret='href'),
                  self.client.parseDOM(i, 'a', {'class': 'title_pl'}),
                  self.client.parseDOM(i, 'a', {'class': 'title_en'}),
                  self.client.parseDOM(i,'img', ret='src'),
                  self.client.parseDOM(i, 'p')
                  ) for i in r]
        except:
            pass
        #for i in r:
        #    self.control.log('AAA %s' % str(i))
        r =[(i[0], i[1], i[2], i[3],re.findall('(\d{4})',i[2][0]),i[4]) for i in r]
        for i in r:
            try:
                #self.control.log('AAA %s' % str(i))
                meta = {'title': i[1][0], 'poster': urlparse.urljoin(mainUrl, i[3][0]), 'year': i[4][0],
                        'plot': i[5][0], 'genre': i[5][0] }
                try:
                    meta['originaltitle'] = i[2][0]
                except:
                    meta['originaltitle'] = i[1][0]
                    pass
                params = {'service': self.host, 'name': 'playselectedmovie', 'category': '', 'isplayable': 'true',
                          'url': i[0][0]}
                params.update(meta)
                self.add2(params)
            except:
                pass

    def getMovieLinkFromXML(self, url):
        try:
            IMAGEFILE = os.path.join(self.control.dataPath, 'efilmytv.jpg')
            cookie = self.s.get(urlparse.urljoin(mainUrl, url), verify=False).cookies.get_dict()
            for i in cookie:
                cookie = i + '=' + cookie[i]
            HEADER = {'Referer': urlparse.urljoin(mainUrl, url),
                      'Cookie':cookie,
                      'User-Agent': self.cache.get(self.control.randomagent, 1)}
            result = self.s.get(urlparse.urljoin(mainUrl, url), headers=HEADER).text
            myfile1 = re.compile(
                '<div id="(.*?)" alt="n" class="embedbg"><img src="(.*?)"/></div><div class="versionholder">').findall(
                result)
            if 'serial' in url:
                myurl = 'http://www.efilmy.tv/seriale.php?cmd=show_player&id=' + myfile1[0][0]
            else:
                #        http://www.efilmy.tv//filmy.php?cmd=show_player&id=87787
                myurl = 'http://www.efilmy.tv//filmy.php?cmd=show_player&id='+ myfile1[0][0]
            self.control.log("url %s " % myurl)
            link2 = self.request(urlparse.urljoin(mainUrl, myurl), headers=HEADER)

            if '<p><strong>Zabezpieczenie przeciwko robotom</strong></p>' in link2:
                mymatch = re.compile(
                    '<input type="hidden" name="id" value=(\d+) />\r\n<input type="hidden" name="mode" value=(\w+) />').findall(
                    link2)
                self.control.log("mymatch %s" % str(mymatch))
                link20 =  self.s.get('http://www.efilmy.tv//mirrory.php?cmd=generate_captcha&time=' + str(random.randint(1, 1000)), stream=True)
                if link20.status_code == 200:
                    with open(IMAGEFILE, 'wb') as f:
                        for chunk in link20:
                            f.write(chunk)

                img = xbmcgui.ControlImage(450, 0, 400, 130, IMAGEFILE)
                wdlg = xbmcgui.WindowDialog()
                wdlg.addControl(img)
                wdlg.show()
                kb = xbmc.Keyboard('', '[CR][CR]Przepisz litery z obrazka', False)
                kb.doModal()
                if (kb.isConfirmed()):
                    solution = kb.getText()
                    if solution == '':
                        raise Exception('You must enter text in the image to access video')
                else:
                    dialog = xbmcgui.Dialog()
                    dialog.ok(" Problem", " Nie wprowadzono kodu Captcha")
                    return ''
                xbmc.sleep(2 * 1000)

                postdata = {'captcha': solution, "id": str(mymatch[0][0]), "mode": str(mymatch[0][1])}
                HEADER['Referer'] = myurl
                #http://www.efilmy.tv//mirrory.php?cmd=check_captcha
                r = self.s.post("http://www.efilmy.tv//mirrory.php?cmd=check_captcha", data=postdata, headers=HEADER)
                link2 = r.text

            # myfile2 = re.compile('Base64.decode\("(.*?)"\)').findall(link2)
            myfile2 = re.search('(eval\(function\(p,a,c,k,e,d\).+)\s+?', link2)
            self.control.log("m2 %s " % myfile2.group(1))
            if myfile2:
                r = unpackstd.unpack(myfile2.group(1))
                r = r.decode('string-escape')
                self.control.log("m3 %s " % r)

                r1 = re.compile('Base64.decode\("(.*?)"\)').findall(r)
                r1 = r1[0]
                # r1 =r1.replace('\\\\','\\')

                import base64
                self.control.log("m4 %s " % r1)
                r = ''
                for byte in r1.split('\\x'):
                    if byte:  # to get rid of empties
                        r += chr(int(byte, 16))

                decode = base64.b64decode(r)
                # decode =decode.replace('\\\\','\\')
                r2 = self.client.parseDOM(decode.lower(), 'iframe', ret='src')[0]
                self.control.log("m2 %s " % r2)
                return self.urlresolve(r2)
            return

        except Exception as e:
            self.control.log('ERROR %s' % e)
            return None

    def listsSearchResults(self, key):
        self.listsItems('http://www.efilmy.tv/szukaj,%s,0.html' % key)

    def sub_handleService(self, params):
    	#params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        if strona == None:
            strona = '1'
        print("Strona", strona)
        print("name", name)
        self.control.log("category: %s, url: %s " % (category, url))
        print("url", url)
        if name == None:
            self.listsMainMenu(self.MENU_TAB)
        elif name == 'main-menu' and category == 'OstatnioDodane':
            self.listsItems4(mainUrl, 'main-movie-content', 'main-list-item')
        elif name == 'main-menu' and category == "Popularne7":
            self.listsItems3('http://www.efilmy.tv/filmy.php?cmd=popularne&dni=7','similar-item')
        elif name == 'main-menu' and category == "Popularne31":
            self.listsItems3('http://www.efilmy.tv/filmy.php?cmd=popularne&dni=31','similar-item')
        elif name == 'main-menu' and category == "Popularne14":
            self.listsItems3('http://www.efilmy.tv/filmy.php?cmd=popularne&dni=14','similar-item')
        elif name == 'main-menu' and category == "listsCategoriesMenu":
            self.listsCategoriesMenu()
        elif name == 'main-menu' and category == "Wszystkie":
            self.listsItems('http://www.efilmy.tv/filmy,p0.html')
        elif name == 'categories-menu' and category != 'None':
            self.listsItems(url)




