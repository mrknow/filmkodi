# -*- coding: utf-8 -*-

'''
    FanFilm Add-on
    Copyright (C) 2016 mrknow

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import os,re,urllib

from resources.lib.libraries import client
from resources.lib.libraries import control


def solvequality(url):
    try:
        q='LQ'
        print ("solve",url)
        if 'openload' in url:
            result = client.request(url)
            data  = client.parseDOM(result, 'meta', attrs={'name':'description'}, ret='content')[0]
            print('##QQQQQQQQQQQQQQQ ', data)
            q=findquality(data)
        return q
    except:
        return q


def findquality(data):
    try:
        control.log('#### DTATA %s' % data )
        q='LQ'
        if '1080' in data:
            return '1080p'
        if '720' in data:
            return 'HD'
        if 'HDTS' in data:
            return 'CAM'
        return q
    except:
        return q


def capimage(data):
    try:
        url = client.parseDOM(data, 'img', ret='src')
        url = [i for i in url if 'captcha' in i]

        if not len(url) > 0: return

        response = keyboard(url[0])

        return {'code': response}
    except:
        pass


def numeric(data):
    try:
        url = re.compile("left:(\d+)px;padding-top:\d+px;'>&#(.+?);<").findall(data)

        if not len(url) > 0: return

        result = sorted(url, key=lambda ltr: int(ltr[0]))
        response = ''.join(str(int(num[1])-48) for num in result)

        return {'code': response}
    except:
        pass


def keyboard(response):
    try:
        i = os.path.join(control.dataPath,'img')
        f = control.openFile(i, 'w')
        f.write(client.request(response))
        f.close()
        f = control.image(450,5,375,115, i)
        d = control.windowDialog
        d.addControl(f)
        control.deleteFile(i)
        d.show()
        t = 'Type the letters in the image'
        k = control.keyboard('', t)
        k.doModal()
        c = k.getText() if k.isConfirmed() else None
        if c == '': c = None
        d.removeControl(f)
        d.close()
        return c
    except:
        return

