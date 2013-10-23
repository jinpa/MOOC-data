# FileSystem.py
# author = Jonathan Huang
import os
import logging

from Course import Course

ROOT_DIR_NAME = 'lytics'

class FileSystem(object):

    # assumes that the dir codeweb is unique in the project.
    @staticmethod
    def getRootDir():
        currentDir = os.path.dirname(os.path.realpath(__file__))
        while True:
            if currentDir == '':
                raise Exception('could not find ' + ROOT_DIR_NAME)
            rootDir, topDir = os.path.split(currentDir)
            if topDir == ROOT_DIR_NAME:
                return currentDir
            currentDir = rootDir

    @staticmethod
    def getSiteDir():
        return os.path.join(FileSystem.getRootDir(), 'lyticssite')

    @staticmethod
    def getDataDir():
        return os.path.join(FileSystem.getRootDir(), 'data')

    @staticmethod
    def getLogDir():
        return os.path.join(FileSystem.getRootDir(),'log')
    
    @staticmethod
    def getResultsDir():
        return os.path.join(FileSystem.getRootDir(),'results')
    
    @staticmethod
    def getBinDir():
        return os.path.join(FileSystem.getRootDir(),'bin')
    
    @staticmethod
    def getSrcDir():
        return os.path.join(FileSystem.getRootDir(),'src')
    
    @staticmethod
    def getWorkingDir():
        return os.path.join(FileSystem.getRootDir(),'working')

    @staticmethod
    def getCourseListPath():    
        #return os.path.join(FileSystem.getDataDir(),'db','courseList2013.txt')
        return os.path.join(FileSystem.getDataDir(),'db','fullCourseList.csv')

    @staticmethod
    def getForumListPath():
        return os.path.join(FileSystem.getDataDir(),'db','forumList2013.txt')

    @staticmethod
    def getForumTypesPath():
        return os.path.join(FileSystem.getDataDir(),'ForumTypes','types.dat')

    @staticmethod
    def getDBListPath():
        return os.path.join(FileSystem.getDataDir(),'db','dbList2013.txt')

    @staticmethod
    def getDBTypes():
        return ['anonymized_forum','anonymized_general','hash_mapping','unanonymizable']    

    @staticmethod
    def loadCourseList():
        path = FileSystem.getCourseListPath()
        with open(path) as fid:
            courseNames = [r.strip().split(', ')[0] for r in fid.readlines()]
        return courseNames

    @staticmethod
    def loadCourseDatasetInfo():
        courseDatasetInfo = []
        path = FileSystem.getCourseListPath()
        with open(path) as fid:
            rows = fid.readlines()
            for r in rows[1:]:
                row = r.strip().split(',')
                courseDatasetInfo.append(Course(*row))
        return courseDatasetInfo

    @staticmethod
    def loadForumList():
        path = FileSystem.getForumListPath()
        with open(path) as fid:
            forumNames = [r.strip() for r in fid.readlines()]
        return forumNames

    @staticmethod
    def loadForumTypes():
        path = FileSystem.getForumTypesPath()
        forumTypes = []
        with open(path) as fid:
            rows = fid.readlines()
            for r in rows:
                forumTypes.append(r.strip().split(';'))
        return forumTypes

    @staticmethod
    def loadDBList():
        path = FileSystem.getDBListPath()
        with open(path) as fid:
            forumNames = [r.strip() for r in fid.readlines()]
        return forumNames

    @staticmethod
    def loadViewBounds():
        path = os.path.join(FileSystem.getDataDir(), \
            'GetBoundaries','viewBounds.csv')
        viewBounds = {}
        with open(path) as fid:
            rows = fid.readlines()
            for r in rows:
                row = r.strip().rstrip(', ').split(', ')
                courseName = row[0]
                intervals = []
                for s in row[3:]:
                    intervals.append(tuple( \
                        [int(x) for x in s.split(':')]))
                bounds = {'begin': int(row[1]), \
                    'end': int(row[2]), \
                    'bounds': intervals}
                viewBounds[courseName] = bounds
        return viewBounds

    @staticmethod
    def createDataDir(dirName):
        dirName = os.path.join(FileSystem.getDataDir(), dirName)
        return FileSystem.createDir(dirName)

    @staticmethod
    def createLogDir(dirName):
        dirName = os.path.join(FileSystem.getLogDir(), dirName)
        return FileSystem.createDir(dirName)

    @staticmethod
    def createResultsDir(dirName):
        dirName = os.path.join(FileSystem.getResultsDir(), dirName)
        return FileSystem.createDir(dirName)

    @staticmethod
    def createSrcDir(dirName):
        dirName = os.path.join(FileSystem.getSrcDir(), dirName)
        return FileSystem.createDir(dirName)

    @staticmethod
    def createWorkingDir(dirName):
        dirName = os.path.join(FileSystem.getWorkingDir(), dirName)
        return FileSystem.createDir(dirName)

    @staticmethod
    def createDir(dirName):
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        return dirName

    @staticmethod
    def startLogger(logDir,logName):
        dirName = FileSystem.createDir(os.path.join(FileSystem.getLogDir(), \
                        logDir))
        path = os.path.join(dirName, logName)
        logging.basicConfig(filename = path, \
                    format = '%(asctime)s %(message)s', \
                    datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO)

    @staticmethod
    def getDefaultLoginPath():
        return os.path.join(FileSystem.getDataDir(),'db','UserInference.dat')

    @staticmethod
    def getDataServerLoginPath():
        return os.path.join(FileSystem.getDataDir(),'db','UserLytics.dat')

    @staticmethod
    def getEventServerLoginPath():
        return os.path.join(FileSystem.getDataDir(),'db','UserEvariste.dat')

