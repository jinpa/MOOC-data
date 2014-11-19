#!/usr/local/bin/python

"""
call with the arguments:
    "populate" to get the data
    "verbose" for verbose output

The script expects to find a DSUser.txt file in the same directory, telling it USER, PASSWORD, SERVER info 
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

#get the connection usernmae/pw from the settings file
connInfo = {}
with open('DSUser.txt') as f:
    for line in f:
       (key, val) = line.split()
       connInfo[key] = val

DScon = mdb.connect(connInfo['SERVER'],connInfo['USER'], connInfo['PASSWORD'])

def DoQuery(con, query):

    if (verbose):
        print (query)
    con.execute(query)

    rows=con.fetchall()
    return rows


classes=[]
with open('Posts-db-list.csv') as f:
    for line in f:
        if (line[0] != "#"):
            classes.append(line.strip())


if ('populate' in sys.argv):

    #we're inserting into an existing table

    print ("course, registered, completed, posts, posters, ngt2, ngt10, startdate,\
        perc-completing, posters:registered, posters:completers, bigposters:registered, bigposters:completers, \
        vbigposters:registered, vbigposters:completers, \
        posters:posts, bigposters:posts, posts:registered, posts:completers")

    with DScon:
        DScur=DScon.cursor()

        for course in classes:
            hmdb = "coursera_" + course + "_hash_mapping"
            forumdb = "coursera_" + course + "_anonymized_forum"
            generaldb = "coursera_" + course + "_anonymized_general"

            query=("select count(*) as posts, count(distinct user_id) as posters from \
                (select user_id from `%s`.forum_posts union all select user_id from `%s`.forum_comments)  \
                as PostsPlus;\
            "% (forumdb, forumdb))

            result = DoQuery(DScur,query)
            posts = result[0][0]
            posters = result [0][1]
       
            if (verbose):
                print ("posts: " + str(posts))
                print ("posters: " + str(posters))

            query=("select count(*) from \
                (\
                select user_id, count(*) as posts from \
                (select user_id from `%s`.forum_posts union all select user_id from `%s`.forum_comments)  as PostsPlus \
                group by user_id having posts >2) as bigPosters;" % (forumdb, forumdb))
            
            ngt2 = DoQuery(DScur,query)[0][0]

            query=("select count(*) from \
                (\
                select user_id, count(*) as posts from \
                (select user_id from `%s`.forum_posts union all select user_id from `%s`.forum_comments)  as PostsPlus \
                group by user_id having posts >10) as bigPosters;" % (forumdb, forumdb))
            
            ngt10 = DoQuery(DScur,query)[0][0]

            if (verbose):
                print ("> 2 posts: " + str(ngt2))

            query=("select count(*) from `%s`.course_grades where achievement_level != 'none';" % (generaldb))
            
            passers = DoQuery(DScur,query)[0][0]

            if (verbose):
                print ("passers: " + str(passers))

            query = ("select count(*) from `%s`.users;" % (generaldb))
            registered = DoQuery(DScur,query)[0][0]
            if (verbose):
                print ("registered: " + str(registered))

            query = ("select date(from_unixtime((min(open_time)))) from `%s`.announcements;" % (generaldb))
            startdate = DoQuery(DScur,query)[0][0]
            if (verbose):
                print ("registered: " + str(registered))

            # calculate derived values

            percCompleted = float(passers)/float(registered)
            pToR = float(posters)/float(registered)
            pToC = float(posters) / float(passers)
            bpToR = float(ngt2) / float(registered)
            vbpToR = float(ngt10) / float(registered)
            vbpToC =  float(ngt10) / float(passers)
            bpToC = float(ngt2) / float(passers)
            npToP = float(posters) / float(posts)
            bpToP = float(ngt2) / float(posts)
            npToC = float(posts) / float (passers)
            npToR = float(posts) / float(registered)


            if (verbose):
                print ("Done with %s.") % (course)

            print ("%s, %s, %s, %s, %s, %s, %s, %s, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f" % \
                (course, registered, passers, posts, posters, ngt2, ngt10, startdate, \
                percCompleted, pToR, pToC, bpToR, bpToC, \
                vbpToR, vbpToC, \
                npToP, bpToP, npToR, npToC))

         




            




 
