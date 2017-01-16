# -*- coding: utf-8 -*-

import sys

sys.path.append('/home/mrknow/Dokumenty/praca/kodi/specto/plugin.video.specto/mylib/')
sys.path.append('/home/mrknow/Dokumenty/praca/kodi/filmkodi/script.mrknow.urlresolver/lib/')

from Crypto.Cipher import DES
from Crypto import Random
import base64


data = {"a":"Rzq+VC9dt2b0WMVzfmYfAsSORD7zU7H2orWeLSGGkpS\/twESdgWwO0b2Fnj9OiDA","b":"aaa4e849a06ff93e6b7947ab14c21ec3","v":"5401354f7b505648"}
from Crypto.Cipher import DES
from Crypto import Random
iv = Random.get_random_bytes(8)
des2 = DES.new(data['b'].decode('hex'), DES.MODE_CFB, data['v'].decode('hex'))
text = 'abcdefghijklmnop'
#cipher_text = des1.encrypt(text)
#cipher_text
#"?\\\x8e\x86\xeb\xab\x8b\x97'\xa1W\xde\x89!\xc3d"
print des2.decrypt(data['a'])


#print decrypt(data['a']+data['v'],data['b'])
exit()
import os, json
import binascii

from cgi import parse_header, parse_multipart
from urlparse import parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from Crypto import Random
from Crypto.Cipher import AES


# ------------------------------
# DEFINE Encryption Class
class Cryptor(object):
    '''
    Provide encryption and decryption function that works with crypto-js.
    https://code.google.com/p/crypto-js/

    Padding implemented as per RFC 2315: PKCS#7 page 21
    http://www.ietf.org/rfc/rfc2315.txt

    The key to make pycrypto work with crypto-js are:
    1. Use MODE_CFB.  For some reason, crypto-js decrypted result from MODE_CBC
       gets truncated
    2. Use Pkcs7 padding as per RFC 2315, the default padding used by CryptoJS
    3. On the JS side, make sure to wrap ciphertext with CryptoJS.lib.CipherParams.create()
    '''

    # AES-256 key (32 bytes)
    KEY = "01ab38d5e05c92aa098921d9d4626107133c7e2ab0e4849558921ebcc242bcb0"
    BLOCK_SIZE = 16

    @classmethod
    def _pad_string(cls, in_string):
        '''Pad an input string according to PKCS#7'''
        in_len = len(in_string)
        pad_size = cls.BLOCK_SIZE - (in_len % cls.BLOCK_SIZE)
        return in_string.ljust(in_len + pad_size, chr(pad_size))

    @classmethod
    def _unpad_string(cls, in_string):
        '''Remove the PKCS#7 padding from a text string'''
        in_len = len(in_string)
        pad_size = ord(in_string[-1])
        if pad_size > cls.BLOCK_SIZE:
            raise ValueError('Input is not padded or padding is corrupt')
        return in_string[:in_len - pad_size]

    @classmethod
    def generate_iv(cls, size=16):
        return Random.get_random_bytes(size)

    @classmethod
    def encrypt(cls, in_string, in_key, in_iv=None):
        '''
        Return encrypted string.
        @in_string: Simple str to be encrypted
        @key: hexified key
        @iv: hexified iv
        '''
        key = binascii.a2b_hex(in_key)

        if in_iv is None:
            iv = cls.generate_iv()
            in_iv = binascii.b2a_hex(iv)
        else:
            iv = binascii.a2b_hex(in_iv)

        aes = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
        return in_iv, aes.encrypt(cls._pad_string(in_string))

    @classmethod
    def decrypt(cls, in_encrypted, in_key, in_iv):
        '''
        Return encrypted string.
        @in_encrypted: Base64 encoded
        @key: hexified key
        @iv: hexified iv
        '''
        key = binascii.unhexlify(in_key)
        #iv = binascii.unhexlify(in_iv)
        iv  = in_iv.decode('hex')
        aes = AES.new(key, AES.MODE_CBC, iv, segment_size=128)

        decrypted = aes.decrypt(binascii.a2b_base64(in_encrypted).rstrip())


        return cls._unpad_string(decrypted)

ala = Cryptor()

print ala.decrypt(data['a'], data['b'], data['v'])


exit()

import urlresolver9 as urlresolver

