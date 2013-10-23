# DavidGlance.py
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
from lyticssite.eventModels.models import *
from Controller import Controller
from DBErrors import *
from ModelHelper import ModelHelper
import logging
from CourseStats import CourseStats

MINAGE = 20
MAXAGE = 70

EDUCATION = [ '', \
    'no schooling completed', \
    'some primary or elementary school', \
    'some high school (but no degree)', \
    'high school diploma (or equivalent)', \
    'some college but no degree', \
    'bachelor\'s degree (e.g., BA, AB, BS)', \
    'associate degree - academic program', \
    'associate degree - occupational/technical/vocational program', \
    'professional school degree (e.g., MD, DDS, DVM, LLB, JD)', \
    'master\'s degree (e.g., MA, MS, MEng, MEd, MSW, MBA)', \
    'doctorate degree (e.g., PhD, EdD)']

class DavidGlance(Controller):

    @Controller.logged
    def binEducation(self):
        results = {}
        edData = Demographic.objects.all().values('education_level')
        for key in EDUCATION:
            results[key] = 0
        for record in edData:
            results[record['education_level']] += 1
        return results

    @Controller.logged
    def binAges(self, bucketSize):
        numBins = (MAXAGE-MINAGE)/bucketSize
        ageHist = numBins*[0]
        ageData = Demographic.objects.all().values('age')
        for record in ageData:
            age = record['age']
            if age < MINAGE or age >= MAXAGE:
                continue
            bin = (age-MINAGE) / bucketSize
            ageHist[bin] += 1
        return ageHist

    @Controller.logged
    def getNumSurvey(self):
        return Demographic.objects.count()

    @Controller.logged
    def getGender(self, gen = 'male'):
        return Demographic.objects.filter(gender = gen).count()

    @Controller.logged
    def getUsers(self):
        try:
            return Users.objects.count()
        except:
            raise CourseDBError

    @Controller.logged
    def getViews(self):
        try:
            return LectureSubmissionMetadata.objects.count()
        except:
            raise CourseDBError

    @Controller.logged
    def checkForDB(self):
        try:
            if LectureSubmissionMetadata.objects.count() < 100 \
                or Users.objects.count() < 100 \
                or Demographic.objects.count() < 100:
                return False
            return True
        except:
            return False

    @Controller.logged
    @Controller.dbErrorHandled
    def runner(self):
        if not self.checkForDB():
            logging.info('Necessary database does not exist, bailing. (' \
                + self.getCourseName() + ')')
            raise CourseDBError

        self.loadUserMap(ignoreErrors = True)
        numRegisteredUsers = self.getUsers()
        numViews = self.getViews()
        numMales = self.getGender('male')
        numFemales = self.getGender('female')
        numSurveyRespondents = self.getNumSurvey()
        ageHist = self.binAges(bucketSize = 10)
        edLevels = self.binEducation()

        path = os.path.join(self.getMainResultsDir(),'results.csv')
        with open(path,'at') as fid:
            fid.write(self.getCourseName() + ', ' \
                + str(self.getCourse().difficulty) + ', ' \
                + str(numRegisteredUsers) + ', ' \
                + str(numMales) + ', ' \
                + str(numFemales) + ', ' \
                + str(numSurveyRespondents) + ', ' \
                + str(numViews) + ', ')
            for b in ageHist:
                fid.write(str(b) + ', ')
            for key in EDUCATION:
                fid.write(str(edLevels[key]) + ', ')
            fid.write('\n')

if __name__ == '__main__':
    projectName = 'DavidGlance'
    params = {'timeout': 10}
    controller = DavidGlance(projectName, params)
    controller.handler()

