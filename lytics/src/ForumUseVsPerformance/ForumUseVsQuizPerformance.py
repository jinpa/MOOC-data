#! /usr/bin/env ipython

# ForumUseVsQuizPerformance.py
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
from Controller import Controller, CourseDBError, NoGradesError
from ForumUseVsEngagement import ForumUseVsEngagement
from ModelHelper import ModelHelper
from CourseStats import CourseStats
import logging
from operator import itemgetter
from numpy import mean,std,percentile
from scipy.stats import pearsonr,spearmanr

ACTIVITY_PERCENTILE_CAP = 95
TODAY = 1373846400
MINPOSTERS = 500
NUMSECSPERWEEK = 7*24*60*60

class ForumUseVsQuizPerformance(ForumUseVsEngagement):

    #def __init__(self, projectName, params):
    #   super(ForumUseVsEngagement, self).__init__(projectName,params)

    def pruneQuizzes(self):
        logging.info('ForumUseVsQuizPerformance.pruneQuizzes(), ' + self.currCourseName)
        markedForDeletion = []
        for quizId in self.quizzes:
            if 'std' not in self.quizzes[quizId]:
                markedForDeletion.append(quizId)
                continue
            if self.quizzes[quizId]['deadline'] > TODAY:
                markedForDeletion.append(quizId)
                continue
            if self.quizzes[quizId]['std'] == 0:
                markedForDeletion.append(quizId)
        for quizId in markedForDeletion:
            del self.quizzes[quizId]

    def getWeekForumActivity(self, quizId):
        logging.info('ForumUseVsQuizPerformance.getWeekForumActivity(), ' + self.currCourseName)
        forumActivityMap = {}
        forumOriginalPostMap = {}
        starttime = self.quizzes[quizId]['deadline'] - NUMSECSPERWEEK
        stoptime = self.quizzes[quizId]['deadline']
        for forumUserId in self.postMap:
            records = self.postMap[forumUserId]
            filteredRecords = [r for r in records \
                if r['timestamp'] >= starttime and r['timestamp'] < stoptime]
            forumActivityMap[forumUserId] = len(filteredRecords)
            forumOriginalPostMap[forumUserId] = len([r for r in filteredRecords if r['original'] == 1])

        return self.normalizeActivity(forumActivityMap), \
                self.normalizeActivity(forumOriginalPostMap)

    def computeAvgWeeklyActivity(self):
        timeStamps = sorted([p['post_time'] \
                for p in ForumPosts.objects.all().values('post_time')])
        # ignore ends
        numPosts = len(timeStamps[100:-100])
        numRegisteredStudents = len(Users.objects.filter(deleted = 0).values('anon_user_id'))
        numPostsPerHundredRegistered = 100.0 * float(numPosts) / numRegisteredStudents
        timeRangeSeconds = float(timeStamps[-100] - timeStamps[100]) 
        self.averageWeeklyActivity = numPostsPerHundredRegistered*NUMSECSPERWEEK/timeRangeSeconds

    # ratio of number of posts that week to average number of posts per week per 100 registered students
    def normalizeActivity(self, activityMap):
        sigma = self.averageWeeklyActivity
        normalizedActivityMap = {}
        for user in activityMap:
            normalizedActivityMap[user] = activityMap[user] / float(sigma)
        return normalizedActivityMap

    # take only last submission, and use z-score
    def getNormalizedQuizScoreMap(self, quizId):
        logging.info('ForumUseVsQuizPerformance.getNormalizedQuizScoreMap(), ' + self.currCourseName)
        scoreMap = {}
        for anonUserId in self.quizScoreMap:
            submissions = self.quizScoreMap[anonUserId]
            currSubmissions = [(s['score'], s['timestamp']) for s in submissions if s['item'] == quizId]
            # only include user if he submitted to current assignment
            if len(currSubmissions) == 0:
                continue
            bestScore = max(currSubmissions, key=itemgetter(1))[0]
            scoreMap[anonUserId] = self.zscore(bestScore, quizId)
        return scoreMap

    def write(self, fid, quizId, forumActivity, forumOriginalPosts, userScore):
        fid.write(str(quizId) + ', ' \
                + str(forumActivity)  + ', ' \
                + str(forumOriginalPosts) + ', ' \
                + str(userScore) + '\n')

    def computeForumVsQuizPerformance(self, quizId,path):
        logging.info('ForumUseVsQuizPerformance.computeForumVsQuizPerformance(), ' + self.currCourseName)
        forumActivityMap, forumOriginalPostMap = self.getWeekForumActivity(quizId)
        scoreMap = self.getNormalizedQuizScoreMap(quizId)
        with open(path,'at') as fid:
            for anonUserId in scoreMap:
                try:
                    forumUserId = self.anonForumIdMap[anonUserId]               
                except KeyError:
                    continue
                userScore = scoreMap[anonUserId]
                try:
                    forumActivity = forumActivityMap[forumUserId]
                    forumOriginalPosts = forumOriginalPostMap[forumUserId]
                except KeyError:
                    forumActivity = 0
                    forumOriginalPosts = 0
                self.write(fid, quizId, forumActivity, \
                        forumOriginalPosts, userScore)

    def loadResults(self, path):
        quizIds = []
        forumActivities = []
        forumOriginalPosts = []
        scores = []
        with open(path) as fid:
            rows = fid.readlines()
            for r in rows[1:]:
                tokens = r.rstrip().split(', ')
                quizIds.append(int(tokens[0]))
                forumActivities.append(float(tokens[1]))
                forumOriginalPosts.append(float(tokens[2]))
                scores.append(float(tokens[3]))
        return quizIds, forumActivities, forumOriginalPosts, scores

    def getCorrelations(self, inputPath, outputPath):
        (quizIds, forumActivities, forumOriginalPosts, scores) = self.loadResults(inputPath)
        if len(quizIds) > 0:
            rhoActivities, pValueActivities = spearmanr(forumActivities,scores)
            rhoOriginalPosts, pValueOriginalPosts = spearmanr(forumOriginalPosts,scores)
            corrActivities, corrpValueActivities = pearsonr(forumActivities,scores)
            corrOriginalPosts, corrpValueOriginalPosts = pearsonr(forumOriginalPosts,scores)
            with open(outputPath,'wt') as fid:
                fid.write('variable, Spearman rho, p_value, Pearson correlation, p_value\n')
                fid.write('ForumActivity, ' + str(rhoActivities) + ', ' \
                                        + str(pValueActivities) + ', ' \
                                        + str(corrActivities) + ', ' \
                                        + str(corrpValueActivities) + '\n')
                fid.write('OriginalPosts, ' + str(rhoOriginalPosts) + ', ' \
                                        + str(pValueOriginalPosts) + ', ' \
                                        + str(corrOriginalPosts) + ', ' \
                                        + str(corrpValueOriginalPosts))

    def basicStats(self, path):
        numRegistered = CourseStats.getNumRegisteredUsers()
        numContributors = CourseStats.getNumContributingUsers()
        numQuizSubmitters = CourseStats.getNumQuizSubmitters()    
        with open(path, 'wt') as fid:
            fid.write('# registered users, ' + str(numRegistered) + '\n')
            fid.write('# forum contributors, ' + str(numContributors) + '\n')
            fid.write('# quiz submitters, ' + str(numQuizSubmitters) + '\n')

    def runner(self):
        logging.info('ForumUseVsQuizPerformance.runner(), ' + self.currCourseName)
        path = os.path.join(self.getResultsDir(),'ForumActivityVsQuizScore.csv')
        pathStats = os.path.join(self.getResultsDir(),'CourseStats.csv')
        pathCorrelation = os.path.join(self.getResultsDir(),'ForumActivityVsQuizScore_regression.csv')
        try:
            print('Working on: ' + self.currCourseName + ' (' + self.progress() +')')
            self.anonForumIdMap = ModelHelper.getAnonForumIdMap()
            self.forumAnonIdMap = ModelHelper.getForumAnonIdMap()
            self.loadQuizInfo()
            self.computeQuizStats()
            self.pruneQuizzes()
            self.loadQuizScoreMap()
            self.loadForumPostMap()
            if len(self.postMap) < MINPOSTERS:
                logging.info('\t\t+ ERROR (Not enough forum activity, skipping...)')
                sys.exit()
            self.computeAvgWeeklyActivity()
            
            with open(path,'wt') as fid:
                fid.write('Quiz Id, ')
                fid.write('# Forum Posts week before deadline, ')
                fid.write('# Original posts week before deadline, ')
                fid.write('Quiz score (normalized)\n')
            for quizId, quizNum in zip(self.quizzes,range(len(self.quizzes))):
                logging.info(' + ForumUseVsQuizPerformance progress: (quiz ' \
                        + str(quizNum) + ' of ' + str(len(self.quizzes)) + ')')   
                self.computeForumVsQuizPerformance(quizId, path)
            self.getCorrelations(path, pathCorrelation)
            self.basicStats(pathStats)

        except CourseDBError:
            logging.info('\t\t+ ERROR (Connection does not exist), skipping...')
            pass
        except NoGradesError:
            logging.info('\t\t+ ERROR (CourseGrades does not exist), skipping...')
            pass

if __name__ == '__main__':
    projectName = 'ForumUseVsQuizPerformance'
    params = {'timeout': 600}
    controller = ForumUseVsQuizPerformance(projectName, params)
    controller.handler()




