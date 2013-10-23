# CourseOverlap.py
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
from DBErrors import *
import logging
import numpy as np


class CourseOverlap(object):

    def loadUsers(self):
        return [x['user_id'] for x in HashMapping.objects.all().values('user_id')]

    def setup(self,projectName):
        self.resultsDir = FileSystem.createResultsDir(projectName)
        self.courseDatasets = FileSystem.loadCourseDatasetInfo()

    def run(self, projectName):
        self.setup(projectName)
        self.users = {}
        for courseId in range(len(self.courseDatasets)):
            courseName = self.courseDatasets[courseId].name
            print('Loading ' + courseName)
            DBSetup.switch(self.courseDatasets[courseId])
            try:
                self.users[courseName]= set(self.loadUsers())
                self.users[courseName][1000]
            except:
                continue

        courseNames = self.users.keys()
        results = np.zeros((len(courseNames),len(courseNames))) #,dtype=np.int)
        for i in range(len(courseNames)):
            courseA = self.users[courseNames[i]]
            print('Intersecting against ' + courseNames[i])
            for j in range(len(courseNames)):
                courseB = self.users[courseNames[j]]
                overlap = len(courseA.intersection(courseB))
                results[i,j] = overlap/float(len(courseA))

        path = os.path.join(self.resultsDir, 'results.csv')
        np.savetxt(path, results, delimiter=",",fmt = '%1.5f')
        path = os.path.join(self.resultsDir, 'courseList.csv')
        with open(path,'wt') as fid:
            for i,course in zip(range(len(courseNames)),courseNames):
                fid.write(str(i) + '\t' + course + '\n')

if __name__ == '__main__':
    projectName = 'CourseOverlap'
    CourseOverlap().run(projectName)

