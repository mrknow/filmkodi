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


import re,urllib,urlparse,json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers



class source:
    def __init__(self):
        self.base_link = 'http://www.filmxy.com/'
        #self.base_link = client.source(self.base_link, output='geturl')
        self.search_link = '?s=%s&quality=41'


    def get_movie(self, imdb, title, year):
        try:
            return


        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []
            """
            if url == None: return sources


            """
            #sources.append({'source': 'uptobox', 'quality': 'HD', 'provider': 'Filmxy', 'url': resolvers.request("http://uptobox.com/kvdc09c1i82g")})
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            #if url.startswith('stack://'): return url
            #url = client.request(url, output='geturl')
            #if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            #else: url = url.replace('https://', 'http://')
            return url
        except:
            return

