# FirstPostBehavior.py
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
    TCnumResponses = 0
    TCnumFirstPosts = 0
    nonTCnumResponses = 0
    nonTCnumFirstPosts = 0
    for poster in posters.posters:
        currUser = posters.posters[poster]
        for courseRecord in currUser:
            numResponses = float(courseRecord.totalContributions)
            numFirstPosts = float(courseRecord.numFirstPosts)
            if courseRecord.inTopFivePercentByContributions == 1:
                TCnumResponses += numResponses
                TCnumFirstPosts += numFirstPosts
            else:
                nonTCnumResponses += numResponses
                nonTCnumFirstPosts += numFirstPosts

    return TCnumResponses, TCnumFirstPosts, nonTCnumResponses, nonTCnumFirstPosts

def run(projectName):
    posters = ForumPosters()
    print('Num Posters: ' + str(posters.getNumPosters()))

    TCnumResponses, TCnumFirstPosts, nonTCnumResponses, nonTCnumFirstPosts \
                    = tallyPosters(posters)
    print('For top contributors:')
    print('\t# responses: ' + str(int(TCnumResponses)))
    print('\t# first posts: ' + str(int(TCnumFirstPosts)))
    print('\t\tratio: ' + str(TCnumResponses/TCnumFirstPosts))
    print('For non top contributors:')
    print('\t# responses: ' + str(int(nonTCnumResponses)))
    print('\t# first posts: ' + str(int(nonTCnumFirstPosts)))
    print('\t\tratio: ' + str(nonTCnumResponses/nonTCnumFirstPosts))

if __name__ == '__main__':
    projectName = 'PerUserPosting'
    run(projectName)

