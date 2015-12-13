# -*- coding: utf-8 -*-

import os
import datetime, time
import random
import hashlib
import codecs

#######################################
# File Helpers
#######################################
def fileExists(filename):
    return os.path.isfile(filename)


def getFileExtension(filename):
    ext_pos = filename.rfind('.')
    if ext_pos != -1:
        return filename[ext_pos+1:]
    else:
        return ''

def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]

def findInSubdirectory(filename, subdirectory=''):
    if subdirectory:
        path = subdirectory
    else:
        path = os.getcwd()
    for root, _, names in os.walk(path):
        if filename in names:
            return os.path.join(root, filename)
    raise 'File not found'


def cleanFilename(s):
    if not s:
        return ''
    badchars = '\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, '')
    return s;


def randomFilename(directory, chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', length = 8, prefix = '', suffix = '', attempts = 10000):
    for _ in range(attempts):
        filename = ''.join([random.choice(chars) for _ in range(length)])
        filename = prefix + filename + suffix
        if not os.path.exists(os.path.join(directory, filename)):
            return filename
    return None


def getFileContent(filename):
    try:
        f = codecs.open(filename,'r','utf-8')
        txt = f.read()
        f.close()
        return txt
    except:
        return ''

def setFileContent(filename, txt, createFolders=False):
    try:
        if createFolders:
            folderPath = os.path.dirname(filename)
            if not os.path.exists(folderPath):
                os.makedirs(folderPath, 0777)
        
        f = codecs.open(filename, 'w','utf-8')
        f.write(txt)
        f.close()
        return True
    except:
        return False

def appendFileContent(filename, txt):
    try:
        f = codecs.open(filename, 'a','utf-8')
        f.write(txt)
        f.close()
        return True
    except:
        return False

def md5(fileName, excludeLine="", includeLine=""):
    """Compute md5 hash of the specified file"""
    m = hashlib.md5()
    try:
        fd = codecs.open(fileName,"rb",'utf-8')
    except IOError:
        print "Unable to open the file in readmode:", fileName
        return
    content = fd.readlines()
    fd.close()
    for eachLine in content:
        if excludeLine and eachLine.startswith(excludeLine):
            continue
        m.update(eachLine)
    m.update(includeLine)
    return m.hexdigest()

def lastModifiedAt(path):
    return datetime.datetime.utcfromtimestamp(os.path.getmtime(path))

def setLastModifiedAt(path, date):
    try:
        stinfo = os.stat(path)
        atime = stinfo.st_atime
        mtime = int(time.mktime(date.timetuple()))
        os.utime(path, (atime, mtime))
        return True
    except:
        pass
    
    return False

def clearDirectory(path):
    try:
        for root, _, files in os.walk(path , topdown = False):
            for name in files:
                os.remove(os.path.join(root, name))
    except:
        return False
    
    return True


# http://akiscode.com/articles/sha-1directoryhash.shtml
# Copyright (c) 2009 Stephen Akiki
# MIT License (Means you can do whatever you want with this)
#  See http://www.opensource.org/licenses/mit-license.php
# Error Codes:
#   -1 -> Directory does not exist
#   -2 -> General error (see stack traceback)

def GetHashofDirs(directory, verbose=0):

    SHAhash = hashlib.sha1()
    if not os.path.exists (directory):
        return -1
      
    try:
        for root, _, files in os.walk(directory):
            for names in files:
                if verbose == 1:
                    print 'Hashing', names
                filepath = os.path.join(root,names)
                try:
                    f1 = codecs.open(filepath, 'rb','utf-8')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue
        
        while 1:
            # Read file in as little chunks
            buf = f1.read(4096)
            if not buf: 
                break
            SHAhash.update(hashlib.sha1(buf).hexdigest())
            f1.close()
        
    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2

    return SHAhash.hexdigest()