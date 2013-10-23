# CourseStats.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from lyticssite.generalModels.models import *
from lyticssite.eventModels.models import *
from lyticssite.hashMapModels.models import *
import logging

class CourseStats(object):

    @staticmethod
    def getNumThreads():
        return ForumThreads.objects.count()

    @staticmethod
    def getNumContributions():
        return ForumPosts.objects.count() + ForumComments.objects.count()

    @staticmethod
    def getNumForumViews():
        return ForumViewLog.objects.count()

    # interval is a pair of timestamps (given in seconds)
    @staticmethod
    def getNumForumViewsInInterval(interval):
        return ForumViewLog.objects.filter(timestamp__gte = interval[0]*1000, timestamp__lt = interval[1]*1000).count()

    @staticmethod
    def getNumRegisteredUsers():
        return Users.objects.count()

    @staticmethod
    def getNumContributingUsers():
        postDicts = ForumPosts.objects.all().values('forum_user_id','anonymous')
        commentDicts = ForumComments.objects.all().values('forum_user_id','anonymous')
        posts = [x['forum_user_id'] for x in postDicts if x['anonymous'] == 0]
        comments = [x['forum_user_id'] for x in commentDicts if x['anonymous'] == 0]
        return len(set(posts + comments))

    @staticmethod
    def getNumQuizSubmitters():
        submissions = QuizSubmissionMetadata.objects.exclude(raw_score__isnull = True).values('anon_user_id') 
        return CourseStats.countUnique([x['anon_user_id'] for x in submissions])

    @staticmethod
    def getNumSubscriptions():
        return ForumSubscribeThreads.objects.count()

    @staticmethod
    def getNumLectureViewers():
        submissions = LectureSubmissionMetadata.objects.all().values('anon_user_id')
        return CourseStats.countUnique([x['anon_user_id'] for x in submissions])
        
    @staticmethod
    def countUnique(x):
        return len(set(x))

    @staticmethod
    def getMaxFinalGrade():
        return max([x['normal_grade'] for x \
            in CourseGrades.objects.all().values('normal_grade')])
    
    @staticmethod
    def getKPercenters(k = 10):
        maxGrade = CourseStats.getMaxFinalGrade()
        grades = CourseGrades.objects.all().values('anon_user_id','normal_grade')
        percenters = [x['anon_user_id'] for x in grades \
                        if x['normal_grade'] > (float(k)/100.0)*maxGrade]
        return percenters

    # get people who watched at least k lectures
    @staticmethod
    def getLectureViewers(k = 1):
        viewers = [u['anon_user_id'] for u in LectureSubmissionMetadata.objects.all().values('anon_user_id')]
        tally = dict((viewer,0) for viewer in viewers)
        for viewer in viewers:
            tally[viewer] += 1
        return [viewer for viewer in tally.keys() if tally[viewer] >= k]



