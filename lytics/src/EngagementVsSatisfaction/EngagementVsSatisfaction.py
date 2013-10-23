# EngagementVsSatisfaction.py
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
from numpy import mean, std, percentile, median

class EngagementVsSatisfaction(Controller):

    @Controller.logged
    def checkForDB(self):
        try:
            if ForumThreads.objects.count() < 100 \
                or Users.objects.count() < 100:
                return False
            return True
        except:
            return False

    def getNumThreadsOpenedMap(self):
        numThreadsOpenedMap = {}
        for userId in self.userToThreadMap:
            numThreadsOpenedMap[userId] = len(self.userToThreadMap[userId])
        return numThreadsOpenedMap

    def getFirstResponseTimeSetMap(self):
        firstResponseTimeSetMap = {}
        for userId in self.userToThreadMap:
            threads = self.userToThreadMap[userId]
            firstResponseTimeSetMap[userId] = [self.firstResponseTimeMap[thread.id] \
                    for thread in threads]
        return firstResponseTimeSetMap

    def getResponseVoteSetMap(self):
        responseVoteSetMap = {}
        for userId in self.userToThreadMap:
            threads = self.userToThreadMap[userId]
            responseVoteSetMap[userId] = []
            for thread in threads:
                
                posts = self.postMap[thread.id]
                postVoteSum = sum([post.votes \
                    for post in posts if post.original == 0 and post.deleted == 0])
                comments = self.commentMap[thread.id]
                commentVoteSum = sum([comment.votes \
                    for comment in comments if comment.deleted == 0])
                responseVoteSetMap[userId].append(float(postVoteSum + commentVoteSum))
        return responseVoteSetMap

    def getNumResponseSetMap(self):
        numResponseSetMap = {}
        for userId in self.userToThreadMap:
            threads = self.userToThreadMap[userId]
            numResponseSetMap[userId] = []
            for thread in threads:
                posts = self.postMap[thread.id]
                comments = self.commentMap[thread.id]
                numResponses = len([p for p in posts if p.deleted == 0]) - 1
                numComments = len([c for c in comments if c.deleted == 0])
                numResponseSetMap[userId].append(numResponses + numComments)
        return numResponseSetMap

    def getLectureSetMap(self):
        lectureSetMap = {}
        for userId in self.userToThreadMap:
            if userId in self.viewMap:
                lectureSetMap[userId] = list(set(self.viewMap[userId]))
            else:
                lectureSetMap[userId] = []
        return lectureSetMap
    
    def getQuizSetMap(self):
        quizSetMap = {}
        for userId in self.userToThreadMap:
            if userId in self.quizMap:
                quizSetMap[userId] = list(set(self.quizMap[userId]))
            else:
                quizSetMap[userId] = []
        return quizSetMap

    @Controller.logged
    def loadUserToThreadMap(self):
        self.userToThreadMap = {}
        for thread in self.threads:
            if thread.deleted == 1 or thread.is_spam == 1:
                continue
            try:
                user_id = self.users.getByForum(thread.forum_user_id)['user']
            except KeyError:
                continue
            try:
                self.userToThreadMap[user_id].append(thread)
            except KeyError:
                self.userToThreadMap[user_id] = [thread]

    @Controller.logged
    def loadPostToThreadIdMap(self):
        self.postToThreadIdMap = {}
        for post in self.posts:
            self.postToThreadIdMap[post.id] = post.thread_id

    @Controller.logged
    def loadPostMap(self):
        self.postMap = {}
        for post in self.posts:
            thread_id = post.thread_id
            try:
                self.postMap[thread_id].append(post)
            except KeyError:
                self.postMap[thread_id] = [post]

    @Controller.logged
    def loadFirstResponseTimeMap(self):
        self.firstResponseTimeMap = {}
        for thread in self.threads:
            posts = self.postMap[thread.id]
            postTimes = [p.post_time \
                for p in posts if p.original == 0 and p.deleted == 0]
            if len(postTimes) > 0:
                self.firstResponseTimeMap[thread.id] = min(postTimes) \
                    - thread.posted_time
            else:
                self.firstResponseTimeMap[thread.id] = float("inf")

    @Controller.logged
    def loadCommentMap(self):
        self.commentMap = {}
        for thread in self.threads:
            self.commentMap[thread.id] = []
        for comment in self.comments:
            thread_id = self.postToThreadIdMap[comment.post_id]
            self.commentMap[thread_id].append(comment)
    
    @Controller.logged
    def loadLectureViewMap(self):
        views = LectureSubmissionMetadata.objects.filter(action = 'view').values('item_id','anon_user_id')
        self.viewMap = {}
        lectureHits = {}
        for record in views:
            try:
                user_id = self.users.getByAnon(record['anon_user_id'])['user']
            except KeyError:
                continue
            try:
                self.viewMap[user_id].append(record['item_id'])
            except KeyError:
                self.viewMap[user_id] = [record['item_id']]
            try:    
                lectureHits[record['item_id']] += 1
            except KeyError:
                lectureHits[record['item_id']] = 1
        self.numLectures = len([x for x in lectureHits.values() if x>1000])

    @Controller.logged
    def loadQuizSubmissionMap(self):
        quizSubmissions = \
            QuizSubmissionMetadata.objects.all().values('item_id','anon_user_id')
        self.quizMap = {}
        for record in quizSubmissions:
            try:
                user_id = self.users.getByAnon(record['anon_user_id'])['user']
            except KeyError:
                continue
            try:
                self.quizMap[user_id].append(record['item_id'])
            except KeyError:
                self.quizMap[user_id] = [record['item_id']]

    def getNumQuizzes(self):
        quizSubmissions = \
            QuizSubmissionMetadata.objects.all().values('item_id')
        counts = {}
        for record in quizSubmissions:
            quiz_id = record['item_id']
            try:
                counts[quiz_id] += 1
            except KeyError:
                counts[quiz_id] = 1
        return len([v for v in counts.values() if v>100])

    @Controller.logged
    def loadData(self):
        self.posts = ForumPosts.objects.all()
        self.comments = ForumComments.objects.all()
        self.threads = ForumThreads.objects.all()
        self.loadUserMap(ignoreErrors = True)
        #assignments and lectures
        self.lectures = [l['id'] \
            for l in LectureMetadata.objects.filter(deleted = 0).values('id')]
       

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        if not self.checkForDB():
            logging.info('Necessary database does not exist, bailing. (' \
                + self.getCourseName() + ')')
            sys.exit()

        self.loadData()

        self.loadUserToThreadMap()
        self.loadPostToThreadIdMap()
        self.loadPostMap()
        self.loadFirstResponseTimeMap()
        self.loadCommentMap()
        self.loadLectureViewMap()
        self.loadQuizSubmissionMap()
        numQuizzes = self.getNumQuizzes()        

        numThreadsOpenedMap = self.getNumThreadsOpenedMap()
        firstResponseTimeSetMap = self.getFirstResponseTimeSetMap()
        responseVoteSetMap = self.getResponseVoteSetMap()
        numResponseSetMap = self.getNumResponseSetMap()
        lectureSetMap = self.getLectureSetMap()
        quizSetMap = self.getQuizSetMap()
        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            for user in self.userToThreadMap:
                numThreadsOpened = numThreadsOpenedMap[user]
                firstResponseTimeSet = firstResponseTimeSetMap[user]
                responseVoteSet = responseVoteSetMap[user]
                numResponseSet = numResponseSetMap[user]
                lectureSet = lectureSetMap[user]
                quizSet = quizSetMap[user]

                #including infinities
                medianFirstResponseTime = median(firstResponseTimeSet)  
                # excluding infinities            
                #avgFirstResponseTime = mean([x for x in firstResponseTimeSet \
                #                            if x != float('inf')])
                medianUpvotes = median(responseVoteSet)
                avgUpvotes = mean(responseVoteSet)
                # conditioned on having a response, median number of responses
                medianNumResponses = median(numResponseSet)
                avgNumResponses = mean(numResponseSet)
                numOpenThreads = numThreadsOpened - len([x for x in numResponseSet if x>0])
                fracOpenThreads = float(numOpenThreads) / float(numThreadsOpened)
                fracLectures = float(len(lectureSet)) / float(self.numLectures)
                fracQuizzes = float(len(quizSet)) / float(numQuizzes)

                fid.write(self.getCourseName() + ', ' \
                    + str(medianFirstResponseTime) + ', ' \
                    #+ str(avgFirstResponseTime) + ', ' \
                    + str(medianUpvotes) + ', ' \
                    + str(avgUpvotes) + ', ' \
                    + str(medianNumResponses) + ', ' \
                    + str(avgNumResponses) + ', ' \
                    + str(numOpenThreads) + ', ' \
                    + str(fracOpenThreads) + ', ' \
                    + str(fracLectures) + ', ' \
                    + str(fracQuizzes) + '\n')

if __name__ == '__main__':
    projectName = 'EngagementVsSatisfaction'
    params = {'timeout': 10}
    controller = EngagementVsSatisfaction(projectName, params)
    controller.handler()

