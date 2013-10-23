#! /usr/bin/env ipython

# testDB.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from lyticssite.generalModels.models import *
from lyticssite.eventModels.models import *

courseDatasetInfo = FileSystem.loadCourseDatasetInfo()

for course in courseDatasetInfo:
    print(course.name)

    DBSetup.switch(course)
 
    #print('\t-----------------')
    #forums = ForumForums.objects.all()
    try:
        userCount = Users.objects.count()
        print('\tUser Count: ' + str(userCount))
    except:
        pass
    try:
        surveyCount = Demographic.objects.count()
        print('\tSurvey response count: ' + str(surveyCount))
    except:
        pass
    

