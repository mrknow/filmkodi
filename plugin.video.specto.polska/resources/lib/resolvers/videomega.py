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


import urlparse,re
from resources.lib.libraries import client
from resources.lib.libraries import control
from resources.lib.libraries import jsunpack



def resolve(url):
    try:
        url = urlparse.urlparse(url).query
        url = urlparse.parse_qsl(url)[0][1]
        url = 'http://videomega.tv/cdn.php?ref=%s' % url
        #control.log("### VIDEOMEGA RES %s" % url)
        result = client.request(url, mobile=True)
        #control.log("### VIDEOMEGA RES %s" % result)
        result = re.compile('eval.*?{}\)\)').findall(result)[-1]
        #control.log("### VIDEOMEGA RES2 %s" % result)
        result = jsunpack.unpack(result)
        #control.log("### VIDEOMEGA RE3 %s" % result)
        #"src", "http://abo.cdn.vizplay.org/m2/769a65801d8e8a110452f2b74d4082d1.mp4?st=-A2O2o2soMR81Niiag5EyA&hash=Dw8Kth5gh-nNyMRbWLZMKA"
        url = re.compile('"src","(.*?)"').findall(result)[-1]
        control.log("### VIDEOMEGA RE4 %s" % url)
        return url
    except:
        return

def check(url):
    try:
        url = urlparse.urlparse(url).query
        url = urlparse.parse_qsl(url)[0][1]
        url = 'http://videomega.tv/cdn.php?ref=%s' % url
        result = client.request(url, mobile=True)
        result = re.compile('eval.*?{}\)\)').findall(result)[-1]
        result = jsunpack.unpack(result)
        url = re.compile('"src","(.*?)"').findall(result)[-1]
        control.log("### VIDEOMEGA RE3                   1111111111  %s" % url)
        if url.startswith('http://N/D/m/'): return False
        return True
    except:
        return False