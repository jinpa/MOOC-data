#!/usr/local/bin/python

"""
call with the argument "create" to create the intermediate table, 
"populate" to put the data in, and "gt" to update the posts-greater-than fields

The script expects to find a LyticsUser.txt file in the same directory, telling it USER, PASSWORD, SERVER info 
Contents of that file can look like this:
USER me
PASSWORD mypw
SERVER myserver.edu

TODO: get the list course courses out of the code, and put it in a file
"""

import sys
import MySQLdb as mdb
import json

localcon = mdb.connect('localhost', 'root', '', 'aggy');

#get the connection usernmae/pw from the settings file
connInfo = {}
with open('LyticsUser.txt') as f:
    for line in f:
       (key, val) = line.split()
       connInfo[key] = val

lyticscon = mdb.connect(connInfo['SERVER'],connInfo['USER'], connInfo['PASSWORD'])


classes=['-20130421-2305-12feb-gametheory',
         '-20130421-2305-12jan-algo1',
         '-20130421-2305-12jan-crypto',
         '-20130421-2305-12jan-pgm',
         '-20130422-0245-12jan-ml',
         '-20130422-0337-12feb-cs101',
         '-20130422-0459-12mar-automata',
         '-20130422-0522-12mar-intrologic',
         '-20130422-0530-12apr-compilers',
         '-20130422-0632-12jan-hci', 
         '-20130422-0720-12-002-crypto',
         '-20130422-0809-12-002-algo',
         '-20130422-0919-12-002-ml',
         '-20130422-0936-002-crypto',
         '-20130422-1039-005-crypto',
         '-20130422-1151-12-001-algo2',
         '-20130422-1204-12-002-gametheory',
         '-20130422-1206-12-003-algo', 
         '-20130422-2135-12-001-organalysis',
         '-20130506-1717-compilers-003',
         '-20130531-1829-12-001-maththink',
         '_2012_hci',
         '_2012_logic',
       #  '_2012_maththink', - missing table in hashmap db
         '_2012_ml',
         '_2012_pgm',
         '_2012_sciwri',
         ]


#classes = ['-20130421-2305-12feb-gametheory',
 #        '-20130421-2305-12jan-algo1']


with localcon:
    localcur=localcon.cursor()

if ('create' in sys.argv):
#if (len(sys.argv)>1 and sys.argv[1] == 'create'):
    #create an aggregate table
    localcur.execute("create table grades_posts  ( \
        course varchar(120),\
        anon_user_id varchar(120), \
        normal_grade float, \
        decile float, \
        forum_user_id varchar(120), \
        num_posts float, \
        no_posts float default 0, \
        gt0 float default 0, \
        gt1 float default 0, \
        gt2 float default 0, \
        gt3 float default 0, \
        gt4 float default 0, \
        reputation float default 0, \
        user_type float default 0);")

if ('populate' in sys.argv):
#if (len(sys.argv)>1 and sys.argv[1] == 'populate'):
    #we're not creating a new aggregate table, we're inserting into an existing one

    with lyticscon:
        lyticscur=lyticscon.cursor()

        for course in classes:
            hmdb = "coursera" + course + "_hash_mapping"
            forumdb = "coursera" + course + "_anonymized_forum"
            generaldb = "coursera" + course + "_anonymized_general"

            query = ("select \"%s\" as course, cg.anon_user_id, cg.normal_grade, floor(normal_grade/10) as decile, \
                hm.forum_user_id, u.access_group_id, \
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

            #print (query)
            lyticscur.execute(query)

            rows=lyticscur.fetchall()

            for row in rows:

                #order of fields: course, anon_user_id, normal_grade, decile, forum_user_id, access_group_id, num_posts, points
                query = ("INSERT INTO grades_posts (course, anon_user_id, normal_grade, decile, forum_user_id, \
                    user_type, num_posts, reputation) VALUES (\'%s\', \'%s\', %s, %s, \'%s\', %s, %s, %s)" % (row[0], row[1], \
                    row[2], row[3], row[4], int(row[5] or 0), int(row[6] or 0), int(row[7] or 0)))
                #print query
                localcur.execute(query)
            localcon.commit()
            print ("done with %s" % course)

if ('update' in sys.argv):
#if (len(sys.argv)>1 and sys.argv[1] == 'updates'):

    #set the 'greater-than' fields

    query = "UPDATE grades_posts set gt4= if(num_posts>4,1,0), gt3 = if(num_posts>3,1,0),  gt2 = if(num_posts>2,1,0),  \
        gt1 = if(num_posts>1,1,0), gt0 = if(num_posts>0,1,0), no_posts = if(num_posts=0,1,0);"      
    print query
    localcur.execute(query)  
    localcon.commit()

if ('aggregate' in sys.argv):

    query = "CREATE TABLE aggregates AS \
        (select course, decile, user_type, sum(num_posts) as totalposts, (sum(no_posts) + sum(gt0)) as students, sum(no_posts) as no_posts, \
        (sum(no_posts) / (sum(no_posts) + sum(gt0))) as percent_no_posts, \
        (sum(gt0) / (sum(no_posts) + sum(gt0))) as percent_gt0, \
        (sum(gt1) / (sum(no_posts) + sum(gt0))) as percent_gt1, \
        (sum(gt2) / (sum(no_posts) + sum(gt0))) as percent_gt2, \
        (sum(gt3) / (sum(no_posts) + sum(gt0))) as percent_gt3, \
        (sum(gt4) / (sum(no_posts) + sum(gt0))) as percent_gt4, \
        sum(gt0) as gt0, sum(gt1) as gt1, sum(gt2) as gt2, sum(gt3) as gt3, sum(gt4) as gt4, \
        avg(reputation) as avg_reputation \
        from grades_posts\
        group by course, decile, user_type);"      
    print query
    localcur.execute(query)  
    localcon.commit()

 
