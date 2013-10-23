# ForumTypes.py
# author = Jonathan Huang
__author__ = 'jhuang11'


import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.forumModels.models import *
from operator import itemgetter

class ForumTypes(object):

    def writeSummary(self, path, fTypes):
        typeSizes = [(key, len(val)) for (key,val) in fTypes.iteritems()]
        sortedTypes = sorted(typeSizes, key = itemgetter(1), reverse = True)
        with open(path,'wt') as fid:
            fid.write('Number of forum ``types'': ' + str(len(fTypes)) + '\n\n\n')
            for (key, _) in sortedTypes:
                currForums = fTypes[key]
                fid.write(str(len(currForums)) + ': ' + key  + '\n')
                for f in currForums:
                    fid.write('\t' + f[0] + '\n')
                    fid.write('\t\t' + f[1] + '\n')
                fid.write('\n\n\n')

    def setup(self, projectName):
        self.resultsDir = FileSystem.createResultsDir(projectName)
        self.courseDatasets = FileSystem.loadCourseDatasetInfo()

    def run(self, projectName):
        self.setup(projectName)
        fTypes = {}
        for course in self.courseDatasets:
            DBSetup.switch(course)

            try:
                forums = list(ForumForums.objects.filter(deleted = 0, parent_id = 0))
            except:
                continue

            for forum in forums:
                try:
                    fTypes[forum.name].append((course.name, forum.description))
                except KeyError:
                    fTypes[forum.name] = [(course.name, forum.description)]


        path = os.path.join(self.resultsDir,'summary.txt')
        self.writeSummary(path, fTypes)


        #for t in fTypes:
        #    print(t + ', ' + str(len(fTypes[t])))



if __name__ == '__main__':
    projectName = 'ForumTypes'
    ForumTypes().run(projectName)
