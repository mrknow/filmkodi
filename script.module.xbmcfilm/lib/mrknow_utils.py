# -*- coding: utf-8 -*-
"""
App name
~~~~~~

:copyright: (c) 2014 by mrknow
:license: GNU GPL Version 3, see LICENSE for more details.
"""

import urllib
from BeautifulSoup import BeautifulSoup
import urlparse, httplib, random, string


def getHostName(url):
    hostName = urlparse.urlparse(url)[1].split('.')
    return hostName[-2] + '.' + hostName[-1]

def soup_get_links(data, mytype, mywhat):
    soup = BeautifulSoup(data)
    mytab = []
    linki_pl = soup.find(mytype, mywhat)
    if linki_pl:
        tag_a = linki_pl.findAll('a')
        if len(tag_a)>0:
            for mytag in tag_a:
                myt1 = ''
                if len(mytag.text)>0:
                    myt1 =  mytag.text
                else:
                    myt1 = getHostName(mytag['href'])
                mytab.append({"link": mytag['href'], "text": myt1, "id":mywhat})
        #lektor_pl
        #wersja_eng
    return mytab
