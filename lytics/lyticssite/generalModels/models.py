# models.py
# author = Jonathan Huang

from django.db import models

class AccessGroups(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=765)
    default = models.IntegerField()
    allow_site_access = models.IntegerField()
    forum_title = models.CharField(max_length=765)
    forum_admin = models.IntegerField()
    forum_moderate = models.IntegerField()
    #forum_banned = models.IntegerField()
    admin_access = models.IntegerField()
    user_admin = models.IntegerField()
    wiki_admin = models.IntegerField()
    wiki_createpage = models.IntegerField()
    i18n_admin = models.IntegerField()
    staging_admin = models.IntegerField()
    navbar = models.IntegerField()
    dev_admin = models.IntegerField()
    log_admin = models.IntegerField()
    prereg_access = models.IntegerField()
    user_level_priority = models.IntegerField()
    class Meta:
        db_table = u'access_groups'

class Announcements(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    message = models.TextField()
    anon_user_id = models.CharField(max_length=360)
    open_time = models.IntegerField()
    close_time = models.IntegerField()
    icon = models.CharField(max_length=765)
    deleted = models.IntegerField()
    email_announcements = models.CharField(max_length=36)
    class Meta:
        db_table = u'announcements'

class AssignmentMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    open_time = models.IntegerField(null=True, blank=True)
    soft_close_time = models.IntegerField(null=True, blank=True)
    hard_close_time = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=765, blank=True)
    maximum_submissions = models.IntegerField()
    deleted = models.IntegerField()
    last_updated = models.IntegerField()
    class Meta:
        db_table = u'assignment_metadata'

class AssignmentPartMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    assignment_id = models.IntegerField()
    sid = models.CharField(max_length=765)
    part_order = models.IntegerField()
    maximum_score = models.IntegerField()
    retry_delay = models.IntegerField()
    optional = models.IntegerField()
    maximum_submissions = models.IntegerField()
    title = models.CharField(max_length=765)
    grader = models.CharField(max_length=765)
    deleted = models.IntegerField()
    class Meta:
        db_table = u'assignment_part_metadata'

class AssignmentSubmissionMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    item_id = models.IntegerField()
    anon_user_id = models.CharField(max_length=360)
    submission_time = models.IntegerField()
    submission_number = models.IntegerField()
    raw_score = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'assignment_submission_metadata'

class CourseGrades(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(unique=True, max_length=360)
    normal_grade = models.FloatField(null=True, blank=True)
    distinction_grade = models.FloatField(null=True, blank=True)
    achievement_level = models.CharField(max_length=33)
    authenticated_overall = models.IntegerField(null=True, blank=True)
    ace_grade = models.FloatField(null=True, blank=True)
    passed_ace = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'course_grades'

class HgAssessmentCalibrationGradings(models.Model):
    id = models.IntegerField(primary_key=True)
    item_number = models.IntegerField(unique=True)
    calibration_set_id = models.IntegerField()
    evaluation_id = models.IntegerField()
    type = models.CharField(max_length=42, blank=True)
    submit_time = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'hg_assessment_calibration_gradings'

class HgAssessmentEvaluationMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360)
    author_group = models.CharField(max_length=21)
    submission_id = models.IntegerField()
    start_time = models.IntegerField()
    save_time = models.IntegerField()
    submit_time = models.IntegerField(null=True, blank=True)
    grade = models.FloatField(null=True, blank=True)
    ignore = models.IntegerField()
    class Meta:
        db_table = u'hg_assessment_evaluation_metadata'

class HgAssessmentMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360)
    open_time = models.IntegerField()
    submission_deadline = models.IntegerField()
    submission_deadline_grace_period = models.IntegerField()
    grading_start = models.IntegerField()
    grading_deadline = models.IntegerField()
    grading_deadline_grace_period = models.IntegerField()
    display_grades_time = models.IntegerField()
    title = models.CharField(max_length=765)
    max_grade = models.FloatField()
    deleted = models.IntegerField()
    class Meta:
        db_table = u'hg_assessment_metadata'

class HgAssessmentOverallEvaluationMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    submission_id = models.IntegerField(unique=True)
    grade = models.FloatField(null=True, blank=True)
    final_grade = models.FloatField(null=True, blank=True)
    staff_grade = models.FloatField(null=True, blank=True)
    peer_grade = models.FloatField(null=True, blank=True)
    self_grade = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'hg_assessment_overall_evaluation_metadata'

class HgAssessmentPeerGradingMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    item_number = models.IntegerField(unique=True)
    peer_grading_set_id = models.IntegerField()
    evaluation_id = models.IntegerField()
    submit_time = models.IntegerField(null=True, blank=True)
    required = models.IntegerField()
    last_required = models.IntegerField()
    class Meta:
        db_table = u'hg_assessment_peer_grading_metadata'

class HgAssessmentPeerGradingSetMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360)
    assessment_id = models.IntegerField()
    start_time = models.IntegerField()
    finish_time = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=27)
    class Meta:
        db_table = u'hg_assessment_peer_grading_set_metadata'

class HgAssessmentSelfGradingSetMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360)
    assessment_id = models.IntegerField()
    start_time = models.IntegerField()
    finish_time = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=27)
    class Meta:
        db_table = u'hg_assessment_self_grading_set_metadata'

class HgAssessmentSubmissionMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360)
    title = models.CharField(max_length=150, blank=True)
    assessment_id = models.IntegerField()
    included_in_training = models.IntegerField()
    included_in_grading = models.IntegerField()
    included_in_ground_truth = models.IntegerField()
    excluded_from_circulation = models.IntegerField()
    anonymized_if_showcased = models.IntegerField()
    blank = models.IntegerField()
    start_time = models.IntegerField()
    save_time = models.IntegerField()
    submit_time = models.IntegerField(null=True, blank=True)
    allocation_score = models.FloatField(null=True, blank=True)
    authenticated_submission_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'hg_assessment_submission_metadata'

class HgAssessmentTrainingMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    item_number = models.IntegerField(unique=True)
    training_set_id = models.IntegerField()
    evaluation_id = models.IntegerField()
    submit_time = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'hg_assessment_training_metadata'

class HgAssessmentTrainingSetMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360)
    assessment_id = models.IntegerField()
    start_time = models.IntegerField()
    finish_time = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=21)
    class Meta:
        db_table = u'hg_assessment_training_set_metadata'

class ItemsSections(models.Model):
    item_type = models.CharField(max_length=30, primary_key=True)
    item_id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField()
    order = models.IntegerField()
    class Meta:
        db_table = u'items_sections'

class LateDaysApplied(models.Model):
    item_type = models.CharField(max_length=30, primary_key=True)
    item_id = models.IntegerField(primary_key=True)
    anon_user_id = models.CharField(max_length=360, primary_key=True)
    late_days_applied = models.IntegerField()
    class Meta:
        db_table = u'late_days_applied'

class LateDaysLeft(models.Model):
    anon_user_id = models.CharField(max_length=360, primary_key=True)
    late_days_left = models.IntegerField()
    class Meta:
        db_table = u'late_days_left'

class LectureMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    open_time = models.IntegerField(null=True, blank=True)
    soft_close_time = models.IntegerField(null=True, blank=True)
    hard_close_time = models.IntegerField(null=True, blank=True)
    maximum_submissions = models.IntegerField()
    title = models.CharField(max_length=765, blank=True)
    source_video = models.CharField(max_length=765, blank=True)
    video_length = models.FloatField(null=True, blank=True)
    quiz_id = models.IntegerField(null=True, blank=True)
    final = models.IntegerField()
    deleted = models.IntegerField()
    last_updated = models.IntegerField()
    class Meta:
        db_table = u'lecture_metadata'

class LectureSubmissionMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    item_id = models.IntegerField()
    anon_user_id = models.CharField(max_length=360)
    submission_time = models.IntegerField()
    submission_number = models.IntegerField()
    raw_score = models.FloatField(null=True, blank=True)
    action = models.CharField(max_length=24)
    class Meta:
        db_table = u'lecture_submission_metadata'

class NavbarList(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    icon = models.CharField(max_length=765)
    link_type = models.CharField(max_length=33)
    link_data = models.CharField(max_length=765)
    order = models.IntegerField()
    class Meta:
        db_table = u'navbar_list'

class QuizMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField()
    open_time = models.IntegerField(null=True, blank=True)
    soft_close_time = models.IntegerField(null=True, blank=True)
    hard_close_time = models.IntegerField(null=True, blank=True)
    maximum_submissions = models.IntegerField()
    title = models.CharField(max_length=765, blank=True)
    duration = models.IntegerField()
    quiz_type = models.CharField(max_length=24)
    proctoring_requirement = models.CharField(max_length=36)
    deleted = models.IntegerField()
    last_updated = models.IntegerField()
    class Meta:
        db_table = u'quiz_metadata'

class QuizSubmissionMetadata(models.Model):
    id = models.IntegerField(primary_key=True)
    item_id = models.IntegerField()
    anon_user_id = models.CharField(max_length=360)
    submission_time = models.IntegerField()
    submission_number = models.IntegerField()
    raw_score = models.FloatField(null=True, blank=True)
    grading_error = models.IntegerField()
    authenticated_submission_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'quiz_submission_metadata'

class Sections(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=765)
    display_order = models.IntegerField()
    last_published_date = models.IntegerField()
    visible_date = models.IntegerField()
    class Meta:
        db_table = u'sections'

class Users(models.Model):
    anon_user_id = models.CharField(max_length=360, primary_key=True)
    locale = models.CharField(max_length=30)
    timezone = models.CharField(max_length=765)
    access_group_id = models.IntegerField()
    registration_time = models.IntegerField()
    last_access_time = models.IntegerField()
    last_access_ip = models.CharField(max_length=765)
    email_announcement = models.IntegerField()
    email_forum = models.IntegerField()
    in_signature_track = models.IntegerField()
    wishes_proctored_exam = models.IntegerField(null=True, blank=True)
    email_review = models.IntegerField()
    deleted = models.IntegerField()
    class Meta:
        db_table = u'users'

class WikiPages(models.Model):
    id = models.IntegerField(primary_key=True)
    canonical_name = models.CharField(unique=True, max_length=300)
    title = models.TextField()
    creator = models.IntegerField()
    created = models.IntegerField()
    locked = models.IntegerField()
    visible = models.IntegerField()
    deleted = models.IntegerField()
    modified = models.IntegerField()
    current_revision = models.IntegerField()
    class Meta:
        db_table = u'wiki_pages'

class WikiRevisions(models.Model):
    id = models.IntegerField(primary_key=True)
    page_id = models.IntegerField()
    anon_user_id = models.CharField(max_length=360)
    timestamp = models.IntegerField()
    comments = models.CharField(max_length=765)
    class Meta:
        db_table = u'wiki_revisions'

