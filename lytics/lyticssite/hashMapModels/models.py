# models.py
# author = Jonathan Huang

from django.db import models

class HashMapping(models.Model):
    user_id = models.IntegerField()
    anon_user_id = models.CharField(max_length=765, primary_key=True)
    forum_user_id = models.CharField(max_length=765)
    session_user_id = models.CharField(max_length=765)
    class Meta:
        db_table = u'hash_mapping'

