#!/usr/local/bin/python

"""
call with the arguments:
    "create" to create the per course, per user table with posting and grade data 
    "populate" to put the data in
    "aggregate" to create an aggregate per-course per-date table
    "verbose" for verbose output
    "index" to create indices

The script expects to find a LyticsUser.txt file in the same directory, telling it USER, PASSWORD, SERVER info 
Contents of that file can look like this:
USER me
PASSWORD mypw
SERVER myserver.edu

Also expects a file called Posts-db-list.csv in the same directory with a list of coursenames that 
 correspond to db names.  Indivdual courses can be commented out w/ #.


"""

import sys
import MySQLdb as mdb
import json

if ('verbose' in sys.argv):
    verbose = True
else:
    verbose = False

localcon = mdb.connect('localhost', 'root', '', 'aggy');

#get the connection usernmae/pw from the settings file
connInfo = {}
with open('LyticsUser.txt') as f:
    for line in f:
       (key, val) = line.split()
       connInfo[key] = val

lyticscon = mdb.connect(connInfo['SERVER'],connInfo['USER'], connInfo['PASSWORD'])

classes=[]
with open('Posts-db-list.csv') as f:
    for line in f:
        if (line[0] != "#"):
            classes.append(line.strip())

with localcon:
    localcur=localcon.cursor()

if ('create' in sys.argv):
    #we're creating the table to hold the aggregates

    query = ("create table courses_users_grades_posts  ( \
        course varchar(120),\
        user_id int(11), \
        posts int default 0, \
        grade float default 0, \
        decile int default 0, \
        reputation float default 0, \
        user_type int default 0, \
        achievement_level enum('normal','distinction','none'), \
        anon_username varchar(120), \
        forum_user_id varchar(120));")

    if (verbose):
        print (query)

    localcur.execute(query)

if ('populate' in sys.argv):

    #we're inserting into an existing table

    with lyticscon:
        lyticscur=lyticscon.cursor()

        for course in classes:
            hmdb = course + "_hash_mapping"
            forumdb = course + "_anonymized_forum"
            generaldb = course + "_anonymized_general"

            query = ("select \"%s\" as course, hm.user_id, cg.anon_user_id, cg.normal_grade, floor(normal_grade/10) as decile, \
                cg.achievement_level, hm.forum_user_id, u.access_group_id as user_type, \
                        (select COUNT(*) from `%s`.forum_posts fp\
                        where fp.forum_user_id = hm.`forum_user_id`\
                        group by hm.forum_user_id) as num_posts, \
                (select points from `%s`.forum_reputation_points frp where frp.forum_user_id = hm.forum_user_id) as points \
                    from `%s`.course_grades cg\
                    left join\
                         `%s`.hash_mapping hm\
                          on (cg.anon_user_id = hm.anon_user_id) \
                    left join `%s`.users u \
                        on (cg.anon_user_id = u.anon_user_id) \
                     ;" % (course, forumdb, forumdb, generaldb, hmdb, generaldb))

            if (verbose):
                print (query)
            lyticscur.execute(query)

            rows=lyticscur.fetchall()
            errors=0
            for row in rows:

                #order of fields fetched: course, user_id, anon_user_id, grade, decile, achievement_level, forum_user_id, user_type, posts, reputation
                user_id = row[1]
                anon_user_id = row[2]
                grade=row[3]
                decile=row[4]
                achievement_level=row[5]
                forum_user_id=row[6]
                user_type=row[7]
                posts=row[8] or 'NULL'
                reputation=row[9] or 'NULL'
               
                if (user_id):

                    query = ("INSERT INTO courses_users_grades_posts\
                            (course, user_id, posts, grade, decile, reputation, user_type, achievement_level, anon_username, forum_user_id) \
                            VALUES (\'%s\', %s, %s, %s, %s, %s, %s, \'%s\', \'%s\', \'%s\'); \
                            " % (course, user_id, posts, grade, decile, reputation, user_type,achievement_level,anon_user_id, forum_user_id))
                    if (verbose):
                        print query
                    localcur.execute(query)
                else:
                    errors += 1    
            localcon.commit()
            print ("Done with %s.  Errors: %s") % (course, str(errors))

if ('index' in sys.argv):
    indices = ['course', 'user_id', 'posts', 'decile', 'user_type', 'achievement_level']
    for col in indices:
        query = "create index %s_index on courses_users_grades_posts (%s);" % (col,col)
        if verbose:
            print query
        localcur.execute(query)



if ('aggregate' in sys.argv):

    query = "CREATE TABLE courses_posters AS \
        (select course, user_type, posts, count(*) as users, avg(grade) as avgrade \
        from courses_users_grades_posts \
        group by course, user_type, posts);"      
    if verbose:
        print query
    localcur.execute(query)  
    localcon.commit()
    query = "create index posts_index on courses_posters(posts);"
    localcur.execute(query)
    query = "create index course_index on courses_posters(course);"
    localcur.execute(query)

 
