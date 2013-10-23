# TopContributorThreadResponses.py
# author = Jonathan Huang
__author__ = 'jhuang11'

# notes: this experiments separates threads started by a top contributor from
# others and compare length of thread

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from util.DBSetup import DBSetup
from lyticssite.forumModels.models import ForumThreads
from numpy import mean,median

def isolateThreadLengths(threads, topUserIds):
    TCthreadLen = []
    nonTCthreadLen = []
    for thread in threads:
        if thread.forum_user_id in topUserIds:
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
        TC, nonTC = isolateThreadLengths(threads,topUserIds)
        TCMedian = median(TC)
        nonTCMedian = median(nonTC)
        TCMean = mean(TC)
        nonTCMean = mean(nonTC)
        medianDiffs.append(TCMedian-nonTCMedian)
        meanDiffs.append(TCMean-nonTCMean)
        print(course.name)
        print('Median thread length started by top contributors: ' + str(TCMedian))
        print('Median thread length started by non top contributors: ' + str(nonTCMedian))
        print('Mean thread length started by top contributors: ' + str(TCMean))
        print('Mean thread length started by non top contributors: ' + str(nonTCMean))
        print(' ')

    print('Average difference between median thread lengths: ' + str(mean(medianDiffs)))
    print('Average difference between mean thread lengths: ' + str(mean(meanDiffs)))


if __name__ == '__main__':
    projectName = 'TopContributors'
    run(projectName)