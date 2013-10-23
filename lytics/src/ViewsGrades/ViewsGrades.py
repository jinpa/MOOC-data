# ViewsGrades.py
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
from lyticssite.hashMapModels.models import *
from lyticssite.eventModels.models import *
from Controller import Controller
from DBErrors import *
from ModelHelper import ModelHelper
import logging
from CourseStats import CourseStats
from numpy import mean, std, percentile

class ViewsGrades(Controller):

    @Controller.logged
    def getUsers(self):
        try:
            return Users.objects.count()
        except:
            raise CourseDBError

# course_id, user_id, grade, num_forum_thread_views
    @Controller.logged
    def getGrades(self):
        Grades = CourseGrades.objects.all()
        self.grademap={}
        for person in Grades:
            self.grademap[person.anon_user_id] = person.normal_grade

    @Controller.logged
    def getViews(self):
        Views = ForumViewLog.objects.all()
        self.viewmap={}
        for view in Views:
            try:
                anon_user_id = self.users.getByLog(view.log_user_id)['anon']
            except KeyError:
                continue
            try:
                self.viewmap[anon_user_id] += 1
            except:
                self.viewmap[anon_user_id] = 1

    @Controller.logged
    def checkForDB(self):
        try:
            if CourseGrades.objects.count() < 100 \
                or ForumViewLog.objects.count() < 100:
                return False
            return True
        except:
            return False

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        if not self.checkForDB():
            logging.info('Necessary database does not exist, bailing. (' \
                + self.getCourseName() + ')')
            return

        self.loadUserMap(ignoreErrors = True)
        numRegisteredUsers = self.getUsers()
        path = os.path.join(self.getMainResultsDir(),'results.csv')
        self.getGrades()
        self.getViews()
        with open(path,'at') as fid:
            #fid.write(self.getCourseName() + ', ' \
            #    + str(numRegisteredUsers) + '\n')
            for user in self.grademap:
                try:
                    myviews = self.viewmap[user]
                except:
                    myviews = 0
                fid.write(self.getCourseName() +', ' + str(user) + ', '+ str(self.grademap[user]) + ', '+ str(myviews) + '\n')


if __name__ == '__main__':
    projectName = 'ViewsGrades'
    params = {'timeout': 10}
    controller = ViewsGrades(projectName, params)
    controller.handler()

