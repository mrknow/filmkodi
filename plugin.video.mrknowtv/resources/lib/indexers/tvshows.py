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


import os,sys,re,json,urllib,urlparse,base64,datetime

try: action = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))['action']
except: action = None

from resources.lib.libraries import trakt
from resources.lib.libraries import control
from resources.lib.libraries import client
from resources.lib.libraries import cache
from resources.lib.libraries import metacache
from resources.lib.libraries import favourites
from resources.lib.libraries import workers
from resources.lib.libraries import views


class tvshows:
    def __init__(self):
        self.list = []

        #self.tmdb_link = 'http://api.themoviedb.org'

        self.trakt_link = 'http://api-v2launch.trakt.tv'
        self.imdb_link = 'http://www.imdb.com'
        #self.tmdb_key = control.tmdb_key
        self.tvdb_key = control.tvdb_key
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.week_date = (self.datetime - datetime.timedelta(days = 7)).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.year_date = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')
        self.trakt_user = control.setting('trakt.user')
        self.imdb_user = control.setting('imdb_user').replace('ur', '')
        self.info_lang = control.setting('infoLang') or 'en'

        #self.tmdb_info_link = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s&append_to_response=credits,content_ratings,external_ids' % ('%s', self.tmdb_key, self.info_lang)
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key, '%s', re.sub('bg', 'en', self.info_lang))
        #self.tmdb_by_imdb = 'http://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id' % ('%s', self.tmdb_key)
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'
        #self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        #self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.tvdb_image = 'http://thetvdb.com/banners/'

        #self.persons_link = 'http://api.themoviedb.org/3/search/person?api_key=%s&query=%s&include_adult=false&page=1' % (self.tmdb_key, '%s')
        #self.genres_link = 'http://api.themoviedb.org/3/genre/tv/list?api_key=%s&language=%s' % (self.tmdb_key, self.info_lang)

        #self.popular_link = 'http://api.themoviedb.org/3/tv/popular?api_key=%s&page=1'
        #self.popular_link = 'https://www.themoviedb.org/remote/tv?language=%s&list_style=poster_card&page=1' % (self.info_lang)
        #self.popular_link = 'http://www.imdb.com/search/title?production_status=released&title_type=tv_series'
        self.popular_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,sort=moviemeter,asc&count=20&start=1'
        self.year_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,sort=moviemeter,asc&count=20&start=1&year=%s'

        self.rating_link = 'http://www.imdb.com/search/title?at=0&count=20&languages=en&num_votes=500,&sort=user_rating&title_type=tv_series,mini_series&start=1'
        self.views_link = 'http://www.imdb.com/search/title?at=0&count=20&languages=en&sort=num_votes&title_type=tv_series,mini_series&start=1'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,&genres=%s&sort=moviemeter,asc&count=20&start=1'

        self.airing_link = 'https://api-v2launch.trakt.tv/calendars/all/shows/%s/1?limit=20' % self.today_date
        #self.airing_link = 'http://api.themoviedb.org/3/tv/airing_today?api_key=%s&page=1'
        #self.airing_link   = 'https://www.themoviedb.org/remote/tv/airing-today?list_style=poster_card&page=1'

        #self.premiere_link = 'http://api.themoviedb.org/3/discover/tv?api_key=%s&first_air_date.gte=%s&first_air_date.lte=%s&page=1' % ('%s', self.year_date, self.today_date)
        self.premiere_link = 'https://api-v2launch.trakt.tv/calendars/all/shows/premieres/%s/7?limit=20' % self.week_date
        #self.active_link = 'http://api.themoviedb.org/3/tv/on_the_air?api_key=%s&page=1'
        #self.active_link  = 'https://www.themoviedb.org/remote/tv/on-the-air?list_style=poster_card&page=1'

        #self.person_link = 'http://api.themoviedb.org/3/person/%s?api_key=%s&append_to_response=tv_credits'
        #self.genre_link = 'http://api.themoviedb.org/3/discover/tv?api_key=%s&with_genres=%s&air_date.gte=%s&air_date.lte=%s&page=1' % ('%s', '%s', self.year_date, self.today_date)
        #self.network_link = 'http://api.themoviedb.org/3/discover/tv?api_key=%s&with_networks=%s&air_date.gte=%s&air_date.lte=%s&page=1' % ('%s', '%s', self.year_date, self.today_date)
        #self.network_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,%S&company=%s&sort=moviemeter,asc&count=40&start=1' % (self.today_date, %s)
        self.trending_link = 'http://api-v2launch.trakt.tv/shows/trending?limit=20&page=1'

        self.search_link = 'http://api-v2launch.trakt.tv/search?type=show&query=%s'
        self.traktlists_link = 'http://api-v2launch.trakt.tv/users/%s/lists' % self.trakt_user
        self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items' % (self.trakt_user, '%s')
        self.traktcollection_link = 'http://api-v2launch.trakt.tv/users/%s/collection/shows' % self.trakt_user
        self.traktwatchlist_link = 'http://api-v2launch.trakt.tv/users/%s/watchlist/shows' % self.trakt_user
        self.traktfeatured_link = 'http://api-v2launch.trakt.tv/recommendations/shows?limit=20'
        self.traktratings_link = 'https://api-v2launch.trakt.tv/users/%s/ratings/shows' % self.trakt_user
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&sort=title:asc&title_type=tv_series,mini_series&start=1'
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist' % self.imdb_user

        self.genres_tab = [('Action', 'action'), ('Adventure', 'adventure'), ('Animation', 'animation'),('Biography', 'biography'),
                           ('Comedy', 'comedy'), ('Crime', 'crime'), ('Drama', 'drama'),('Family', 'family'), ('Fantasy', 'fantasy'),
                           ('History', 'history'), ('Horror', 'horror'),('Music ', 'music'), ('Musical', 'musical'), ('Mystery', 'mystery'),
                           ('Romance', 'romance'),('Science Fiction', 'sci_fi'), ('Sport', 'sport'), ('Thriller', 'thriller'), ('War', 'war'),('Western', 'western')]


    def get(self, url, idx=True):
        try:
            try: url = getattr(self, url + '_link')
            except: pass

            try: u = urlparse.urlparse(url).netloc.lower()
            except: pass


            #if u in self.tmdb_link:
            #    self.list = cache.get(self.tmdb_list, 24, url)
            #    self.worker()

            #elif u in self.tmdb_link2:
            #    self.list = cache.get(self.tmdb_list2, 24, url)
            #    self.worker()

            if u in self.trakt_link and '/users/' in url:
                self.list = cache.get(self.trakt_list, 0, url)
                self.list = sorted(self.list, key=lambda k: k['title'])
                if idx == True: self.worker()

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url)
                if idx == True: self.worker()


            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_list, 0, url, idx)
                self.worker()

            elif u in self.imdb_link and '/search/title' in url:
                control.log("><><><><> ******************** %s" % url)

                self.list = cache.get(self.imdb_list2, 24, url)
                self.worker()

            elif u in self.imdb_link:
                control.log("><><><><> ******************** %s" % u)


                self.list = cache.get(self.imdb_list, 24, url)
                self.worker()


            if idx == True: self.tvshowDirectory(self.list)
            return self.list
        except:
            pass


    def favourites(self):
        try:
            items = favourites.getFavourites('tvshows')
            self.list = [i[1] for i in items]

            for i in self.list:
                if not 'name' in i: i['name'] = i['title']
                try: i['title'] = i['title'].encode('utf-8')
                except: pass
                try: i['name'] = i['name'].encode('utf-8')
                except: pass
                if not 'year' in i: i['year'] = '0'
                if not 'duration' in i: i['duration'] = '0'
                if not 'imdb' in i: i['imdb'] = '0'
                if not 'tmdb' in i: i['tmdb'] = '0'
                if not 'tvdb' in i: i['tvdb'] = '0'
                if not 'tvrage' in i: i['tvrage'] = '0'
                if not 'poster' in i: i['poster'] = '0'
                if not 'banner' in i: i['banner'] = '0'
                if not 'fanart' in i: i['fanart'] = '0'

            self.worker()
            self.list = sorted(self.list, key=lambda k: k['title'])
            self.tvshowDirectory(self.list)
        except:
            return


    def search(self, query=None):
        try:
            if query == None:
                t = control.lang(30231).encode('utf-8')
                k = control.keyboard('', t) ; k.doModal()
                self.query = k.getText() if k.isConfirmed() else None
            else:
                self.query = query

            if (self.query == None or self.query == ''): return

            url = self.search_link % urllib.quote_plus(self.query)
            self.list = cache.get(self.trakt_list, 0, url)

            self.worker()
            self.tvshowDirectory(self.list)
            return self.list
        except:
            return


    def person(self, query=None):
        try:
            if query == None:
                t = control.lang(30231).encode('utf-8')
                k = control.keyboard('', t) ; k.doModal()
                self.query = k.getText() if k.isConfirmed() else None
            else:
                self.query = query

            if (self.query == None or self.query == ''): return

            url = self.persons_link % urllib.quote_plus(self.query)
            self.list = cache.get(self.tmdb_person_list, 0, url)

            for i in range(0, len(self.list)): self.list[i].update({'action': 'tvshows'})
            self.addDirectory(self.list)
            return self.list
        except:
            return


    def genres(self):
        try:
            for i in self.genres_tab:
                self.list.append({'name': i[0], 'url': self.genre_link % i[1], 'image': 'tvGenres.png', 'action': 'tvshows'})
            self.addDirectory(self.list)
            return self.list


        except:
            return


    def networks(self):
        networks = [
        ('ABC', '2'), ('CBS', '16'), ('NBC', '6|582'), ('FOX', '19|303'), ('CW', '71|194'), ('A&E', '129|567|891'),
        ('ABC Family', '75'), ('AMC', '174'), ('Animal Planet', '91'), ('Bravo', '74|312|485'),
        ('Cartoon Network', '56|217|262'), ('Cinemax', '359'), ('Comedy Central', '47|278'),
        ('Disney Channel', '54|515|539|730'), ('Disney XD', '44'), ('Discovery Channel', '64|106|755'),
        ('E! Entertainment', '76|407|645'), ('FX', '88'), ('Hallmark', '384'), ('HBO', '49'), ('HGTV', '210|482'),
        ('History Channel', '65|238|893'), ('Discovery ID', '244'), ('Lifetime', '34|892'), ('MTV', '33|335|488'),
        ('National Geographic', '43|799'), ('Nickelodeon', '13|35|234|259|416'), ('Showtime', '67|643'),
        ('Spike', '55'), ('Starz', '318'), ('Syfy', '77|586'), ('TBS', '68'), ('TLC', '84'), ('TNT', '41|613|939'),
        ('Travel Channel', '209'), ('TV Land', '397'), ('USA', '30'), ('VH1', '158')]

        for i in networks: self.list.append({'name': i[0], 'url': self.network_link % ('%s', i[1]), 'image': 'tvshows.jpg', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def years(self):
        year = (self.datetime.strftime('%Y'))

        for i in range(int(year)-0, int(year)-50, -1): self.list.append({'name': str(i), 'url': self.year_link % (str(i)), 'image': 'tvshows.jpg', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def userlists(self):
        try:
            userlists = []
            if trakt.getTraktCredentials() == False: raise Exception()
            userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link)
        except:
            pass
        try:
            self.list = []
            if self.imdb_user == '': raise Exception()
            userlists += cache.get(self.imdb_user_list, 0, self.imdblists_link)
        except:
            pass

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'tvUserlists.jpg', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def imdb_list2(self, url, idx=True):
        #control.log("><><><><> imdb_list2 ******************** %s" % idx)
        #http://ia.media-imdb.com/images/M/MV5BMTg3OTc0NzkyOV5BMl5BanBnXkFtZTgwMDMwMTM3MjE@._V1_SX640_SY720_.jpg
        try:
            if url == self.imdbwatchlist_link:
                def imdb_watchlist_id(url):
                    return re.compile('/export[?]list_id=(ls\d*)').findall(client.request(url))[0]
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url


            headers = {'Accept-Language': 'en-US'}
            result = str(client.request(url,headers=headers))

            try:
                if idx == True: raise Exception()
                pages = client.parseDOM(result, 'div', attrs = {'class': 'desc'})[0]
                pages = re.compile('Page \d+? of (\d*)').findall(pages)[0]
                for i in range(1, int(pages)):
                    u = url.replace('&start=1', '&start=%s' % str(i*100+1))
                    result += str(client.request(u))
            except:
                pass

            result = result.replace('\n','')
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'tr', attrs = {'class': '.+?'})
            items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return

        try:
            next = client.parseDOM(result, 'span', attrs = {'class': 'pagination'})
            next += client.parseDOM(result, 'div', attrs = {'class': 'pagination'})
            name = client.parseDOM(next[-1], 'a')[-1]
            if 'laquo' in name: raise Exception()
            next = client.parseDOM(next, 'a', ret='href')[-1]
            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next).query)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                try: title = client.parseDOM(item, 'a')[1]
                except: pass
                try: title = client.parseDOM(item, 'a', attrs = {'onclick': '.+?'})[-1]
                except: pass
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'year_type'})[0]
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                name = '%s (%s)' % (title, year)
                try: name = name.encode('utf-8')
                except: pass

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = 'tt' + re.sub('[^0-9]', '', imdb.rsplit('tt', 1)[-1])
                imdb = imdb.encode('utf-8')

                poster = '0'
                try: poster = client.parseDOM(item, 'img', ret='src')[0]
                except: pass
                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: pass
                if not ('_SX' in poster or '_SY' in poster): poster = '0'
                poster = re.sub('_SX\d*|_SY\d*|_CR\d+?,\d+?,\d+?,\d*','_SX500', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})
                genre = client.parseDOM(genre, 'a')
                genre = ' / '.join(genre)
                if genre == '': genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')

                try: duration = re.compile('(\d+?) mins').findall(item)[-1]
                except: duration = '0'
                duration = client.replaceHTMLCodes(duration)
                duration = duration.encode('utf-8')

                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': 'rating rating-list'})[0]
                except: votes = '0'
                try: votes = re.compile('[(](.+?) votes[)]').findall(votes)[0]
                except: votes = '0'
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except: mpaa = '0'
                try: mpaa = client.parseDOM(mpaa, 'span', ret='title')[0]
                except: mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

                director = client.parseDOM(item, 'span', attrs = {'class': 'credit'})
                director += client.parseDOM(item, 'div', attrs = {'class': 'secondary'})
                try: director = [i for i in director if 'Director:' in i or 'Dir:' in i][0]
                except: director = '0'
                director = director.split('With:', 1)[0].strip()
                director = client.parseDOM(director, 'a')
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                cast = client.parseDOM(item, 'span', attrs = {'class': 'credit'})
                cast += client.parseDOM(item, 'div', attrs = {'class': 'secondary'})
                try: cast = [i for i in cast if 'With:' in i or 'Stars:' in i][0]
                except: cast = '0'
                cast = cast.split('With:', 1)[-1].strip()
                cast = client.replaceHTMLCodes(cast)
                cast = cast.encode('utf-8')
                cast = client.parseDOM(cast, 'a')
                if cast == []: cast = '0'

                plot = '0'
                try: plot = client.parseDOM(item, 'span', attrs = {'class': 'outline'})[0]
                except: pass
                try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except: pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: pass

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': '0', 'cast': cast, 'plot': plot, 'tagline': tagline, 'name': name, 'code': imdb, 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': '0', 'next': next})
                #self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': '0', 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0', 'cast': '0', 'plot': plot, 'name': title, 'code': '0', 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})

            except:
                pass

        return self.list


    def trakt_list(self, url):
        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full,images'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

            result = trakt.getTrakt(u)
            result = json.loads(result)

            items = []
            for i in result:
                try: items.append(i['show'])
                except: pass
            if len(items) == 0:
                items = result
        except:
            return

        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            p = str(int(q['page']) + 1)
            if p == '5': raise Exception()
            q.update({'page': p})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            next = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = item['title']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['year']
                year = re.sub('[^0-9]', '', str(year))
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                tmdb = item['ids']['tmdb']
                if tmdb == None or tmdb == '': tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                tvrage = item['ids']['tvrage']
                if tvrage == None or tvrage == '': tvrage = '0'
                tvrage = re.sub('[^0-9]', '', str(tvrage))
                tvrage = tvrage.encode('utf-8')

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                tvdb = item['ids']['tvdb']
                if tvdb == None or tvdb == '': raise Exception()
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                poster = '0'
                try: poster = item['images']['poster']['medium']
                except: pass
                if poster == None or not '/posters/' in poster: poster = '0'
                poster = poster.rsplit('?', 1)[0]
                poster = poster.encode('utf-8')

                banner = poster
                try: banner = item['images']['banner']['full']
                except: pass
                if banner == None or not '/banners/' in banner: banner = '0'
                banner = banner.rsplit('?', 1)[0]
                banner = banner.encode('utf-8')

                fanart = '0'
                try: fanart = item['images']['fanart']['full']
                except: pass
                if fanart == None or not '/fanarts/' in fanart: fanart = '0'
                fanart = fanart.rsplit('?', 1)[0]
                fanart = fanart.encode('utf-8')

                try: premiered = item['first_aired']
                except: premiered = '0'
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: studio = item['network']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try: genre = item['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')

                try: duration = str(item['runtime'])
                except: duration = '0'
                if duration == None: duration = '0'
                duration = duration.encode('utf-8')

                try: rating = str(item['rating'])
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = rating.encode('utf-8')

                try: votes = str(item['votes'])
                except: votes = '0'
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == None: votes = '0'
                votes = votes.encode('utf-8')

                try: mpaa = item['certification']
                except: mpaa = '0'
                if mpaa == None: mpaa = '0'
                mpaa = mpaa.encode('utf-8')

                try: plot = item['overview']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': '0', 'plot': plot, 'name': title, 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvrage': tvrage, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'next': next})
            except:
                pass

        return self.list


    def trakt_user_list(self, url):
        try:
            result = trakt.getTrakt(url)
            items = json.loads(result)
        except:
            pass

        for item in items:
            try:
                name = item['name']
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = self.traktlist_link % item['ids']['slug']
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        return self.list


    def imdb_list(self, url, idx=True):
        try:
            if url == self.imdbwatchlist_link:
                def imdb_watchlist_id(url):
                    return re.compile('/export[?]list_id=(ls\d*)').findall(client.request(url))[0]
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url

            result = str(client.request(url))

            try:
                if idx == True: raise Exception()
                pages = client.parseDOM(result, 'div', attrs = {'class': 'desc'})[0]
                pages = re.compile('Page \d+? of (\d*)').findall(pages)[0]
                for i in range(1, int(pages)):
                    u = url.replace('&start=1', '&start=%s' % str(i*100+1))
                    result += str(client.request(u))
            except:
                pass

            result = result.replace('\n','')
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return

        try:
            next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[-1]
            name = client.parseDOM(next, 'a')[-1]
            if 'laquo' in name: raise Exception()
            next = client.parseDOM(next, 'a', ret='href')[-1]
            next = '%s%s' % (url.split('?', 1)[0], next)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = client.parseDOM(item, 'a', attrs = {'onclick': '.+?'})[-1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'year_type'})[0]
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = 'tt' + re.sub('[^0-9]', '', imdb.rsplit('tt', 1)[-1])
                imdb = imdb.encode('utf-8')

                poster = '0'
                try: poster = client.parseDOM(item, 'img', ret='src')[0]
                except: pass
                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: pass
                if not ('_SX' in poster or '_SY' in poster): poster = '0'
                poster = re.sub('_SX\d*|_SY\d*|_CR\d+?,\d+?,\d+?,\d*','_SX500', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except: plot = '0'
                plot = plot.rsplit('<span>', 1)[0].strip()
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': '0', 'duration': '0', 'rating': rating, 'votes': '0', 'mpaa': '0', 'cast': '0', 'plot': plot, 'name': title, 'code': imdb, 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': '0'})
            except:
                pass

        return self.list


    def imdb_user_list(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'div', attrs = {'class': 'list_name'})
        except:
            pass

        for item in items:
            try:
                name = client.parseDOM(item, 'a')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = url.split('/list/', 1)[-1].replace('/', '')
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        return self.list


    def worker(self):
        self.meta = []
        total = len(self.list)

        for i in range(0, total): self.list[i].update({'metacache': False})
        self.list = metacache.fetch(self.list, self.info_lang)

        for r in range(0, total, 25):
            threads = []
            for i in range(r, r+25):
                if i <= total: threads.append(workers.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

        #self.list = [i for i in self.list if not i['tvdb'] == '0']

        if len(self.meta) > 0: metacache.insert(self.meta)


    def super_info(self, i):
        #control.log("##################><><><><> super_info START  %s" % i)
        try:
            if self.list[i]['metacache'] == True: raise Exception()

            try: imdb = self.list[i]['imdb']
            except: imdb = '0'
            try: tmdb = self.list[i]['tmdb']
            except: tmdb = '0'
            try: tvdb = self.list[i]['tvdb']
            except: tvdb = '0'
            try: tvrage = self.list[i]['tvrage']
            except: tvrage = '0'

            """
            if not tmdb == '0':
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                url = self.tmdb_info_link % tmdb

                item = client.request(url, timeout='10')
                if item == None: raise Exception()
                item = json.loads(item)

                if tvdb == '0':
                    tvdb = item['external_ids']['tvdb_id']
                    if tvdb == '' or tvdb == None: tvdb = '0'
                    tvdb = re.sub('[^0-9]', '', str(tvdb))
                    tvdb = tvdb.encode('utf-8')
                    self.list[i].update({'tvdb': tvdb})

                if tvrage == '0':
                    tvrage = item['external_ids']['tvrage_id']
                    if tvrage == '' or tvrage == None: tvrage = '0'
                    tvrage = re.sub('[^0-9]', '', str(tvrage))
                    tvrage = tvrage.encode('utf-8')
                    self.list[i].update({'tvrage': tvrage})

                if imdb == '0':
                    imdb = item['external_ids']['imdb_id']
                    if imdb == '' or imdb == None: imdb = '0'
                    if not imdb == '0': imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                    imdb = imdb.encode('utf-8')
                    self.list[i].update({'imdb': imdb})


            elif not imdb == '0':
                url = self.tmdb_by_imdb % imdb
                result = client.request(url, timeout='10')
                result = json.loads(result)

                tmdb = result['tv_results'][0]['id']
                if tmdb == '' or tmdb == None: tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')
                self.list[i].update({'tmdb': tmdb})

                if not tmdb == '0':
                    url = self.tmdb_info_link % tmdb

                    item = client.request(url, timeout='10')
                    if item == None: raise Exception()
                    item = json.loads(item)

                    tvdb = item['external_ids']['tvdb_id']
                    if tvdb == '' or tvdb == None: tvdb = '0'
                    tvdb = re.sub('[^0-9]', '', str(tvdb))
                    tvdb = tvdb.encode('utf-8')
                    self.list[i].update({'tvdb': tvdb})

                    tvrage = item['external_ids']['tvrage_id']
                    if tvrage == '' or tvrage == None: tvrage = '0'
                    tvrage = re.sub('[^0-9]', '', str(tvrage))
                    tvrage = tvrage.encode('utf-8')
                    self.list[i].update({'tvrage': tvrage})
            """

            if tvdb == '0' and not imdb == '0':
                url = self.tvdb_by_imdb % imdb

                result = client.request(url, timeout='10')

                try: tvdb = client.parseDOM(result, 'seriesid')[0]
                except: tvdb = '0'

                try: name = client.parseDOM(result, 'SeriesName')[0]
                except: name = '0'
                dupe = re.compile('[***]Duplicate (\d*)[***]').findall(name)
                if len(dupe) > 0: tvdb = str(dupe[0])

                if tvdb == '': tvdb = '0'
                self.list[i].update({'tvdb': tvdb})


            if not tvdb == '0':
                url = self.tvdb_info_link % tvdb
                item2 = client.request(url, timeout='10')

                if imdb == '0':
                    try: imdb = client.parseDOM(item2, 'IMDB_ID')[0]
                    except: pass
                    if imdb == '': imdb = '0'
                    imdb = imdb.encode('utf-8')
                    self.list[i].update({'imdb': imdb})


            if imdb == '0':
                url = self.imdb_by_query % (urllib.quote_plus(self.list[i]['title']), self.list[i]['year'])
                item3 = client.request(url, timeout='10')
                item3 = json.loads(item3)
                imdb = item3['imdbID']
                if imdb == None or imdb == '' or imdb == 'N/A': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')
                self.list[i].update({'imdb': imdb})


            try: poster = item['poster_path']
            except: poster = ''
            if poster == '' or poster == None: poster = '0'
            if not poster == '0': poster = '%s%s' % (self.tmdb_poster, poster)
            if poster == '0':
                try: poster = client.parseDOM(item2, 'poster')[0]
                except: poster = '0'
                if not poster == '0': poster = self.tvdb_image + poster
            poster = client.replaceHTMLCodes(poster)
            poster = poster.encode('utf-8')
            if not poster == '0': self.list[i].update({'poster': poster})


            try: banner = client.parseDOM(item2, 'banner')[0]
            except: banner = ''
            if not banner == '': banner = self.tvdb_image + banner
            else: banner = '0'
            banner = client.replaceHTMLCodes(banner)
            banner = banner.encode('utf-8')
            if not banner == '0': self.list[i].update({'banner': banner})


            try: fanart = item['backdrop_path']
            except: fanart = ''
            if fanart == '' or fanart == None: fanart = '0'
            if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
            if fanart == '0':
                try: fanart = client.parseDOM(item2, 'fanart')[0]
                except: fanart = '0'
                if not fanart == '0': fanart = self.tvdb_image + fanart
            fanart = client.replaceHTMLCodes(fanart)
            fanart = fanart.encode('utf-8')
            if not fanart == '0' and self.list[i]['fanart'] == '0': self.list[i].update({'fanart': fanart})


            try: premiered = item['first_air_date']
            except: premiered = ''
            try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
            except: premiered = ''
            if premiered == '' or premiered == None:
                try: premiered = client.parseDOM(item2, 'FirstAired')[0]
                except: premiered = '0'
            if premiered == '': premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = premiered.encode('utf-8')
            if not premiered == '0': self.list[i].update({'premiered': premiered})


            try: studio = item['networks'][0]['name']
            except: studio = ''
            if studio == '' or studio == None:
                try: studio = client.parseDOM(item2, 'Network')[0]
                except: studio = ''
            if studio == '': studio = '0'
            studio = client.replaceHTMLCodes(studio)
            studio = studio.encode('utf-8')
            if not studio == '0': self.list[i].update({'studio': studio})

 
            try: genre = item['genres']
            except: genre = []
            try: genre = [x['name'] for x in genre]
            except: genre = []
            if genre == '' or genre == None or genre == []:
                try: genre = client.parseDOM(item2, 'Genre')[0]
                except: genre = ''
                genre = [x for x in genre.split('|') if not x == '']
            genre = ' / '.join(genre)
            if genre == '': genre = '0'
            genre = client.replaceHTMLCodes(genre)
            genre = genre.encode('utf-8')
            if not genre == '0': self.list[i].update({'genre': genre})


            try: duration = str(item['episode_run_time'][0])
            except: duration = ''
            if duration == '' or duration == None:
                try: duration = client.parseDOM(item2, 'Runtime')[0]
                except: duration = ''
            if duration == '': duration = '0'
            duration = client.replaceHTMLCodes(duration)
            duration = duration.encode('utf-8')
            if not duration == '0': self.list[i].update({'duration': duration})


            try: rating = str(item['vote_average'])
            except: rating = ''
            if rating == '' or rating == None:
                try: rating = client.parseDOM(item2, 'Rating')[0]
                except: rating = ''
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = rating.encode('utf-8')
            if not rating == '0': self.list[i].update({'rating': rating})


            try: votes = str(item['vote_count'])
            except: votes = ''
            try: votes = str(format(int(votes),',d'))
            except: pass
            if votes == '' or votes == None:
                try: votes = client.parseDOM(item2, 'RatingCount')[0]
                except: votes = '0'
            if votes == '': votes = '0'
            votes = client.replaceHTMLCodes(votes)
            votes = votes.encode('utf-8')
            if not votes == '0': self.list[i].update({'votes': votes})


            try: mpaa = item['content_ratings']['results'][-1]['rating']
            except: mpaa = ''
            if mpaa == '' or mpaa == None:
                try: mpaa = client.parseDOM(item2, 'ContentRating')[0]
                except: mpaa = ''
            if mpaa == '': mpaa = '0'
            mpaa = client.replaceHTMLCodes(mpaa)
            mpaa = mpaa.encode('utf-8')
            if not mpaa == '0': self.list[i].update({'mpaa': mpaa})


            try: cast = item['credits']['cast']
            except: cast = []
            try: cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
            except: cast = []
            if cast == []:
                try: cast = client.parseDOM(item2, 'Actors')[0]
                except: cast = ''
                cast = [x for x in cast.split('|') if not x == '']
                try: cast = [(x.encode('utf-8'), '') for x in cast]
                except: cast = []
            if len(cast) > 0: self.list[i].update({'cast': cast})


            try: plot = item['overview']
            except: plot = ''
            if plot == '' or plot == None:
                try: plot = client.parseDOM(item2, 'Overview')[0]
                except: plot = ''
            if plot == '': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
            if not plot == '0': self.list[i].update({'plot': plot})


            self.meta.append({'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'lang': self.info_lang, 'item': {'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'tvrage': tvrage, 'poster': poster, 'banner': banner, 'fanart': fanart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': cast, 'plot': plot}})
        except:
            pass


    def tvshowDirectory(self, items):
        #control.log("******************** tvshowDirectory %s" % items)
        if items == None or len(items) == 0: return

        isFolder = True if control.setting('autoplay') == 'false' and control.setting('host_select') == '1' else False
        isFolder = False if control.window.getProperty('PseudoTVRunning') == 'True' else isFolder

        traktMode = False if trakt.getTraktCredentials() == False else True

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')
        sysaddon = sys.argv[0]

        try:
            favitems = favourites.getFavourites('tvshows')
            favitems = [i[0] for i in favitems]
        except:
            pass

        try:
            if traktMode == False: raise Exception()
            indicators = trakt.syncTVShows(timeout=720)
            indicators = json.loads(indicators)
        except:
            pass


        for i in items:
            try:
                label = i['name']
                systitle = sysname = urllib.quote_plus(i['title'])
                sysimage = urllib.quote_plus(i['poster'])
                imdb, tmdb, tvdb, tvrage, year = i['imdb'], i['tmdb'], i['tvdb'], i['tvrage'], i['year']

                poster, banner, fanart = i['poster'], i['banner'], i['fanart']
                if poster == '0': poster = addonPoster
                if banner == '0' and poster == '0': banner = addonBanner
                elif banner == '0': banner = poster


                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                if i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                sysmeta = urllib.quote_plus(json.dumps(meta))


                url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&tvrage=%s' % (sysaddon, systitle, year, imdb, tmdb, tvdb, tvrage)

                try:
                    if traktMode == False: raise Exception()
                    match = [i for i in indicators if str(i['show']['ids']['tvdb']) == tvdb][0]
                    num_1 = 0
                    for i in range(0, len(match['seasons'])): num_1 += len(match['seasons'][i]['episodes'])
                    num_2 = int(match['show']['aired_episodes'])
                    if num_1 >= num_2: meta.update({'playcount': 1, 'overlay': 7})
                except:
                    pass


                cm = []

                if isFolder == False:
                    cm.append((control.lang(30232).encode('utf-8'), 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((control.lang(30233).encode('utf-8'), 'Action(Info)'))

                if not action == 'tvSearch':
                    cm.append((control.lang(30234).encode('utf-8'), 'RunPlugin(%s?action=tvPlaycount&name=%s&year=%s&imdb=%s&tvdb=%s&query=7)' % (sysaddon, systitle, year, imdb, tvdb)))
                    cm.append((control.lang(30235).encode('utf-8'), 'RunPlugin(%s?action=tvPlaycount&name=%s&year=%s&imdb=%s&tvdb=%s&query=6)' % (sysaddon, systitle, year, imdb, tvdb)))

                if traktMode == True:
                    cm.append((control.lang(30236).encode('utf-8'), 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))

                if action == 'tvFavourites':
                    cm.append((control.lang(30238).encode('utf-8'), 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))
                elif action.startswith('tvSearch'):
                    cm.append((control.lang(30237).encode('utf-8'), 'RunPlugin(%s?action=addFavourite&meta=%s&query=0&content=tvshows)' % (sysaddon, sysmeta)))
                else:
                    if not imdb in favitems and not tvdb in favitems: cm.append((control.lang(30237).encode('utf-8'), 'RunPlugin(%s?action=addFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))
                    else: cm.append((control.lang(30238).encode('utf-8'), 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=tvshows)' % (sysaddon, sysmeta)))

                cm.append((control.lang(30239).encode('utf-8'), 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&tvrage=%s)' % (sysaddon, systitle, year, imdb, tmdb, tvdb, tvrage)))

                cm.append((control.lang(30240).encode('utf-8'), 'RunPlugin(%s?action=addView&content=tvshows)' % sysaddon))


                item = control.item(label=label, iconImage=poster, thumbnailImage=poster)

                try: item.setArt({'poster': poster, 'tvshow.poster': poster, 'season.poster': poster, 'banner': banner, 'tvshow.banner': banner, 'season.banner': banner})
                except: pass

                if settingFanart == 'true' and not fanart == '0':
                    item.setProperty('Fanart_Image', fanart)
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setInfo(type='Video', infoLabels = meta)
                item.setProperty('Video', 'true')
                item.addContextMenuItems(cm, replaceItems=True)
                control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=True)
            except:
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()
            url = '%s?action=tvshows&url=%s' % (sysaddon, urllib.quote_plus(url))
            addonNext = control.addonNext()
            item = control.item(label=control.lang(30241).encode('utf-8'), iconImage=addonNext, thumbnailImage=addonNext)
            item.addContextMenuItems([], replaceItems=False)
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
            control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=True)
        except:
            pass


        control.content(int(sys.argv[1]), 'tvshows')
        control.directory(int(sys.argv[1]), cacheToDisc=True)
        views.setView('tvshows', {'skin.confluence': 500})


    def addDirectory(self, items):
        if items == None or len(items) == 0: return

        sysaddon = sys.argv[0]
        addonFanart = control.addonFanart()
        addonThumb = control.addonThumb()
        artPath = control.artPath()

        for i in items:
            try:
                try: name = control.lang(i['name']).encode('utf-8')
                except: name = i['name']

                if i['image'].startswith('http://'): thumb = i['image']
                elif not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass

                cm = []

                try: cm.append((control.lang(30239).encode('utf-8'), 'RunPlugin(%s?action=tvshowsToLibrary&url=%s)' % (sysaddon, urllib.quote_plus(i['context']))))
                except: pass

                item = control.item(label=name, iconImage=thumb, thumbnailImage=thumb)
                item.addContextMenuItems(cm, replaceItems=False)
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
                control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=True)
            except:
                pass

        control.directory(int(sys.argv[1]), cacheToDisc=True)


    """
    def tmdb_list(self, url):
        try:
            result = client.request(url % self.tmdb_key)
            result = json.loads(result)
            try: items = result['results']
            except: items = result['tv_credits']['cast']
        except:
            return

        try:
            next = str(result['page'])
            total = str(result['total_pages'])
            if next == total: raise Exception()
            if not 'page=' in url: raise Exception()
            next = '%s&page=%s' % (url.split('&page=', 1)[0], str(int(next)+1))
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = item['name']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['first_air_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item['poster_path']
                if poster == '' or poster == None: raise Exception()
                else: poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')

                try: fanart = item['backdrop_path']
                except: fanart = '0'
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')

                premiered = item['first_air_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: rating = str(item['vote_average'])
                except: rating = '0'
                if rating == '' or rating == None: rating = '0'
                rating = rating.encode('utf-8')

                try: votes = str(item['vote_count'])
                except: votes = '0'
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == '' or votes == None: votes = '0'
                votes = votes.encode('utf-8')

                try: plot = item['overview']
                except: plot = '0'
                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': '0', 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0', 'cast': '0', 'plot': plot, 'name': title, 'code': '0', 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})
            except:
                pass

        return self.list


    def tmdb_person_list(self, url):
        try:
            result = client.request(url)
            result = json.loads(result)
            items = result['results']
        except:
            return

        for item in items:
            try:
                name = item['name']
                name = name.encode('utf-8')

                url = self.person_link % (item['id'], '%s')
                url = url.encode('utf-8')

                image = '%s%s' % (self.tmdb_image, item['profile_path'])
                image = image.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list


    def tmdb_genre_list(self, url):
        try:
            result = client.request(url)
            result = json.loads(result)
            items = result['genres']
        except:
            return

        for item in items:
            try:
                name = item['name']
                name = name.encode('utf-8')

                url = self.genre_link % ('%s', item['id'])
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url})
            except:
                pass

        return self.list
    """
