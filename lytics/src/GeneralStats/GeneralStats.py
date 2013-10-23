#! /usr/bin/env ipython

# GeneralStats.py
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
from Controller import Controller
from DBErrors import *
import logging
from numpy import median, mean

class GeneralStats(Controller):

    @Controller.logged
    def getNumForums(self):
        return ForumForums.objects.count()

    @Controller.logged
    def getNumThreads(self):
        return ForumThreads.objects.count()

    @Controller.logged
    def getNumPosts(self):
        return ForumPosts.objects.count()

    @Controller.logged
    def getNumComments(self):
        return ForumComments.objects.count()
        
    @Controller.logged
    def getNumContributingUsers(self):
        postDicts = ForumPosts.objects.all().values('forum_user_id','anonymous')
        commentDicts = ForumComments.objects.all().values('forum_user_id','anonymous')
        posts = [x['forum_user_id'] for x in postDicts if x['anonymous'] == 0]
        comments = [x['forum_user_id'] for x in commentDicts if x['anonymous'] == 0]
        return len(set(posts + comments))

    @Controller.logged
    def getNumPostsByThread(self):
        posts = [x['thread_id'] for x in ForumPosts.objects.all().values('thread_id')]
        postCount = {}
        for threadId in posts:
            try:
                postCount[threadId] += 1
            except KeyError:
                postCount[threadId] = 1
        return postCount.values()

    @Controller.logged
    def getPostThreadMap(self):
        posts = [(x['id'],x['thread_id']) for x in ForumPosts.objects.all().values('id','thread_id')]
        postMap = {}
        for postId, threadId in posts:
            postMap[postId] = threadId
        return postMap

    @Controller.logged
    def getNumCommentsByThread(self, postMap = None):
        logging.info('getNumCommentsByThread')
        if postMap == None:
            postMap = self.getPostThreadMap()
        comments = [postMap[x['post_id']] for x in ForumComments.objects.all().values('post_id')]
        commentsCount = {}
        for threadId in comments:
            try:
                commentsCount[threadId] += 1
            except KeyError:
                commentsCount[threadId] = 1
        return commentsCount.values()
         
    @Controller.logged       
    def computeGeneralStats(self):
        results = {}
        results['numForums'] = self.getNumForums()
        results['numThreads'] = self.getNumThreads()
        results['numPosts'] = self.getNumPosts()
        results['numComments'] = self.getNumComments()
        results['numContributingUsers'] = self.getNumContributingUsers()
            
        numPostsPerThread = self.getNumPostsByThread()
        numCommentsPerThread = self.getNumCommentsByThread()
        results['avgPostsPerThread'] = mean(numPostsPerThread)
        results['medianPostsPerThread'] = median(numPostsPerThread)
        results['avgCommentsPerThread'] = mean(numCommentsPerThread)
        results['medianCommentsPerThread'] = median(numCommentsPerThread)
        return results

    def saveStats(self, results, path):
        fid = open(path,'at')
        #fid.write('CourseDB, # Forums, # Threads, # Posts, # Comments, # Contributors, ' \
        #            + 'Avg. # Posts Per Thread, Median # Posts Per Thread, ' \
        #            + 'Avg. # Comments Per Thread, Median # Comments Per Thread' + '\n')
        fid.write(self.getCourseName() + ', ')
        fid.write(str(results['numForums']) + ', ')
        fid.write(str(results['numThreads']) + ', ')
        fid.write(str(results['numPosts']) + ', ')
        fid.write(str(results['numComments']) + ', ')
        fid.write(str(results['numContributingUsers']) + ', ')
        fid.write(str(results['avgPostsPerThread']) + ', ')
        fid.write(str(results['medianPostsPerThread']) + ', ')
        fid.write(str(results['avgCommentsPerThread']) + ', ')
        fid.write(str(results['medianCommentsPerThread']) + '\n')
        fid.close()

    @Controller.logged
    def checkForDB(self):
        try:
            if ForumThreads.objects.count() < 100:
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
            sys.exit()
        path = os.path.join(self.getMainResultsDir(), 'GeneralStats.csv')
        results = self.computeGeneralStats()
        self.saveStats(results, path)

if __name__ == '__main__':
    projectName = 'GeneralStats'
    params = {'timeout': 10}
    controller = GeneralStats(projectName, params)
    controller.handler()
