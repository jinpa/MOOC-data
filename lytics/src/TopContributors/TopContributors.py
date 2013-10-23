# TopContributors.py
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
from lyticssite.eventModels.models import *
from Controller import Controller
from DBErrors import *
from ModelHelper import ModelHelper
import logging
from CourseForums import CourseForums
from numpy import mean

class TopContributors(Controller):

    # why are the lengths of sortedContributors and sortedByReputation different?
    def superPosterPostsPerWeek(self, sortedContributors,contributionsMap, \
                                        numWeeks, limit):
        invNumWeeks = 1.0/numWeeks
        superPosterCPW = []
        for forumUserId in sortedContributors[:(limit+1)]:
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
        sortedByReputation = self.forumData.sortForumUsersByReputation()

        numTop = 3*[0]
        numTop[0] = int(.01*len(sortedByContribution))
        numTop[1] = int(.05*len(sortedByContribution))
        numTop[2] = int(.10*len(sortedByContribution))

        self.forumData.getForumUserToNumContributions()
        contributionsMap = self.forumData.forumUserToNumContributionsMap
        topContributorsPPW = 3*[0.0]
        for i in range(3):
            topContributorsPPW[i] = self.superPosterPostsPerWeek(sortedByContribution, \
                                              contributionsMap,numWeeks,numTop[i])
        bestReputationPPW = 3*[0.0]
        for i in range(3):
            bestReputationPPW[i] = self.superPosterPostsPerWeek(sortedByReputation, \
                                              contributionsMap,numWeeks,numTop[i])


        sortedContributorsPath = os.path.join(self.getMainResultsDir(), \
                                              self.getCourseName() + '_contribution.csv')
        with open(sortedContributorsPath,'wt') as fid:
            for forumUserId in sortedByContribution:
                fid.write(str(forumUserId) + '\n')

        sortedReputationsPath =  os.path.join(self.getMainResultsDir(), \
                                              self.getCourseName() + '_reputations.csv')
        with open(sortedReputationsPath,'wt') as fid:
            for forumUserId in sortedByReputation:
                fid.write(str(forumUserId) + '\n')

        summarizedResultsPath = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(summarizedResultsPath, 'at') as fid:
            fid.write(self.getCourseName() + ', ' \
                + str(topContributorsPPW[0]) + ', ' \
                + str(topContributorsPPW[1]) + ', ' \
                + str(topContributorsPPW[2]) + ', ' \
                + str(bestReputationPPW[0]) + ', ' \
                + str(bestReputationPPW[1]) + ', ' \
                + str(bestReputationPPW[2]) + ', ' \
                + '\n')

if __name__ == '__main__':
    projectName = 'TopContributors'
    params = {'timeout': 10}
    controller = TopContributors(projectName, params)
    controller.handler()


