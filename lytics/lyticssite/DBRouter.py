# DBRouter.py
# author = Jonathan Huang
import sys,os
sys.path.append('../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
import settings
from Course import Course

class DBRouter(object):

    def __init__(self):
        self.course = {}

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'forumModels':
            return self._getForumDBName()
        if model._meta.app_label == 'generalModels':
            return self._getGeneralDBName()
        if model._meta.app_label == 'hashMapModels':
            return self._getHashMapDBName()
        if model._meta.app_label == 'eventModels':
            return self._getEventDBName()
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        if db == 'default':
            return True
        return False

    def setCourse(self, course):
        self.course = course

    def _getForumDBName(self):
        return self.course.dbName + '_anonymized_forum'
    
    def _getGeneralDBName(self):
        return self.course.dbName + '_anonymized_general'

    def _getHashMapDBName(self):
        return self.course.dbName + '_hash_mapping'

    def _getEventDBName(self):
        return 'activity_' + self.course.name

