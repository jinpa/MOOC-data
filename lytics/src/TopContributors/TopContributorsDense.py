# TopContributorsDense.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from lyticssite.generalModels.models import *
from lyticssite.eventModels.models import *
from Controller import Controller
from DBErrors import *
from ModelHelper import ModelHelper
import logging
from CourseForums import CourseForums
from numpy import mean

class TopContributorsDense(Controller):

    # why are the lengths of sortedContributors and sortedByReputation different?
    def superPosterPostsPerWeek(self, sortedContributors,contributionsMap, \
                                        numWeeks, limit):
        invNumWeeks = 1.0/numWeeks
        superPosterCPW = []
        for forumUserId in sortedContributors[:(limit)]:
            contributionsPerWeek = contributionsMap[forumUserId]*invNumWeeks
            superPosterCPW.append(float(contributionsPerWeek))
        return mean(superPosterCPW)

    @Controller.logged
    def loadData(self):
        self.forumData = CourseForums()

    @Controller.logged
    def checkForDB(self):
        try:
            if ForumThreads.objects.count() < 30:
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
            #raise CourseDBError

        self.loadData()
        numWeeks = self.getCourse().numWeeks
        if numWeeks == None:
            logging.info('No duration meta-information for course, bailing. (' \
                + self.getCourseName() + ')')
            return

        sortedByContribution = self.forumData.sortForumUsersByContributions()

        numPercentileSplits = 100
        percentileInc = .01
        numTop = numPercentileSplits*[0]
        for i in range(numPercentileSplits):
            numTop[i] = int(percentileInc*(i+1)*len(sortedByContribution))

        self.forumData.getForumUserToNumContributions()
        contributionsMap = self.forumData.forumUserToNumContributionsMap
        topContributorsPPW = numPercentileSplits*[0.0]
        for i in range(numPercentileSplits):
            topContributorsPPW[i] = self.superPosterPostsPerWeek(sortedByContribution, \
                                              contributionsMap,numWeeks,numTop[i])

        summarizedResultsPath = os.path.join(self.getMainResultsDir(),'resultsDensePercentiles.csv')
        with open(summarizedResultsPath, 'at') as fid:
            fid.write(self.getCourseName() + ', ')
            for i in range(numPercentileSplits):
                fid.write(str(topContributorsPPW[i]))
                if i < numPercentileSplits-1:
                    fid.write(', ')
            fid.write('\n')

if __name__ == '__main__':
    projectName = 'TopContributors'
    params = {'timeout': 10}
    controller = TopContributorsDense(projectName, params)
    controller.handler()

