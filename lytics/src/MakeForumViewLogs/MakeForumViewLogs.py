#! /usr/bin/env ipython

# MakeForumViewLogs.py
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

class MakeForumViewLogs(Controller):

    #def __init__(self, projectName, params):
    #   super(ForumUseVsEngagement, self).__init__(projectName,params)

    def getActivityLogFile(self):
        activityLogDir = os.path.join(FileSystem.getDataDir(),'ActivityLogsCoursera')
        path = os.path.join(activityLogDir, \
                self.courseDatasetInfo[self.currCourseName])
        return path

    def unzip(self, path):
        logging.info('MakeForumViewLogs.unzip(), ' + self.currCourseName)
        zipExec = RunExternal(['gunzip',path],3600)
        zipExec.run()   
        
    def zip(self,path):
        logging.info('MakeForumViewLogs.zip(), ' + self.currCourseName)
        zipExec = RunExternal(['gzip',path],3600)
        zipExec.run()   

    def getViews(self, path):
        logging.info('MakeForumViewLogs.getViews(), ' + self.currCourseName)
        views = []
        logFile = open(path)
        linecount = 1
        for line in logFile:
            if linecount % 20000 == 0:
                logging.info('\t+ getViews(): on line ' \
                            + str(linecount) + ' for ' + self.currCourseName)
            jObj = json.loads(line)
            if 'key' in jObj:
                if jObj['key'] == 'pageview':
                    url = jObj['page_url']
                    parseResult = urlparse.urlparse(url)
                    query = urlparse.parse_qs(parseResult.query)
                    if 'thread_id' in query:
                        try:
                            record = {'threadId': int(query['thread_id'][0]), \
                                    'forumUserId': jObj['username'], \
                                    'timestamp': jObj['timestamp'], \
                                    'userIp': jObj['user_ip']}
                            views.append(record)
                        except ValueError:
                            logging.info('\tError parsing line: ' + str(line))
            linecount += 1
        logFile.close()
        logging.info('\t+ getViews() finished for ' + self.currCourseName)
        return views
    
    def writeViews(self, views, path):
        logging.info('MakeForumViewLogs.writeViews(), ' + self.currCourseName)
        with open(path,'wt') as fid:
            #fid.write('forum_user_id, thread_id, timestamp, user_ip\n')
            for record,cnt in zip(views,range(len(views))):
                if cnt % 1000000 == 0:
                    logging.info('\t\t+ writeViews(): ' + str(cnt) + \
                        ' of ' + str(len(views)) + ' for ' + self.currCourseName)
                fid.write(str(record['forumUserId']) + ', ' \
                            + str(record['threadId']) + ', ' \
                            + str(record['timestamp']) + ', ' \
                            + str(record['userIp']) + '\n')

    def runner(self):
        logging.info('MakeForumViewLogs.runner(), ' + self.currCourseName)
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
            outputPath = os.path.join(outputDir, self.currCourseName + '.viewlog')

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
    projectName = 'MakeForumViewLogs'
    params = {'timeout': 10}
    controller = MakeForumViewLogs(projectName, params)
    controller.handler()




