# -*- coding: utf-8 -*-
import re, sys, os, cgi
import urllib, urllib2
import xbmcgui,xbmc

scriptID = sys.modules[ "__main__" ].scriptID
scriptname = "mrknow Polish films online"

class Player:
    def __init__(self):
        pass
    
    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon,year='',plot=''):
    	if videoUrl == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Mo¿e to chwilowa awaria.', 'Spróbuj ponownie za jakiœ czas')
            return False
        print ("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",title, icon,year,plot)
        try:
            if icon == '' or  icon == 'None':
                icon = "DefaultVideo.png"
            liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
            if year == '':
                liz.setInfo( type="video", infoLabels={ "Title": title} )
            else:
                liz.setInfo( type="video", infoLabels={ "Title": title, "Plot": plot, "Year": int(year) } )
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl, liz)
        except:
            d = xbmcgui.Dialog()
            if pType=="video":
                d.ok('Wyst¹pi³ b³¹d!', 'B³¹d przy przetwarzaniu, lub wyczerpany limit czasowy ogl¹dania.', 'Zarejestruj siê i op³aæ abonament.', 'Aby ogl¹daæ za darmo spróbuj ponownie za jakiœ czas.')
            elif pType=="music":
                d.ok('Wyst¹pi³ b³¹d!', 'B³¹d przy przetwarzaniu.', 'Aby wys³uchaæ spróbuj ponownie za jakiœ czas.')
            return False
        return True
        