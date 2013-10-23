#! /usr/bin/env ipython

# Sandbox.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from lyticssite.generalModels.models import *
from Controller import *
from ModelHelper import ModelHelper
import logging
from numpy import mean,std,percentile
from CourseStats import CourseStats


class Sandbox(Controller):

    @Controller.logged
    def runner(self):
        try:
            print('Working on: ' + self.getCourseName() \
                    + ' (' + self.progress() +')')
            self.anonForumIdMap = ModelHelper.getAnonForumIdMap()
            self.forumAnonIdMap = ModelHelper.getForumAnonIdMap()

            numRegisteredUsers = Users.objects.count()         
            
            path = os.path.join(self.getMainResultsDir(),'results.csv')
            with open(path,'at') as fid:
                fid.write(self.getCourseName() + ', ' + str(numRegisteredUsers) + '\n')   
        except CourseDBError:
                logging.info('\t\t+ ERROR (Connection does not exist), skipping...')
                pass
        except NoGradesError:
                logging.info('\t\t+ ERROR (CourseGrades does not exist), skipping...')
                pass

if __name__ == '__main__':
    projectName = 'Sandbox'
    params = {'timeout': 10}
    controller = Sandbox(projectName, params)
    controller.handler()




