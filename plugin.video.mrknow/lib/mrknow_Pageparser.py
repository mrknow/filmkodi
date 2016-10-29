# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys, math
import xbmcaddon, xbmc, xbmcgui

try: import urlresolver
except:
    import urlresolver9 as urlresolver


#hmf = urlresolver2.HostedMediaFile(url=u, include_disabled=True, include_universal=False)
#if hmf.valid_url() == True: url = hmf.resolve()

try:
    import simplejson as json
except ImportError:
    import json
import urlparse, httplib, random, string

ptv = xbmcaddon.Addon()
scriptID = ptv.getAddonInfo('id')
scriptname = ptv.getAddonInfo('name')
# dbg = ptv.getSetting('default_debug') in ('true')
ptv = xbmcaddon.Addon(scriptID)

import mrknow_pLog, mrknow_pCommon, mrknow_urlparser, mrknow_utils
from BeautifulSoup import BeautifulSoup

log = mrknow_pLog.pLog()


class mrknow_Pageparser:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.up = mrknow_urlparser.mrknow_urlparser()

    def hostSelect(self, v):
        hostUrl = False
        d = xbmcgui.Dialog()
        if len(v) > 0:
            valTab = []
            for i in range(len(v)):
                valTab.append(str(i + 1) + '. ' + self.getHostName(v[i], True))
            item = d.select("Wybor hostingu", valTab)
            if item >= 0: hostUrl = v[item]
        else:
            d.ok('Brak linkow', 'Przykro nam, ale nie znalezlismy zadnego linku do video.',
                 'Sproboj ponownie za jakis czas')
        return hostUrl

    def getHostName(self, url, nameOnly=False):
        hostName = ''
        match = re.search('http[s]?://(.+?)/', url)
        if match:
            hostName = match.group(1)
            if (nameOnly):
                n = hostName.split('.')
                hostName = n[-2]
        return hostName

    def getVideoLink(self, url, referer=''):
        nUrl = ''
        if not 'http' in url: url = 'http:'+url
        host = self.getHostName(url)
        log.info("PAGEPARSER video hosted by: " + host + ' url: '+url)

        if host == 'livemecz.com':
            nUrl = self.livemecz(url)
            print "Self", nUrl
        if host == 'www.drhtv.com.pl':
            nUrl = self.drhtv(url)
        elif host == 'www.realtv.com.pl':
            nUrl = self.realtv(url)
        elif host == 'www.transmisje.info':
            nUrl = self.transmisjeinfo(url)
        elif host == '79.96.137.217' or host == 'http://178.216.200.26':
            nUrl = self.azap(url)
        elif host == 'bbpolska.webd.pl':
            nUrl = self.bbpolska(url)
        elif host == 'fotosend.pl':
            nUrl = self.azap(url)
        elif host == 'typertv.com' or host == 'www.typertv.com.pl':
            nUrl = self.typertv(url)
        elif host == 'streamon.pl':
            nUrl = self.streamon(url)
        elif host == 'goodcast.tv':
            nUrl = self.goodcasttv(url)
        elif host == 'mecz.tv':
            nUrl = self.mecztv(url)
        elif host == 'www.fupptv.pl':
            nUrl = self.fupptvpl(url)
        elif host == 'team-cast.pl':
            nUrl = self.teamcastpl(url)
        elif host == 'www.yousat.tv':
            nUrl = self.yousattv(url)
        elif host == 'zobacztv.beep.pl':
            nUrl = self.zobaczxyz(url)
        elif host == 'alltube.tv':
            nUrl = self.alltubetv(url, referer='')
        elif host == 'zobaczmyto.tv':
            nUrl = self.zobacztotv(url, referer='')
        elif host == 'zalukaj.tv':
            nUrl = self.zalukajtv(url, referer='')
        elif host == 'zalukaj.com':
            nUrl = self.zalukajtv(url, referer='')
        elif host == 'www.efilmy.tv' or host == 'efilmy.tv':
            nUrl = self.efilmytv(url, referer='')
        elif host == 'www.filmydokumentalne.eu':
            nUrl = self.filmydokumentalneeu(url, referer='')
        elif host == 'www.tvseriesonline.pl':
            nUrl = self.tvseriesonline(url, referer='')
        elif 'looknij.tv' in host:
            nUrl = self.looknijtv(url, referer='')
        elif 'ustream.tv' in host:
            nUrl = self.ustream(url, referer='')
        elif 'telewizjoner.pl' in host:
            nUrl = self.nettvpw(url, referer='')
        elif 'screen-tv.pl' in host:
            nUrl = self.screentv(url, referer='')
        elif 'bajkionline.com' in host:
            nUrl = self.bajkionlinecom(url, referer='')
        elif 'bajkipopolsku.com' in host:
            nUrl = self.bajkionlinecom(url, referer='')
        elif 'kreskowkazone.pl' in host:
            nUrl = self.kreskowkazone(url, referer='')
        elif nUrl == '':
            print "Jedziemy na ELSE - " + url + "Host" + host
            nUrl = self.pageanalyze(url, host)

        print ("PAGEPARSER Link:", nUrl)
        return nUrl

    def kreskowkazone(self, url, referer):
        log.info("Kreskowka resolver")
        COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "kreskowkazone.cookie"
        HEADER = {'Referer': url,'User-Agent': mrknow_urlparser.HOST, 'Content-Type':"application/x-www-form-urlencoded",
                  "X-Requested-With": "XMLHttpRequest","Accept-Language": "en-US,en;q=0.5", "Accept": "text/html, */*; q=0.01"}


        tab = []
        tab2 = []
        query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True,
                      'save_cookie': True, 'use_post': False, 'return_data': True, 'use_header': True, 'header': HEADER}
        link = self.cm.getURLRequestData(query_data)
        result = self.cm.parseDOM(link, 'tr', {'class': 'wiersz'})

        query_data = {'url': "http://www.kreskowkazone.pl/images/statystyki.gif", 'use_host': False, 'use_cookie': True, 'cookiefile': COOKIEFILE,
                              'load_cookie': True, 'save_cookie': False, 'use_post': False, 'return_data': True, 'use_header': True, 'header': HEADER}
        link = self.cm.getURLRequestData(query_data)

        for i in result:
            log.info("--------------")

            result2 = self.cm.parseDOM(i, 'td', {'class': 'wiersz1 center border-c2'})
            #for j in result2:
            #    #log.info("Match1 %s " % j)
            try:
                tab.append(result2[1] + ' - ' + result2[2]+ ' - ' + result2[3].replace('<span class="sprites ','').replace(' center"></span>','').upper())
                mymatch= re.compile('<a class="nasz_player sprites play center" href="(.*?)" title="(.*)" (.*?)="(.*?)"></a>').findall(i)
                tab2.append(mymatch[0][3])
                #log.info("Link %s" % mymatch)
            except: pass
            d = xbmcgui.Dialog()
        video_menu = d.select("Wybór strony video", tab)
        if video_menu != "":
            #log.info("TAB %s " % tab2[video_menu])
            query_data = {'url': 'http://www.kreskowkazone.pl/odcinki_emb', 'use_host': False, 'use_cookie': True,
                          'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': False, 'use_post': False, 'return_data': True,
                          'use_header': True, 'header': HEADER, 'raw_post_data': True}
            postdata = "o="+tab2[video_menu]
            link = self.cm.getURLRequestData(query_data,postdata)
            #log.info("DAT %s " % link)
            try:
                srcVideo = self.cm.parseDOM(link, 'iframe', ret='src')[0]
                log.info("DAT %s " % srcVideo )
                #OtherResolver = HostedMediaFile(url=url).resolve()
                hmf = urlresolver.HostedMediaFile(url=srcVideo, include_disabled=True, include_universal=False)
                if hmf.valid_url() == True: linkVideo = hmf.resolve()
                log.info('XYXYXYXYXYYXYXYX   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
                if linkVideo == False:
                    linkVideo = self.up.getVideoLink(srcVideo,url)
                return linkVideo
            except:
                linkVideo = self.up.getVideoLink(srcVideo ,url)
            return linkVideo
        else:
            return ''

    def bajkionlinecom(self, url, referer):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        #                  <iframe width="720" height="490" frameborder="0" scrolling="no" src="http://www.typertv.com.pl/emded/canal.php" allowfullscreen>
        match1 = re.compile('<iframe(.*?)src="(.*?)"(.*?)>').findall(link)
        if match1:
            if 'http' not in match1[0][1]:
                mylink = 'http:'+match1[0][1]
            else:
                mylink=match1[0][1]

            try:
                hmf = urlresolver.HostedMediaFile(url=mylink, include_disabled=True, include_universal=False)
                if hmf.valid_url() == True: OtherResolver = hmf.resolve()
                log.info('XYXYXYXYXYYXYXYX   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % OtherResolver)
                if OtherResolver == False:
                    linkVideo = self.up.getVideoLink(mylink,url)
                else:
                    return OtherResolver
            except:
                return self.up.getVideoLink(mylink, url)
        return ''

    def efilmytv(self, url, referer):
        COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "efilmytv.cookie"
        IMAGEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "efilmytv.jpg"
        linkVideo = ''
        query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True,
                      'save_cookie': True, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        myfile1 = re.compile(
            '<div id="(.*?)" alt="n" class="embedbg"><img src="(.*?)"/></div><div class="versionholder">').findall(link)
        log.info("m %s" % myfile1)
        if len(myfile1) > 0:
            if 'serial' in url:
                log.info("SERRRRRRR")
                myurl = 'http://www.efilmy.tv/seriale.php?cmd=show_player&id='
            else:
                log.info("Filmy")
                myurl = 'http://www.efilmy.tv//filmy.php?cmd=show_player&id='
            log.info("url %s " % myurl)

            HEADER = {'Referer': myurl + myfile1[0][0],
                      'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'}

            query_data = {'url': myurl + myfile1[0][0],
                          'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': True,
                          'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': False, 'use_post': False,
                          'return_data': True}
            link2 = self.cm.getURLRequestData(query_data)
            print("link2", link2)
            if '<p><strong>Zabezpieczenie przeciwko robotom</strong></p>' in link2:
                log.info("link %s" % link2)
                mymatch = re.compile(
                    '<input type="hidden" name="id" value=(\d+) />\r\n<input type="hidden" name="mode" value=(\w+) />').findall(
                    link2)
                print(("mymatch", mymatch))
                query_data = {'url': 'http://www.efilmy.tv//mirrory.php?cmd=generate_captcha&time=' + str(
                    random.randint(1, 1000)), 'use_host': False, 'use_header': True, 'header': HEADER,
                              'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': False,
                              'use_post': False, 'return_data': True}
                link20 = self.cm.getURLRequestData(query_data)
                with open(IMAGEFILE, 'wb') as f:
                    f.write(link20)
                img = xbmcgui.ControlImage(450, 0, 400, 130, IMAGEFILE)
                wdlg = xbmcgui.WindowDialog()
                wdlg.addControl(img)
                wdlg.show()
                kb = xbmc.Keyboard('', 'Type the letters in the image', False)
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
                query_data = {'url': 'http://www.efilmy.tv//mirrory.php?cmd=check_captcha', 'use_host': False,
                              'use_header': True, 'header': HEADER, 'use_cookie': True, 'cookiefile': COOKIEFILE,
                              'load_cookie': True, 'save_cookie': True, 'use_post': True, 'return_data': True}
                postdata = {'captcha': solution, "id": str(mymatch[0][0]), "mode": str(mymatch[0][1])}
                link2 = self.cm.getURLRequestData(query_data, postdata)

            myfile2 = re.compile('Base64.decode\("(.*?)"\)').findall(link2)
            log.info("m2 %s " % myfile2)
            if len(myfile2) > 0:
                import base64
                decode = base64.b64decode(myfile2[0])
                print("myfile", decode)
                myfile3 = re.compile('<IFRAME SRC="([^"]+)".*?>').findall(decode)
                myfile4 = re.compile('<iframe src="([^"]+)".*?>').findall(decode)
                if len(myfile3) > 0:
                    #linkVideo = self.up.getVideoLink(myfile3[0])
                    linkVideo = myfile3[0]
                    hmf = urlresolver.HostedMediaFile(url=linkVideo, include_disabled=True, include_universal=False)
                    if hmf.valid_url() == True:
                        linkVideo = hmf.resolve()

                if len(myfile4) > 0:
                    query_data = {'url': myfile4[0], 'use_host': False, 'use_header': True, 'header': HEADER,
                                  'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True,
                                  'save_cookie': False, 'use_post': False, 'return_data': True}
                    link20 = self.cm.getURLRequestData(query_data)
                    mymatch1 = re.compile(
                        ' <a href="(.*?)" style="display:block;width:100%;height:320px" id="player">').findall(link20)
                    linkVideo = mymatch1[0]+'|Referer='+url

        return linkVideo

    def zalukajtv(self, url, referer):
        linkVideo = ''
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        myfile1 = re.compile('<iframe allowTransparency="true" src="(.*?)" width="490" height="370" scrolling="no" frameborder="0">').findall(link)
        soup = BeautifulSoup(url)
        linki_ost1 = soup.find('div', {"id": "lol2"})
        if linki_ost1:
            myfile2 = linki_ost1.find('a', {"target":"_blank"})
            log.info("myfile2 :%s"% myfile2 )
            if myfile2:
                return self.up.getVideoLink(myfile2['href'])

        log.info("m:%s"% myfile1)
        if len(myfile1) > 0 and linkVideo=='':
            log.info("url   %s " % myfile1[0])
            query_data = { 'url': 'http://zalukaj.tv' + myfile1[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link2 = self.cm.getURLRequestData(query_data)
            myfile2 = re.compile('<a href="(.*?)">').findall(link2)
            log.info("m:%s"% myfile2)

            if len(myfile2)>0:
                if len(myfile2)==1:
                    query_data = { 'url': 'http://zalukaj.tv' + myfile2[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
                    link3 = self.cm.getURLRequestData(query_data)
                    myfile3 = re.compile('<iframe src="([^"]+)".*?>').findall(link3)
                    log.info("m:%s"% myfile3)
                    if len(myfile3)>0:
                        return self.up.getVideoLink(myfile3[0])
                        linkVideo = myfile3[0]


            linkVideo = myfile1[0][0]

        return linkVideo

    def filmydokumentalneeu(self, url, referer):
        linkVideo = ''
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        # match1=re.compile('<div id="news">\n          \t<h1><span>(.*?)</span>(.*?)</h1>\n\t\t\t\n\n<div class="fb-social-plugin fb-follow" data-font="lucida grande" data-href="(.*?)" data-width="450"></div>\n\n<div class="fb-social-plugin fb-like" data-font="lucida grande" data-ref="above-post" data-href="(.*?)" data-width="450"></div>\n<p>(.*)</p>\n<p><iframe(.*)></iframe>').findall(link)
        match1 = re.compile('<p><iframe(.*)></iframe>').findall(link)
        match10 = re.compile('<embed(.*)>').findall(link)
        if len(match1) > 0:
            match2 = re.compile('src="(.*?)"').findall(match1[0])
            if len(match2) > 0:
                linkVideo = self.up.getVideoLink(self.cm.html_special_chars(match2[0]))
        elif len(match10) > 0:
            match2 = re.compile('src="(.*?)"').findall(match10[0])
            if len(match2) > 0:
                linkVideo = self.up.getVideoLink(self.cm.html_special_chars(match2[0]))
        return linkVideo

    def alltubetv(self, url, referer):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile(
            '<td><img src="(.*?)"\s.*alt="(.*?)">(.*?)</td>\s.*<td style="width: 100px;">\s.*<a href="#!" class="watch"\s.*data-iframe="(.*?)">.*\s.*\s.*\s.*\s.*\s.*\s.*<td style="width: 80px;"\s.*class="text-center">(.*?)</td>'
        ).findall(link)
        #log.info("Match1 %s"% match1)
        tab = []
        tab2 = []
        if match1:
            for i in range(len(match1)):
                #log.info("Link ALL %s" % match1[i][3].decode('base64'))
                tab.append(match1[i][1] + ' - ' + match1[i][4])
                tab2.append(match1[i][3].decode('base64'))
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór strony video", tab)
            if video_menu != "":
                linkVideo = tab2[video_menu]
                log.info('All pageparser   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)

                if 'http://alltube.tv/special.php' in linkVideo:
                    query_data = {'url': linkVideo, 'use_host': False, 'use_cookie': False, 'use_post': False,'return_data': True}
                    link = self.cm.getURLRequestData(query_data)
                    match = re.search('<iframe src="(.+?)"', link)
                    if match:
                        linkVideo = match.group(1)
                log.info('All pageparser   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
                #linkVideo = self.up.getVideoLink(tab2[video_menu], url)
                try:
                    hmf = urlresolver.HostedMediaFile(url=linkVideo, include_disabled=True, include_universal=False)
                    if hmf.valid_url() == True: OtherResolver = hmf.resolve()
                    log.info('XYXYXYXYXYYXYXYX   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % OtherResolver)
                    if OtherResolver == False:
                        OtherResolver = self.up.getVideoLink(linkVideo,url)
                    else:
                        return OtherResolver
                except:
                    OtherResolver = self.up.getVideoLink(linkVideo, url)
                    return OtherResolver
        else:
            return ''

    def tvseriesonline(self, url, referer):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        # Sprawdamy linki napisy
        linki_lektor = mrknow_utils.soup_get_links(link, "li", {"id": "lektor_pl"})
        linki_pl = mrknow_utils.soup_get_links(link, "li", {"id": "napisy_pl"})
        linki_en = mrknow_utils.soup_get_links(link, "li", {"id": "wersja_eng"})
        linki_all = linki_lektor + linki_pl + linki_en
        tab = []
        tab2 = []
        if len(linki_all) > 0:
            for i in range(len(linki_all)):
                # print("Link", linki_all[i]['text'], linki_all[i]['id']['id'])
                tab.append(linki_all[i]['id']['id'] + ' - ' + mrknow_utils.getHostName(linki_all[i]['text']))
                tab2.append(linki_all[i]['link'])
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór strony video", tab)
            if video_menu != "":
                linkVideo = self.up.getVideoLink(tab2[video_menu], url)
                return linkVideo
        else:
            return ''

    def zobacztotv(self, url, referer):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<div class="play-free" id="loading-(.*?)">Oglądaj na:<br />(.*?)</div>').findall(link)

        tab = []
        tab2 = []
        if len(match1) > 0:
            for i in range(len(match1)):
                match2 = re.compile("\$\('#(.*?)-" + match1[i][0] + "'\).load\('(.*?)'\);").findall(link)
                if len(match2) > 0:
                    tab.append('Strona - ' + match2[0][0])
                    tab2.append(match2[0][1])
            d = xbmcgui.Dialog()
            video_menu = d.select("Wybór strony video", tab)
            if video_menu != "":
                query_data = {'url': tab2[video_menu], 'use_host': False, 'use_cookie': False, 'use_post': False,
                              'return_data': True}
                link = self.cm.getURLRequestData(query_data)
                match = re.search('<iframe src="(.*?)"', link)
                if match:
                    linkVideo = match.group(1)
                    try:
                        hmf = urlresolver.HostedMediaFile(url=linkVideo, include_disabled=True, include_universal=False)
                        if hmf.valid_url() == True: OtherResolver = hmf.resolve()
                        if OtherResolver == False:
                            OtherResolver = self.up.getVideoLink(linkVideo, url)
                        else:
                            return OtherResolver
                    except:
                        OtherResolver = self.up.getVideoLink(linkVideo, url)
                        return OtherResolver

                    linkVideo = self.up.getVideoLink(match.group(1), url)
                    return linkVideo
            else:
                return ''
        else:
            return ''

    def screentv(self, url, referer):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        #                  <iframe width="720" height="490" frameborder="0" scrolling="no" src="http://www.typertv.com.pl/emded/canal.php" allowfullscreen>
        match1 = re.compile(
            '<iframe name="stream" id="stream-frame-iframe" src="embed/(.*?)"scrolling="no"> </iframe>').findall(link)
        if match1:
            mylink = 'http://screen-tv.pl/embed/' + match1[0]
            return self.pageanalyze(mylink, url)

    def typertv(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        #                  <iframe width="720" height="490" frameborder="0" scrolling="no" src="http://www.typertv.com.pl/emded/canal.php" allowfullscreen>
        match1 = re.compile('<iframe (.*?)src="(.*?)/emded/(.*?)" (.*?)></iframe>').findall(link)
        if match1:
            mylink = match1[0][1] + '/emded/' + match1[0][2]
            return self.pageanalyze(mylink, url)

    def nettvpw(self, url, referer=''):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<embed src="(.*?)" width="700" height="418" (.*?)></embed>').findall(link)
        if len(match1) > 0:
            return self.getVideoLink(match1[0][0], match1[0][0])

        else:
            return self.pageanalyze(url, url)

    def zobaczxyz(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile(
            '<iframe(.*?)width="700px" height="500px" src="(.*?)" allowfullscreen="" scrolling="no" frameborder="0"></iframe>').findall(
            link)
        if len(match1) > 0:
            nUrl = self.pageanalyze(match1[0][1], match1[0][1])
            return nUrl
        else:
            return ''

    def looknijtv(self, url, referer):
        import looknijtv
        self.looklink = looknijtv.looknijtv()
        link = self.looklink.getMovieLinkFromXML(url)
        return link

    def ustream(self, url, referer):
        video_id = '0'
        query = urlparse.urlparse(url)
        channel = query.path
        p = urlparse.parse_qs(query.query)
        params = query.path.split("/")
        if query.path[:16] == '/swf/live/viewer':
            video_id = p['cid'][0]
        if query.path[:9] == '/channel/':
            query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
            link = self.cm.getURLRequestData(query_data)
            match1 = re.compile('<meta name="ustream:channel_id" content="(.*?)"').findall(link)
            video_id = match1[0]
        query_data = {'url': 'https://api.ustream.tv/channels/' + video_id + '.json', 'use_host': False,
                      'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        data = json.loads(link)

        if video_id != '0':
            if data['channel']['status'] == u'live' and video_id != '0':
                nUrl = data['channel']['stream']['hls']
                return nUrl
            else:
                return ''

        else:
            return ''

    def yousattv(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<a href="(.*?)"(.*?)><span class="belka1a">(.*?)</span></a>').findall(link)
        if len(match1[0][0]) > 0:
            nUrl = self.getVideoLink(match1[0][0])
            return nUrl
        else:
            return ''

    def fupptvpl(self, url):
        nUrl = self.up.getVideoLink(url, url)
        return nUrl

    def teamcastpl(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<iframe(.*?)src="(.*?)"(.*?)></iframe>').findall(link)
        if len(match1) > 0:
            nUrl = self.pageanalyze(match1[0][1], url)
            return nUrl
        else:
            nUrl = self.pageanalyze(url, url)
            return nUrl

    def mecztv(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile(
            '<iframe frameborder="0" height="480" marginheight="0px" marginwidth="0px" name="livemecz.com" scrolling="no" src="(.*?)" width="640"></iframe>').findall(
            link)
        if len(match1[1]) > 0:
            query_data = {'url': match1[0], 'use_host': False, 'use_cookie': False, 'use_post': False,
                          'return_data': True}
            link = self.cm.getURLRequestData(query_data)
            match2 = re.compile(
                '<iframe marginheight="0" marginwidth="0" name="mecz.tv" src="(.*?)" frameborder="0" height="480" scrolling="no" width="640"></iframe>').findall(
                link)
            if len(match2[0]) > 0:
                query_data = {'url': match2[0], 'use_host': False, 'use_cookie': False, 'use_post': False,
                              'return_data': True}
                link = self.cm.getURLRequestData(query_data)
                match3 = re.compile('<iframe(.*?)src="(.*?)"(.*?)>').findall(link)
                if len(match3) > 0:
                    nUrl = self.pageanalyze(match3[0][1], url)
                else:
                    nUrl = self.pageanalyze(match2[0], url)
            # nUrl = self.pageanalyze('http://goodcast.tv/' + match1[0][0], 'http://goodcast.tv/' + match1[0][0])

            # return nUrl
            return False

    def goodcasttv(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile(
            '<iframe frameborder="0" width="630" height="360" margin="0px" name="goodcast.tv" scrolling="no" src="(.*?)"></iframe>').findall(
            link)
        query_data = {'url': match1[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match2 = re.compile(
            '<iframe width="630px" height="350px" scrolling="no" frameborder="0" src="(.*?)"></iframe>').findall(link)
        match3 = re.compile("file: '(.*?)',").findall(link)
        if len(match2) > 0:
            nUrl = self.up.getVideoLink(match2[0], url)
            return nUrl
        if len(match3) > 0:
            nUrl = self.up.getVideoLink(match1[0], url)
            return nUrl

    def streamon(self, url):
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "streamon.cookie"
        nUrl = self.pageanalyze(url, url)
        return nUrl

    def azap(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<meta http-equiv="Refresh" content="(.*?); url=(.*?)" />').findall(link)
        if len(match1) > 0:
            url = match1[0][1]
            nUrl = self.up.getVideoLink(url)
            return nUrl

        else:
            return self.pageanalyze(match1[0])

    def bbpolska(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div id="player">(.*?)</div>').findall(link)
        if len(match) > 0:
            match1 = re.compile('src="(.*?)"').findall(match[0])
            return self.pageanalyze(match1[0], match1[0])
        else:
            return False

        match = re.compile(
            '<iframe width="(.*?)" height="(.*?)" src="(.*?)" scrolling="no" frameborder="0" style="border: 0px none transparent;">').findall(
            link)
        return self.pageanalyze('http://www.transmisje.info' + match[0][2], 'http://www.transmisje.info')

    def transmisjeinfo(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile(
            '<iframe width="(.*?)" height="(.*?)" src="(.*?)" scrolling="no" frameborder="0" style="border: 0px none transparent;">').findall(
            link)
        return self.pageanalyze('http://www.transmisje.info' + match[0][2], 'http://www.transmisje.info')

    def realtv(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile(
            '<iframe frameborder="0" height="420" marginheight="0px" marginwidth="0px" name="RealTV.com.pl" scrolling="no" src="(.*?)" width="650">').findall(
            link)
        return self.pageanalyze(match[0], 'http://www.realtv.com.pl')

    def livemecz(self, url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile(
            '<iframe frameborder="0" height="480" marginheight="0px" marginwidth="0px" name="livemecz.com" scrolling="no" src="(.+?)" width="640"></iframe>').findall(
            link)
        query_data = {'url': match[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        link = self.cm.getURLRequestData(query_data)
        match = re.compile(
            '<iframe marginheight="0" marginwidth="0" name="livemecz.com" src="(.*?)" frameborder="0" height="480" scrolling="no" width="640">').findall(
            link)
        videolink = self.pageanalyze(match[0], 'http://livemecz.com/')
        return videolink

    def drhtv(self, url):
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "streamon.cookie"
        return self.pageanalyze(url, url, '', 'Accept-Encoding: gzip, deflate')

    def pageanalyze(self, url, referer='', cookie='', headers=''):
        print ('DANE', url, referer, cookie, headers)

        if cookie != '':
            query_data = {'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True,
                          'cookiefile': cookie, 'use_post': False, 'return_data': True}
            link = self.cm.getURLRequestData(query_data)
        elif headers != '':
            query_data = {'url': url, 'use_host': True, 'host': headers, 'use_cookie': False, 'use_post': False,
                          'return_data': True}
            link = self.cm.getURLRequestData(query_data)
        elif referer != '':
            print "Refe"
            query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True,
                          'header': {'Referer': referer,
                                     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}}
            link = self.cm.getURLRequestData(query_data)
        else:
            query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
            link = self.cm.getURLRequestData(query_data)

        match = re.compile(
            '<script type="text/javascript"> channel="(.*?)"; width="(.*?)"; height="(.*?)";</script><script type="text/javascript" src="http://yukons.net/share.js"></script>').findall(
            link)
        match1000 = re.compile(
            '<script type="text/javascript"> channel="(.*?)"; width="(.*?)"; height="(.*?)";</script>\n<script type="text/javascript" src="http://yukons.net/share.js"></script>').findall(
            link)
        match1 = re.compile(
            "<script type='text/javascript'>fid='(.*?)'; v_width=(.*?); v_height=(.*?);</script><script type='text/javascript' src='http://www.reyhq.com/player.js'></script>").findall(
            link)
        match2 = re.compile("<script type='text/javascript' src='http://www.sawlive.tv/embed/(.*?)'>").findall(link)
        match3 = re.compile("<script type='text/javascript' src='http://sawlive.tv/embed/(.*?)'>").findall(link)
        match4 = re.compile('<script type="text/javascript" src="http://www.ilive.to/embed/(.*?)">').findall(link)
        match5 = re.compile(
            "<script type='text/javascript'> channel='(.*?)'; user='(.*?)'; width='640'; height='400';</script><script type='text/javascript' src='http://jimey.tv/player/jimeytv_embed.js'>").findall(
            link)
        match6 = re.compile(
            "<script type='text/javascript'> width=(.*?), height=(.*?), channel='(.*?)', e='(.*?)';</script><script type='text/javascript' src='http://www.mips.tv/content/scripts/mipsEmbed.js'>").findall(
            link)
        match7 = re.compile(
            '<script type="text/javascript">fid="(.*?)"; v_width=(.*?); v_height=(.*?);</script><script type="text/javascript" src="http://www.ukcast.tv/embed.js"></script>').findall(
            link)
        match8 = re.compile(
            '<script type="text/javascript"> channel="(.*?)"; vwidth="(.*?)"; vheight="(.*?)";</script><script type="text/javascript" src="http://castamp.com/embed.js"></script>').findall(
            link)
        match9 = re.compile(
            "<script type='text/javascript'>id='(.*?)'; width='(.*?)'; height='(.*?)';</script><script type='text/javascript' src='http://liveview365.tv/js/player.js'></script>").findall(
            link)
        match10 = re.compile(
            '<script type="text/javascript"> channel="(.*?)"; width="(.*?)"; height="(.*?)";</script>\r\n<script type="text/javascript" src="http://yukons.net/share.js"></script>').findall(
            link)
        match11 = re.compile('<iframe width="600px" height="400px" scrolling="no" frameborder="0" src="http://www.putlive.in/(.*?)"></iframe>').findall(link)
        match12 = re.compile(
            '<iframe frameborder=0 marginheight=0 marginwidth=0 scrolling=\'no\'src="(.*?)" width="(.*?)" height="(.*?)">').findall(
            link)
        match13 = re.compile(
            "<script type='text/javascript'> width=640, height=480, channel='(.*?)', g='(.*?)';</script><script type='text/javascript' src='http://www.ucaster.eu/static/scripts/ucaster.js'></script>").findall(
            link)
        match14 = re.compile(
            "<script type='text/javascript'>fid='(.*?)'; v_width=(.*?); v_height=(.*?);</script><script type='text/javascript' src='http://www.flashwiz.tv/player.js'></script>").findall(
            link)
        match15 = re.compile(
            '<script type="text/javascript"> fid="(.*?)"; v_width=(.*?); v_height=(.*?);</script><script type="text/javascript" src="http://www.yycast.com/javascript/embedPlayer.js"></script>').findall(
            link)
        match16 = re.compile(
            "<script type='text/javascript'> width=(.*?), height=(.*?), channel='(.*?)', g='(.*?)';</script><script type='text/javascript' src='http://www.liveflash.tv/resources/scripts/liveFlashEmbed.js'></script>").findall(
            link)
        match17 = re.compile(
            '<script type="text/javascript">ca="(.*?)";width="(.*?)"; height="(.*?)";</script><script type="text/javascript" src="https://ovcast.com/js/embed.js"></script>').findall(
            link)
        match18 = re.compile(
            "<script type=\'text/javascript\'>id=\'(.*?)\'; width=\'(.*?)\'; height=\'(.*?)\';</script><script type=\'text/javascript\' src=\'http://stream4.tv/player.js\'>").findall(
            link)
        match19 = re.compile(
            "<script type='text/javascript'>id='(.*?)'; width='(.*?)'; height='(.*?)';</script><script type='text/javascript' src='http://goodcast.org/player.js'></script>").findall(
            link)
        match20 = re.compile('<script type="text/javascript" src="http://(.*?)jjcast.com/(.*?)">').findall(link)
        match21 = re.compile(
            '<script type="text/javascript" language="JavaScript" src="http://hqstream.tv/pl?(.*?)"></script>').findall(
            link)
        match22 = re.compile(
            "<script type='text/javascript'>(.*?)</script><script type='text/javascript' src='http://cdn.tiv.pw/stream(.*?).js'></script>").findall(
            link)
        match23 = re.compile(
            '<script type="text/javascript" src="http://7cast.net/embed/(.*?)/(.*?)/(.*?)"></script>').findall(link)
        match24 = re.compile(
            '<script type=\'text/javascript\'> file=\'(.*?)\'(.*?)</script>\n<script type=\'text/javascript\' src=\'http://abcast.biz/embedPlayer.js\'>').findall(
            link)
        match25 = re.compile(
            '<script type=\'text/javascript\'> file=\'(.*?)\'; width=\'(.*?)\'; height=\'(.*?)\';</script><script type=\'text/javascript\' src=\'http://flexstream.net/embedPlayer.js\'></script>').findall(
            link)
        match26 = re.compile(
            '<script type=\'text/javascript\'> file=\'(.*?)\'(.*?)</script><script type=\'text/javascript\' src=\'http://abcast.biz/embedPlayer.js\'></script>').findall(
            link)
        match27 = re.compile(
            '<script type=\'text/javascript\'> file=\'(.*?)\'(.*?)</script>\n<script type=\'text/javascript\' src=\'http://www.freelivestream.tv/embedPlayerScript.js\'></script>').findall(
            link)
        match28 = re.compile(
            '<script type=\'text/javascript\'>id=\'(.*?)\'(.*?)</script><script type=\'text/javascript\' src=\'http://up4free.com/player.js\'></script>').findall(
            link)
        match29 = re.compile(
            '<script type=\'text/javascript\'>id=\'(.*?)\'(.*?)</script><script type=\'text/javascript\' src=\'http://goodcast.me/player.js\'></script>').findall(
            link)
        match30 = re.compile(
            '<script type=\'text/javascript\' src=\'http://www.shidurlive.com/embed/(.*?)\'></script>').findall(link)
        match31 = re.compile(
            '<script type="text/javascript"> id="(.*?)"; ew="(.*?)"; eh="(.*?)";</script><script type="text/javascript" src="http://www.castalba.tv/js/embed.js"></script>').findall(
            link)
        match32 = re.compile(
            '<script type=\'text/javascript\'> file=\'(.*?)\'(.*?)</script><script type=\'text/javascript\' src=\'http://abcast.net/abc.js\'></script>').findall(
            link)
        match33 = re.compile(
            '<script type=\'text/javascript\'>id=\'(.*?)\'(.*?)</script><script type=\'text/javascript\' src=\'http://player.goodcast.co/goodcast/player.js\'></script>').findall(
            link)
        match34 = re.compile(
            '<script type="text/javascript"> fid="(.*?)"; v_width=(.*?); v_height=(.*?);</script><script type="text/javascript" src="http://static.castto.me/js/embedplayer.js">').findall(
            link)
        match35 = re.compile('<script type="text/javascript" src="http://www.byetv.org/(.*?)"></script>').findall(link)
        match36 = re.compile('<script type="text/javascript" src="http://www.hdcast.me/(.*?)"></script>').findall(link)
        match37 = re.compile(
            "<script type='text/javascript'> file='(.*?)'(.*?)</script><script type='text/javascript' src='http://pxstream.tv/embedPlayerScript.js'></script>").findall(
            link)
        match38 = re.compile(
            "<script type='text/javascript'>id='(.*?)';(.*?)</script><script type='text/javascript' src='http://deltatv.pw/player.js'></script>").findall(
            link)
        match39 = re.compile(
            "<script type='text/javascript'> id='(.*?)';(.*?)</script><script type='text/javascript' src='http://ultracast.me/player.js'></script>").findall(
            link)
        match40 = re.compile(
            "<script type='text/javascript'>(.*?)</script><script type='text/javascript' src='http://shidurlive.com/embed/(.*?)'></script>").findall(
            link)
        match41 = re.compile(
            "<script type='text/javascript'>id='(.*?)'(.*?)</script><script type='text/javascript' src='http://biggestplayer.me/player.js'></script>").findall(
            link)
        match42 = re.compile(
            "<script type='text/javascript'> file='(.*?)';(.*?)</script><script type='text/javascript' src='http://pxstream.tv/embedRouter.js'></script>").findall(
            link)
        match43 = re.compile(
            "<script type='text/javascript'>id='(.*?)';(.*?)</script><script type='text/javascript' src='http://js.p2pcast.tv/p2pcast/player.js'></script>").findall(
            link)
        match44 = re.compile("<script type='text/javascript'>(.*?)channel='(.*?)',(.*?)</script><script type='text/javascript' src='http://tutelehd.com/embedPlayer.js'></script>").findall(link)

        match1001 = re.compile("file : '(.*?)'").findall(link)

        if len(match) > 0:
            return self.up.getVideoLink('http://yukons.net/' + match[0][0], referer)
        elif len(match1000) > 0:
            return self.up.getVideoLink('http://yukons.net/' + match1000[0][0], referer)
        elif len(match1) > 0:
            return self.up.getVideoLink('http://www.reyhq.com/' + match1[0][0])
        elif len(match2) > 0:
            print ("Match2", match2)
            return self.up.getVideoLink('http://www.sawlive.tv/embed/' + match2[0], url)
        elif len(match3) > 0:
            return self.up.getVideoLink('http://www.sawlive.tv/embed/' + match3[0], url)
        elif len(match4) > 0:
            print ("Match4", match4)
            return self.up.getVideoLink('http://www.ilive.to/embed/' + match4[0], referer)
        elif len(match6) > 0:
            print ("Match6", match6[0])
            return self.up.getVideoLink(
                'http://mips.tv/embedplayer/' + match6[0][2] + '/' + match6[0][3] + '/' + match6[0][0] + '/' +
                match6[0][1])
        elif len(match7) > 0:
            print ("Match7", match7)
            return self.up.getVideoLink(
                'http://www.ukcast.tv/embed.php?u=' + match7[0][0] + '&amp;vw=' + match7[0][1] + '&amp;vh=' + match7[0][
                    2])
        elif len(match8) > 0:
            print ("Match8", match8)
            query_data = {'url': 'http://castamp.com/embed.js', 'use_host': False, 'use_cookie': False,
                          'use_post': False, 'return_data': True}
            link = self.cm.getURLRequestData(query_data)
            print("Link", link)
            chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
            string_length = 8;
            randomstring = '';
            for i in range(0, string_length):
                rnum = int(math.floor(random.randint(0, len(chars))))
                print("AAA", rnum, chars[1])
                randomstring = randomstring + chars[rnum]
            return self.up.getVideoLink(
                'http://castamp.com/embed.php?c=' + match8[0][0] + '&tk=' + randomstring + '&vwidth=710&vheight=460',
                referer)
        elif len(match9) > 0:
            print ("Match9", match9)
            return self.up.getVideoLink('http://liveview365.tv/embedded?id=' + match9[0][0], referer)
        elif len(match10) > 0:
            print ("Match10", match10)
            return self.up.getVideoLink('http://yukons.net/' + match10[0][0])
        elif len(match11) > 0:
            print ("Match11", 'http://www.putlive.in/' + match11[0])
            return self.up.getVideoLink('http://www.putlive.in/' + match11[0], referer)
        elif len(match12) > 0:
            print ("Match12", match12)
            return self.up.getVideoLink(match12[0][0], referer)
        elif len(match13) > 0:
            print ("Match13", match13)
            return self.up.getVideoLink(
                'http://www.ucaster.eu/embedded/' + match13[0][0] + '/' + match13[0][1] + '/400/480', referer)
        elif len(match14) > 0:
            print ("Match14", match14)
            return self.up.getVideoLink(
                'http://www.flashwiz.tv/embed.php?live=' + match14[0][0] + '&vw=' + match14[0][1] + '&vh=' + match14[0][
                    2], referer)
        elif len(match15) > 0:
            print ("Match15", match15)
            return self.up.getVideoLink(
                'http://www.yycast.com/embed.php?fileid=' + match15[0][0] + '&vw=' + match15[0][1] + '&vh=' +
                match15[0][2], referer)
        elif len(match16) > 0:
            print ("Match16", match16)
            return self.up.getVideoLink(
                'http://www.liveflash.tv/embedplayer/' + match16[0][2] + '/' + match16[0][3] + '/' + match16[0][
                    0] + '/' + match16[0][1], referer)
        elif len(match17) > 0:
            print ("Match17", match17)
            return self.up.getVideoLink(
                'https://ovcast.com/gen.php?ch=' + match17[0][0] + '&width=' + match17[0][1] + '&height=' + match17[0][
                    2], referer)
        elif len(match18) > 0:
            print ("Match18", match18)
            return self.up.getVideoLink(
                'http://stream4.tv/player.php?id=' + match18[0][0] + '&width=' + match18[0][1] + '&height=' +
                match18[0][2], referer)
        elif len(match19) > 0:
            print ("Match19", match19)
            return self.up.getVideoLink(
                'http://goodcast.org/stream.php?id=' + match19[0][0] + '&width=' + match19[0][1] + '&height=' +
                match19[0][2], referer)
        elif len(match20) > 0:
            print ("Match20", match20)
            return self.up.getVideoLink('http://jjcast.com/' + match20[0][1].replace('embed', 'player'), referer)
        elif len(match21) > 0:
            print ("Match21", match21)
            return self.up.getVideoLink('http://hqstream.tv/player.php' + match21[0], referer)
        elif len(match22) > 0:
            print ("Match22", match22)
            return self.up.getVideoLink('http://cdn.tiv.pw/stream' + +match22[0] + '.html', referer)
        elif len(match23) > 0:
            print ("Match23", match23)
            return self.up.getVideoLink('http://7cast.net/player/' + match23[0][0] + '/650/450', referer)
        elif len(match24) > 0:
            print ("Match24", match24)
            return self.up.getVideoLink(
                'http://abcast.biz/embed.php?file=' + match24[0][0] + '&amp;width=640&amp;height=400', referer)
        elif len(match25) > 0:
            print ("Match25", match25)
            return self.up.getVideoLink(
                'http://flexstream.net/embed.php?file=' + match25[0][0] + '&amp;width=640&amp;height=400', referer)
        elif len(match26) > 0:
            print ("Match26", match26)
            return self.up.getVideoLink(
                'http://abcast.biz/embed.php?file=' + match26[0][0] + '&amp;width=640&amp;height=400', referer)
        elif len(match27) > 0:
            print ("Match27", match27)
            return self.up.getVideoLink(
                'http://www.freelivestream.tv/embedPlayer.php?file=' + match27[0][0] + '&amp;width=600&amp;height=400',
                referer)
        elif len(match28) > 0:
            print ("Match28", match28, url)
            # http://embed.up4free.com/stream.php?id=nsajfnidg&width=700&height=450&stretching=
            url2 = 'http://embed.up4free.com/stream.php?id=' + match28[0][0] + '&width=700&height=450&stretching='
            mylink10 = mrknow_Pageparser()
            mylink3 = mylink10.pageanalyze(url2, url)
            print("MyLink3", mylink3, referer)

            print("MyLink3", url2, mylink3, match28[0][0], link)
            return mylink3
        elif len(match29) > 0:
            print ("Match29", match29)
            return self.up.getVideoLink(
                'http://goodcast.me/stream.php?id=' + match29[0][0] + '&amp;width=640&amp;height=480&amp;stretching=',
                referer)
        elif len(match30) > 0:
            print ("Match30", match30)
            return self.up.getVideoLink('http://www.shidurlive.com/embed/' + match30[0], referer)
        elif len(match31) > 0:
            print ("Match31", match31)
            return self.up.getVideoLink('http://castalba.tv/embed.php?cid=' + match31[0][
                0] + '&amp;wh=640&amp;ht=400&amp;r=' + self.getHostName(referer), referer)
        elif len(match32) > 0:
            print ("Match32", match32)
            return self.up.getVideoLink(
                'http://abcast.net/abc.php?file=' + match32[0][0] + '&amp;width=640&amp;height=400', referer)
        elif len(match33) > 0:
            print ("Match33", match33, referer)
            host = self.getHostName(url)
            if host == 'embed.up4free.com':
                return self.up.getVideoLink('http://goodcast.co/stream.php?id=' + match33[0][
                    0] + '&amp;width=640&amp;height=480&amp;stretching=', url)
            else:
                return self.up.getVideoLink('http://goodcast.co/stream.php?id=' + match33[0][
                    0] + '&amp;width=640&amp;height=480&amp;stretching=', referer)
        elif len(match34) > 0:
            print ("Match34", match34, referer)
            mylink = self.up.getVideoLink(
                'http://static.castto.me/embed.php?channel=' + match34[0][0] + '&vw=710&vh=460', referer)
            print("Match34", mylink)
            return mylink

        elif len(match35) > 0:
            print ("Match35", match35, referer)
            link = match35[0].replace('channel.php?file=', 'http://www.byetv.org/embed.php?a=')
            mylink = self.up.getVideoLink(link, referer)
            return mylink
        elif len(match36) > 0:
            print ("Match36", match36, referer)
            mylink = self.up.getVideoLink('http://hdcast.me/' + match36[0].replace('embed.php?', 'embedplayer.php?'),
                                          referer)
            return mylink
        elif len(match37) > 0:
            print ("Match37", match37, referer, match37[0][0])
            return self.up.getVideoLink('http://pxstream.tv/embed.php?file=' + match37[0][0] + '&width=710&height=460',
                                        referer)
        elif len(match38) > 0:
            print ("Match38", match38, referer)
            return self.up.getVideoLink('http://deltatv.pw/stream.php?id=' + match38[0][0] + '&width=710&height=460',
                                        referer)
        elif len(match39) > 0:
            print ("Match39", match39, referer)
            return self.up.getVideoLink(
                'http://www.ultracast.me/player.php?id=' + match39[0][0] + '&width=710&height=460', referer)
        elif len(match40) > 0:
            print ("Match40", match40)
            return self.up.getVideoLink('http://www.shidurlive.com/embed/' + match40[0][1], referer)
        elif len(match41) > 0:
            print ("Match41", match41)
            return self.up.getVideoLink(
                'http://biggestplayer.me/stream.php?id=' + match41[0][0] + '&width=690&height=440', referer)
        elif len(match42) > 0:
            print ("Match42", match42)
            return self.up.getVideoLink('http://pxstream.tv/embed.php?file=' + match42[0][0] + '&width=710&height=460',
                                        referer)
        elif len(match43) > 0:
            print ("Match43", match43)
            return self.up.getVideoLink(
                'http://p2pcast.tv/stream.php?id=' + match43[0][0] + '&live=0&p2p=0&stretching=uniform', referer)
        elif len(match44) > 0:
            print ("Match44", match44)
            return self.up.getVideoLink('http://tutelehd.com/embed/embed.php?channel=' + match44[0][1] + '&w=690&h=440',
                                        referer)
        elif len(match1001) > 0:
            print ("match1001", match1001)
            if len(match1001) > 0:
                return match1001[0] + " live=true timeout=30"
            else:
                return ''

        else:
            print ("jEDZIEMY NA ELSE", link)
            return self.up.getVideoLink(url, referer)
