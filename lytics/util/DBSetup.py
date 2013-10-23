# DBSetup.py
# author = Jonathan Huang
from django.core.management import setup_environ
import sys,os
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())

os.environ['DJANGO_SETTINGS_MODULE'] = 'lyticssite.settings'
from django.conf import settings
#setup_environ(settings)

from Course import Course
from DBRouter import DBRouter
from django.db import router 

class DBSetup(object):
    
    #def __init__():
    #    self.DBList = FileSystem.loadDBList()

    @staticmethod
    def switch(course):
        currRouter = DBRouter()
        #currRouter.courseName = courseName
        currRouter.setCourse(course)
        router.routers = [currRouter]
    

