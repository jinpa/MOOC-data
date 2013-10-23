# GetBoundaries.py
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

hour = 3600
day = 24*hour
year = 365*day
PMTMidnightRef = 1379314800 - 5*year

class GetBoundaries(Controller):
    
    def roundToMidnight(self,timestamp):
        return int((timestamp - PMTMidnightRef)/day)*day + PMTMidnightRef

    @Controller.logged
    def getCourseStart(self):
        return self.roundToMidnight(self.posts[20])

    @Controller.logged
    def getCourseEnd(self):
        return self.roundToMidnight(max(self.views[-1], self.posts[-1]))

    @Controller.logged
    def setThreshold(self):
        views25 = int(percentile(self.views,25))
        views75 = int(percentile(self.views,75))
        numHrsBetween = (views75-views25)/float(hour)
        viewsPerHour = len([x for x in self.views if x>views25 and x<=views75])/float(numHrsBetween)
        viewsPerDay = viewsPerHour * 24
        self.threshold = viewsPerDay/10.0

    def checkViews(self, left,right):
        numViews = len([x for x in self.views if x>= left and x < right])
        if numViews > self.threshold:
            return True
        else:
            return False

    def addDay(self, bounds, currDay):
        if len(bounds) == 0 or bounds[-1][-1] != currDay-day:
            bounds.append([currDay,currDay])
        else:
            bounds[-1][-1] = currDay
        return bounds

    @Controller.logged
    def computeBounds(self, start, finish):
        timestamp = start
        bounds = []
        dateChecks = []
        while timestamp < finish:
            dateChecks.append((timestamp,self.checkViews(timestamp,timestamp+day)))
            timestamp += day
        for prev,curr,next in zip(dateChecks[:-2],dateChecks[1:-1],dateChecks[2:]):
            if prev[1] and curr[1] and next[1]:
                bounds = self.addDay(bounds, curr[0])
        return bounds

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        try:
            self.posts = sorted([x['post_time'] \
                for x in ForumPosts.objects.all().values('post_time')])
            self.views = sorted([int(x['timestamp']/1000.0) \
                for x in ForumViewLog.objects.all().values('timestamp')])
        except:
            raise CourseDBError

        self.setThreshold()
        start = self.getCourseStart()
        finish = self.getCourseEnd()
        bounds = self.computeBounds(start, finish)

        path = os.path.join(self.getMainDataDir(),'viewBounds.csv')
        with open(path,'at') as fid:
            fid.write(self.getCourseName() + ', ')
            fid.write(str(start) + ', ' + str(finish) + ', ')
            for bound in bounds:
                fid.write(str(bound[0]) + ':' + str(bound[1]) + ', ')
            fid.write('\n')
                
if __name__ == '__main__':
    projectName = 'GetBoundaries'
    params = {'timeout': 10}
    controller = GetBoundaries(projectName, params)
    controller.handler()











