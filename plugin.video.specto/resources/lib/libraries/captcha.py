# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

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


def request(data):
    captcha = solvemedia(data)
    if not captcha == None: return captcha

    captcha = recaptcha(data)
    if not captcha == None: return captcha

    captcha = capimage(data)
    if not captcha == None: return captcha

    captcha = numeric(data)
    if not captcha == None: return captcha


def solvemedia(data):
    try:
        url = client.parseDOM(data, 'iframe', ret='src')
        url = [i for i in url if 'api.solvemedia.com' in i]

        if not len(url) > 0: return

        result = client.request(url[0], referer='')

        response = client.parseDOM(result, 'iframe', ret='src')
        response += client.parseDOM(result, 'img', ret='src')
        response = [i for i in response if '/papi/media' in i][0]
        response = 'http://api.solvemedia.com' + response
        response = keyboard(response)

        post = {}
        f = client.parseDOM(result, 'form', attrs = {'action': 'verify.noscript'})[0]
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post.update({'adcopy_response': response})

        client.request('http://api.solvemedia.com/papi/verify.noscript', post=post)

        return {'adcopy_challenge': post['adcopy_challenge'], 'adcopy_response': 'manual_challenge'}
    except:
        pass


def recaptcha(data):
    try:
        url = []
        if data.startswith('http://www.google.com'): url += [data]
        url += client.parseDOM(data, 'script', ret='src', attrs = {'type': 'text/javascript'})
        url = [i for i in url if 'http://www.google.com' in i]

        if not len(url) > 0: return

        result = client.request(url[0])
        challenge = re.compile("challenge\s+:\s+'(.+?)'").findall(result)[0]
        response = 'http://www.google.com/recaptcha/api/image?c=' + challenge
        response = keyboard(response)

        return {'recaptcha_challenge_field': challenge, 'recaptcha_challenge': challenge, 'recaptcha_response_field': response, 'recaptcha_response': response}
    except:
        pass


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

