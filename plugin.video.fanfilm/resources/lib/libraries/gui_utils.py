import xbmcgui
import time
import os
import xbmcaddon
#from utilities import notification, setSetting, getString
#import traktapi
import logging
import control
from trakt_api2 import TraktAPI2

#__addon__ = xbmcaddon.Addon("script.trakt")

def get_pin():
    AUTH_BUTTON = 200
    LATER_BUTTON = 201
    NEVER_BUTTON = 202
    ACTION_PREVIOUS_MENU = 10
    ACTION_BACK = 92
    INSTRUCTION_LABEL = 203
    CENTER_Y = 6
    CENTER_X = 2

    logger = logging.getLogger(__name__)
    
    class PinAuthDialog(xbmcgui.WindowXMLDialog):
        auth = False
        
        def onInit(self):
            self.pin_edit_control = self.__add_editcontrol(30, 240, 40, 450)
            self.setFocus(self.pin_edit_control)
            auth = self.getControl(AUTH_BUTTON)
            never = self.getControl(NEVER_BUTTON)
            #instuction = self.getControl(INSTRUCTION_LABEL)
            #instuction.setLabel( "1) " + control.lang(32159).encode('utf-8').format("[COLOR red]http://trakt.tv/pin/999[/COLOR]") + "\n2) " + control.lang(32160).encode('utf-8') + "\n3) " + control.lang(32161).encode('utf-8') + "\n\n" + control.lang(32162).encode('utf-8'))
            self.pin_edit_control.controlUp(never)
            self.pin_edit_control.controlLeft(never)
            self.pin_edit_control.controlDown(auth)
            self.pin_edit_control.controlRight(auth)
            auth.controlUp(self.pin_edit_control)
            auth.controlLeft(self.pin_edit_control)
            never.controlDown(self.pin_edit_control)
            never.controlRight(self.pin_edit_control)
            
        def onAction(self, action):
            if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
                self.close()

        def onControl(self, control2):
            pass

        def onFocus(self, control2):
            pass

        def onClick(self, control2):
            print 'onClick: %s' % (control2)
            if control2 == AUTH_BUTTON:
                if not self.__get_token():
                    control.infoDialog('Trakt PIN Authorization Failed.', 'Trakt ERROR')
                    return
                self.auth = True
                self.close()

            if control2 == LATER_BUTTON:
                control.infoDialog(control.lang(32157) + control.lang(32150))
                control.set_setting('last_reminder', str(int(time.time())))

            if control == NEVER_BUTTON:
                control.infoDialog(control.lang(32157) + control.lang(32151))
                control.set_setting('last_reminder', '-1')

            if control in [AUTH_BUTTON, LATER_BUTTON, NEVER_BUTTON]:
                self.close()
        
        def __get_token(self):
            pin = self.pin_edit_control.getText().strip()
            print("PIN",pin)
            if pin:
                try:
                    trakt_api = TraktAPI2(use_https=False, timeout=300)
                    result = trakt_api.get_token(pin=pin)
                    print("---",result)
                    control.set_setting('trakt_oauth_token', result['access_token'])
                    control.set_setting('trakt_refresh_token', result['refresh_token'])
                    TOKEN = result['access_token']
                    trakt_api = TraktAPI2(TOKEN, use_https=False, timeout=300)
                    profile = trakt_api.get_user_profile(cached=False)
                    print("Profile",profile)
                    print("Profile",profile['username'])
                    control.set_setting('trakt_user', profile['username'])
                    control.infoDialog('Trakt Authorization Success !', 'Trakt Success')

                    return True
                except Exception as e:
                    print('Trakt Authorization Failed: %s') % (e)
                    control.infoDialog('Trakt Authorization Failed: '+str(e), 'Trakt ERROR')
                    return False
            return False
        
        # have to add edit controls programatically because getControl() (hard) crashes XBMC on them
        def __add_editcontrol(self, x, y, height, width):
            media_path = os.path.join(control.addonPath, 'resources', 'skins', 'Default', 'media')
            temp = xbmcgui.ControlEdit(0, 0, 0, 0, '', font='font12', textColor='0xFFFFFFFF', focusTexture=os.path.join(media_path, 'button-focus2.png'),
                                       noFocusTexture=os.path.join(media_path, 'button-nofocus.png'), _alignment=CENTER_Y | CENTER_X)
            temp.setPosition(x, y)
            temp.setHeight(height)
            temp.setWidth(width)
            self.addControl(temp)
            return temp
    #dialog = PinAuthDialog(os.path.join(control.addonPath, 'resources', 'media', 'trakt', 'script-trakt-PinAuthDialog.xml'), control.addonPath)
    dialog = PinAuthDialog('TraktPinAuthDialog.xml',os.path.join(control.addonPath))
    dialog.doModal()
    if dialog.auth:
        control.infoDialog(control.lang(32157), control.lang(32152), 3000)
    del dialog
