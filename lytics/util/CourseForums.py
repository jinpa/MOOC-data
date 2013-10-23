# CourseForums.py
# author = Jonathan Huang
import sys
sys.path.append('../util')
from FileSystem import FileSystem

sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from lyticssite.forumModels.models import *
from lyticssite.eventModels.models import ForumViewLog
from operator import itemgetter

class CourseForums:
    FORUMTYPES = ['general', 'social', 'content', 'support', 'other']

    def __init__(self):
        self.forumTypes = list(FileSystem.loadForumTypes())
        self.forums = list(ForumForums.objects.all())
        self.threads = list(ForumThreads.objects.all())
        self.posts = list(ForumPosts.objects.all())
        self.comments = list(ForumComments.objects.all())
        self.reputations = list(ForumReputationPoints.objects.all())
        try:
            self.views = list(ForumViewLog.objects.all())
        except:
            pass
        self._buildForumIndex()
        self._getForumParentMap()
        self._getForumTypeMap()
        self._getThreadToForumMap()
        self._getThreadToPostMap()
        self._getPostToThreadMap()
        self._getPostToForumMap()
        self._getCommentToPostMap()
        self._getCommentToThreadMap()
        self._getCommentToForumMap()
        try:
            self._getViewToThreadMap()
        except:
            pass

    def getThreadsByType(self, type):
        return [t for t in self.threads if self.getThreadType(t.id) == type]

    def getPostsByType(self, type):
        return [p for p in self.posts if self.getPostType(p.id) == type]

    def getCommentsByType(self, type):
        return [c for c in self.comments if self.getCommentType(c.id) == type]

    def getViewsByType(self, type):
        return [v for v in self.views if self.getViewType(v.id) == type]

    def getThreadType(self, threadId):
        return self.forumTypeMap[self.threadToForumMap[threadId]]

    def getPostType(self, postId):
        return self.forumTypeMap[self.postToForumMap[postId]]

    def getCommentType(self, commentId):
        return self.forumTypeMap[self.commentToForumMap[commentId]]

    def getViewType(self, viewId):
        return self.getThreadType(self.viewToThreadMap[viewId])

    # as needed maps
    def getForumUserToThreadMap(self):
        try:
            self.forumUserToThreadMap
        except AttributeError:
            self.forumUserToThreadMap = {}
            for thread in self.threads:
                try:
                    self.forumUserToThreadMap[thread.forum_user_id].append(thread)
                except KeyError:
                    self.forumUserToThreadMap[thread.forum_user_id] = [thread]

    def getForumUserToPostMap(self):
        try:
            self.forumUserToPostMap
        except AttributeError:
            self.forumUserToPostMap = {}
            for post in self.posts:
                try:
                    self.forumUserToPostMap[post.forum_user_id].append(post)
                except KeyError:
                    self.forumUserToPostMap[post.forum_user_id] = [post]

    def getForumUserToCommentMap(self):
        try:
            self.forumUserToCommentMap
        except AttributeError:
            self.forumUserToCommentMap = {}
            for comment in self.comments:
                try:
                    self.forumUserToCommentMap[comment.forum_user_id].append(comment)
                except KeyError:
                    self.forumUserToCommentMap[comment.forum_user_id] = [comment]

    def getForumUserToReputationMap(self):
        try:
            self.forumUserToReputationMap
        except AttributeError:
            self.forumUserToReputationMap = {}
            self.getForumUserToNumContributions()
            for record in self.reputations:
                self.forumUserToReputationMap[record.forum_user_id] = record.points
            for forum_user_id in self.forumUserToNumContributionsMap:
                if forum_user_id not in self.forumUserToReputationMap:
                    self.forumUserToReputationMap[forum_user_id] = 0

    def getForumUserToNumContributions(self):
        try:
            self.forumUserToNumContributionsMap
        except AttributeError:
            self.forumUserToNumContributionsMap = {}
            self.getForumUserToPostMap()
            self.getForumUserToCommentMap()
            for forumUserId in self.forumUserToPostMap:
                try:
                    self.forumUserToNumContributionsMap[forumUserId] += len(self.forumUserToPostMap[forumUserId])
                except KeyError:
                    self.forumUserToNumContributionsMap[forumUserId] = len(self.forumUserToPostMap[forumUserId])
            for forumUserId in self.forumUserToCommentMap:
                try:
                    self.forumUserToNumContributionsMap[forumUserId] += len(self.forumUserToCommentMap[forumUserId])
                except KeyError:
                    self.forumUserToNumContributionsMap[forumUserId] = len(self.forumUserToCommentMap[forumUserId])

    def getPostRankMap(self):
        try:
            self.postRankMap
        except AttributeError:
            self.postRankMap = {}
            for thread in self.threads:
                times = [(post.id, post.post_time) for post in self.threadToPostMap[thread.id]]
                sortedPairs = sorted(times, key = itemgetter(1))
                sortedIds = [x[0] for x in sortedPairs]
                for postId,rank in zip(sortedIds,range(len(sortedIds))):
                    self.postRankMap[postId] = rank

    # there are people who are contributors who don't have
    # a recorded reputation
    def sortForumUsersByContributions(self):
        self.getForumUserToNumContributions()
        sortedForumUsers = sorted(self.forumUserToNumContributionsMap.iteritems(), key = itemgetter(1), reverse = True)
        return [x[0] for x in sortedForumUsers]

    def sortForumUsersByReputation(self):
        self.getForumUserToReputationMap()
        sortedForumUsers = sorted(self.forumUserToReputationMap.iteritems(), key = itemgetter(1), reverse = True)
        return [x[0] for x in sortedForumUsers]

    # always computed
    def _buildForumIndex(self):
        self.forumById = {}
        for forum in self.forums:
            self.forumById[forum.id] = forum

    def _getForumTypeMap(self):
        self.forumTypeMap = {}
        for forum in self.forums:
            if forum.parent_id < 0:
                continue
            highestForumId = self._findHighestForum(forum.id)
            forumName = self.forumById[highestForumId].name
            self.forumTypeMap[forum.id] = self._categorize(forumName)

    def _getForumParentMap(self):
        self.forumParentMap = {}
        for forum in self.forums:
            self.forumParentMap[forum.id] = forum.parent_id

    def _getThreadToForumMap(self):
        self.threadToForumMap = {}
        for thread in self.threads:
            self.threadToForumMap[thread.id] = thread.forum_id

    def _getThreadToPostMap(self):
        self.threadToPostMap = {}
        for post in self.posts:
            try:
                self.threadToPostMap[post.thread_id].append(post)
            except KeyError:
                self.threadToPostMap[post.thread_id] = [post]

    def _getPostToThreadMap(self):
        self.postToThreadMap = {}
        for post in self.posts:
            self.postToThreadMap[post.id] = post.thread_id

    def _getPostToForumMap(self):
        self.postToForumMap = {}
        for post in self.posts:
            self.postToForumMap[post.id] = \
                self.threadToForumMap[self.postToThreadMap[post.id]]

    def _getCommentToPostMap(self):
        self.commentToPostMap = {}
        for comment in self.comments:
            self.commentToPostMap[comment.id] = comment.post_id

    def _getCommentToThreadMap(self):
        self.commentToThreadMap = {}
        for comment in self.comments:
            self.commentToThreadMap[comment.id] = \
                self.postToThreadMap[self.commentToPostMap[comment.id]]

    def _getCommentToForumMap(self):
        self.commentToForumMap = {}
        for comment in self.comments:
            self.commentToForumMap[comment.id] = \
                self.threadToForumMap[self.commentToThreadMap[comment.id]]

    def _getViewToThreadMap(self):
        self.viewToThreadMap = {}
        for view in self.views:
            self.viewToThreadMap[view.id] = view.thread_id

    def _findHighestForum(self, forumId):
        while self.forumParentMap[forumId] > 0:
            forumId = self.forumParentMap[forumId]
        return forumId

    def _categorize(self, forumName):
        forumNameLower = forumName.lower()
        for typeList, idx in zip(self.forumTypes, range(len(self.forumTypes))):
            if forumNameLower in typeList:
                return idx
        return len(self.forumTypes)