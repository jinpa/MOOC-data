#!/usr/local/bin/python

"""
Script to turn a Coursera event log file into a mysql table listing anon_user_id's and # of forum views for each student in the course.
Give it the name of the eventlog file as the first command line argument.
Other possible arguments are "verbose", "create", and "insert"

It's not a bad idea to grep the logfile first for the expression "thread_id", and then just run this script on the output of that.

TODO:  some users may want to output csv to STDOUT rather than writing to a mysql db - should make an option to do that.
"""


import sys, json, re
import MySQLdb as mdb

if ('nodb' not in sys.argv):
    localcon = mdb.connect('localhost', 'root', '', 'aggy')
    with localcon:
        localcur=localcon.cursor()

ClickDict={}
StudentCounts={}
verbose = False
clickstream = open(sys.argv[1])
if ('verbose' in sys.argv):
    verbose = True

thread = re.compile("forum/thread\?thread_id")

def addOne(studentID):
    if studentID in StudentCounts:
        StudentCounts[studentID] +=1
    else:
        StudentCounts[studentID] = 1


#with open(infile) as clickstream:

for line in clickstream:    

    ClickDict = eval(line)  
    
    if (verbose):
        for key in ClickDict:
            print ("%s:%s" % (key, ClickDict[key]))
    

    result = thread.search(ClickDict ['page_url'])
    if (result):
        if (verbose):
            print ("got one!")
        addOne(ClickDict['username'])

if (verbose):
    for student in StudentCounts:
        print ("%s:%s" % (student, StudentCounts[student]))

if ('create' in sys.argv):

    CreateStatement = ("create table forum_views (course varchar(120), anon_user_id varchar(120), views float);")
    #if (verbose):
    #    print (CreateStatement)
    localcur.execute(CreateStatement)
    localcon.commit()

if ('insert' in sys.argv):

    for studentID in StudentCounts.keys():
        InsertStatement = ("INSERT INTO forum_views \
                            (course, anon_user_id, views) \
                            VALUES ('-20130422-0720-12-002-crypto',\'%s\',%s);" % \
                            (studentID, str(StudentCounts[studentID])))
        if (verbose):
            print (InsertStatement)
        localcur.execute(InsertStatement)
        localcon.commit()

clickstream.close()
