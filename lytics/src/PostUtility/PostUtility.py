# PostUtility.py
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
from numpy import mean, std, percentile,log

class PostUtility(Controller):

    @Controller.logged
    def collectData(self):
        results = []
        for post in self.posts:
            if post.original == 1:
                continue
            numVotes = post.votes
            numWords = len(post)
            timeFromOriginal = post.post_time - self.timeMap[self.threadMap[post.id]]
            results.append((numVotes, numWords, log(float(timeFromOriginal))))
        return results

    def makeThreadMap(self):
        self.threadMap = {}
        for post in self.posts:
            self.threadMap[post.id] = post.thread_id
        self.timeMap = {}
        for thread in self.threads:
            self.timeMap[thread.id] = thread.posted_time

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
        self.posts = ForumPosts.objects.all()
        self.threads = ForumThreads.objects.all()
        self.makeThreadMap()
        results = self.collectData()

        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            for (votes,words,time) in results:
                fid.write(self.getCourseName() + ', ' \
                    + str(votes) + ', ' \
                    + str(words) + ', ' \
                    + str(time) + '\n')

if __name__ == '__main__':
    projectName = 'PostUtility'
    params = {'timeout': 10}
    controller = PostUtility(projectName, params)
    controller.handler()

