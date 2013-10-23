# PlotBoundaries.py
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
from DBErrors import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import logging
import numpy as np

hour = 3600
day = 24*hour
year = 365*day
PMTMidnightRef = 1379314800 - 5*year

class PlotBoundaries(object):

    def getHistList(self):
        bins = self.getBins()
        binSpacing = bins[1] - bins[0]
        hist = (len(bins)-1)*[0]
        for timestamp in self.views:
            xVal = timestamp
            if xVal < bins[0] or xVal>= bins[-1]:
                continue
            binIdx = int((xVal-bins[0])/float(binSpacing))
            hist[binIdx] +=1
        binCenters = [(x+y)/2 for x,y in zip(bins[1:],bins[:-1])]
        return (hist,binCenters,bins)

    def getBins(self):
        begin = self.viewBounds[self.courseName]['begin']
        finish = self.viewBounds[self.courseName]['end']
        numDays = (finish-begin)/day
        return [begin + day*x for x in range(numDays+1)]

    def plotHist(self, figId, path):
        plt.figure(figId)
        fig,y1 = plt.subplots()
        hist, binCenters, bins = self.getHistList()
        y1.bar(binCenters,hist,day)
        
        plt.xlim((bins[0],bins[-1]))
        intervals = self.viewBounds[self.courseName]['bounds']
        for interval in intervals:
            plt.hlines(5, interval[0], interval[1], color = 'r',linewidths = 10)
        plt.savefig(path)

    def loadViews(self):
        return [int(x['timestamp']/1000.0) for x in ForumViewLog.objects.all().values('timestamp')]

    def setup(self,projectName):
        self.resultsDir = FileSystem.createResultsDir(projectName)
        self.courseDatasets = FileSystem.loadCourseDatasetInfo()

    def run(self, projectName):
        self.viewBounds = FileSystem.loadViewBounds()
        self.setup(projectName)

        for courseId in range(len(self.courseDatasets)):
            self.courseName = self.courseDatasets[courseId].name
            print('Loading ' + self.courseName)
            DBSetup.switch(self.courseDatasets[courseId])
            try:
                self.views = self.loadViews()
                self.views[1000]
                self.viewBounds[self.courseName]
            except:
                continue
            path = os.path.join(self.resultsDir, self.courseName + '.png')
            self.plotHist(courseId, path)

if __name__ == '__main__':
    projectName = 'PlotBoundaries'
    PlotBoundaries().run(projectName)

