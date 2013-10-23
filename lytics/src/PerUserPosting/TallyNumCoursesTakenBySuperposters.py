# TallyNumCoursesTakenBySuperposters.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from src.PerUserPosting.ForumPosters import *
from operator import itemgetter

def tallyPosters(posters):
    results = {}
    for poster in posters.posters:
        currUser = posters.posters[poster]
        numCourses = len(currUser)
        if sum([c.inTopFivePercentByContributions for c in currUser]) == 0:
            continue
        try:
            results[numCourses] += 1
        except KeyError:
            results[numCourses] = 1
    sortedResults = sorted(results.iteritems(), key = itemgetter(1),\
                           reverse=True)
    return sortedResults

def run(projectName):
    posters = ForumPosters()
    print('Num Posters: ' + str(posters.getNumPosters()))

    results = tallyPosters(posters)
    print('# courses\t\t# superposters taking that many courses')
    for (numCourses,numStudents) in results:
        print(str(numCourses) + '\t\t' + str(numStudents))



if __name__ == '__main__':
    projectName = 'PerUserPosting'
    run(projectName)

