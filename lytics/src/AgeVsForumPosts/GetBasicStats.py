# GetBasicStats.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from lyticssite.generalModels.models import *
from lyticssite.hashMapModels.models import *
from lyticssite.eventModels.models import *
from UserMap import UserMap
from DBErrors import *
import logging
import numpy as np


class GetBasicStats(object):

    def loadCourseNames(self):
        path = 'coursenames.txt'
        with open(path) as fid:
            return [r.strip() for r in fid.readlines()]

    def loadUsers(self):
        return [x['user_id'] for x in HashMapping.objects.all().values('user_id')]
    
    def loadSurveyRespondents(self):
        userIds = [u['user_id'] for u in Demographic.objects.all().values('user_id')]
        survey = []
        for id in userIds:
            try:
                self.userMap.getByUser(id)
                survey.append(id)
            except KeyError:
                pass
        return survey

    def loadPosters(self):
        forumUserIds = [u['forum_user_id'] for u in ForumPosts.objects.all().values('forum_user_id')] + \
            [u['forum_user_id'] for u in ForumComments.objects.all().values('forum_user_id')]
        posters = []
        for id in forumUserIds:
            try:
                posters.append(self.userMap.getByForum(id)['user'])
            except KeyError:
                pass
        return posters


    def setup(self,projectName):
        self.resultsDir = FileSystem.createResultsDir(projectName)
        self.courseDatasets = FileSystem.loadCourseDatasetInfo()
        self.courseNames = self.loadCourseNames()

    def run(self, projectName):
        self.setup(projectName)
        self.users = {}
        numSurveyRespondents = []
        numPosters = []
        numUsers = []
        numIntersection = []
        allUsers = []
        for courseId in range(len(self.courseDatasets)):
            courseName = self.courseDatasets[courseId].name
            if courseName not in self.courseNames:
                continue
            print('Loading ' + courseName)
            DBSetup.switch(self.courseDatasets[courseId])
            try:
                self.users[courseName]= list(set(self.loadUsers()))
                self.users[courseName][100]
            except KeyError:
                continue
            allUsers += self.users[courseName]
            self.userMap = UserMap(True)
            surveyRespondents = set(self.loadSurveyRespondents())
            posters = set(self.loadPosters())

            numUsers.append(len(self.users[courseName]))
            numSurveyRespondents.append(len(surveyRespondents))
            numPosters.append(len(posters))
            numIntersection.append(len(posters.intersection(surveyRespondents)))

     
        totalEnrollments = sum(numUsers)
        totalUsers = len(set(allUsers))
        totalSurveyRespondents = sum(numSurveyRespondents)
        fracPosters = sum(numPosters)/float(totalEnrollments)
        fracPostersSurveyed = sum(numIntersection) / float(totalSurveyRespondents)
        path = os.path.join(self.resultsDir, 'basicStats.csv')
        with open(path,'wt') as fid:
            fid.write('Number of enrollments: ' + str(totalEnrollments) + '\n')
            fid.write('Number of users: ' + str(totalUsers) + '\n')
            fid.write('Number of survey respondents: ' + str(totalSurveyRespondents) + '\n')
            fid.write('Fraction of enrolled users who posted: ' + str(fracPosters) + '\n')
            fid.write('Fraction of survey respondents who posted: ' + str(fracPostersSurveyed) + '\n')

if __name__ == '__main__':
    projectName = 'AgeVsForumPosts'
    GetBasicStats().run(projectName)

