# Course.py
# author = Jonathan Huang

class Course(object):

    def __init__(self, courseName, courseInstitution, \
                coursePlatform, courseYear, dbName, activityLogFile, \
                startTime, endTime, numWeeks, \
                stemVsNot, difficulty):
        self.name = courseName
        self.institution = courseInstitution
        self.platform = coursePlatform
        self.year = self._softCastToInt(courseYear)
        self.dbName = dbName
        self.activityLogFile = activityLogFile
        self.startTime = self._softCastToInt(startTime)
        self.endTime = self._softCastToInt(endTime)
        self.numWeeks = self._softCastToInt(numWeeks)
        self.stemVsNot = stemVsNot
        self.difficulty = difficulty

    def _softCastToInt(self, x):
        try:
            return int(x)
        except ValueError:
            return None
