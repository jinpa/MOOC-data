#! /usr/bin/env python

# splitList.py
# author = Jonathan Huang



fname = 'courseList_raw.txt'
fid = open(fname)
rows = fid.readlines()
fid.close()

courses = set([])
suffixes = ['anonymized_forum','anonymized_general','hash_mapping','unanonymizable']
for r in rows:
    s = r.split(' ')[1]
    #if s[-5:] == 'forum':
    #    print(s)
    #print(s)
    suffIdx = -1
    for suff in suffixes:
        suffIdx = max(suffIdx,s.find(suff))
    if suffIdx < 0:
        continue
    prefix = s[:suffIdx-1]
    suffix = s[suffIdx:]
    if prefix.find('2013')==-1:
        continue
    courses.add(prefix)
courseDict = {}
for c in courses:
    cList = c.split('-')
    try:
        int(cList[-1])
        baseCourse = cList[-2]
    except:
        baseCourse = cList[-1]
    try:
        courseDict[baseCourse].append(c)
    except:
        courseDict[baseCourse] = [c]
    print(c)
           
#for c in courseDict:
    #print(c)
    #for courseInstance in courseDict[c]:
    #    print('\t+ ' + courseInstance)

