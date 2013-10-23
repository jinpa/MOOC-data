# AgeVsForumPosts.py
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
from Controller import Controller
from DBErrors import *
from ModelHelper import ModelHelper
import logging
from CourseStats import CourseStats
from numpy import mean, std, percentile

employmentOptions = {'employed full-time (35 or more hours per week)': 'employedfulltime', \
        'employed part-time (less than 35 hours per week)': 'employedparttime', \
        'unemployed and looking for work': 'unemployedlooking', \
        'unemployed and not looking for work': 'unemployednotlooking', \
        'unable to work': 'unabletowork', \
        'homemaker, taking care of a family member, or on maternity/paternity leave': 'homemaker', \
        'retired': 'retired', \
        'self-employed (35 or more hours per week)': 'selffulltime', \
        'self-employed (less than 35 hours per week)': 'selfparttime', \
        '': ''}

studentOptions = {'No, I am not currently a student.': 'notstudent', \
                    'Yes, I am currently a part-time student.': 'parttime', \
                    'Yes, I am currently a full-time student.': 'fulltime', \
                    '': ''}

englishOptions = {'none': 0, \
                'knowledge of a few phrases': 1, \
                'sufficient for limited situations': 2, \
                'sufficient for most situations': 3, \
                'native English speaker or equivalent': 4, \
                '': -1 }

class AgeVsForumPosts(Controller):

    @Controller.logged
    def loadDemographics(self):
        try:
            demoData = list(Demographic.objects.all().values('user_id','age','gender','current_employment_status','current_student','english_writing'))
        except:
            raise CourseDBError
        self.ageMap = {}
        self.genderMap = {}
        self.employmentMap = {}
        self.studentStatusMap = {}
        self.englishMap = {}
        for record in demoData:
            self.ageMap[record['user_id']] = record['age']
            self.genderMap[record['user_id']] = record['gender']
            self.employmentMap[record['user_id']] = record['current_employment_status']
            self.studentStatusMap[record['user_id']] = record['current_student']
            self.englishMap[record['user_id']] = record['english_writing']
    
    @Controller.logged
    def loadPosts(self):
        try:
            forumData = list(ForumPosts.objects.all().values('forum_user_id','post_time'))
            forumData[100]
        except:
            raise CourseDBError
        allTimes = sorted([record['post_time'] for record in forumData])
        weekInSeconds = 7*24*3600
        timeCutoff = allTimes[20] + weekInSeconds      
        self.postMap = {}
        for record in forumData:
            if record['post_time'] < timeCutoff:
                continue
            try:
                user_id = self.users.getByForum(record['forum_user_id'])['user']
            except KeyError:
                continue
            try:
                self.postMap[user_id] += 1
            except KeyError:
                self.postMap[user_id] = 1

    @Controller.logged
    def loadComments(self):
        try:
            forumData = list(ForumComments.objects.all().values('forum_user_id','post_time'))
            forumData[100]
        except:
            raise CourseDBError
        allTimes = sorted([record['post_time'] for record in forumData])
        weekInSeconds = 7*24*3600
        timeCutoff = allTimes[20] + weekInSeconds      
        self.commentMap = {}
        for record in forumData:
            if record['post_time'] < timeCutoff:
                continue
            try:
                user_id = self.users.getByForum(record['forum_user_id'])['user']
            except KeyError:
                continue
            try:
                self.commentMap[user_id] += 1
            except KeyError:
                self.commentMap[user_id] = 1

    @Controller.logged
    def loadGrades(self):
        try:
            gradeData = list(CourseGrades.objects.all().values('anon_user_id','normal_grade'))
            gradeData[100]
        except:
            raise CourseDBError
        self.gradeMap = {}
        for record in gradeData:
            try:
                user_id = self.users.getByAnon(record['anon_user_id'])['user']
            except KeyError:
                continue
            self.gradeMap[user_id] = record['normal_grade']
        self.normalizeGrades()

    def normalizeGrades(self):
        meanScore = mean(self.gradeMap.values())
        stdScore = std(self.gradeMap.values())
        self.zscores = {}
        for user_id in self.gradeMap:
            self.zscores[user_id] = (self.gradeMap[user_id] - meanScore)/stdScore

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        self.loadUserMap(ignoreErrors = True)
        self.loadDemographics()
        self.loadPosts()
        self.loadComments()
        self.loadGrades()
        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            for user in self.ageMap:
                age = self.ageMap[user]
                gender = self.genderMap[user]
                employment = employmentOptions[self.employmentMap[user]]
                studentStatus = studentOptions[self.studentStatusMap[user]]           
                englishAbility = englishOptions[self.englishMap[user]]           
                if age > 120:
                    logging.info('\tSuspicious reported age: ' + str(age))
                    continue
                if user in self.postMap:
                    numPosts = self.postMap[user]
                else:
                    numPosts = 0
                if user in self.commentMap:
                    numComments = self.commentMap[user]
                else:
                    numComments = 0
                if user in self.gradeMap:
                    grade = self.zscores[user]
                else:
                    grade = None
                fid.write(self.getCourseName() + ', ' \
                        + str(age) + ', ' + str(gender) + ', ' + employment + ', '
                        + str(englishAbility) + ', ' \
                        + studentStatus + ', ' + str(grade) + ', ' + str(numPosts) + ', ' \
                        + str(numComments) + ', ' + str(numPosts+numComments) + '\n')
        

if __name__ == '__main__':
    projectName = 'AgeVsForumPosts'
    params = {'timeout': 10}
    controller = AgeVsForumPosts(projectName, params)
    controller.handler()

