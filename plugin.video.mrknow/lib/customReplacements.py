# -*- coding: utf-8 -*-
import os.path
import re
from string import lower


import common
import utils.fileUtils as fu
from utils.regexUtils import findall



class CustomReplacements(object):

    def __init__(self):

        self.simpleScheme = {'(@PLATFORM@)':    os.environ.get('OS'),
                             '(@CURRENT_URL@)': fu.getFileContent(os.path.join(common.Paths.cacheDir, 'lasturl')),
                             '(@LANGUAGE@)':    self.languageShortName(common.language)
                             }

        self.complexScheme = {  'import':     '(#*@IMPORT=([^@]+)@)',
                                'find':       '(#*@FIND\(.*?\)@)',
                                'catch':      '(#*@CATCH\([^\)]+\)@)'
                              }


    def languageShortName(self, longName):
        if str(longName).lower() == 'german':
            return 'de'
        else:
            return 'en'

    def regex(self, item):
        return self.complexScheme.get(item)

    def __replaceImports(self, pathToImports, data):
        while True:
            m_reg = findall(data, self.regex('import'))
            if len(m_reg) > 0:
                for idat in m_reg:
                    if idat[0].startswith('#'):
                        data = data.replace(idat[0],'')
                        continue
                    filename = idat[1]
                    pathImp = os.path.join(common.Paths.modulesDir, filename)
                    if not os.path.exists(pathImp):
                        pathImp = os.path.join(pathToImports, filename)
                        if not (os.path.exists(pathImp)):
                            common.log('Skipped Import: ' + filename)
                            continue
                    dataImp = fu.getFileContent(pathImp)
                    dataImp = dataImp.replace('\r\n','\n')
                    data = data.replace(idat[0], dataImp)
            else:
                break
        return data

    def __replaceParameters(self, data, params=[]):
        i=1
        for par in params:
            matches = findall(data,'(@PARAM' + str(i) + '@)')
            if matches:
                for m in matches:
                    ptemp = str(par).strip()
                    data = data.replace(m, ptemp)
            i = i + 1
        return data

    def __replaceFinders(self, data):
        m_reg = findall(data, self.regex('find'))
        if len(m_reg) > 0:
            for idat in m_reg:
                if idat.startswith('#'):
                    continue
                ps = idat[6:-2].strip().split(',')
                method = ps[0].strip("'")
                param1 = ps[1].strip("'")
                param2 = ps[2].strip("'")
                param3 = ps[3].strip("'")

                if method == 'JS1':
                    jsName = param1
                    idName = param2
                    varName = param3
                    regex = "(?:java)?scr(?:'\+')?ipt[^<]+" + idName + "\s*=\s*[\"']([^\"']+)[\"'][^<]*</scr(?:'\+')?ipt\s*>[^<]*<scr(?:'\+')?ipt[^<]*src=[\"']" + jsName + "[\"']"
                    lines = "item_infos=" + regex + "\nitem_order=" + varName
                    data = data.replace(idat, lines)
        return data

    def __replaceCatchers(self, data):
        m_reg = findall(data, self.regex('catch'))
        if not (m_reg is None or len(m_reg) == 0):
            for idat in m_reg:
                if idat.startswith('#'):
                    continue
                ps = idat[7:-2].strip().split(',')
                catcherName = ps.pop(0).strip()

                # import catcher file and insert parameters
                pathImp = os.path.join(common.Paths.catchersDir, catcherName + '.txt')
                if not (os.path.exists(pathImp)):
                    common.log('Skipped Catcher: ' + catcherName)
                    continue
                dataImp = fu.getFileContent(pathImp)
                for i in range(len(ps)):
                    dataImp = dataImp.replace('@PARAM' + str(i+1) + '@',ps.pop(i).strip())

                dataImp = dataImp.replace('\r\n','\n')
                dataImp += "\nitem_info_name=type\nitem_info_build=video\nitem_url_build=%s"
                data = data.replace(idat, dataImp)
        return data

    def __replaceSimpleVars(self, data):
        for s in self.simpleScheme:
            m_reg = findall(data, s)
            value = self.simpleScheme.get(s)
            for idat in m_reg:
                data = data.replace(idat, value)
        return data

    def __replaceConditions(self, data):
        starts = [match.start() for match in re.finditer(re.escape('@IF('), data)]
        for j in range(len(starts)-1,-1,-1):
            s = starts[j]
            p_reg = re.compile('((@IF\((.+?)\)@).*?(@ENDIF@))', re.IGNORECASE + re.DOTALL + re.MULTILINE)
            m_reg = p_reg.findall(data[s:])
            if len(m_reg) > 0:
                for m in m_reg:
                    new_reg=p_reg.match(m[0])
                    condStr = new_reg.group(3)
                    hidePassage=False
                    if condStr.find('==') != -1:
                        condArr=condStr.split('==')
                        hidePassage = condArr[0].strip().lower() != condArr[1].strip().lower()
                    elif condStr.find('!=') != -1:
                        condArr=condStr.split('!=')
                        hidePassage = condArr[0].strip().lower() == condArr[1].strip().lower()

                    if hidePassage:
                        data = data.replace(str(new_reg.group(1)),'')
                    else:
                        tmpdata = str(new_reg.group(1))
                        tmpdata = tmpdata.replace(str(new_reg.group(2)),'',1)
                        tmpdata = tmpdata[:-len(str(new_reg.group(4)))]
                        data = data.replace(str(new_reg.group(1)),tmpdata)
        return data




    def replace(self, pathToImports, data, lItem, params=[]):
        data = self.__replaceParameters(data, params)
        data = self.__replaceConditions(data)
        data = self.__replaceImports(pathToImports, data)
        data = self.__replaceParameters(data, params)
        data = self.__replaceFinders(data)
        data = self.__replaceCatchers(data)
        data = self.__replaceSimpleVars(data)
        data = self.__replaceConditions(data)
        return data
