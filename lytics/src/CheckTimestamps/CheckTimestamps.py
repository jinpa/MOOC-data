# CheckTimestamps.py
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

class CheckTimestamps(Controller):

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        self.loadUserMap(ignoreErrors = True)
        
        try:
            posts = [x['post_time'] for x in ForumPosts.objects.all().values('post_time')]
            views = [x['timestamp'] for x in ForumViewLog.objects.all().values('timestamp')]  
        except:
            raise CourseDBError
        
        posts10 = int(percentile(posts,10))
        posts50 = int(percentile(posts,50))
        views10 = int(percentile(views,10)/1000)
        views50 = int(percentile(views,50)/1000)

        views25 = int(percentile(views,25))
        views75 = int(percentile(views,75))
        numHrsBetween = (views75-views25)/float(1000*3600)
        viewsPerHour = len([x for x in views if x>views25 and x<=views75])/float(numHrsBetween)

        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            fid.write(self.getCourseName() + '\n' \
                + str(posts10) + '\t' + str(posts50) + '\n' \
                + str(views10) + '\t' + str(views50) + '\n' \
                + str(viewsPerHour) + '\n\n')

        path = os.path.join(self.getMainResultsDir(), self.getCourseName() + '.csv')
        with open(path,'wt') as fid:
            for v in views:
                fid.write(str(v) + '\n')

if __name__ == '__main__':
    projectName = 'CheckTimestamps'
    params = {'timeout': 10}
    controller = CheckTimestamps(projectName, params)
    controller.handler()

