# UserMap.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from lyticssite.forumModels.models import *
from lyticssite.generalModels.models import *
from lyticssite.hashMapModels.models import *
from lyticssite.eventModels.models import *
from DBErrors import CourseDBError

class UserMap(object):

    def __init__(self, ignoreErrors):
        self._loadForumHashMap(ignoreErrors)
        self._getUserLogMap(ignoreErrors)
        self.byUser = {}
        self.byAnon = {}
        self.byForum = {}
        self.byLog = {}
        for user in self.forumHash:
            userData = {'user': user.user_id, \
                    'anon': user.anon_user_id, \
                    'forum': user.forum_user_id}
            try:
                log_id = self.userLogMap[user.user_id]
                userData['log'] = log_id
            except KeyError:
                pass
            self.byUser[user.user_id] = userData
            self.byAnon[user.anon_user_id] = userData
            self.byForum[user.forum_user_id] = userData
            if 'log' in userData:
                self.byLog[log_id] = userData

    def getByUser(self, userKey):
        return self.byUser[userKey]

    def getByAnon(self, anonKey):
        return self.byAnon[anonKey]

    def getByForum(self, forumKey):
        return self.byForum[forumKey]

    def getByLog(self, logKey):
        return self.byLog[logKey]
        
    def isMemberByUser(self, userKey):
        return userKey in self.byUser

    def isMemberByAnon(self, anonKey):
        return anonKey in self.byAnon

    def isMemberByForum(self, forumKey):
        return forumKey in self.byForum

    def isMemberByLog(self, logKey):
        return logKey in self.byLog

    # force eager loading of databases
    def _loadForumHashMap(self, ignoreErrors):
        try:
           self.forumHash = list(HashMapping.objects.all())
        except:
            if not ignoreErrors:
                raise CourseDBError
            else:
                self.forumHash = []

    def _loadLogHashMap(self, ignoreErrors):
        try:
            self.logHashMap = list(LogHashMapping.objects.all())
        except:
            if not ignoreErrors:
                raise CourseDBError
            else:
                self.logHashMap = []

    def _getUserLogMap(self, ignoreErrors):
        self._loadLogHashMap(ignoreErrors)
        self.userLogMap = {}
        for user in self.logHashMap:
            self.userLogMap[user.user_id] = user.log_user_id


