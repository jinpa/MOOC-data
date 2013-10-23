#! /usr/bin/env ipython

# MakeVideoLogs.py
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
from Controller import Controller, CourseDBError, NoGradesError
from ModelHelper import ModelHelper
from RunExternal import RunExternal
import logging
import json
import urlparse

class MakeVideoLogs(Controller):

    #def __init__(self, projectName, params):
    #   super(ForumUseVsEngagement, self).__init__(projectName,params)

    def getActivityLogFile(self):
        activityLogDir = os.path.join(FileSystem.getDataDir(),'ActivityLogsCoursera')
        path = os.path.join(activityLogDir, \
                self.courseDatasetInfo[self.currCourseName])
        return path

    def unzip(self, path):
        logging.info('MakeVideoLogs.unzip(), ' + self.currCourseName)
        zipExec = RunExternal(['gunzip',path],3600)
        zipExec.run()   
        
    def zip(self,path):
        logging.info('MakeVideoLogs.zip(), ' + self.currCourseName)
        zipExec = RunExternal(['gzip',path],3600)
        zipExec.run()   
    
    def insert(self, D, key, jObj, jObjkey):
        try:
            D[key] = jObj[jObjkey]
        except KeyError:
            D[key] = ''

    def getViews(self, path):
        logging.info('MakeVideoLogs.getViews(), ' + self.currCourseName)
        views = []
        logFile = open(path)
        linecount = 1
        for line in logFile:
            if linecount % 20000 == 0:
                logging.info('\t+ getViews(): on line ' \
                            + str(linecount) + ' for ' + self.currCourseName)
            jObj = json.loads(line)
            if 'key' in jObj:
                if jObj['key'] == 'user.video.lecture.action':
                    action = json.loads(jObj['value'])
                    parseResult = urlparse.urlparse(jObj['page_url'])
                    query = urlparse.parse_qs(parseResult.query)
                    if 'lecture_id' in query:
                        try:
                            record = {'lectureId': int(query['lecture_id'][0]), \
                                      'logUserId': jObj['username'], \
                                      'userIp': jObj['user_ip']}
                            self.insert(record, 'eventTimestamp', action, 'eventTimestamp')
                            self.insert(record, 'readyState', action, 'readyState')
                            self.insert(record, 'action', action, 'type')
                            self.insert(record, 'networkState', action, 'networkState')
                            self.insert(record, 'error', action, 'error')
                            self.insert(record, 'playbackRate', action, 'playbackRate')
                            self.insert(record, 'paused', action, 'paused')
                            self.insert(record, 'currentTime', action, 'currentTime')
                            self.insert(record, 'prevTime', action, 'prevTime')
                            views.append(record)
                        except ValueError:
                            logging.info('\tError parsing line: ' + str(line))
            linecount += 1
        logFile.close()
        logging.info('\t+ getViews() finished for ' + self.currCourseName)
        return views
    
    def writeViews(self, views, path):
        logging.info('MakeVideoLogs.writeViews(), ' + self.currCourseName)
        with open(path,'wt') as fid:
            #fid.write('forum_user_id, thread_id, timestamp, user_ip\n')
            for record,cnt in zip(views,range(len(views))):
                if cnt % 1000000 == 0:
                    logging.info('\t\t+ writeViews(): ' + str(cnt) + \
                        ' of ' + str(len(views)) + ' for ' + self.currCourseName)
                fid.write(str(record['logUserId']) + ', ' \
                            + str(record['lectureId']) + ', ' \
                            + str(record['eventTimestamp']) + ', ' \
                            + str(record['userIp']) + ', ' \
                            + str(record['readyState']) + ', ' \
                            + str(record['action']) + ', ' \
                            + str(record['networkState']) + ', ' \
                            + str(record['error']) + ', ' \
                            + str(record['playbackRate']) + ', ' \
                            + str(record['paused']) + ', ' \
                            + str(record['currentTime']) + ', ' \
                            + str(record['prevTime']) + '\n')

    def runner(self):
        logging.info('MakeVideoLogs.runner(), ' + self.currCourseName)
        self.courseDatasetInfo = FileSystem.loadCourseDatasetInfo()
        try:
            if self.currCourseName not in self.courseDatasetInfo \
                or self.courseDatasetInfo[self.currCourseName] is None:
                print(self.currCourseName + ' has no activity log.  Exiting...')
                sys.exit()

            print('Working on: ' + self.currCourseName + ' (' + self.progress() +')')
            activityLogFileZipped = self.getActivityLogFile()
            activityLogFileUnzipped = activityLogFileZipped[:-3]
            
            outputDir = os.path.join(FileSystem.getDataDir(), 'ActivityLogsCoursera')
            outputPath = os.path.join(outputDir, self.currCourseName + '.videolog')

            if os.path.exists(outputPath):
                logging.info('Output file already exists: ' + outputPath)
                sys.exit()
            if os.path.exists(activityLogFileZipped):
                self.unzip(activityLogFileZipped)
            if not os.path.exists(activityLogFileUnzipped):
                logging.info('Error finding file ' + activityLogFileUnzipped)
                sys.exit()
            views = self.getViews(activityLogFileUnzipped)
            self.writeViews(views,outputPath)
            self.zip(activityLogFileUnzipped)

        except CourseDBError:
            logging.info('\t\t+ ERROR (Connection does not exist), skipping...')
            pass
        except NoGradesError:
            logging.info('\t\t+ ERROR (CourseGrades does not exist), skipping...')
            pass

if __name__ == '__main__':
    projectName = 'MakeVideoLogs'
    params = {'timeout': 10}
    controller = MakeVideoLogs(projectName, params)
    controller.handler()




