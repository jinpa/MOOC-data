#! /usr/bin/env ipython

# testController.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.classModels.models import *
from Controller import Controller


class TestController(Controller):

    def runner(self):
        logging.info('TestController.runner(), ' + self.currDB)
        forums = ForumForums.objects.all()
        for f in forums:
            print(f.name)

if __name__ == '__main__':
    projectName = 'TestController'
    params = {'timeout': 10}
    controller = TestController(projectName, params)
    controller.handler()