def check_openload(myurl):
    z = False
    hmf = urlresolver.HostedMediaFile(myurl, include_disabled=True, include_universal=False)
    if hmf:
        print 'yay! we can resolve this one'
        z = hmf.resolve()
        print ("Z",z)
    else:
        print 'dupa'
    print z


url = 'http://flashx.tv/embed-05em2bhzu9wd-647x500.html'
url = 'https://openload.co/embed/vV5LcJYYGQ0'
url = 'https://openload.co/embed/Uay6TwC1kY8'
#url = 'http://thevideo.me/8rz91niympku'
#url= 'http://www.bitvid.sx/file/20b10a72c320d'
#url = 'http://vidup.me/3per79allwuc'
#url='http://streamin.to/embed-qv8ofqzra5zb-600x480.html'
#url = '//vshare.io/v/e475f88/width-560/height-490/'
check_openload(url)
exit()


url = 'https://openload.co/f/lw38lEUrP1A'
try: check_openload(url)
except: pass
url = 'http://openload.co/embed/3728IVNxWAA'
try: check_openload(url)
except: pass
url = 'http://openload.co/embed/ExatdBfcJ38'
try: check_openload(url)
except: pass

exit()

from resources.lib.sources import sezonlukdizi_tv

from resources.lib.libraries import client
from resources.lib.libraries import cleantitle
from resources.lib.libraries import control
from resources.lib import resolvers

from resources.lib.resolvers import yadisk
from resources.lib.sources.movie25_mv import source


"""
my = source()
a = my.get_movie('tt1431045','Deadpool','2016')
control.log('############ DAYT res-1 %s' % a)
#
b = my.get_sources(a,'','','')
control.log('############ DAYT res-2 %s' % b)
exit
#{'tmdb': '60948', 'tvdb': '272644', 'tvshowtitle': '12 Monkeys', 'imdb': 'tt3148266', 'year': '2015', 'action': 'seasons', 'tvrage': '36903'}
imdb = 'tt3148266'
tvdb = '272644'
title = '12 Monkeys'
year = '2015'
data = '2016-05-23'

#c=my.get_show('tt3148266',tvdb,'12 Monkeys','2015')
#control.log('############ DAYT res-1 %s' % c)
#PARAMS: {'tmdb': '60948', 'episode': '6', 'name': '12 Monkeys S02E06', 'title': 'Immortal', 'tvdb': '272644', 'season': '2', 'tvshowtitle': '12 Monkeys', 'date': '2016-05-23', 'meta': '{"rating": "8.0", "code": "tt3148266", "tmdb": "60948", "imdb": "tt3148266", "year": "2015", "duration": "2700", "plot": "Cole\'s partnership with Ramse is put to the test when they travel back to the 1970s to try to prevent the Twelve from murdering a disturbed Vietnam veteran with a connection to the Witness.", "votes": "47", "thumb": "http://thetvdb.com/banners/episodes/272644/5565074.jpg", "title": "Immortal", "tvdb": "272644", "mpaa": "TV-14", "fanart": "http://thetvdb.com/banners/fanart/original/272644-20.jpg", "season": "2", "status": "Continuing", "poster": "http://thetvdb.com/banners/posters/272644-12.jpg", "tvshowtitle": "12 Monkeys", "studio": "Syfy", "genre": "Mystery / Science-Fiction", "tvrage": "36903", "banner": "http://thetvdb.com/banners/graphical/272644-g5.jpg", "episode": "6", "name": "12 Monkeys S02E06", "premiered": "2016-05-23", "cast": [["Aaron Stanford", ""], ["Amanda Schull", ""], ["Kirk Acevedo", ""], ["Barbara Sukowa", ""], ["Todd Stashwick", ""], ["Emily Hampshire", ""], ["Noah Bean", ""], ["Tom Noonan", ""]], "trailer": "plugin://plugin.video.specto/?action=trailer&name=12+Monkeys"}', 'imdb': 'tt3148266', 'year': '2015', 'action': 'sources', 'tvrage': '36903', 'alter': '0'}
#d=my.get_episode(c,imdb,tvdb,title,data,'2','6')
#control.log('############ DAYT res-1 %s' % d)
#e=my.get_sources(d,'','','')

#url = 'http://ok.ru/video/86215559923'
#print resolvers.request(url)


{"jsonrpc":"2.0","method":"getConfiguration","id":3,"params":{"message":{"id":"FFAE5FDB-5E71-4951-8419-AACCB4BE90FC","timestamp":"2016-10-15T12:12:56Z"
}}}:

"""
import json
url = 'https://gm2.redefine.pl/rpc/system/'
post = json.loads('{"jsonrpc":"2.0","method":"getConfiguration","id":3,"params":{"message":{"id":"FFAE5FDB-5E71-4951-8419-AACCB4BE90FC","timestamp":"2016-10-15T12:12:56Z"}}}:')
headers = {'X-Requested-With' : 'XMLHttpRequest',
           'User-Agent':'mipla_ios/122'}

