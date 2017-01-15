# -*- coding: utf-8 -*-

import time, datetime
import re
import sys, traceback


#######################################
# Time and Date Helpers
#######################################

def timediff(mytime, unit='seconds'):
    dtNow = datetime.datetime.utcnow()
    datePart = mytime.split(' ')[0]
    dpArr = datePart.split('/')
    timePart = mytime.split(' ')[1]
    tpArr = timePart.split(':')
    d = datetime.date(int(dpArr[0]), int(dpArr[1]), int(dpArr[2]))
    t = datetime.time(int(tpArr[0]), int(tpArr[1]))
    dt = datetime.datetime.combine(d,t)

    diff = dtNow - dt

    if unit == 'seconds':
        return str(diff.seconds)
    elif unit == 'minutes':
        return str(diff.seconds/60)
    elif unit == 'sapo':
        #Math.floor(new Date().getTime()/1000)-Math.floor(new Date().getTime()/1000)-time
        #return str(1304805500 + diff.seconds*75)
        return time.time()
    else:
        return '0'


def convTimestamp(timestamp, newfrmt = '', offsetStr = ''):
    date = datetime.datetime.fromtimestamp(int(timestamp))
    
    if offsetStr:
        date = datetimeoffset(date, offsetStr)

    if newfrmt == '':
        if date.year != 1900:
            newfrmt = "%y/%m/%d"
        else:
            newfrmt = "%m/%d"

    return date.strftime(newfrmt)

    
def convDate(language, datestr, frmt, newfrmt = '', offsetStr = ''):
    ''''
    locale.setlocale(locale.LC_ALL, '')
    try:
        c = time.strptime(str(datestr).rstrip(),str(smart_unicode(frmt)).rstrip())
    except:
        xbmc.output('conversion failed')
        return datestr

    if c.tm_year != 1900:
        return time.strftime("%y/%m/%d",c)
    else:
        return time.strftime("%m/%d",c)
    '''

    try:
        datestr = datestr.encode('utf-8')
    except:
        datestr = datestr

    monthsEN = {
        'January':  1,
        'February': 2,
        'March':    3,
        'April':    4,
        'May':      5,
        'June':     6,
        'July':     7,
        'August':   8,
        'September':9,
        'October':  10,
        'November': 11,
        'December': 12
    }

    monthsDE = {
        'Januar':   1,
        'Februar':  2,
        u'März':    3,
        'Maerz':    3,
        'April':    4,
        'Mai':      5,
        'Juni':     6,
        'Juli':     7,
        'August':   8,
        'September':9,
        'Oktober':  10,
        'November': 11,
        'Dezember': 12
    }


    datesyms = {
        #DAY
        '%d':'\d{1,2}',
        '%a':'\w{3}',
        '%A':'[A-Za-z]{3,}',

        #MONTH
        '%m':'\d{2}',
        '%b':'\w{3}',
        '%B':'\w{3,}',

        #YEAR
        '%y':'\d{2}',
        '%Y':'\d{4}',

        #HOUR
        '%H':'\d{2}',
        '%I':'\d{1,2}',

        #AM/PM
        '%p':'\w{2}',
        '%P':'\w{2}',

        #MINUTE/SECOND
        '%M':'\d{2}',
        '%S':'\d{2}'
    }

    patFrmt = '(%\w)'
    idxFrmt = re.findall(patFrmt,frmt, re.DOTALL + re.IGNORECASE)

    try:
        for item in idxFrmt:
            if datesyms.has_key(item):
                frmt = frmt.replace(item,'(' + datesyms[item] + ')')

        p = re.compile(frmt, re.DOTALL + re.IGNORECASE)
        try:
            datestr = datestr.replace('ä','ae')  # ä
        except:
            datestr = datestr.replace(u'ä','ae')   # ä

        try:
            datestr = datestr.replace('\xe4','ae')
        except:
            pass

        m = p.match(datestr)
        if not m:
            return datestr

        second = 0
        minute = 0
        hour = 0
        dayhalf = ''
        day = 1
        month = 1
        year = 1900

        for item in m.groups(0):
            if not (idxFrmt[list(m.groups(0)).index(item)] is None):
                sym = idxFrmt[list(m.groups(0)).index(item)]
                if sym == '%B':
                    if monthsDE.has_key(item.capitalize()):
                        month = monthsDE[item.capitalize()]
                        continue
                    if monthsEN.has_key(item.capitalize()):
                        month = monthsEN[item.capitalize()]
                        continue
                elif sym == '%m':
                    month = int(item)
                elif sym == '%d':
                    day = int(item)
                elif sym == '%y' or sym == '%Y':
                    year = int(item)
                elif sym in ['%H','%I']:
                    hour = int(item)
                elif sym == '%M':
                    minute = int(item)
                elif sym == '%S':
                    second = int(item)
                elif sym == '%P':
                    dayhalf = str(item)

        if dayhalf != '' and dayhalf.lower() == 'pm' and hour < 12:
            hour = hour + 12
        if dayhalf != '' and dayhalf.lower() == 'am' and hour == 12:
            hour = 0
        date = datetime.datetime(year, month, day, hour, minute, second)

        if offsetStr:
            date = datetimeoffset(date, offsetStr)

        if newfrmt == '':
            if date.year != 1900:
                newfrmt = "%y/%m/%d"
            else:
                newfrmt = "%m/%d"

        return date.strftime(newfrmt)
    except:
        traceback.print_exc(file = sys.stdout)
        return datestr


def datetimeoffset(date, offsetStr):

    fak = 1
    if offsetStr[0] == '-':
        fak = -1
        offsetStr = offsetStr[1:]
    offsethours = int(offsetStr.split(':')[0])
    offsetminutes = int(offsetStr.split(':')[1])

    pageOffSeconds = fak*(offsethours * 3600 + offsetminutes *60)
    localOffSeconds = -1 * time.timezone
    offSeconds = localOffSeconds - pageOffSeconds

    offset=date + datetime.timedelta(seconds=offSeconds)

    return offset


def getUnixTimestamp():
    return int(time.time())


def utcToGmt(date):
    return date - datetime.timedelta(seconds = time.timezone)

def strToDatetime(dateStr, dformat):
    try:
        result = datetime.datetime.strptime(dateStr, dformat)
    except TypeError:
        result = datetime.datetime(*(time.strptime(dateStr, dformat)[0:6]))
    return result