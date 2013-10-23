# ThreadDistribution.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from Controller import Controller
from DBErrors import *
from ModelHelper import ModelHelper
import logging
from CourseStats import CourseStats
from numpy import mean, std, percentile

typeCategories = ['general','social','content','support','other']

class ThreadDistribution(Controller):

    def buildForumIndex(self):
        self.ForumById = {}
        for forum in self.forums:
            self.ForumById[forum.id] = forum

    def findTop(self, idx):
        while self.ForumById[idx].parent_id > 0:
            idx = self.ForumById[idx].parent_id
        return idx

    def categorize(self, name):
        nameLower = name.lower()
        for typeList, idx in zip(self.forumTypes, range(len(self.forumTypes))):
            if nameLower in typeList:
                return idx
        print('\t*** Placing forum=' + nameLower + ' in Other category')
        return len(self.forumTypes)

    # creates map from forum id numbers to a category
    def getForumNameMap(self):
        self.nameMap = {}
        for forum in self.forums:
            if forum.parent_id < 0:
                continue
            topMostIdx = self.findTop(forum.id)
            forumName = self.ForumById[topMostIdx].name
            self.nameMap[forum.id] = self.categorize(forumName)

    def findDistribution(self):
        dist = len(typeCategories) * [0]
        for thread in self.threads:
            try:
                dist[self.nameMap[thread.forum_id]] += 1.0
            except:
                print(self.ForumById[thread.forum_id].parent_id)
                #print(self.nameMap[thread.forum_id])
        invZ = 1.0/float(sum(dist))
        return [x*invZ for x in dist]

    @Controller.logged
    def checkForDB(self):
        try:
            if ForumThreads.objects.count() < 100:
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
            #sys.exit()
            return

        try:
            self.threads = list(ForumThreads.objects.all())
            self.forums = list(ForumForums.objects.all())
        except:
            return
            #raise CourseDBError

        self.forumTypes = FileSystem.loadForumTypes()
        self.buildForumIndex()
        self.getForumNameMap()
        dist = self.findDistribution()

        path = os.path.join(self.getMainResultsDir(),self.getCourseName() + '.csv')
        with open(path,'wt') as fid:
            for n,x in zip(typeCategories,dist):
                fid.write(n + ', ' + str(x) + '\n')


if __name__ == '__main__':
    projectName = 'ForumTypes'
    params = {'timeout': 10}
    controller = ThreadDistribution(projectName, params)
    controller.handler()
