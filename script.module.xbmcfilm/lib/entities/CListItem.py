
import string


class CListItem(object):
    
    def __init__(self):
        self.infos = {}

    def __getitem__(self, key):
        return self.getInfo(key)

    def __setitem__(self, key, value):
        self.setInfo(key, value)

    def getInfo(self, key):
        if self.infos.has_key(key):
            return self.infos[key]
        return None

    def setInfo(self, key, value):
        self.infos[key] = value


    def merge(self, item):
        for key in item.infos.keys():
            if not self[key]:
                self[key] = item[key]

    def __str__(self):
        txt = ''
        for key in self.infos.keys():
            txt += str(string.ljust(key, 15)) + ':\t' + str(self[key]) + '\n'
        return txt
    



# STATIC FUNCTIONS

def create():
    return CListItem()
