# TopContributorPositions.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from util.DBSetup import DBSetup
from util.CourseForums import CourseForums

NUMBINS = 4

def getPostToThreadLenMap(forumData):
    threadLenMap = {}
    for thread in forumData.threads:
        threadLenMap[thread.id] = len(forumData.threadToPostMap[thread.id])
        # thread.num_posts doesn't work because of deleted posts.  This one used is somewhat of a hack because
        # it doesn't quite correctly handle deleted posts.
    postToThreadLenMap = {}
    for post in forumData.posts:
        postToThreadLenMap[post.id] = threadLenMap[post.thread_id]
    return postToThreadLenMap

def tallyPositions(forumData, topUserIds):
    resultsTC = {}
    resultsNonTC = {}
    continuousHistTC = NUMBINS*[0]
    continuousHistNonTC = NUMBINS*[0]
    forumData.getPostRankMap()
    postToThreadLenMap = getPostToThreadLenMap(forumData)
    for post in forumData.posts:
        position = forumData.postRankMap[post.id]
        try:
            frac = position/float(postToThreadLenMap[post.id])
        except ZeroDivisionError:
            continue
        binnedFrac = int(frac*(NUMBINS))
        if post.forum_user_id in topUserIds:
            continuousHistTC[binnedFrac] += 1
            try:
                resultsTC[position] += 1
            except KeyError:
                resultsTC[position] = 1
        else:
            continuousHistNonTC[binnedFrac] += 1
            try:
                resultsNonTC[position] += 1
            except KeyError:
                resultsNonTC[position] = 1
    return resultsTC, resultsNonTC, continuousHistTC, continuousHistNonTC

def getTopFivePercent(sortedForumUserIds):
    numUsers = len(sortedForumUserIds)
    cap = int(.05*numUsers)
    return sortedForumUserIds[:(cap+1)]

def addResultsDict(cumulativeDict, resultsDict):
    for key in resultsDict:
        try:
            cumulativeDict[key] += resultsDict[key]
        except KeyError:
            cumulativeDict[key] = resultsDict[key]
    return cumulativeDict

def addResultsList(cumulativeList, resultsList):
    return [x+y for x,y in zip(cumulativeList,resultsList)]

def summarization(ofid, results, num, delimiter = ':\t\t'):
    for i in range(num):
        if i in results:
            ofid.write(str(i) + delimiter + str(results[i]) + '\n')
        else:
            ofid.write(str(i) + delimiter +'0\n')

def normalize(hist):
    invZ = 1.0/sum(hist)
    return [x*invZ for x in hist]

def run(projectName):
    courseDatasets = FileSystem.loadCourseDatasetInfo()
    resultsDir = os.path.join(FileSystem.getResultsDir(),projectName)
    outputPath = os.path.join(resultsDir,'topContributorPositions.txt')

    cumulativeResultsTC = {}
    cumulativeResultsNonTC = {}
    cumulativeContHistTC = NUMBINS*[0]
    cumulativeContHistNonTC = NUMBINS*[0]
    ofid = open(outputPath,'wt')
    for course in courseDatasets:
        print(course.name)
        path = os.path.join(resultsDir, course.name + '_contribution.csv')
        try:
            with open(path) as fid:
                forumUserIds = [r.strip() for r in fid.readlines()]
        except IOError:
            continue

        topUserIds = getTopFivePercent(forumUserIds)
        DBSetup.switch(course)
        forumData = CourseForums()

        resultsTC, resultsNonTC, continuousHistTC, continuousHistNonTC = tallyPositions(forumData, topUserIds)
        cumulativeResultsTC = addResultsDict(cumulativeResultsTC, resultsTC)
        cumulativeResultsNonTC = addResultsDict(cumulativeResultsNonTC, resultsNonTC)
        cumulativeContHistTC = addResultsList(cumulativeContHistTC, continuousHistTC)
        cumulativeContHistNonTC = addResultsList(cumulativeContHistNonTC, continuousHistNonTC)
        ofid.write('--------------------------------------------\n')
        ofid.write('Course: ' + course.name + '\n')
        ofid.write('Top contributor post position histogram\n')
        summarization(ofid, resultsTC, 10)
        ofid.write('\n\n')
        ofid.write('Non top contributor post position histogram\n')
        summarization(ofid, resultsNonTC, 10)

    ofid.write('**************************************\n')
    ofid.write('Aggregated over courses:\n')
    ofid.write('Top contributor post position histogram\n')
    summarization(ofid, cumulativeResultsTC, 20)
    ofid.write('\n\n')
    ofid.write('Non top contributor post position histogram\n')
    summarization(ofid, cumulativeResultsNonTC, 20)
    ofid.close()

    normalizedCumulativeContHistTC = normalize(cumulativeContHistTC)
    normalizedCumulativeContHistNonTC = normalize(cumulativeContHistNonTC)
    outputPathTC = os.path.join(resultsDir,'normalizedPositionHistTC.csv')
    with open(outputPathTC,'wt') as ofid:
        for i in range(NUMBINS):
            ofid.write(str(i) + ', ' + str(normalizedCumulativeContHistTC[i]) + '\n')
    outputPathNonTC = os.path.join(resultsDir,'normalizedPositionHistNonTC.csv')
    with open(outputPathNonTC,'wt') as ofid:
        for i in range(NUMBINS):
            ofid.write(str(i) + ', ' + str(normalizedCumulativeContHistNonTC[i]) + '\n')

if __name__ == '__main__':
    projectName = 'TopContributors'
    run(projectName)