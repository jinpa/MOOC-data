#! /usr/bin/env ipython

# NonTextFeatures.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.classModels.models import *
import logging
from operator import itemgetter
from numpy import mean, median
from Text import Text

class NonTextFeatures(object):
 
    def getPostThreadMap(self,posts):
        logging.info('getPostThreadMap: ' + self.currDB)
        postMap = {}
        for post in posts:
            postMap[post.id] = post.thread_id
        return postMap
   
    def getNumPosts(self, threads):
        logging.info('getNumPosts: ' + self.currDB)
        results = {}
        for thread in threads:
            results[thread.id] = thread.num_posts
        return results

    def getAvgPostLen(self, threads, posts):
        logging.info('getAvgPostLen: ' + self.currDB)
        wordCount = {}
        for thread in threads:
            wordCount[thread.id] = []
        for post in posts:
            string = Text(post.post_text)
            wordCount[post.thread_id].append(string.getNumTokens())
        results = {}
        for thread in threads:
            try:
                results[thread.id] = mean(wordCount[thread.id])
            except ZeroDivisionError:
                results[thread.id] = 0
        return results

    def postTime(self, threads):
        logging.info('postTime: ' + self.currDB)
        results = {}
        for thread in threads:    
            results[thread.id] = thread.posted_time
        return results

    def postTimeRank(self, threads):
        logging.info('postTimeRank: ' + self.currDB)
        results = {}
        for thread in threads:    
            results[thread.id] = thread.posted_time
        sortedPairs = sorted(results.iteritems(), key = itemgetter(1))
        for (threadId, timestamp), idx in zip(sortedPairs, range(len(sortedPairs))):
            results[threadId] = idx
        return results

    # returns infinity if there is no response
    def timeToFirstResponse(self, threads, posts):
        logging.info('timeToFirstResponse: ' + self.currDB)
        results = {}
        for post in posts:
            if post.original == 1:
                continue
            try:
                results[post.thread_id] = min(post.post_time, results[post.thread_id])
            except KeyError:
                results[post.thread_id] = post.post_time
        for thread in threads:
            try:
                results[thread.id] -= thread.posted_time
            except KeyError:
                results[thread.id] = float("inf")
        return results

    def numContributors(self, threads, posts, comments, postMap):
        logging.info('numContributors: ' + self.currDB)
        results = {}
        contributorLists = {}
        for thread in threads:
            contributorLists[thread.id] = []
        for post in posts:
            contributorLists[post.thread_id].append(post.forum_user_id)
        for comment in comments:
            threadId = postMap[comment.post_id]
            contributorLists[threadId].append(comment.forum_user_id)
        for threadId in contributorLists:
            results[threadId] = len(set(contributorLists[threadId]))
        return results

    # not counting original post
    # returns 0 if there was just one post
    def timeOfHighestVotedPost(self, threads, posts):
        logging.info('timeOfHighestVotedPost: ' + self.currDB)
        results = {}
        maxVotes = {}
        for thread in threads:
            results[thread.id] = -1
            maxVotes[thread.id] = 0
        for post in posts:
            if post.votes > maxVotes[post.thread_id] and post.original == 0:
                results[post.thread_id] = post.post_time
                maxVotes[post.thread_id] = post.votes
        return results
 
    # this function returns whether the original post on a thread got more votes
    # than any other post on the same thread   
    def originalPostVotes(self, threads, posts):
        logging.info('originalPostVotes: ' + self.currDB)
        results = {}
        originalVotes = {}
        maxVotes = {}
        for thread in threads:
            maxVotes[thread.id] = -1
        for post in posts:
            if post.votes > maxVotes[post.thread_id] and post.original == 0:
                maxVotes[post.thread_id] = post.votes
            if post.original == 1:
                originalVotes[post.thread.id] = post.votes
        for thread in threads:
            results[thread.id] = int(originalVotes[thread.id] > maxVotes[thread.id])
        return results

    def originalPostNumTokens(self, threads, posts):
        logging.info('originalPostNumTokens: ' + self.currDB)
        results = {}
        for thread in threads:
            results[thread.id] = 0
        for post in posts:
            if post.original == 1:
                string = Text(post.post_text)
                results[post.thread_id] = string.getNumTokens()    
        return results

    def computeFeatures(self):
        logging.info('computeFeatures(' + self.currDB + ')')
        DBSetup.switch(self.currDB)
        
        threads = ForumThreads.objects.all()
        posts = ForumPosts.objects.all()
        comments = ForumComments.objects.all()
        postMap = self.getPostThreadMap(posts)

        features = {}
        features['numPosts'] = self.getNumPosts(threads)
        features['avgPostLen'] = self.getAvgPostLen(threads, posts)
        features['postTime'] = self.postTime(threads)
        features['postTimeRank'] = self.postTimeRank(threads)
        features['timeToFirstResponse'] = self.timeToFirstResponse(threads,posts)
        features['numContributors'] = self.numContributors(threads,posts,comments,postMap)
        features['timeOfHighestVotedPost'] = self.timeOfHighestVotedPost(threads,posts)
        features['originalPostVotes'] = self.originalPostVotes(threads,posts)
        features['originalPostNumTokens'] = self.originalPostNumTokens(threads,posts)
        return features    

    def saveFeatures(self, features):
        logging.info('saveFeatures(' + self.currDB + ')')
        path = os.path.join(self.dataPath, self.currDB + '.csv')
        keys = features.keys()
        threadIds = features[keys[0]].keys()
        with open(path,'wt') as fid:
            fid.write('threadId, ')
            for k in keys:
                fid.write(str(k) + ', ')
            fid.write('\n')
            for threadId in threadIds:
                fid.write(str(threadId) + ', ')    
                for k in keys:
                    fid.write(str(features[k][threadId]) + ', ')
                fid.write('\n')
        logging.info(' ... done saving.')

    def __init__(self):
        projectName = 'NonTextFeatures'
        FileSystem.startLogger(projectName, 'log')
        self.dbNames = FileSystem.loadForumList()
        self.dataPath = FileSystem.createDataDir(projectName)
       
    def run(self):
        for dbName in self.dbNames:
            self.currDB = dbName
            features = self.computeFeatures()
            self.saveFeatures(features)

if __name__ == '__main__':
    NonTextFeatures().run()


