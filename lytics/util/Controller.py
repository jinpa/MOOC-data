# Controller.py
# author = Jonathan Huang

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from Course import Course
from UserMap import UserMap
import logging
from optparse import OptionParser
import subprocess
from functools import wraps
from DBErrors import *

usage = "usage: %prog [options] courseId"
parser = OptionParser(usage)
parser.add_option('-l','--run_locally', \
        action='store_true', dest='runLocally', default=False)
(options, args) = parser.parse_args()
if len(args) != 0 and len(args) != 1:
    parser.error("incorrect number of arguments")

class Controller(object):

    def __init__(self, projectName, params):
        self.projectName = projectName
        FileSystem.startLogger(self.projectName, 'log')
        self.courseDatasets = FileSystem.loadCourseDatasetInfo()
        self.numCourses = len(self.courseDatasets)
        self.dataDir = FileSystem.createDataDir(self.projectName)
        self.resultsDir = FileSystem.createResultsDir(self.projectName)
        self.workingDir = FileSystem.createWorkingDir(self.projectName)
        self.executable = sys.argv[0]
        self.params = params

    def _setupCourseDirs(self):
        self.currResultsDir = FileSystem.createDir(os.path.join(\
                                    self.resultsDir,self.getCourseName()))
        self.currDataDir = FileSystem.createDir(os.path.join(\
                                    self.dataDir,self.getCourseName()))
        self.currWorkingDir = FileSystem.createDir(os.path.join(\
                                    self.workingDir,self.getCourseName()))

    def getResultsDir(self):
        return self.currResultsDir

    def getDataDir(self):
        return self.currDataDir

    def getWorkingDir(self):
        return self.currWorkingDir

    def getMainResultsDir(self):
        return self.resultsDir

    def getMainDataDir(self):
        return self.dataDir

    def getHandle(self, courseId):
        return self.projectName + '_' + str(courseId)

    def getCourse(self):
        return self.courseDatasets[self.courseId]

    def getCourseName(self):
        return self.courseDatasets[self.courseId].name

    def loadUserMap(self, ignoreErrors = True):
        self.users = UserMap(ignoreErrors)

    def _submitJob(self, courseId):
        logging.info('Submitted job for project ' + self.projectName + \
                    ' with courseId ' + str(courseId) + '.')
        self.stdout = os.path.join(self.workingDir, self.getHandle(courseId) + '.out')
        self.stderr = os.path.join(self.workingDir, self.getHandle(courseId) + '.err')
        args = []
        args.append(str(courseId))
        script = "source /scratch/users/jhuang11/venv/lytics/bin/activate; cd %s;python %s %s" \
                % (os.getcwd(),self.executable," ".join(args))
        command = ('echo "%s" | qsub -l walltime=28800 -o %s -e %s ') % (script,self.stdout,self.stderr)
        if 'timeout' in self.params:
            timeout = self.params['timeout']
        else:
            timeout = 3600
        qsubRunner = subprocess.Popen(command, shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

    def runner(self):
        logging.info('Error. runner not implemented.')

    def progress(self):
        return str(self.courseId) + ' of ' + str(self.numCourses)

    @classmethod
    def logged(cls,func):
        """

        @param func:
        @return:
        """

        @wraps(func)
        def withLogging(self, *args, **kwargs):
            logging.info(func.__name__ + ', ' + self.getCourseName())
            result = func(self,*args, **kwargs)
            logging.info('Finished: ' + func.__name__ + ', ' + self.getCourseName())
            return result
        return withLogging

    @classmethod
    def dbErrorHandled(cls,func):
        @wraps(func)
        def withErrorHandling(self, *args, **kwargs):
            try:
                print('Working on: ' + self.getCourseName() \
                    + ' (' + self.progress() +')')
                #self.runner()
                return func(self,*args,**kwargs)
            except CourseDBError:
                logging.info('\t\t+ ERROR for ' + self.getCourseName() \
                        + ' (Connection does not exist), skipping...')
                pass
            except NoGradesError:
                logging.info('\t\t+ ERROR (CourseGrades does not exist), skipping...')
                pass
        return withErrorHandling

    def handler(self):
        if options.runLocally == True:
            try:
                self.courseId = int(args[0])
                runAll = False
            except (ValueError, IndexError):
                runAll = True
            if runAll == False:
                self.currCourse = self.getCourse()
                #self._setupCourseDirs()
                DBSetup.switch(self.currCourse)
                self.runner()
            else:
                for courseId in range(len(self.courseDatasets)):
                    self.courseId = courseId
                    self.currCourse = self.getCourse()
                    #self._setupCourseDirs()
                    DBSetup.switch(self.currCourse)
                    self.runner()
            sys.exit(0)
        try:
            int(args[0])
            argExists = True
        except (ValueError,IndexError):
            argExists = False
        if argExists:
            self.courseId = int(args[0])
            self.currCourse = self.getCourse()
            #self._setupCourseDirs()
            DBSetup.switch(self.currCourse)
            self.runner()
            sys.exit(0)
        else:
            for courseId in range(len(self.courseDatasets)):
                self._submitJob(courseId)

