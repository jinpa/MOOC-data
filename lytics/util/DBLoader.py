# DBLoader.py
# author = Jonathan Huang
import sys,os
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())

class DBLoader(object):
    
    @staticmethod
    def loadLoginInfo(path):
        loginInfo = {}
        with open(path) as f:
            for line in f:
                (key, val) = line.split()
                loginInfo[key] = val
        return loginInfo

    @staticmethod
    def load():
        dbNames = FileSystem.loadDBList()
        databases = {}
        databases['default'] = DBLoader.getDefaultDB()
        for dbName in dbNames:
            if 'activity_' == dbName[:9]:
                databases[dbName] = DBLoader.getEventDB(dbName)
            else:
                databases[dbName] = DBLoader.getCourseDataDB(dbName)
        return databases

    @staticmethod
    def getDefaultDB():
        path = FileSystem.getDefaultLoginPath()
        loginInfo = DBLoader.loadLoginInfo(path)
        loginInfo['NAME'] = 'lyticsdb'
        return loginInfo

    @staticmethod
    def getEventDB(dbName):
        path = FileSystem.getEventServerLoginPath()
        loginInfo = DBLoader.loadLoginInfo(path)
        loginInfo['NAME'] = dbName
        return loginInfo

    @staticmethod
    def getCourseDataDB(dbName):
        path = FileSystem.getDataServerLoginPath()
        loginInfo = DBLoader.loadLoginInfo(path)
        loginInfo['NAME'] = dbName
        return loginInfo

    

