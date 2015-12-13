# -*- coding: utf-8 -*-

class pLog:
  __DEBUG = 0
  __INFO = 1
  __WARN = 2
  __ERROR = 3

  def __init__(self, prefix = ''):
    self.logLevel = self.__INFO
    if prefix <> '':
      prefix = '-' + prefix
    self.prefix = prefix
  
  def setLevel(self, level):
    if level >= 0 and level <= 3:
      self.logLevel = level
  
  def info(self, message):
    self.log(message, self.__INFO)
  
  def debug(self, message):
    self.log(message, self.__DEBUG)
  
  def error(self, message):
    self.log(message, self.__ERROR)
    
  def warn(self, message):
    self.log(message, self.__WARN)
  
  def log(self, message, level):
    if self.logLevel <= level:
      print '[xbmcfilm.com %s %d] %s' %(self.prefix, level, message)
