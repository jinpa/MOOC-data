# models.py
# author = Jonathan Huang

import sys
import os.path
sys.path.append('../../util')
from Text import Text
from django.db import models

class ActivityLog(models.Model):
    id = models.IntegerField(primary_key=True)
    forum_user_id = models.CharField(max_length=255)
    module = models.CharField(max_length=765)
    action = models.CharField(max_length=765)
    item_id = models.IntegerField()
    metadata = models.TextField()
    timestamp = models.IntegerField()
    class Meta:
        db_table = u'activity_log'

class ForumForums(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    name = models.CharField(max_length=765)
    description = models.TextField()
    type = models.CharField(max_length=15)
    deleted = models.IntegerField()
    can_post = models.IntegerField()
    show_threads = models.IntegerField()
    resolved_tag = models.IntegerField()
    display_order = models.IntegerField()
    open_time = models.IntegerField()
    class Meta:
        db_table = u'forum_forums'

class ForumThreads(models.Model):
    id = models.IntegerField(primary_key=True)
    forum_id = models.IntegerField()
    forum = models.ForeignKey(ForumForums, db_column = 'forum_id')
    forum_user_id = models.CharField(max_length=255)
    posted_time = models.IntegerField()
    last_updated_time = models.IntegerField()
    last_updated_user = models.IntegerField()
    deleted = models.IntegerField()
    is_spam = models.IntegerField()
    stickied = models.IntegerField()
    approved = models.IntegerField()
    unresolved = models.IntegerField()
    instructor_replied = models.IntegerField()
    num_posts = models.IntegerField()
    num_views = models.IntegerField()
    votes = models.IntegerField()
    locked = models.IntegerField()
    anonymous = models.IntegerField()
    title = models.TextField()

    def getPosts(self):
        return self.forumposts_set.all()

    def getComments(self):
        comments = []
        for p in self.getPosts():
            comments += p.forumcomments_set.all()
        return comments

    def numComments(self):
        return len(self.getComments())

    def avgPostLength(self):
        return float(sum([len(p) for p in self.getPosts()]))/self.num_posts

    def avgCommentLength(self):
        comments = self.getComments()
        try:
            return float(sum([len(p) for p in comments]))/len(comments)
        except ZeroDivisionError:
            return 0

    def getContributorIds(self):
        posters = [p.forum_user_id for p in sef.getPosts] 
        commenters = [c.forum_user_id for c in self.getComments()]
        return set(posters + commenters)

    class Meta:
        db_table = u'forum_threads'


class ForumPosts(models.Model):
    id = models.IntegerField(primary_key=True)
    thread_id = models.IntegerField()
    thread = models.ForeignKey(ForumThreads, db_column = 'thread_id')
    forum_user_id = models.CharField(max_length=255)
    post_time = models.IntegerField()
    edit_time = models.IntegerField()
    deleted = models.IntegerField()
    is_spam = models.IntegerField()
    original = models.IntegerField()
    stickied = models.IntegerField()
    approved = models.IntegerField()
    anonymous = models.IntegerField()
    votes = models.IntegerField()
    post_text = models.TextField()
    user_agent = models.TextField()
    text_type = models.CharField(max_length=24)

    def __len__(self):
        string = Text(self.post_text)
        return string.getNumTokens()

    class Meta:
        db_table = u'forum_posts'

class ForumComments(models.Model):
    id = models.IntegerField(primary_key=True)
    post_id = models.IntegerField()
    post = models.ForeignKey(ForumPosts, db_column = 'post_id')
    forum_user_id = models.CharField(max_length=255)
    post_time = models.IntegerField()
    deleted = models.IntegerField()
    is_spam = models.IntegerField()
    votes = models.IntegerField()
    anonymous = models.IntegerField()
    comment_text = models.TextField()
    user_agent = models.TextField()
    text_type = models.CharField(max_length=24)

    def __len__(self):
        string = Text(self.comment_text)
        return string.getNumTokens()

    class Meta:
        db_table = u'forum_comments'

class ForumReporting(models.Model):
    id = models.IntegerField(primary_key=True)
    forum_user_id = models.CharField(unique=True, max_length=255)
    report_type = models.CharField(max_length=39)
    item_type = models.CharField(max_length=21)
    item_id = models.IntegerField()
    description = models.TextField()
    timestamp = models.IntegerField()
    class Meta:
        db_table = u'forum_reporting'

class ForumReputationPoints(models.Model):
    forum_user_id = models.CharField(max_length=255, primary_key=True)
    points = models.IntegerField()
    class Meta:
        db_table = u'forum_reputation_points'

class ForumReputationRecord(models.Model):
    forum_user_id = models.CharField(unique=True, max_length=255)
    pc_id = models.IntegerField()
    type = models.CharField(max_length=21)
    direction = models.IntegerField()
    timestamp = models.IntegerField()
    class Meta:
        db_table = u'forum_reputation_record'

class ForumSubscribeForums(models.Model):
    forum_user_id = models.CharField(unique=True, max_length=255)
    forum_id = models.IntegerField(unique=True)
    start_time = models.IntegerField()
    class Meta:
        db_table = u'forum_subscribe_forums'

class ForumSubscribeThreads(models.Model):
    # WARNING: weird django primary_key hack here!
    forum_user_id = models.CharField(unique=True, \
            max_length=255, primary_key=True)
    thread_id = models.IntegerField(unique=True)
    start_time = models.IntegerField()
    class Meta:
        db_table = u'forum_subscribe_threads'

class ForumTags(models.Model):
    id = models.IntegerField(primary_key=True)
    tag_name = models.CharField(unique=True, max_length=255, blank=True)
    class Meta:
        db_table = u'forum_tags'

class ForumTagsThreads(models.Model):
    tag_id = models.IntegerField()
    thread_id = models.IntegerField(unique=True)
    timestamp = models.IntegerField()
    class Meta:
        db_table = u'forum_tags_threads'


class KvsCourseForumReadrecord(models.Model):
    key = models.TextField(primary_key=True)
    value = models.TextField(blank=True)
    class Meta:
        db_table = u'kvs_course.120.forum_readrecord'

