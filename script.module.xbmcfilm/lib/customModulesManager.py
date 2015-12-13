# -*- coding: utf-8 -*-

import urllib
import os
import zipfile

from utils import xbmcUtils, fileUtils


class CustomModulesManager:
    
    def __init__(self, customModulesFolder, customModulesRepo):
        self._customModulesFolder = customModulesFolder
        
        if not os.path.exists(self._customModulesFolder):
            os.makedirs(self._customModulesFolder, 0777)
        
        self._customModulesRepo = customModulesRepo
        self._customModulesFile = os.path.join(self._customModulesFolder, 'custom.cfg')
        self.modules = []
            

    def getCustomModules(self):
        head = [\
            '########################################################',
            '#                    Custom Modules                    #',
            '########################################################',
            ''
            ]        
                
        txt = '\n'.join(head)
        
        self.modules = []
        for root, _, files in os.walk(self._customModulesFolder , topdown = False):
            for name in files:
                if name.endswith('.module'):
                    self.modules.append(name)
                    txt += fileUtils.getFileContent(os.path.join(root, name)) + '\n'
        fileUtils.setFileContent(self._customModulesFile, txt)



    def downloadCustomModules(self):
        
        def get_dir_listing(url):
            
            
            f = urllib.urlopen(url)
            response = f.read()
            f.close()
            
            text = response.split("\n")
            urls = []
            httptag = "http://"
            tag=' href="'
            for line in text:
                if tag in line.lower():
                    for i, _ in enumerate(line):
                        if tag == line[i:i+len(tag)].lower():
                            textline = line[i+len(tag):]
                            end = textline.find('"')
                            u = textline[:end]
                            if not httptag in u and not ".." in u and not "&#109;&#97;&#105;&#108;&#116;&#111;&#58;" in u and not "mailto:" in u:
                                if url[-1] != "/":
                                    u = url+"/"+u
                                else:
                                    u = url+u
                                if not "/." in u:
                                    urls.append(u)
        
            return urls
        
        
        def downloadFile(url, file_path):
            urllib.urlretrieve(url, file_path)
            return os.path.isfile(file_path)
        
        
        def extract(fileOrPath, directory):                
            if not directory.endswith(':') and not os.path.exists(directory):
                os.mkdir(directory)
        
            zf = zipfile.ZipFile(fileOrPath)
        
            for _, name in enumerate(zf.namelist()):
                if name.endswith('/'):
                    os.makedirs(os.path.join(directory, name), 0777)
                else:
                    outfile = open(os.path.join(directory, name), 'wb')
                    outfile.write(zf.read(name))
                    outfile.flush()
                    outfile.close()
                    
    
    
        repo_url = self._customModulesRepo
       
        xbmcUtils.showBusyAnimation()
        files = get_dir_listing(repo_url)
        menuItems = map(lambda x: x.replace(repo_url,'').replace('.zip',''), files)
        xbmcUtils.hideBusyAnimation()
        
        select = xbmcUtils.select('Select module', menuItems)
        if select:
            target = os.path.join(self._customModulesFolder, select + '.zip')
            
            xbmcUtils.showBusyAnimation()
            index = menuItems.index(select)
            success = downloadFile(files[index], target)
            xbmcUtils.hideBusyAnimation()
           
            if success:
                extract(target, self._customModulesFolder)
                os.remove(target)
                return True
            else:
                return False
            
        return None
    
    
    def removeCustomModule(self, moduleName):    
        try:
            customCfg = self._customModulesFile
            content = fileUtils.getFileContent(customCfg)
            lines = content.splitlines()
            
            startIdx = -1
            cfgUrl = ''
            for i in range(0, len(lines)):
                if lines[i].startswith("title=%s" % moduleName):
                    startIdx = i
                
                elif startIdx > -1 and lines[i].startswith("url="):
                    tmp = lines[i][4:]
                    cfgUrl = os.path.join(self._customModulesFolder, tmp)
                    break
                
            if os.path.isfile(cfgUrl):
                os.remove(cfgUrl)
                os.remove(cfgUrl.replace(".cfg", ".module"))
                
                # remove all folder that start with cfg name and a dot
                baseDir = os.path.dirname(cfgUrl)
                prefix = os.path.basename(cfgUrl).replace(".cfg", ".")
                dirs = fileUtils.get_immediate_subdirectories(baseDir)
                for d in dirs:
                    if d.startswith(prefix):
                        fileUtils.clearDirectory(os.path.join(baseDir, d))
                        os.removedirs(os.path.join(baseDir, d))

                return True
        except:
            pass
        
        return False    