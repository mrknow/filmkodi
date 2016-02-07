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


import sys,re,json,urllib,urlparse,datetime

from resources.lib.libraries import control
from resources.lib.libraries import client
from resources.lib.libraries import workers


class channels:
    def __init__(self):
        self.list = [] ; self.items = []

        self.uk_datetime = self.uk_datetime()
        self.systime = (self.uk_datetime).strftime('%Y%m%d%H%M%S%f')
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'

        self.sky_now_link = 'http://epgservices.sky.com/5.1.1/api/2.0/channel/json/%s/now/nn/0'
        self.sky_programme_link = 'http://tv.sky.com/programme/channel/%s/%s/%s.json'


    def get(self):
        channels = [('01', 'Sky Premiere', '1409'), ('02', 'Sky Premiere +1', '1823'), ('03', 'Sky Showcase', '1814'), ('04', 'Sky Greats', '1815'), ('05', 'Sky Disney', '1838'), ('06', 'Sky Family', '1808'), ('07', 'Sky Action', '1001'), ('08', 'Sky Comedy', '1002'), ('09', 'Sky Crime', '1818'), ('10', 'Sky Drama', '1816'), ('11', 'Sky Sci Fi', '1807'), ('12', 'Sky Select', '1811'), ('13', 'Film4', '1627'), ('14', 'TCM', '5605')] 

        threads = []
        for i in channels: threads.append(workers.Thread(self.sky_list, i[0], i[1], i[2]))
        [i.start() for i in threads]
        [i.join() for i in threads]

        threads = []
        for i in range(0, len(self.items)): threads.append(workers.Thread(self.items_list, self.items[i]))
        [i.start() for i in threads]
        [i.join() for i in threads]

        try: self.list = sorted(self.list, key=lambda k: k['num'])
        except: pass

        self.channelDirectory(self.list)
        return self.list


    def sky_list(self, num, channel, id):
        try:
            url = self.sky_now_link % id
            result = client.request(url, timeout='10')
            result = json.loads(result)
            match = result['listings'][id][0]['url']

            dt1 = (self.uk_datetime).strftime('%Y-%m-%d')
            dt2 = int((self.uk_datetime).strftime('%H'))
            if (dt2 < 6): dt2 = 0
            elif (dt2 >= 6 and dt2 < 12): dt2 = 1
            elif (dt2 >= 12 and dt2 < 18): dt2 = 2
            elif (dt2 >= 18): dt2 = 3

            url = self.sky_programme_link % (id, str(dt1), str(dt2))
            result = client.request(url, timeout='10')
            result = json.loads(result)
            result = result['listings'][id]
            result = [i for i in result if i['url'] == match][0]

            year = result['d']
            year = re.findall('[(](\d{4})[)]', year)[0].strip()
            year = year.encode('utf-8')

            title = result['t']
            title = title.replace('(%s)' % year, '').strip()
            title = client.replaceHTMLCodes(title)
            title = title.encode('utf-8')

            self.items.append((title, year, channel, num))
        except:
            pass


    def items_list(self, i):
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

            self.list.append({'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'name': name, 'code': imdb, 'imdb': imdb, 'poster': poster, 'channel': i[2], 'num': i[3]})
        except:
            pass


    def uk_datetime(self):
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours = 0)
        d = datetime.datetime(dt.year, 4, 1)
        dston = d - datetime.timedelta(days=d.weekday() + 1)
        d = datetime.datetime(dt.year, 11, 1)
        dstoff = d - datetime.timedelta(days=d.weekday() + 1)
        if dston <=  dt < dstoff:
            return dt + datetime.timedelta(hours = 1)
        else:
            return dt


    def channelDirectory(self, items):
        if items == None or len(items) == 0: return

        playbackMenu = control.lang(30292).encode('utf-8') if control.setting('autoplay') == 'true' else control.lang(30291).encode('utf-8')

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart = control.addonFanart()
        sysaddon = sys.argv[0]


        for i in items:
            try:
                label = "[B]%s[/B] : %s" % (i['channel'].upper(), i['name'])
                sysname = urllib.quote_plus(i['name'])
                systitle = urllib.quote_plus(i['title'])
                imdb, tmdb, year = i['imdb'], '0', i['year']

                poster, banner = i['poster'], i['poster']
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

                cm = []
                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))
                cm.append((control.lang(30293).encode('utf-8'), 'Action(Info)'))
                cm.append((control.lang(30294).encode('utf-8'), 'RunPlugin(%s?action=refresh)' % (sysaddon)))
                cm.append((control.lang(30295).encode('utf-8'), 'RunPlugin(%s?action=openSettings)' % (sysaddon)))
                cm.append((control.lang(30296).encode('utf-8'), 'RunPlugin(%s?action=openPlaylist)' % (sysaddon)))

                item = control.item(label=label, iconImage=poster, thumbnailImage=poster)

                try: item.setArt({'poster': poster, 'banner': banner})
                except: pass

                if not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setInfo(type='Video', infoLabels = meta)
                item.setProperty('Video', 'true')
                #item.setProperty('IsPlayable', 'true')
                item.addContextMenuItems(cm, replaceItems=True)
                control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=False)
            except:
                pass

        control.content(int(sys.argv[1]), 'movies')
        control.directory(int(sys.argv[1]), cacheToDisc=True)


