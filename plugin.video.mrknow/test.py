#o=107984:d6409c8683f029ee9a82629175a972b5
#o=107991:58c49f51a3049f43be326cf7b8107415

import random, string, sys

sys.path.append('/home/mrknow/Dokumenty/praca/kodi/plugin.video.mrknow/mylib/')
sys.path.append('/home/mrknow/Dokumenty/praca/kodi/plugin.video.mrknow/lib/')

print ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(25))


web_url = 'http://embed.nowvideo.sx/embed/?v=27e41183d1328'
web_url = 'http://videomega.tv/iframe.php?width=720&height=400&ref=98vnW2gQtGGtQg2Wnv89'
web_url = 'http://vidto.me/embed-hthii6ksp7uz-730x411.html'
web_url = 'http://openload.co/embed/XfsaMfvMRNo'


from urlresolver.hmf import HostedMediaFile

alina = HostedMediaFile(url=web_url).resolve()
print(alina)

import  mrknow_pCommon
mrknow_pCommon.mystat(url='http://aso.pl')