# ForumPosters.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())

class CourseUserRecord(object):

    def __init__(self, courseName, userId, totalContributions, \
                 numFirstPosts, numPosts, numComments, contributionsPerWeek, \
                 avgPostPosition, rankByContributions, rankByReputation, \
                 inTopFivePercentByContributions, inTopFivePercentByReputation):
        self.courseName = courseName
        self.userId = self._softCastToInt(userId)
        self.totalContributions = self._softCastToInt(totalContributions)
        self.numFirstPosts = self._softCastToInt(numFirstPosts)
        self.numPosts = self._softCastToInt(numPosts)
        self.numComments = self._softCastToInt(numComments)
        self.contributionsPerWeek = self._softCastToFloat(contributionsPerWeek)
        self.avgPostPosition = self._softCastToFloat(avgPostPosition)
        self.rankByContributions = self._softCastToInt(rankByContributions)
        self.rankByReputation = self._softCastToInt(rankByReputation)
        self.inTopFivePercentByContributions = self._softCastToInt(inTopFivePercentByContributions)
        self.inTopFivePercentByReputation = self._softCastToInt(inTopFivePercentByReputation)

    def _softCastToInt(self, x):
        try:
            return int(x)
        except ValueError:
            return None

    def _softCastToFloat(self, x):
        try:
            return float(x)
        except ValueError:
            return None

class ForumPosters(object):

    def __init__(self):
        self.projectName = 'PerUserPosting'
        self.resultsDir = os.path.join(FileSystem.getResultsDir(), self.projectName)
        self.path = os.path.join(self.resultsDir, 'results.csv')

        self.posters = {}
        self._loadPosters()

    def getNumPosters(self):
        return len(self.posters.keys())

    def _loadPosters(self):
        with open(self.path) as fid:
            rows = fid.readlines()
            for r in rows:
                row = r.strip().split(', ')
                record = CourseUserRecord(*row)
                self._insertRecord(record)

    def _insertRecord(self,record):
        try:
            self.posters[record.userId].append(record)
        except KeyError:
            self.posters[record.userId] = [record]












