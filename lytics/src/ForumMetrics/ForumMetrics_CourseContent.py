# ForumMetrics_CourseContent.py
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
from CourseStats import CourseStats
from UserMap import UserMap
from numpy import mean, median

class ForumMetrics_CourseContent(Controller):

    self.FORUMTYPE = 'content'

    @Controller.logged
    def loadActives(self):
        # return a list of users who got > 5% of max final grade
        threshold = 5
        activeAnonId = CourseStats.getKPercenters(threshold)
        self.activesByAnon = {}
        for id in activeAnonId:
            try:
                self.activesByAnon[id] = self.users.getByAnon(id)
            except KeyError:
                pass

    @Controller.logged
    def loadLectureActives(self):
        threshold = 5
        lectureActiveAnonId = CourseStats.getLectureViewers(threshold)
        self.lectureActivesByAnon = {}
        for id in lectureActiveAnonId:
            try:
                self.lectureActivesByAnon[id] = self.users.getByAnon(id)
            except KeyError:
                pass


    @Controller.logged
    def loadContributions(self):
        postsByUser = []
        commentsByUser = []
        for x in self.posts:
            try:
                postsByUser.append(self.users.getByForum(x.forum_user_id))
            except KeyError:
                pass
        for x in self.comments:
            try:
                commentsByUse r.append(self.users.getByForum(x.forum_user_id))
            except KeyError:
                pass
        self.contributionsByUser = postsByUser + commentsByUser

    @Controller.logged
    def contributionByActives(self):
        # return percentage of forum contributions done by actives
        # get posts
        count = 0
        for user in self.contributionsByUser:
            if user['anon'] in self.activesByAnon:
                count += 1
        return float(count) / float(len(self.contributionsByUser))

    @Controller.logged
    def contributionByLectureActives(self):
        count = 0
        for user in self.contributionsByUser:
            if user['anon'] in self.lectureActivesByAnon:
                count += 1
        return float(count) / float(len(self.contributionsByUser))

    @Controller.logged
    def viewingByActives(self):
        #number of actives who view
        if not self.viewsExists:
            return None
        viewers = {}
        for view in self.views:
            viewers[view.log_user_id] = 1
        count = 0
        for anonId in self.activesByAnon:
            logUserId = self.users.getByAnon(anonId)['log']
            if logUserId in viewers:
                count += 1
        return float(count) / float(len(self.activesByAnon))

    @Controller.logged
    def subscriptionsByActives(self):
        return float(CourseStats.getNumSubscriptions() \
            - CourseStats.getNumContributingUsers()) / float(len(self.activesByAnon))

    @Controller.logged
    def subscriptionsByLectureActives(self):
        return float(CourseStats.getNumSubscriptions() \
            - CourseStats.getNumContributingUsers()) / float(len(self.lectureActivesByAnon))

    @Controller.logged
    def numThreadsPerActive(self):
        return float(CourseStats.getNumThreads()) / float(len(self.activesByAnon))

    @Controller.logged
    def numThreadsPerLectureActive(self):
        return float(CourseStats.getNumThreads()) / float(len(self.lectureActivesByAnon))

    @Controller.logged
    def numContributionsPerActive(self):
        return float(CourseStats.getNumContributions()) / float(len(self.activesByAnon))
    
    @Controller.logged
    def numContributionsPerLectureActive(self):
        return float(CourseStats.getNumContributions()) / float(len(self.lectureActivesByAnon))
    
    @Controller.logged
    def numViewsPerHourPerActive(self):
        if not self.viewsExists:
            return None
        #return float(CourseStats.getNumForumViews()) / float(len(self.activesByAnon))
        numHours = 0.0
        numViews = 0.0
        day = 24*3600.0
        for interval in self.viewBounds['bounds']:
            numHours += (interval[1] + 2*day - interval[0])/3600.0
            numViews += CourseStats.getNumForumViewsInInterval([interval[0]-day,interval[1]+day])
        return (numViews/numHours) / float(len(self.activesByAnon))

    @Controller.logged
    def numViewsPerHourPerLectureActive(self):
        if not self.viewsExists:
            return None
        numHours = 0.0
        numViews = 0.0
        day = 24*3600.0
        for interval in self.viewBounds['bounds']:
            numHours += (interval[1] + 2*day - interval[0])/3600.0
            numViews += CourseStats.getNumForumViewsInInterval([interval[0]-day,interval[1]+day])
        return (numViews/numHours) / float(len(self.lectureActivesByAnon))

    @Controller.logged
    def viewContributionRatio(self):
        if not self.viewsExists:
            return None
        return float(CourseStats.getNumForumViews())/float(CourseStats.getNumContributions())

    @Controller.logged
    def timeToFirstResponse(self):
        results = {}
        for post in self.posts:
            if post.original == 1:
                continue
            try:
                results[post.thread_id] = min(post.post_time, results[post.thread_id])
            except KeyError:
                results[post.thread_id] = post.post_time
        for thread in self.threads:
            try:
                results[thread.id] -= thread.posted_time
                if results[thread.id] > 90*24*3600: # filter out response times longer than a month
                    results[thread.id] = float("inf")
            except KeyError:
                results[thread.id] = float("inf")
        #return [results[id] for id in results if results[id] != float("inf")]
        return results

    @Controller.logged
    def timeBetweenPosts(self):
        times = {}
        commentTimes = {}
        for comment in self.comments:
            try:
                commentTimes[comment.post_id].append(comment.post_time)
            except KeyError:
                commentTimes[comment.post_id] = [comment.post_time]
        for post in self.posts:
            postTimes = [post.post_time]
            if post.id in commentTimes:
                postTimes += commentTimes[post.id]
            try:
                times[post.thread_id] += postTimes
            except KeyError:
                times[post.thread_id] = postTimes
        betweenTime = []
        thresh = 30*24*3600
        for threadId in times:
            sortedTimes = sorted(times[threadId])
            if len(sortedTimes) >=2:
                betweenTime += [x-y for x,y \
                    in zip(sortedTimes[1:],sortedTimes[:-1]) if x-y<= thresh]
        return betweenTime

    @Controller.logged
    def avgPostLen(self):
        wordCount = []
        for post in self.posts:
            string = Text(post.post_text)
            wordCount.append(string.getNumTokens())
        return mean(wordCount)

    @Controller.logged
    def avgContributionsPerThread(self):
        return float(len(self.contributionsByUser))/float(CourseStats.getNumThreads())

    @Controller.logged
    def numInstructorPosts(self):
        count = 0
        for c in self.contributionsByUser:
            if c['forum'] == self.instructorForumId:
                count += 1
        return count

    @Controller.logged
    def avgInstructorPostLen(self):
        wordCount = []
        for post in self.posts:
            if post.forum_user_id == self.instructorForumId:
                string = Text(post.post_text)
                wordCount.append(string.getNumTokens())
        if len(wordCount) == 0:
            wordCount = [0.0]
        return mean(wordCount)

    def checkViewBounds(self, timestamp):
        for interval in self.viewBounds['bounds']:
            if timestamp >= interval[0] and timestamp < interval[1]:
                return True
        return False

    @Controller.logged
    def avgInstructorBoost(self):
        instructorPostTimes = self.getInstructorPostTimes()
        if len(instructorPostTimes) == 0:
            return (None, None, None, None)
        postsBefore = []
        postsAfter = []
        viewsBefore = []
        viewsAfter = []
        onThreadBefore = []
        onThreadAfter = []
        onThreadViewsBefore = []
        onThreadViewsAfter = []
        hourInSecs = 3600
        numBeforeHours = 24
        numAfterHours = 24
        for thread, t in instructorPostTimes:
            count = ForumPosts.objects.filter(post_time__gte = t-numBeforeHours*hourInSecs, \
                        post_time__lt = t).exclude(thread_id = thread).count() \
                + ForumComments.objects.filter(post_time__gte = t-numBeforeHours*hourInSecs, \
                        post_time__lt = t).exclude(post__thread_id = thread).count()
            postsBefore.append(float(count)/float(numBeforeHours))
            count = ForumPosts.objects.filter(post_time__gt = t, \
                        post_time__lte = t+numAfterHours*hourInSecs).exclude(thread_id = thread).count() \
                + ForumComments.objects.filter(post_time__gt = t, \
                        post_time__lte = t+numAfterHours*hourInSecs).exclude(post__thread_id = thread).count()
            postsAfter.append(float(count)/float(numAfterHours))
            
            count = ForumPosts.objects.filter(post_time__gte = t-numBeforeHours*hourInSecs, \
                        post_time__lt = t, thread_id = thread).count() \
                + ForumComments.objects.filter(post_time__gte = t-numBeforeHours*hourInSecs, \
                        post_time__lt = t, post__thread_id = thread).count()
            onThreadBefore.append(float(count)/float(numBeforeHours))
            count = ForumPosts.objects.filter(post_time__gt = t, \
                        post_time__lte = t+numAfterHours*hourInSecs, thread_id = thread).count() \
                + ForumComments.objects.filter(post_time__gt = t, \
                        post_time__lte = t+numAfterHours*hourInSecs, post__thread_id = thread).count()
            onThreadAfter.append(float(count)/float(numAfterHours))

            if self.viewsExists and self.checkViewBounds(t):
                count = ForumViewLog.objects.filter(timestamp__gte = 1000*(t-numBeforeHours*hourInSecs), \
                        timestamp__lt = 1000*t).count()
                viewsBefore.append(float(count)/float(numBeforeHours))
                if count == 0:
                    print( ' -- ' + self.getCourseName() + ' ' + str(thread) + ' ' + str(t))
                count = ForumViewLog.objects.filter(timestamp__gt = 1000*t, \
                        timestamp__lte = 1000*(t+numAfterHours*hourInSecs)).count() 
                viewsAfter.append(float(count)/float(numAfterHours))

                count = ForumViewLog.objects.filter(timestamp__gte = 1000*(t-numBeforeHours*hourInSecs), \
                        timestamp__lt = 1000*t, thread_id = thread).count()
                onThreadViewsBefore.append(float(count)/float(numBeforeHours))
                count = ForumViewLog.objects.filter(timestamp__gt = 1000*t, \
                        timestamp__lte = 1000*(t+numAfterHours*hourInSecs), thread_id = thread).count() 
                onThreadViewsAfter.append(float(count)/float(numAfterHours))

        postBoost = sum(postsAfter) / sum(postsBefore)
        try:
            onThreadPostBoost = sum(onThreadAfter) / sum(onThreadBefore)
        except ZeroDivisionError:
            print('ERROR: '+ self.getCourseName())
            onThreadPostBoost = None
            pass
        if self.viewsExists:
            #print(' + ' + str(viewsBefore) + ' ' + str(len(instructorPostTimes)))
            try:
                viewBoost = sum(viewsAfter) / sum(viewsBefore)
            except ZeroDivisionError:
                print('ERROR: '+ self.getCourseName())
                #raise ZeroDivisionError
                viewBoost = None
                pass
            try:
                onThreadViewBoost = sum(onThreadViewsAfter) / sum(onThreadViewsBefore)
            except ZeroDivisionError:
                print('ERROR: '+ self.getCourseName())
                onThreadViewBoost = None
                pass
        else:
            viewBoost = None
            onThreadViewBoost = None
        # now postBoost and viewBoost are really "off-thread" boosts
        return postBoost, viewBoost, onThreadPostBoost, onThreadViewBoost

    def getInstructorPostTimes(self):
        times = []
        for post in self.posts:
            if post.forum_user_id == self.instructorForumId:
                times.append((post.thread_id, post.post_time))
        return times

    def getInstructorGroup(self):
        groups = AccessGroups.objects.all()
        for g in groups:
            if g.forum_title == 'Instructor':
                return g.id

    def getInstructorForumIds(self):
        instructorId = self.getInstructorGroup()
        instructorAnonId = Users.objects.filter(access_group_id = instructorId, \
            deleted = 0).values('anon_user_id')
        self.instructorForumId = \
            self.users.getByAnon(instructorAnonId[0]['anon_user_id'])['forum']

    @Controller.logged
    def avgReputation(self):
        reputationList = [float(x.points) for x in self.reputations]
        return mean(reputationList)

    @Controller.logged
    def checkForDB(self):
        try:
            ForumViewLog.objects.count()
            allViewBounds = FileSystem.loadViewBounds()
            self.viewBounds = allViewBounds[self.getCourseName()]
            self.viewBounds['bounds'][0]
            self.viewsExists = True
        except:
            self.viewsExists = False
            pass
        try:
            if CourseGrades.objects.count() < 100 \
                or ForumThreads.objects.count() < 100 \
                or Users.objects.count() < 100:
                return False
            return True
        except:
            return False


    @Controller.logged
    def loadData(self):
        type = CourseForums.FORUMTYPES.index(self.FORUMTYPE) # content

        self.forumData = CourseForums()
        self.posts = self.forumData.getPostsByType(type)
        self.comments = self.forumData.getCommentsByType(type)
        self.threads = self.forumData.getThreadsByType(type)
        self.views = self.forumData.getThreadsByType(type)
        self.reputations = self.forumData.reputations

        self.loadUserMap(ignoreErrors = True)
        self.loadActives()
        self.loadLectureActives()
        self.loadContributions()
        self.getInstructorForumIds()

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        if not self.checkForDB():
            logging.info('Necessary database does not exist, bailing. (' \
                + self.getCourseName() + ')')
            sys.exit()

        self.loadData()
        
        firstResponseTimes = self.timeToFirstResponse().values()
        finiteFirstResponseTimes = [t for t in firstResponseTimes if t != float("inf")]
        numOpenThreads = CourseStats.getNumThreads() - len(finiteFirstResponseTimes)
        ratioOpenThreads = float(numOpenThreads) / CourseStats.getNumThreads()
        betweenTimes = self.timeBetweenPosts()
        (postBoost, viewBoost, onThreadPostBoost, onThreadViewBoost) = self.avgInstructorBoost()

        path = os.path.join(self.getMainResultsDir(),'resultsBy_' + self.FORUMTYPE + '.csv')
        with open(path,'at') as fid:
            fid.write(self.getCourseName() + ', ' \
                + str(len(self.activesByAnon)) + ', ' \
                + str(len(self.lectureActivesByAnon)) + ', ' \
                + str(self.contributionByActives()) + ', ' \
                + str(self.contributionByLectureActives()) + ', ' \
                #+ str(self.viewingByActives()) + ', ' \
                + str(self.subscriptionsByActives()) + ', ' \
                + str(self.subscriptionsByLectureActives()) + ', ' \
                + str(self.numThreadsPerActive()) + ', ' \
                + str(self.numThreadsPerLectureActive()) + ', ' \
                + str(self.numContributionsPerActive()) + ', ' \
                + str(self.numContributionsPerLectureActive()) + ', ' \
                + str(self.numViewsPerHourPerActive()) + ', ' \


if __name__ == '__main__':
    projectName = 'ForumMetrics'
    params = {'timeout': 100}
    controller = ForumMetrics_CourseContent(projectName, params)
    controller.handler()

