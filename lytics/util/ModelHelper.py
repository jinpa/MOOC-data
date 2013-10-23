# ModelHelper.py
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

class ModelHelper(object):

    @staticmethod
    def getAnonForumIdMap():
        hashmapping = HashMapping.objects.all()
        anonForumIdMap = {}
        for user in hashmapping:
            anonForumIdMap[user.anon_user_id] = user.forum_user_id
        return anonForumIdMap

    @staticmethod
    def getForumAnonIdMap():
        hashmapping = HashMapping.objects.all()
        forumAnonIdMap = {}
        for user in hashmapping:
            forumAnonIdMap[user.forum_user_id] = user.anon_user_id
        return forumAnonIdMap

    @staticmethod
    def getPostToThreadMap(posts):
        postToThreadMap = {}
        for post in posts:
            postToThreadMap[post.id] = post.thread_id
        return postToThreadMap

    @staticmethod
    def getCommentToPostMap(comments):
        commentToPostMap = {}
        for comment in comments:
            commentToPostMap[comment.id] = comment.post_id
        return commentToPostMap

    @staticmethod
    def getCommentToThreadMap(comments,posts,postToThreadMap = None):
        if postToThreadMap == None:
            postToThreadMap = ModelHelper.getPostToThreadMap(posts)
        commentToPostMap = ModelHelper.getCommentToPostMap(comments)
        commentToThreadMap = {}
        for comment in comments:
            commentToThreadMap[comment.id] = \
                postToThreadMap[commentToPostMap[comment.id]]
        return commentToThreadMap

    @staticmethod
    def getThreadToForumMap(threads):
        threadToForumMap = {}
        for thread in threads:
            threadToForumMap[thread.id] = thread.forum
