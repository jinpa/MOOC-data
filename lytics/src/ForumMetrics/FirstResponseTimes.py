# FirstResponseTimes.py
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
from UserMap import UserMap
from numpy import mean, median, std, percentile

class ForumMetrics(Controller):

    @Controller.logged
    def timeToFirstResponse(self):
        results = {}
        for post in self.posts:
            if post.original == 1:
                continue
            try:
                results[post.thread_id] = min(post.post_time, results[post.thread_id])
            except KeyError:
                results[post.thread_id] = post.post_time
        for thread in self.threads:
            try:
                results[thread.id] -= thread.posted_time
                if results[thread.id] > 90*24*3600: # filter out response times longer than a month
                    results[thread.id] = float("inf")
            except KeyError:
                results[thread.id] = float("inf")
        #return [results[id] for id in results if results[id] != float("inf")]
        return results

    @Controller.logged
    def checkForDB(self):
        try:
            ForumViewLog.objects.count()
            self.viewsExists = True
        except:
            self.viewsExists = False
            pass
        try:
            if ForumThreads.objects.count() < 100:
                return False
            return True
        except:
            return False

    @Controller.logged
    def loadData(self):
        self.posts = ForumPosts.objects.all()
        self.threads = ForumThreads.objects.all()

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        if not self.checkForDB():
            logging.info('Necessary database does not exist, bailing. (' \
                + self.getCourseName() + ')')
            sys.exit()

        self.loadData()
        
        firstResponseTimes = self.timeToFirstResponse().values()

        path = os.path.join(self.getMainResultsDir(),'firstResponseTimes' \
                                + self.getCourseName() + '.csv')
        with open(path,'at') as fid:
            for t in firstResponseTimes:
                fid.write(str(t) + '\n')


if __name__ == '__main__':
    projectName = 'ForumMetrics'
    params = {'timeout': 10}
    controller = ForumMetrics(projectName, params)
    controller.handler()

