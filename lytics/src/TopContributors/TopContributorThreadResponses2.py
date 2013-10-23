# TopContributorThreadResponses2.py
# author = Jonathan Huang

__author__ = 'jhuang11'

# notes: this experiments separates threads that have a post by a top contributor from
# others and compare length of thread

# note that we have somewhat of a causality issue here, since top contributors might
# be biased in their selection of threads to post on (maybe they typically seek out longer threads
# to post on)

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from util.DBSetup import DBSetup
from lyticssite.forumModels.models import ForumThreads, ForumPosts
from numpy import mean,median

def threadIntersects(topUserIdSet, threadId, postMap):
    if len(topUserIdSet.intersection(postMap[threadId])) > 0:
        return True
    return False

def createPostMap(posts):
    postMap = {}
    for post in posts:
        try:
            postMap[post.thread_id].append(post.forum_user_id)
        except KeyError:
            postMap[post.thread_id] = [post.forum_user_id]
    return postMap

def isolateThreadLengths(threads, posts, topUserIds):
    TCthreadLen = []
    nonTCthreadLen = []
    postMap = createPostMap(posts)
    topUserIdSet = set(topUserIds)
    for thread in threads:
        if threadIntersects(topUserIdSet, thread.id, postMap):
            TCthreadLen.append(thread.num_posts)
        else:
            nonTCthreadLen.append(thread.num_posts)
    return TCthreadLen, nonTCthreadLen

def getTopFivePercent(sortedForumUserIds):
    numUsers = len(sortedForumUserIds)
    cap = int(.05*numUsers)
    return sortedForumUserIds[:(cap+1)]

def run(projectName):
    courseDatasets = FileSystem.loadCourseDatasetInfo()
    resultsDir = os.path.join(FileSystem.getResultsDir(),projectName)

    medianDiffs = []
    meanDiffs = []
    for course in courseDatasets:
        path = os.path.join(resultsDir, course.name + '_contribution.csv')
        try:
            with open(path) as fid:
                forumUserIds = [r.strip() for r in fid.readlines()]
        except IOError:
            continue

        topUserIds = getTopFivePercent(forumUserIds)
        DBSetup.switch(course)

        threads = ForumThreads.objects.all()
        posts = ForumPosts.objects.all()
        TC, nonTC = isolateThreadLengths(threads, posts,topUserIds)
        TCMedian = median(TC)
        nonTCMedian = median(nonTC)
        TCMean = mean(TC)
        nonTCMean = mean(nonTC)
        medianDiffs.append(TCMedian-nonTCMedian)
        meanDiffs.append(TCMean-nonTCMean)
        print(course.name)
        print('Median thread length for threads with posts by top contributors: ' + str(TCMedian))
        print('Median thread length for threads without posts by top contributors: ' + str(nonTCMedian))
        print('Mean thread length for threads with posts by top contributors: ' + str(TCMean))
        print('Mean thread length for threads without posts by top contributors: ' + str(nonTCMean))
        print(' ')

    print('Average difference between median thread lengths: ' + str(mean(medianDiffs)))
    print('Average difference between mean thread lengths: ' + str(mean(meanDiffs)))


if __name__ == '__main__':
    projectName = 'TopContributors'
    run(projectName)