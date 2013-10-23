# TopContributorCounts.py
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


def getTopFivePercent(sortedForumUserIds):
    numUsers = len(sortedForumUserIds)
    cap = int(.05*numUsers)
    return sortedForumUserIds[:(cap+1)]

def run(projectName):
    courseDatasets = FileSystem.loadCourseDatasetInfo()
    resultsDir = os.path.join(FileSystem.getResultsDir(),projectName)
    outputPath = os.path.join(resultsDir,'topContributorPositions.txt')

    numTopContributors = 0
    numContributors = 0
    for course in courseDatasets:
        print(course.name)
        path = os.path.join(resultsDir, course.name + '_contribution.csv')
        try:
            with open(path) as fid:
                forumUserIds = [r.strip() for r in fid.readlines()]
        except IOError:
            continue

        topUserIds = getTopFivePercent(forumUserIds)
        numTopContributors += len(topUserIds)
        numContributors += len(forumUserIds)

    print('Number of Top Contributors: ' + str(numTopContributors))
    print('Number of contributors: ' + str(numContributors))



if __name__ == '__main__':
    projectName = 'TopContributors'
    run(projectName)