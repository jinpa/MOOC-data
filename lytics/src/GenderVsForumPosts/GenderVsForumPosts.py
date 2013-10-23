# GenderVsForumPosts.py
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

class GenderVsForumPosts(Controller):

    @Controller.logged
    def loadGenders(self):
        try:
            demoData = list(Demographic.objects.all().values('user_id','gender'))
        except:
            raise CourseDBError
        self.genderMap = {}
        for record in demoData:
            self.genderMap[record['user_id']] = record['gender']

    @Controller.logged
    def loadPosts(self):
        try:
            forumData = list(ForumPosts.objects.all().values('forum_user_id'))
        except:
            raise CourseDBError
        self.postMap = {}
        for record in forumData:
            try:
                user_id = self.users.getByForum(record['forum_user_id'])['user']
            except KeyError:
                continue
            try:
                self.postMap[user_id] += 1
            except KeyError:
                self.postMap[user_id] = 1

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        self.loadUserMap(ignoreErrors = True)
        
        self.loadGenders()
        self.loadPosts()
        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            for user in self.genderMap:
                gender = self.genderMap[user]
                if user in self.postMap:
                    numPosts = self.postMap[user]
                else:
                    numPosts = 0
                fid.write(self.getCourseName() + ', ' \
                            + str(gender) + ', ' + str(numPosts) + '\n')

if __name__ == '__main__':
    projectName = 'GenderVsForumPosts'
    params = {'timeout': 10}
    controller = GenderVsForumPosts(projectName, params)
    controller.handler()

