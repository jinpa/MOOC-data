# CrossCourseSuperposting.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from src.PerUserPosting.ForumPosters import *
import numpy as np

def tallyPosters(posters):
    results = np.zeros((2,2))
    numSamps = 0
    for poster in posters.posters:
        currUser = posters.posters[poster]
        numCourses = len(currUser)
        if numCourses != 2:
            continue
        super0 = currUser[0].inTopFivePercentByContributions
        super1 = currUser[1].inTopFivePercentByContributions
        results[super0, super1] += 1
        results[super1, super0] += 1
        numSamps += 1
    return results/sum(sum(results)), numSamps

def run(projectName):
    posters = ForumPosters()
    print('Num Posters: ' + str(posters.getNumPosters()))

    results, numSamps = tallyPosters(posters)
    print(results)
    print(numSamps)

    marg = sum(results).reshape((2,1))
    print(marg)
    approx = np.dot(marg,marg.transpose())
    print(approx)

if __name__ == '__main__':
    projectName = 'PerUserPosting'
    run(projectName)

