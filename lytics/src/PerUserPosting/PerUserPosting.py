# PerUserPosting.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from util.Controller import Controller
from util.CourseForums import CourseForums
import logging
from numpy import mean

SUPERPOSTERRATE = .05

class PerUserPosting(Controller):

    def getRankByReputationMap(self, sortedByReputation):
        rankByReputationMap = {}
        for forumUserId,idx in zip(sortedByReputation,range(len(sortedByReputation))):
            rankByReputationMap[forumUserId] = idx
        return rankByReputationMap

    def getAvgPostPositionMap(self, sortedByContribution):
        avgPostPositionMap = {}
        self.forumData.getForumUserToPostMap()
        self.forumData.getPostRankMap()
        for forumUserId in sortedByContribution:
            try:
                userPosts = self.forumData.forumUserToPostMap[forumUserId]
            except KeyError:
                avgPostPositionMap[forumUserId] = None
                continue
            avgPostPositionMap[forumUserId] = \
                    mean([float(self.forumData.postRankMap[post.id]) for post in userPosts])

        return avgPostPositionMap

    def getNumFirstPostsMap(self, sortedByContribution):
        numFirstPostsMap = {}
        self.forumData.getForumUserToPostMap()
        for forumUserId in sortedByContribution:
            numFirstPostsMap[forumUserId] = 0
            if forumUserId not in self.forumData.forumUserToPostMap:
                continue
            for post in self.forumData.forumUserToPostMap[forumUserId]:
                if post.original == 1:
                    numFirstPostsMap[forumUserId] += 1
        return numFirstPostsMap

    @Controller.logged
    def computePostingBehaviors(self):
        sortedByContribution = self.forumData.sortForumUsersByContributions()
        sortedByReputation = self.forumData.sortForumUsersByReputation()
        self.forumData.getForumUserToNumContributions()
        contributionsMap = self.forumData.forumUserToNumContributionsMap
        rankByReputationMap = self.getRankByReputationMap(sortedByReputation)
        avgPostPositionMap = self.getAvgPostPositionMap(sortedByContribution)
        numFirstPostsMap = self.getNumFirstPostsMap(sortedByContribution)

        self.posters = []
        for forumUserId,idx in zip(sortedByContribution,range(len(sortedByContribution))):
            try:
                user = self.users.getByForum(forumUserId)
            except KeyError:
                continue
            totalContributions = contributionsMap[forumUserId]
            contributionsPerWeek = float(contributionsMap[forumUserId])/self.numWeeks
            try:
                numPosts = len(self.forumData.forumUserToPostMap[forumUserId])
            except KeyError:
                numPosts = 0
            try:
                numComments = len(self.forumData.forumUserToCommentMap[forumUserId])
            except KeyError:
                numComments = 0
            numFirstPosts = numFirstPostsMap[forumUserId]
            rankByContributions = idx
            rankByReputation = rankByReputationMap[forumUserId]
            avgPostPosition = avgPostPositionMap[forumUserId]
            inTopFivePercentByContributions = int(rankByContributions/float(len(sortedByContribution)) <= SUPERPOSTERRATE)
            inTopFivePercentByReputation = int(rankByReputation/float(len(sortedByContribution)) <= SUPERPOSTERRATE)

            poster = {'userId': user['user'], \
                      'totalContributions': totalContributions, \
                      'numFirstPosts': numFirstPosts, \
                      'numPosts': numPosts, \
                      'numComments': numComments, \
                      'contributionsPerWeek': contributionsPerWeek, \
                      'avgPostPosition': avgPostPosition, \
                      'rankByContributions': rankByContributions, \
                      'rankByReputation': rankByReputation, \
                      'inTopFivePercentByContributions': inTopFivePercentByContributions, \
                      'inTopFivePercentByReputation': inTopFivePercentByReputation}
            self.posters.append(poster)


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
        self.numWeeks = self.getCourse().numWeeks
        if self.numWeeks == None:
            logging.info('No duration meta-information for course, bailing. (' \
                + self.getCourseName() + ')')
            return

        self.loadUserMap(ignoreErrors = True)
        self.computePostingBehaviors()


        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            for poster in self.posters:
                fid.write(self.getCourseName() + ', ' \
                            + str(poster['userId']) + ', ' \
                            + str(poster['totalContributions']) + ', ' \
                            + str(poster['numFirstPosts']) + ', ' \
                            + str(poster['numPosts']) + ', ' \
                            + str(poster['numComments']) + ', ' \
                            + str(poster['contributionsPerWeek']) + ', ' \
                            + str(poster['avgPostPosition']) + ', ' \
                            + str(poster['rankByContributions']) + ', ' \
                            + str(poster['rankByReputation']) + ', ' \
                            + str(poster['inTopFivePercentByContributions']) + ', ' \
                            + str(poster['inTopFivePercentByReputation']) + ', ' \
                            + '\n')



if __name__ == '__main__':
    projectName = 'PerUserPosting'
    params = {'timeout': 10}
    controller = PerUserPosting(projectName, params)
    controller.handler()


