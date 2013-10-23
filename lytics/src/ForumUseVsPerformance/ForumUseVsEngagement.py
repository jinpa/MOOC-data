#! /usr/bin/env ipython

# ForumUseVsEngagement.py
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
from ModelHelper import ModelHelper
import logging
from numpy import mean,std,percentile
from scipy.stats import linregress,spearmanr

ACTIVITY_PERCENTILE_CAP = 95

class ForumUseVsEngagement(Controller):

    def loadQuizInfo(self):
        logging.info('ForumUseVsEngagement.loadQuizInfo(), ' + self.currCourseName)
        try:
            quizItems = QuizMetadata.objects.all()
            numQuizItems = len(quizItems) 
        except:
            raise CourseDBError
        self.quizzes = {}
        for item in quizItems:
            if item.quiz_type != 'quiz' and item.quiz_type != 'homework' \
                    or item.deleted == 1 or item.parent_id != -1:
                continue
            self.quizzes[item.id] = {'deadline': item.hard_close_time, 'type': item.quiz_type}

    # call loadQuizInfo first
    def computeQuizStats(self):
        logging.info('ForumUseVsEngagement.computeQuizStats(), ' + self.currCourseName)
        try:
            quizSubmissions = QuizSubmissionMetadata.objects.exclude(raw_score__isnull = True).values( \
                            'item_id','raw_score')
        except:
            raise CourseDBError
        scores = {}
        for submission in quizSubmissions:    
            quizId = submission['item_id']
            if quizId in self.quizzes:
                try:
                    scores[quizId].append(submission['raw_score'])
                except KeyError:
                    scores[quizId] = [submission['raw_score']]
        for quizId in scores:
            meanScore = mean(scores[quizId])
            stdScore = std(scores[quizId])
            self.quizzes[quizId]['mean'] = meanScore
            self.quizzes[quizId]['std'] = stdScore

    def zscore(self,score,quizId):
        return (score - self.quizzes[quizId]['mean'])/self.quizzes[quizId]['std']

    def loadForumPostMap(self):
        logging.info('ForumUseVsEngagement.loadForumPostMap(), ' + self.currCourseName)
        # forum ask events, which forum?
        try:
            forumPosts = ForumPosts.objects.all()
            forumComments = ForumComments.objects.all()
        except:
            raise CourseDBError
        self.postMap = {}
        for post in forumPosts:
            record = {'timestamp': post.post_time,'original': post.original}
            try:
                self.postMap[post.forum_user_id].append(record)
            except KeyError:
                self.postMap[post.forum_user_id] = [record]
        for comment in forumComments:
            record = {'timestamp': comment.post_time, 'original': 0}
            try:
                self.postMap[comment.forum_user_id].append(record)
            except KeyError:
                self.postMap[comment.forum_user_id] = [record]

    def getForumActivity(self):
        logging.info('ForumUseVsEngagement.getForumActivity(), ' + self.currCourseName)
        self.overallForumActivityMap = {}
        for user in self.postMap:
            self.overallForumActivityMap[user] = len(self.postMap[user])

    # make sure to run getForumActivity first
    def normalizeForumActivity(self):
        logging.info('ForumUseVsEngagement.normalizeForumActivity(), ' + self.currCourseName)
        sigma = percentile(self.overallForumActivityMap.values(), ACTIVITY_PERCENTILE_CAP)
        self.normalizedActivityMap = {}
        for user in self.overallForumActivityMap:
            self.normalizedActivityMap[user] = self.overallForumActivityMap[user] / float(sigma)
    
    def loadQuizScoreMap(self):
        logging.info('ForumUseVsEngagement.getQuizScoreMap(), ' + self.currCourseName)
        try:
            quizScores = QuizSubmissionMetadata.objects.exclude(raw_score__isnull = True).values( \
                            'item_id','anon_user_id','submission_time','raw_score')
        except:
            raise CourseDBError
        self.quizScoreMap = {}
        for submission in quizScores:
            userId = submission['anon_user_id']
            submission = { \
                    'item': submission['item_id'], \
                    'timestamp': submission['submission_time'], \
                    'score': submission['raw_score'],
                    }
            try:
                self.quizScoreMap[userId].append(submission)
            except:
                self.quizScoreMap[userId] = [submission]

    def loadFinalScoreMap(self):
        logging.info('ForumUseVsEngagement.loadFinalScoreMap(), ' + self.currCourseName)
        try:
            grades = CourseGrades.objects.all().values('anon_user_id','normal_grade')
        except:
            raise CourseDBError  
        if len(grades) == 0:
            raise NoGradesError
        self.gradeMap = {}
        for user in grades:
            self.gradeMap[user['anon_user_id']] = float(user['normal_grade'])

    # call getFinalScoreMap first
    def computeFinalScoreStats(self):
        logging.info('ForumUseVsEngagement.computeFinalScoreStats(), ' + self.currCourseName)
        allNonzeroScores = [x for x in self.gradeMap.values() if x > 0]
        meanScore = mean(allNonzeroScores)
        stdScore = std(allNonzeroScores)
        self.finalScore = {'mean': meanScore, 'std': stdScore}

    def normalizeFinalScores(self):
        logging.info('ForumUseVsEngagement.normalizeFinalScores(), ' + self.currCourseName)
        self.normalizedGradeMap = {}    
        mu = self.finalScore['mean']
        sigma = self.finalScore['std']
        for user in self.gradeMap:
            self.normalizedGradeMap[user] = (self.gradeMap[user] - mu)/sigma

    def getNumLectures(self):
        logging.info('ForumUseVsEngagement.getNumLectures(), ' + self.currCourseName)
        lectures = LectureMetadata.objects.filter(deleted = 0).values('id')
        return len(lectures)

    def loadLecturesViewed(self):
        logging.info('ForumUseVsEngagement.getLecturesViewed(), ' + self.currCourseName)
        try:
            lectures = LectureSubmissionMetadata.objects.all().values('item_id','anon_user_id')
        except:
            raise CourseDBError
        self.lectureMap = {}
        for event in lectures:
            try:
                self.lectureMap[event['anon_user_id']].add(event['item_id'])
            except KeyError:
                self.lectureMap[event['anon_user_id']] = set([event['item_id']])

    def normalizeLectureMap(self):
        logging.info('ForumUseVsEngagement.normalizeLectureMap(), ' + self.currCourseName)
        numLectures = float(self.getNumLectures())
        self.normalizedLectureMap = {}
        for user in self.lectureMap:
            self.normalizedLectureMap[user] = float(len(self.lectureMap[user]))/numLectures

    def allForumVsFinalScore(self):
        logging.info('ForumUseVsEngagement.allForumVsFinalScore(), ' + self.currCourseName)
        forumActivities = []
        finalGrades = []
        
        for anonUserId in self.normalizedGradeMap:
            try:
                forumUserId = self.anonForumIdMap[anonUserId]
                rawGrade = self.gradeMap[anonUserId]
                finalGrade = self.normalizedGradeMap[anonUserId]
            except KeyError:
                continue
            try:
                forumActivity = self.normalizedActivityMap[forumUserId]
            except KeyError:
                forumActivity = 0    
            if rawGrade > 0:
                forumActivities.append(forumActivity)
                finalGrades.append(finalGrade)
        path = os.path.join(self.getResultsDir(),'allForumVsFinalScore.csv')
        with open(path,'wt') as fid:
            for (forumActivity,finalGrade) in zip(forumActivities, finalGrades):
                fid.write(str(forumActivity) + ', ' + str(finalGrade) + '\n')
        slope, intercept, rValue, pValue, stdErr = \
                    linregress(forumActivities,finalGrades)
        rho, pValueSpearman = spearmanr(forumActivities,finalGrades)
        path = os.path.join(self.getResultsDir(),'allForumVsFinalScore_regression.csv')
        with open(path,'wt') as fid:
            fid.write('slope, intercept, R^2, p_value, std_err, spearmansrho, p_value_spearman\n')
            fid.write(str(slope) + ', ' \
                    + str(intercept) + ', ' \
                    + str(rValue**2) + ', ' \
                    + str(pValue) + ', ' \
                    + str(stdErr) + ', ' \
                    + str(rho) + ', ' \
                    + str(pValueSpearman) + '\n')

    def allForumVsLecturesViewed(self):
        logging.info('ForumUseVsEngagement.allForumVsLecturesViewed(), ' + self.currCourseName)
        forumActivities = []
        lecturesViewed = []
        for anonUserId in self.normalizedLectureMap:
            try:
                forumUserId = self.anonForumIdMap[anonUserId]
                numLecturesViewed = self.normalizedLectureMap[anonUserId]
            except KeyError:
                continue
            try:
                forumActivity = self.normalizedActivityMap[forumUserId]
            except KeyError:
                forumActivity = 0
            if numLecturesViewed > 0:
                lecturesViewed.append(numLecturesViewed)
                forumActivities.append(forumActivity)
        path = os.path.join(self.getResultsDir(), 'allForumVsLecturesViewed.csv')
        with open(path,'wt') as fid:
            for (forumActivity, numViewed) in zip(forumActivities, lecturesViewed):
                fid.write(str(forumActivity) + ', ' + str(numViewed) + '\n')
        slope, intercept, rValue, pValue, stdErr = \
                    linregress(forumActivities,lecturesViewed)
        rho, pValueSpearman = spearmanr(forumActivities,lecturesViewed)
        path = os.path.join(self.getResultsDir(), 'allForumVsLecturesViewed_regression.csv')
        with open(path,'wt') as fid:
            fid.write('slope, intercept, R^2, p_value, std_err\n')
            fid.write(str(slope) + ', ' \
                    + str(intercept) + ', ' \
                    + str(rValue**2) + ', ' \
                    + str(pValue) + ', ' \
                    + str(stdErr) + ', ' \
                    + str(rho) + ', ' \
                    + str(pValueSpearman) + '\n')



    #def __init__(self, projectName, params):
    #   super(ForumUseVsEngagement, self).__init__(projectName,params)

    def runner(self):
        logging.info('ForumUseVsEngagement.runner(), ' + self.currCourseName)
        try:
            print('Working on: ' + self.currCourseName + ' (' + self.progress() +')')
            self.anonForumIdMap = ModelHelper.getAnonForumIdMap()
            self.forumAnonIdMap = ModelHelper.getForumAnonIdMap()
            self.loadQuizInfo()
            self.loadFinalScoreMap()
            self.loadForumPostMap()
            self.getForumActivity()
            self.normalizeForumActivity()
            self.computeFinalScoreStats()
            self.normalizeFinalScores()
            self.loadLecturesViewed()
            self.normalizeLectureMap()
            
            self.allForumVsFinalScore()
            self.allForumVsLecturesViewed()
        except CourseDBError:
            logging.info('\t\t+ ERROR (Connection does not exist), skipping...')
            pass
        except NoGradesError:
            logging.info('\t\t+ ERROR (CourseGrades does not exist), skipping...')
            pass


if __name__ == '__main__':
    projectName = 'ForumUseVsEngagement'
    params = {'timeout': 10}
    controller = ForumUseVsEngagement(projectName, params)
    controller.handler()




