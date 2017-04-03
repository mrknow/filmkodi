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


import re,urllib,urlparse, json, base64

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import control
from resources.lib.libraries import videoquality
from resources.lib.libraries import cache



from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://cda-hd.pl/'
        self.search_link = '/?s=%s'

    def do_search(self, title, year, video_type):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % urllib.quote_plus(cleantitle.query(title))
            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'class': 'item'})
            for row in result:
                row_type = client.parseDOM(row, 'div', attrs={'class': 'typepost'})[0]
                if row_type != video_type:
                    continue
                names = client.parseDOM(row, 'span', attrs={'class': 'tt'})[0]
                names = names.split('/')
                year_found = client.parseDOM(row, 'span', attrs={'class': 'year'})
                if self.name_matches(names, title, year) and (len(year_found) == 0 or year_found[0] == year):
                    url = client.parseDOM(row, 'a', ret='href')[0]
                    return urlparse.urljoin(self.base_link, url)
        except :
            return

    def name_matches(self, names_found, title, year):
        for name in names_found:
            name = name.strip().encode('utf-8')
            name = name.replace('&#8217;','')
            # if ends with year
            clean_found_title = cleantitle.get(name)
            clean_title = cleantitle.get(title)
            # sometimes they add year to title so we need to check thet
            if clean_found_title == clean_title or clean_found_title == (clean_title + year):
                return True
        return False

    def get_first_not_none(self, collection):
        return next(item for item in collection if item is not None)


    def get_movie(self, imdb, title, year):
        return self.do_search(title, year, 'Film')


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        return self.do_search(tvshowtitle, year, 'Serial')


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            result = client.request(url)
            # cant user dom parser here because HTML is bugged div is not closed
            result = re.findall ('<ul class="episodios">(.*?)</ul>', result, re.MULTILINE | re.DOTALL)
            for item in result:
                season_episodes = re.findall ('<li>(.*?)</li>', item, re.MULTILINE | re.DOTALL)
                for row in season_episodes:
                    s = client.parseDOM(row, 'div', attrs={'class': 'numerando'})[0].split('x')
                    season_found = s[0].strip()
                    episode_found = s[1].strip()
                    if(season_found != season):
                        break
                    if episode_found == episode :
                        return client.parseDOM(row, 'a', ret='href')[0]

        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        #sources.append({'source': i[1].encode('utf-8'), 'quality': 'SD', 'provider': 'Alltube', 'url': url1, 'vtype':i[2].encode('utf-8')})
        try:
            sources = []

            if url == None: return sources

            result = client.request(url)
            box_result = client.parseDOM(result, 'li', attrs={'class': 'elemento'})

            if (len(box_result) != 0):
                sources = self.get_links_from_box(box_result)

            sources += self.get_from_main_player(result, sources)

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
           return resolvers.request(url)
        except:
            return

    def get_from_main_player(self, result, sources):

        q = 'SD'
        if len(sources) == 0 and (len(client.parseDOM(result, 'span', attrs={'class': 'calidad2'})) > 0):
            q = 'HD'
        player2 = client.parseDOM(result, 'div', attrs={'id': 'player2'})
        links = client.parseDOM(player2, 'iframe', ret='src')

        player_nav = client.parseDOM(result, 'div', attrs={'class': 'player_nav'})
        transl_type = client.parseDOM(player_nav, 'a')
        result_sources = []
        for i in range(0, len(links)):
            url = links[i]
            if (self.url_not_on_list(url, sources)):
                lang, info = self.get_lang_by_type(transl_type[i])
                host = url.split("//")[-1].split("/")[0]
                result_sources.append(
                    {'source': host, 'quality': q,  'url': url, 'vtype': info, 'provider': 'CdaHD'})

        return result_sources

    def url_not_on_list(self, url, sources):
        for el in sources:
            if el.get('url') == url:
                return False
        return True

    def get_links_from_box(self, result):
        sources = []
        for row in result:
            src_url = client.parseDOM(row, 'a', ret='href')[0]
            lang_type = client.parseDOM(row, 'span', attrs={'class': 'c'})[0]
            quality_type = client.parseDOM(row, 'span', attrs={'class': 'd'})[0]
            host = client.parseDOM(row, 'img', ret='alt')[0]
            lang, info = self.get_lang_by_type(lang_type)
            q = 'SD'
            if quality_type == 'Wysoka': q = 'HD'
            sources.append(
                {'source': host, 'quality': q,'url': src_url, 'vtype': info, 'provider': 'CdaHD'})

        return sources

    def get_lang_by_type(self, lang_type):
        if lang_type == 'Lektor PL':
            return 'pl', 'Lektor'
        if lang_type == 'Dubbing PL':
            return 'pl', 'Dubbing'
        if lang_type == 'Napisy PL':
            return 'pl', 'Napisy'
        if lang_type == 'PL':
            return 'pl', None
        return 'en', None




