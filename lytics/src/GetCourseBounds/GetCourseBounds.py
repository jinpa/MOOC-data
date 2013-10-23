# GetCourseBounds.py
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
import logging
from CourseStats import CourseStats
from numpy import mean, std, percentile
import datetime,time


hour = 3600
day = 24*hour
week = 7*day
year = 365*day
MAXNUMWEEKS = 20
nowish = 1379314800
PMTMidnightRef = nowish - 5*year

class GetCourseBounds(Controller):

    def roundToMidnight(self,timestamp):
        return int((timestamp - PMTMidnightRef)/day)*day + PMTMidnightRef

    def getDayOfTwentiethPost(self):
        return self.roundToMidnight(self.postTimes[20])

    def getBounds(self):
        weekMarks = [PMTMidnightRef + week*weekNum for weekNum in range(52*10)]
        twenty = self.getDayOfTwentiethPost()
        self.low = max([x for x in weekMarks if x <= twenty]) - 2*week
        self.high = self.low + MAXNUMWEEKS*week

    def binPosts(self):
        results = MAXNUMWEEKS*[0]
        for post in self.timestamps:
            if post >= self.low and post < self.high:
                bin = (post - self.low)/week
                results[bin] += 1
        return results

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        try:
            self.timestamps = sorted(x['submission_time'] \
                for x in QuizSubmissionMetadata.objects.all().values('submission_time'))
            self.postTimes = sorted([x['post_time'] \
                for x in ForumPosts.objects.all().values('post_time')])
            self.dueDates = [x.hard_close_time for x in QuizMetadata.objects.filter(\
                        hard_close_time__lt = nowish) if x.deleted == 0]
        except:
            raise CourseDBError
        self.getBounds()
        results = self.binPosts()
        bestWeek = percentile(results,80)
        inClass = [y for x,y in zip(results,range(len(results))) if x > .25*bestWeek]

        try:
            lastDueDate = max(self.dueDates)
            lastDueDateIdx = (lastDueDate-self.low)/week
        except:
            print('ERROR: ' + self.getCourseName())
            lastDueDateIdx = inClass[-1]
        startWeek = self.low + week*inClass[0]
        ##endWeek = self.low + week*(inClass[-1]+1)
        endWeek = self.low + week*(lastDueDateIdx + 1)
        durationInWeeks = inClass[-1] - inClass[0] + 1

        startStr = datetime.datetime.fromtimestamp(startWeek).strftime('%Y-%m-%d %H:%M:%S')
        endStr = datetime.datetime.fromtimestamp(endWeek).strftime('%Y-%m-%d %H:%M:%S')
        print('\tStart: ' + startStr)
        print('\tEnd: ' + endStr)
        print('\tDuration in weeks: ' + str(durationInWeeks))

        path = os.path.join(self.getMainResultsDir(),'results.csv')
        if self.getCourseName() == '':
            print('!!!!!!!!!!!!!!!!!!' + self.getCourse().dbName)
        with open(path,'at') as fid:
            fid.write(self.getCourseName() + ', ')
            fid.write(str(startWeek) + ', ')
            fid.write(str(endWeek) + ', ')
            fid.write(str(durationInWeeks) + ', ')
            for b in results:
                fid.write(str(b) + ', ')
            fid.write('\n')

if __name__ == '__main__':
    projectName = 'GetCourseBounds'
    params = {'timeout': 10}
    controller = GetCourseBounds(projectName, params)
    controller.handler()