result = client.source(url, post=post, headers=headers)
print result

"""

src='http://dayt.se/forum/search.php?do=process'

post={'titleonly':1,'securitytoken':'guest','do':'process','q':'London + Has Fallen','B1':''}
result = client.source(src, post=post)
result = client.parseDOM(result, 'h3', attrs={'class': 'searchtitle'})
result = [(client.parseDOM(i, 'a', attrs={'class': 'title'}, ret='href')[0],client.parseDOM(i, 'a', attrs={'class': 'title'})[0]) for i in result]
control.log('############ DAYT res-1 %s' % result)
result = [i for i in result if title in cleantitle.movie(i[1])]
result = [i[0] for i in result if any(x in i[1] for x in years)][0]
result = re.compile('(.+?)(?:&amp)').findall(result)[0]

control.log('############ DAYT res-1 %s' % result)



exit()
result = client.parseDOM(result, 'iframe', ret='src')
result = [i for i in result if 'pasep' in i][0]

control.log('############ DAYT res-1 %s' % result)
result = client.source(result)
result = client.parseDOM(result, 'iframe', ret='src')[0]
result = client.source(result)
result = client.parseDOM(result, 'iframe', ret='src')[0]
control.log('############ DAYT res-2 %s' % result)
#control.log('############ DAYT res-2 %s' % resolvers.request(result))


result10 = client.parseDOM(result2, 'div', attrs = {'id': '5throw'})[0]
result10 = client.parseDOM(result10, 'a', attrs = {'rel': 'nofollow'}, ret='href')
for i in result10:
    print resolvers.request(i)


control.log('############ DAYT res-2 %s' % result10)
https://cloclo9.cldmail.ru/2dfVwUu76bo9TkKgZDPE/G/GT9F/FoCczQknq?key=9170c586eac96c6fbe53d3b77bf5d59b1ac4538a


src='https://cloud.mail.ru/public/GT9F/FoCczQknq'
src='https://cloud.mail.ru/public/6i3K/8aL4QRjZU'
#print resolvers.request(src)

result20 = client.source(src)
title= client.parseDOM(result20, 'title')
print title

vid = src.split('public')[-1]
token  = re.compile('"tokens":{"download":"([^"]+)"}').findall(result20)[0]
weblink = re.compile('"weblink_get":\[{"count":\d+,"url":"([^"]+)"}\]').findall(result20)[0]
print("Dane",token,weblink,vid)


if len(token)>0 and len(weblink)>0:
    url = weblink + vid + '?key='+token

    #result20 = json.loads(result20)
    control.log('############ DAYT res-2 %s' % url)
    #https://cloclo9.cldmail.ru/2dfVwUu76bo9TkKgZDPE/G/GT9F/FoCczQknq?key=9170c586eac96c6fbe53d3b77bf5d59b1ac4538a






src=' http://dayt.se/forum/forumdisplay.php?356-The-Flash'
mytitile = cleantitle.tv('S%02dE%02d' % (2,19)).lower()
control.log('############ DAYT mytitle %s' % mytitile)


result = client.source(src)
result = client.parseDOM(result, 'h3', attrs={'class': 'threadtitle'})
result = [(client.parseDOM(i, 'a', attrs={'class': 'title'}, ret='href')[0],client.parseDOM(i, 'a', attrs={'class': 'title'})[0]) for i in result]
result = [i for i in result if mytitile in i[1].lower()]
result = [(re.compile('(.+?)(?:&amp)').findall(i[0]), i[1]) for i in result][0][0]
control.log('############ DAYT res-2 %s' % result[0])

    #a = client.parseDOM(i, 'a', attrs={'class': 'title'})[0]
    #a1 = client.parseDOM(i, 'a', attrs={'class': 'title'},ret='href')[0]

    #control.log('############ DAYT res-20 %s' % a)
    #control.log('############ DAYT res-21 %s' % a1)
"""