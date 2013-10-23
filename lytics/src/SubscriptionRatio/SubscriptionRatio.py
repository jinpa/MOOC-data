#! /usr/bin/env ipython

# SubscriptionRatio.py
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
from Controller import Controller, CourseDBError, NoGradesError
from ModelHelper import ModelHelper
import logging
from numpy import mean,std,percentile
from CourseStats import CourseStats


class SubscriptionRatio(Controller):

    # number of subscriptions by all percenters
    def countSubscriptions(self, percenters):
        subscriptions = ForumSubscribeThreads.objects.all()
        D = {}
        for s in subscriptions:
            anonUserId = self.forumAnonIdMap[s.forum_user_id]
            try:
                D[anonUserId] += 1
            except KeyError:
                D[anonUserId] = 0
        cnt = 0
        for anonUserId in percenters:
            try:
                cnt += D[anonUserId]
            except KeyError:
                pass
        return cnt

    def runner(self):
        logging.info('SubscriptionRatio.runner(), ' + self.currCourseName)

        try:
            print('Working on: ' + self.currCourseName + ' (' + self.progress() +')')
        
            self.anonForumIdMap = ModelHelper.getAnonForumIdMap()
            self.forumAnonIdMap = ModelHelper.getForumAnonIdMap()
            for k in range(100):
                percenters = CourseStats.getKPercenters(k)
                numPercenters = len(percenters)
                numSubscriptions = self.countSubscriptions(percenters)
                ratio = float(numSubscriptions)/ numPercenters
        
                path = os.path.join(self.resultsDir,'results' + str(k) + '.csv')
                with open(path,'at') as fid:
                    fid.write(self.currCourseName + ', ' \
                            + str(numSubscriptions) + ', ' \
                            + str(numPercenters) + ', ' \
                            + str(ratio) + '\n')
        except CourseDBError:
            logging.info('\t\t+ ERROR (Connection does not exist), skipping...')
            pass
        except NoGradesError:
            logging.info('\t\t+ ERROR (CourseGrades does not exist), skipping...')
            pass


if __name__ == '__main__':
    projectName = 'SubscriptionRatio'
    params = {'timeout': 10}
    controller = SubscriptionRatio(projectName, params)
    controller.handler()




