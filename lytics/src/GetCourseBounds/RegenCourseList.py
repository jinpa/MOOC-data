# RegenCourseList.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())

def loadBoundData(boundDataPath):
    boundData = {}
    with open(boundDataPath) as fid:
        rows = fid.readlines()
        for r in rows[1:]:
            row = r.strip().split(', ')
            courseName = row[0]
            startTime = int(row[1])
            endTime = int(row[2])
            duration = int(row[3])
            boundData[courseName] = {'startTime': startTime, \
                                    'endTime': endTime, \
                                    'duration': duration}
    return boundData


def writeData(path, courseData, boundData):
    with open(path,'wt') as fid:
        fid.write('CourseName,University,Platform,' \
                + 'Year,LyticsDB,ActivityLogsCoursera,' \
                + 'StartTime,EndTime,NumWeeks,' \
                + 'STEMvsNot,Difficulty\n')
        for course in courseData:
            try:
                bounds = boundData[course.name]
            except KeyError:
                bounds = {'startTime': '', 'endTime': '', 'duration': ''}
            fid.write(course.name + ',' + course.institution + ',' \
                + course.platform + ',' + str(course.year) + ',' \
                + course.dbName + ',' + course.activityLogFile + ',' \
                + str(bounds['startTime']) + ',' \
                + str(bounds['endTime']) + ',' \
                + str(bounds['duration']) + ',' \
                + course.stemVsNot + ',' + course.difficulty + '\n')



def run(projectName):
    boundDataDir = os.path.join(FileSystem.getResultsDir(),projectName)
    boundDataPath = os.path.join(boundDataDir,'results.csv')
    outputPath = os.path.join(boundDataDir,'fullCourseList.csv')

    courseData = FileSystem.loadCourseDatasetInfo()
    boundData = loadBoundData(boundDataPath)
    writeData(outputPath, courseData, boundData)

if __name__ == '__main__':
    projectName = 'GetCourseBounds'
    run(projectName)
