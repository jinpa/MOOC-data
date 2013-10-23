#! /usr/bin/env python

# StartProject.py
# author = Jonathan Huang



import os.path
import sys
sys.path.append('util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())

if len(sys.argv) == 2:
    projectName = sys.argv[1]
else:
    print('Usage: ./StartProject.py [projectname]')
    sys.exit()

dirName = FileSystem.createSrcDir(projectName)
path = os.path.join(dirName, projectName + '.py')

strImport = '\
import sys\n\
import os.path\n\
sys.path.append(\'../../util\')\n\
from FileSystem import FileSystem\n\
sys.path.append(FileSystem.getRootDir())\n\
sys.path.append(FileSystem.getSiteDir())\n\
from  DBSetup import DBSetup\n\
from lyticssite.forumModels.models import *\n\
from lyticssite.generalModels.models import *\n\
from lyticssite.hashMapModels.models import *\n\
from lyticssite.eventModels.models import *\n\
from Controller import Controller\n\
from DBErrors import *\n\
from ModelHelper import ModelHelper\n\
import logging\n\
from CourseStats import CourseStats\n\
from numpy import mean, std, percentile\n\n'

strClass = '\
class ' + projectName + '(Controller):\n\n\
    @Controller.logged\n\
    def getUsers(self):\n\
        try:\n\
            return Users.objects.count()\n\
        except:\n\
            raise CourseDBError\n\n\
    @Controller.logged\n\
    @Controller.dbErrorHandled\n\
    def runner(self):\n\
        self.loadUserMap(ignoreErrors = True)\n\
        numRegisteredUsers = self.getUsers()\n\
        path = os.path.join(self.getMainResultsDir(),\'results.csv\')\n\
        with open(path,\'at\') as fid:\n\
            fid.write(self.getCourseName() + \', \' \\\n\
                + str(numRegisteredUsers) + \'\\n\')\n\
\n'

strMain = '\
if __name__ == \'__main__\':\n\
    projectName = \'' + projectName + '\'\n\
    params = {\'timeout\': 10}\n\
    controller = ' + projectName + '(projectName, params)\n\
    controller.handler()\n\n'

with open(path,'wt') as fid:
    fid.write(strImport)
    fid.write(strClass)
    fid.write(strMain)


