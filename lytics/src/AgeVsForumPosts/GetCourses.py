# GetCourses.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from numpy import mean, std, percentile



def run(projectName):
    path = os.path.join(FileSystem.getResultsDir(),projectName,'results.csv')
    fid = open(path)
    rows = fid.readlines()
    fid.close()
    courseNames = []
    for r in rows:
        courseNames.append(r.strip().split(', ')[0])
    courseNames = list(set(courseNames))
    for course in courseNames:
        print(course)

if __name__ == '__main__':
    projectName = 'AgeVsForumPosts'
    run(projectName)



