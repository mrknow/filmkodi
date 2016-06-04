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


import os,sys,re,json,urllib,urlparse,datetime
import re

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


class movies:
    def __init__(self):
        self.list = []

        #self.tmdb_link = 'http://api.themoviedb.org'
        self.trakt_link = 'http://api-v2launch.trakt.tv'
        self.imdb_link = 'http://www.imdb.com'
        #self.tmdb_key = control.tmdb_key
        self.fanarttv_key = control.fanarttv_key
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.month2_date = (self.datetime - datetime.timedelta(days = 60)).strftime('%Y-%m-%d')
        self.year_date = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')
        self.year_date10 = (self.datetime - datetime.timedelta(days = 3650)).strftime('%Y-%m-%d')
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb_user').replace('ur', '')
        self.info_lang = control.setting('infoLang') or 'en'

        #self.tmdb_info_link = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,releases' % ('%s', self.tmdb_key, self.info_lang)
        self.imdb_info_link = 'http://www.omdbapi.com/?i=%s&plot=full&r=json'

        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'

        self.persons_link = 'http://www.imdb.com/search/name?count=100&name=%s'
        self.personlist_link = 'http://www.imdb.com/search/name?count=100&gender=male,female'
        self.genres_tab = [('Action', 'action'), ('Adventure', 'adventure'), ('Animation', 'animation'),('Biography', 'biography'),
                           ('Comedy', 'comedy'), ('Crime', 'crime'), ('Drama', 'drama'),('Family', 'family'), ('Fantasy', 'fantasy'),
                           ('History', 'history'), ('Horror', 'horror'),('Music ', 'music'), ('Musical', 'musical'), ('Mystery', 'mystery'),
                           ('Romance', 'romance'),('Science Fiction', 'sci_fi'), ('Sport', 'sport'), ('Thriller', 'thriller'), ('War', 'war'),('Western', 'western')]
        #self.certifications_link = 'http://api.themoviedb.org/3/certification/movie/list?api_key=%s' % self.tmdb_key


        #self.featured_link = 'http://api.themoviedb.org/3/discover/movie?api_key=%s&primary_release_date.gte=%s&primary_release_date.lte=%s&page=1' % ('%s', self.year_date, self.month2_date)
        #self.popular_link = 'http://api.themoviedb.org/3/movie/popular?api_key=%s&page=1'
        #self.views_link = 'http://api.themoviedb.org/3/movie/top_rated?api_key=%s&page=1'
        #self.theaters_link = 'http://api.themoviedb.org/3/movie/now_playing?api_key=%s&page=1'
        #self.search_link = 'http://api.themoviedb.org/3/search/movie?api_key=%s&query=%s'
        #self.genre_link = 'http://api.themoviedb.org/3/discover/movie?api_key=%s&with_genres=%s&primary_release_date.gte=%s&primary_release_date.lte=%s&page=1' % ('%s', '%s', self.year_date, self.today_date)
        #self.year_link = 'http://api.themoviedb.org/3/discover/movie?api_key=%s&year=%s&primary_release_date.lte=%s&page=1' % ('%s', '%s', self.today_date)

        self.popular_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=500,&production_status=released&groups=top_1000&sort=moviemeter,asc&count=20&start=1'
        self.featured_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=500,&production_status=released&release_date=date[365],date[60]&sort=moviemeter,asc&count=20&start=1'
        self.boxoffice_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&sort=boxoffice_gross_us,desc&count=20&start=1'
        self.oscars_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&groups=oscar_best_picture_winners&sort=year,desc&count=20&start=1'
        self.trending_link = 'http://api-v2launch.trakt.tv/movies/trending?limit=20&page=1'
        self.views_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=500,&production_status=released&sort=num_votes,desc&count=20&start=1'
        self.theaters_link = 'http://www.imdb.com/search/title?title_type=feature&languages=en&num_votes=200,&release_date=%s,%s&sort=release_date_us,desc&count=20&start=1' % (self.year_date, self.today_date)
        self.search_link = 'http://api-v2launch.trakt.tv/search?type=movie&query=%s&limit=20'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=100,&genres=%s&sort=moviemeter,asc&count=20&start=1'
        self.year_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=100,&production_status=released&year=%s&sort=moviemeter,asc&count=20&start=1'

        self.person_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&role=%s&sort=year,desc&count=40&start=1'
        self.certification_link = 'http://api.themoviedb.org/3/discover/movie?api_key=%s&certification=%s&certification_country=US&primary_release_date.lte=%s&page=1' % ('%s', '%s', self.today_date)

        self.scn_link = 'http://predb.me'
        self.scn_page = 'http://predb.me/?search=720p+%s+tag:-foreign&cats=movies-hd&page=%s'
        self.added_link = 'http://predb.me?start=1'

        self.traktlists_link = 'http://api-v2launch.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api-v2launch.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api-v2launch.trakt.tv/users/me/collection/movies'
        self.traktwatchlist_link = 'http://api-v2launch.trakt.tv/users/me/watchlist/movies'
        self.traktfeatured_link = 'http://api-v2launch.trakt.tv/recommendations/movies?limit=40'
        self.trakthistory_link = 'http://api-v2launch.trakt.tv/users/me/history/movies?limit=40&page=1'
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&sort=title:asc&title_type=feature,short,tv_movie,tv_special,video,documentary,game&start=1'
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist' % self.imdb_user


    def get(self, url, idx=True):
        try:
            try: url = getattr(self, url + '_link')
            except: pass

            try: u = urlparse.urlparse(url).netloc.lower()
            except: pass

            if u in self.trakt_link and '/users/' in url:
                try:
                    if url == self.trakthistory_link: raise Exception()
                    if not '/users/me/' in url: raise Exception()
                    if trakt.getActivity() > cache.timeout(self.trakt_list, url, self.trakt_user): raise Exception()
                    self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
                except:
                    self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)

                if '/users/me/' in url:
                    self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['title'].lower()))

                if idx == True: self.worker()

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True: self.worker()


            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_list, 0, url, idx)
                if idx == True: self.worker()

            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 24, url)
                if idx == True: self.worker()


            elif u in self.scn_link:
                self.list = cache.get(self.scn_list, 24, url)
                if idx == True: self.worker()


            if idx == True: self.movieDirectory(self.list)
            return self.list
        except:
            pass


    def widget(self):
        setting = control.setting('movie_widget')

        if setting == '2':
            self.get(self.featured_link)
        elif setting == '3':
            self.get(self.trending_link)
        else:
            self.get(self.added_link)


    def favourites(self):
        try:
            items = favourites.getFavourites('movies')
            self.list = [i[1] for i in items]

            for i in self.list:
                if not 'name' in i: i['name'] = '%s (%s)' % (i['title'], i['year'])
                try: i['title'] = i['title'].encode('utf-8')
                except: pass
                try: i['name'] = i['name'].encode('utf-8')
                except: pass
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
            self.movieDirectory(self.list)
        except:
            return


    def search(self, query=None):
        #try:
            if query == None:
                t = control.lang(30201).encode('utf-8')
                k = control.keyboard('', t) ; k.doModal()
                self.query = k.getText() if k.isConfirmed() else None
            else:
                self.query = query

            if (self.query == None or self.query == ''): return


            url = self.search_link % (urllib.quote_plus(self.query))
            self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)

            self.worker()
            self.movieDirectory(self.list)
            return self.list
        #except:
        #    return


    def person(self, query=None):
        try:
            if query == None:
                t = control.lang(30201).encode('utf-8')
                k = control.keyboard('', t) ; k.doModal()
                self.query = k.getText() if k.isConfirmed() else None
            else:
                self.query = query

            if (self.query == None or self.query == ''): return

            url = self.persons_link % urllib.quote_plus(self.query)
            self.list = cache.get(self.imdb_person_list, 0, url)

            for i in range(0, len(self.list)): self.list[i].update({'action': 'movies'})
            self.addDirectory(self.list)
            return self.list
        except:
            return


    def genres(self):
        for i in self.genres_tab:
            #for i in range(0, len(self.list)): self.list[i].update({'image': 'genres.png', 'action': 'movies'})
            self.list.append({'name': i[0], 'url': self.genre_link % i[1], 'image': 'genres.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list


    def certifications(self):
        try:
            url = self.certifications_link
            self.list = cache.get(self.tmdb_certification_list, 24, url)

            for i in range(0, len(self.list)): self.list[i].update({'image': 'movieCertificates.jpg', 'action': 'movies'})
            self.addDirectory(self.list)
            return self.list
        except:
            return


    def years(self):
        year = (self.datetime.strftime('%Y'))

        for i in range(int(year)-0, int(year)-50, -1): self.list.append({'name': str(i), 'url': self.year_link % str(i), 'image': 'movieYears.jpg', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list



    def persons(self):
        self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
        for i in range(0, len(self.list)): self.list[i].update({'action': 'movies'})
        self.addDirectory(self.list)
        return self.list

    def userlists(self):
        try:
            userlists = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            activity = trakt.getActivity()
        except:
            pass
        #control.log('@@ TRAKT LIST %s - %s' %(userlists,activity))
        try:
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlists_link,
                                            self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
        except:
            pass
        try:
            self.list = []
            if self.imdb_user == '': raise Exception()
            userlists += cache.get(self.imdb_user_list, 0, self.imdblists_link)
        except:
            pass
        try:
            self.list = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link,
                                            self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlikedlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
        except:
            pass

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'movies'})
        #self.addDirectory(self.list, queue=True)
        self.addDirectory(self.list)

        return self.list

    def trakt_list(self, url, user):
        #control.log('### TRAKT LISTS')
        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full,images'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

            result = trakt.getTrakt(u)
            result = json.loads(result)

            items = []
            for i in result:
                try: items.append(i['movie'])
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
            #control.log("##################><><><><> trakt_list item  %s" % item)

            try:
                title = item['title']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['year']
                year = re.sub('[^0-9]', '', str(year))
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                name = '%s (%s)' % (title, year)
                try: name = name.encode('utf-8')
                except: pass

                tmdb = item['ids']['tmdb']
                if tmdb == None or tmdb == '': tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

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

                try:
                    premiered = item['released']
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')


                try:
                    genre = item['genres']
                    genre = [i.title() for i in genre]
                except: genre = '0'
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

                plot = item['overview']
                if plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                try: tagline = item['tagline']
                except: tagline = None
                if tagline == None and not plot == '0': tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                elif tagline == None: tagline = '0'
                tagline = client.replaceHTMLCodes(tagline)
                try: tagline = tagline.encode('utf-8')
                except: pass

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': tagline, 'name': name, 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': banner, 'fanart': fanart, 'next': next})
            except:
                pass

        return self.list

    def trakt_user_list(self, url, user):
        try:
            result = trakt.getTrakt(url)
            items = json.loads(result)
        except:
            pass

        for item in items:
            try:
                try:
                    name = item['list']['name']
                except:
                    name = item['name']
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                try:
                    url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except:
                    url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['name'].lower()))
        return self.list


    def imdb_list(self, url, idx=True):
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

                fanart = 'http://films4u.org/imdb/bgs/'+imdb+'.jpg'
                fanart = fanart.encode('utf-8')


                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: pass

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': '0', 'cast': cast, 'plot': plot, 'tagline': tagline, 'name': name, 'code': imdb, 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})
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

    def imdb_person_list(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'tr', attrs = {'class': '.+? detailed'})
        except:
            return

        for item in items:
            try:
                name = client.parseDOM(item, 'a', ret='title')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = re.findall('(nm\d*)', url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = client.parseDOM(item, 'img', ret='src')[0]
                if not ('._SX' in image or '._SY' in image): raise Exception()
                image = re.sub('_SX\d*|_SY\d*|_CR\d+?,\d+?,\d+?,\d*','_SX500', image)
                image = client.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list

    def scn_list(self, url):

        def predb_items():
            try:
                years = [(self.datetime).strftime('%Y'), (self.datetime - datetime.timedelta(days = 365)).strftime('%Y')]
                months = (self.datetime - datetime.timedelta(days = 180)).strftime('%Y%m%d')

                result = ''
                for i in years:
                    result += client.request(self.scn_page % (str(i), '1'))
                    result += client.request(self.scn_page % (str(i), '2'))

                items = client.parseDOM(result, 'div', attrs = {'class': 'post'})
                items = [(client.parseDOM(i, 'a', attrs = {'class': 'p-title'}), re.compile('(\d{4}-\d{2}-\d{2})').findall(i)) for i in items]
                items = [(i[0][0], i[1][0]) for i in items if len(i[0]) > 0 and len(i[1]) > 0]
                items = [(re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|3D)(\.|\)|\]|\s)(.+)', '', i[0]), re.compile('[\.|\(|\[|\s](\d{4})[\.|\)|\]|\s]').findall(i[0]), re.sub('[^0-9]', '', i[1])) for i in items]
                items = [(i[0], i[1][-1], i[2]) for i in items if len(i[1]) > 0]
                items = [i for i in items if int(months) <= int(i[2])]
                items = sorted(items,key=lambda x: x[2])[::-1]
                items = [(re.sub('(\.|\(|\[|LIMITED|UNCUT)', ' ', i[0]).strip(), i[1]) for i in items]
                items = [x for y,x in enumerate(items) if x not in items[:y]]
                items = items[:150]

                return items
            except:
                return


        def predb_list(i):
            try:
                url = self.imdb_by_query % (urllib.quote_plus(i[0]), i[1])
                item = client.request(url, timeout='10')
                item = json.loads(item)

                title = item['Title']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['Year']
                year = re.sub('[^0-9]', '', str(year))
                year = year.encode('utf-8')

                name = '%s (%s)' % (title, year)
                try: name = name.encode('utf-8')
                except: pass

                imdb = item['imdbID']
                if imdb == None or imdb == '' or imdb == 'N/A': raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                poster = item['Poster']
                if poster == None or poster == '' or poster == 'N/A': poster = '0'
                if not ('_SX' in poster or '_SY' in poster): poster = '0'
                poster = re.sub('_SX\d*|_SY\d*|_CR\d+?,\d+?,\d+?,\d*','_SX500', poster)
                poster = poster.encode('utf-8')

                genre = item['Genre']
                if genre == None or genre == '' or genre == 'N/A': genre = '0'
                genre = genre.replace(', ', ' / ')
                genre = genre.encode('utf-8')

                duration = item['Runtime']
                if duration == None or duration == '' or duration == 'N/A': duration = '0'
                duration = re.sub('[^0-9]', '', str(duration))
                duration = duration.encode('utf-8')

                rating = item['imdbRating']
                if rating == None or rating == '' or rating == 'N/A' or rating == '0.0': rating = '0'
                rating = rating.encode('utf-8')

                votes = item['imdbVotes']
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == None or votes == '' or votes == 'N/A': votes = '0'
                votes = votes.encode('utf-8')

                mpaa = item['Rated']
                if mpaa == None or mpaa == '' or mpaa == 'N/A': mpaa = '0'
                mpaa = mpaa.encode('utf-8')

                director = item['Director']
                if director == None or director == '' or director == 'N/A': director = '0'
                director = director.replace(', ', ' / ')
                director = re.sub(r'\(.*?\)', '', director)
                director = ' '.join(director.split())
                director = director.encode('utf-8')

                writer = item['Writer']
                if writer == None or writer == '' or writer == 'N/A': writer = '0'
                writer = writer.replace(', ', ' / ')
                writer = re.sub(r'\(.*?\)', '', writer)
                writer = ' '.join(writer.split())
                writer = writer.encode('utf-8')

                cast = item['Actors']
                if cast == None or cast == '' or cast == 'N/A': cast = '0'
                cast = [x.strip() for x in cast.split(',') if not x == '']
                try: cast = [(x.encode('utf-8'), '') for x in cast]
                except: cast = []
                if cast == []: cast = '0'

                plot = item['Plot']
                if plot == None or plot == '' or plot == 'N/A': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: pass

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'name': name, 'code': imdb, 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': '0'})
            except:
                pass


        try:
            items = cache.get(predb_items, 24)

            start = re.compile('start=(\d*)').findall(url)[-1]
            start = int(start)

            if len(items) > (start + 30): next = self.scn_link + '?start=%s' % (start + 30)
            else: next = ''
        except:
            return

        threads = []
        for i in range(start - 1, start + 29):
            try: threads.append(workers.Thread(predb_list, items[i]))
            except: pass
        [i.start() for i in threads]
        [i.join() for i in threads]

        for i in range(0, len(self.list)): self.list[i].update({'next': next})

        return self.list


    def worker(self):

        self.meta = []
        total = len(self.list)
        #control.log("##################><><><><> WORKER TOTAL  %s" % total)


        for i in range(0, total): self.list[i].update({'metacache': False})
        self.list = metacache.fetch(self.list, self.info_lang)

        for r in range(0, total, 25):
            threads = []
            for i in range(r, r+25):
                if i <= total: threads.append(workers.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

        self.list = [i for i in self.list if not i['imdb'] == '0']
        #control.log("##################><><><><> WORKER   %s" % str(len(self.meta)))

        if len(self.meta) > 0: metacache.insert(self.meta)


    def super_info(self, i):
        try:
            #control.log("##################><><><><> META ID  %s" % str(i))
            zero ='0'.encode('utf-8')

            if self.list[i]['metacache'] == True: raise Exception()

            try: imdb = self.list[i]['imdb']
            except: imdb = '0'

            if not imdb == '0': url = self.imdb_info_link % imdb
            else: raise Exception()

            item = client.request(url, timeout='10')
            item = json.loads(item)
            #control.log("##################><><><><> META TITLE  %s" % item['Title'])
            #control.log("##################><><><><> META ALL %s" % item)

            imdb = item['imdbID']
            if imdb == '' or imdb == None: imdb = '0'
            if not imdb == '0': imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
            imdb = imdb.encode('utf-8')
            if not imdb == '0': self.list[i].update({'imdb': imdb, 'code': imdb})

            """
            try:
                #url2 = 'http://webservice.fanart.tv/v3/movies/%s?api_key=%s' % (imdb, self.fanarttv_key)
                #item2 = client.request(url2, timeout='10')
                #item2 = json.loads(item2)
                #control.log("><><><><> ITEM4  %s" % item2['moviebackground'][0]['url'])

            except:
                pass

            try:
                tmdb = item2['tmdb_id']
                if tmdb == '' or tmdb == None: tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')
                if not tmdb == '0': self.list[i].update({'tmdb': tmdb})
            except:
                tmdb = zero

            """
            try:
                poster = item['Poster']
                if poster == '' or poster == None: poster = '0'
                #if not poster == '0': poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')
                if not poster == '0': self.list[i].update({'poster': poster})
            except:
                poster = zero

            """
            try:
                fanart = item2['moviebackground'][0]['url']
                if fanart == '' or fanart == None: fanart = '0'
                #if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')
                if not fanart == '0' and self.list[i]['fanart'] == '0': self.list[i].update({'fanart': fanart})
            except:
                fanart = zero
            """

            try:
                if not imdb == '0':
                    fanart = 'http://films4u.org/imdb/bgs/'+imdb+'.jpg'
                    fanart= fanart.encode('utf-8')

                else:
                    fanart = zero
            except:
                fanart = zero

            #    http://fanart.filmkodi.com/tt0006333.jpg
            try:
                premiered = item['Released']
                premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
            except: premiered = '0'
            if premiered == '' or premiered == None: premiered = '0'
            premiered = premiered.encode('utf-8')
            if not premiered == '0': self.list[i].update({'premiered': premiered})

            #studio = item['production_companies']
            #try: studio = [x['name'] for x in studio][0]
            #except:
            studio = '0'
            #if studio == '' or studio == None: studio = '0'
            studio = studio.encode('utf-8')
            #if not studio == '0': self.list[i].update({'studio': studio})

            try: genre = item['Genre']
            except: genre = '0'
            if genre == '' or genre == None or genre == []: genre = '0'
            genre = genre.encode('utf-8')
            if not genre == '0': self.list[i].update({'genre': genre})

            try: duration = str(item['Runtime'].replace(' min',''))
            except: duration = '0'
            if duration == '' or duration == None: duration = '0'
            duration = duration.encode('utf-8')
            if not duration == '0': self.list[i].update({'duration': duration})

            try: rating = str(item['imdbRating'])
            except: rating = '0'
            if rating == '' or rating == None: rating = '0'
            rating = rating.encode('utf-8')
            if not rating == '0': self.list[i].update({'rating': rating})

            try:
                votes = str(item['imdbVotes'])
                votes = str(format(int(votes),',d'))
            except:
                votes = '0'
            if votes == '' or votes == None: votes = '0'
            votes = votes.encode('utf-8')
            if not votes == '0': self.list[i].update({'votes': votes})


            try:
                mpaa = item['Country']
            except:
                mpaa = '0'
            if mpaa == '' or mpaa == None: mpaa = '0'
            mpaa = mpaa.encode('utf-8')
            if not mpaa == '0': self.list[i].update({'mpaa': mpaa})

            try: cast = item['Actors']
            except: cast = '0'
            if cast == None or cast == '' or cast == 'N/A': cast = '0'
            cast = [x.strip() for x in cast.split(',') if not x == '']
            try: cast = [(x.encode('utf-8'), '') for x in cast]
            except: cast = []
            if cast == []: cast = '0'
            if not cast == '0': self.list[i].update({'cast': cast})

            try: writer = item['Writer']
            except: writer = '0'
            if writer  == '' or writer == None: writer= '0'
            writer = writer.encode('utf-8').replace(', ', ' / ')
            if len(writer) > 0: self.list[i].update({'writer': writer})


            """
            tagline = item['tagline']
            if (tagline == '' or tagline == None) and not plot == '0': tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
            elif tagline == '' or tagline == None: tagline = '0'
            try: tagline = tagline.encode('utf-8')
            except: pass
            if not tagline == '0': self.list[i].update({'tagline': tagline})
            """
            plot = item['Plot']
            if plot == '' or plot == None: plot = '0'
            plot = plot.encode('utf-8')
            if not plot == '0': self.list[i].update({'plot': plot})

            director = item['Director']
            if director == '' or director == None or director == []: director = '0'
            director = director.encode('utf-8')
            if not director == '0': self.list[i].update({'director': director})

            #self.meta.append({'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.info_lang, 'item': {'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster, 'fanart': fanart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline}})
            self.meta.append({'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'lang': self.info_lang, 'item': {'code': imdb, 'imdb': imdb, 'tmdb': '0', 'poster': poster, 'fanart': fanart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': zero}})
            #control.log("><><><><> ITEM META IMDB %s" % imdb)

        except:
            pass


    def movieDirectory(self, items):
        if items == None or len(items) == 0: return

        isFolder = True if control.setting('autoplay') == 'false' and control.setting('host_select') == '1' else False
        isFolder = False if control.window.getProperty('PseudoTVRunning') == 'True' else isFolder

        playbackMenu = control.lang(30204).encode('utf-8') if control.setting('autoplay') == 'true' else control.lang(30203).encode('utf-8')

        traktMode = False if trakt.getTraktCredentials() == False else True

        cacheToDisc = False if not action == 'movieSearch' else True

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')
        sysaddon = sys.argv[0]

        try:
            favitems = favourites.getFavourites('movies')
            favitems = [i[0] for i in favitems]
        except:
            pass

        try:
            if traktMode == True: raise Exception()
            from metahandler import metahandlers
            metaget = metahandlers.MetaData(preparezip=False)
        except:
            pass
        try:
            if traktMode == False: raise Exception()
            indicators = trakt.syncMovies(timeout=720)
            indicators = json.loads(indicators)
        except:
            pass


        for i in items:
            try:
                label = i['name']
                sysname = urllib.quote_plus(label)
                systitle = urllib.quote_plus(i['title'])
                imdb, tmdb, year = i['imdb'], i['tmdb'], i['year']


                poster, banner, fanart = i['poster'], i['banner'], i['fanart']
                if poster == '0': poster = addonPoster
                if banner == '0' and poster == '0': banner = addonBanner
                elif banner == '0': banner = poster


                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                if i['duration'] == '0': meta.update({'duration': '120'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                sysmeta = urllib.quote_plus(json.dumps(meta))


                url = '%s?action=play&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s&t=%s' % (sysaddon, sysname, systitle, year, imdb, tmdb, sysmeta, self.systime)
                sysurl = urllib.quote_plus(url)

                if isFolder == True:
                    url = '%s?action=sources&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s' % (sysaddon, sysname, systitle, year, imdb, tmdb, sysmeta)


                try:
                    if traktMode == True: raise Exception()
                    playcount = metaget._get_watched('movie', imdb, '', '')
                    if playcount == 7: meta.update({'playcount': 1, 'overlay': 7})
                    else: meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                try:
                    if traktMode == False: raise Exception()
                    playcount = [i for i in indicators if str(i['movie']['ids']['imdb']) == imdb][0]
                    meta.update({'playcount': 1, 'overlay': 7})
                except:
                    pass


                cm = []

                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                cm.append((control.lang(30205).encode('utf-8'), 'Action(Info)'))

                if not action == 'movieSearch':
                    cm.append((control.lang(30206).encode('utf-8'), 'RunPlugin(%s?action=moviePlaycount&title=%s&year=%s&imdb=%s&query=7)' % (sysaddon, systitle, year, imdb)))
                    cm.append((control.lang(30207).encode('utf-8'), 'RunPlugin(%s?action=moviePlaycount&title=%s&year=%s&imdb=%s&query=6)' % (sysaddon, systitle, year, imdb)))

                if traktMode == True:
                    cm.append((control.lang(30208).encode('utf-8'), 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)' % (sysaddon, sysname, imdb)))

                if action == 'movieFavourites':
                    cm.append((control.lang(30210).encode('utf-8'), 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=movies)' % (sysaddon, sysmeta)))
                elif action == 'movieSearch':
                    cm.append((control.lang(30209).encode('utf-8'), 'RunPlugin(%s?action=addFavourite&meta=%s&query=0&content=movies)' % (sysaddon, sysmeta)))
                else:
                    if not imdb in favitems: cm.append((control.lang(30209).encode('utf-8'), 'RunPlugin(%s?action=addFavourite&meta=%s&content=movies)' % (sysaddon, sysmeta)))
                    else: cm.append((control.lang(30210).encode('utf-8'), 'RunPlugin(%s?action=deleteFavourite&meta=%s&content=movies)' % (sysaddon, sysmeta)))

                cm.append((control.lang(30211).encode('utf-8'), 'RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb)))

                cm.append((control.lang(30212).encode('utf-8'), 'RunPlugin(%s?action=addView&content=movies)' % sysaddon))


                item = control.item(label=label, iconImage=poster, thumbnailImage=poster)

                try: item.setArt({'poster': poster, 'banner': banner})
                except: pass

                if settingFanart == 'true' and not fanart == '0':
                    item.setProperty('Fanart_Image', fanart)
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setInfo(type='Video', infoLabels = meta)
                item.setProperty('Video', 'true')
                #item.setProperty('IsPlayable', 'true')
                item.addContextMenuItems(cm, replaceItems=True)
                control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=isFolder)
            except:
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()
            url = '%s?action=movies&url=%s' % (sysaddon, urllib.quote_plus(url))
            addonNext = control.addonNext()
            item = control.item(label=control.lang(30213).encode('utf-8'), iconImage=addonNext, thumbnailImage=addonNext)
            item.addContextMenuItems([], replaceItems=False)
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
            control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=True)
        except:
            pass


        control.content(int(sys.argv[1]), 'movies')
        control.directory(int(sys.argv[1]), cacheToDisc=cacheToDisc)
        views.setView('movies', {'skin.confluence': 500})


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

                try: cm.append((control.lang(30211).encode('utf-8'), 'RunPlugin(%s?action=moviesToLibrary&url=%s)' % (sysaddon, urllib.quote_plus(i['context']))))
                except: pass

                item = control.item(label=name, iconImage=thumb, thumbnailImage=thumb)
                item.addContextMenuItems(cm, replaceItems=False)
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
                control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=True)
            except:
                pass

        control.directory(int(sys.argv[1]), cacheToDisc=True)


