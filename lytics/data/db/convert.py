#! /usr/bin/env python

# convert.py
# author = Jonathan Huang



fname = 'courseList_raw.txt'
fid = open(fname)
rows = fid.readlines()
fid.close()

for r in rows:
    s = r.split(' ')[1]
    #if s[-5:] == 'forum':
     #   print(s)
    print(s)
