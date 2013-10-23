# SortCoursesByTopContributors.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from operator import itemgetter

def run(projectName):
    path = os.path.join(FileSystem.getResultsDir(),projectName,'results.csv')
    outPath = os.path.join(FileSystem.getResultsDir(),projectName,'resultsSorted.csv')
    strings = {}
    numContributions = {}
    with open(path) as fid:
        rows = fid.readlines()
        for r in rows:
            row = r.strip().split(', ')
            courseName = row[0]
            strings[courseName] = r
            numContributions[courseName] = float(row[1])

    sortedCourseNames = sorted(numContributions.iteritems(), \
                               key = itemgetter(1), reverse = True)

    with open(outPath,'wt') as fid:
        for courseName,_ in sortedCourseNames:
            fid.write(strings[courseName])


if __name__ == '__main__':
    projectName = 'TopContributors'
    run(projectName)