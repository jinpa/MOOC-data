# FetchInstructorPosts.py
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

JUSTORIGINAL = True

class FetchInstructorPosts(Controller):


    def getInstructorPosts(self):
        instructorPosts = []
        for post in self.posts:
            if post.forum_user_id == self.instructorForumId:
                otherPostIds = self.threadMap[post.thread_id]
                otherPosts = []
                for postId in otherPostIds:
                    otherPosts.append(self.textMap[postId])
                instructorPosts.append((post.id,post.thread_id, \
                    post.post_text, otherPosts,post.original))
        return instructorPosts

    def getInstructorGroup(self):
        groups = AccessGroups.objects.all()
        for g in groups:
            if g.forum_title == 'Instructor':
                return g.id

    def getInstructorForumIds(self):
        instructorId = self.getInstructorGroup()
        instructorAnonId = Users.objects.filter(access_group_id = instructorId, \
            deleted = 0).values('anon_user_id')
        self.instructorForumId = \
            self.users.getByAnon(instructorAnonId[0]['anon_user_id'])['forum']

    def createTextMap(self):
        self.textMap = {}
        for post in self.posts:
            self.textMap[post.id] = post.post_text

    def createThreadMap(self):
        self.threadMap = {}
        for post in self.posts:
            try:
                self.threadMap[post.thread_id].append(post.id)
            except KeyError:
                self.threadMap[post.thread_id] = [post.id]

    @Controller.logged
    def checkForDB(self):
        try:
            if ForumThreads.objects.count() < 100: 
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
            sys.exit()

        self.loadUserMap(ignoreErrors = True)
        self.posts = ForumPosts.objects.all()
        self.createThreadMap()
        self.createTextMap()
        self.getInstructorForumIds()
        instructorPosts = self.getInstructorPosts()
        #if len(instructorPosts) > 0:
            #self._setupCourseDirs()

        splitter = '--------------------------------------------\n'
        splitterSmall = '\n--------------\n'
        for (postId,threadId,text,otherPosts,original) in instructorPosts:
            path = os.path.join(self.getMainResultsDir(),\
                self.getCourseName() + '_' + str(threadId) + '_' + str(postId) + '.csv')
            if JUSTORIGINAL and original == 0:
                continue
            with open(path,'wt') as fid:
                fid.write(splitter)
                fid.write(splitter)
                fid.write(text.encode('utf-8','ignore') + '\n')
                fid.write(splitter)
                fid.write(splitter)
                if not JUSTORIGINAL:
                    for post in otherPosts:
                        fid.write(post.encode('utf-8','ignore'))
                        fid.write(splitterSmall)

if __name__ == '__main__':
    projectName = 'FetchInstructorPosts'
    params = {'timeout': 10}
    controller = FetchInstructorPosts(projectName, params)
    controller.handler()

