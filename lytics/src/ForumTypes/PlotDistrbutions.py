# PlotDistrbutions.py
# author = Jonathan Huang
__author__ = 'jhuang11'

import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import numpy as np

def listsum(L,r):
    assert(len(r)>0)
    result = L[r[0]]
    for i in r[1:]:
        result = [x+y for x,y in zip(result,L[r[i]])]
    return result

def run(projectName):
    categories = [[],[],[],[],[]]
    numClasses = 0
    classNames = []
    path = os.path.join(FileSystem.getResultsDir(),projectName)
    for fname in os.listdir(path):
        if fname[-4:] == '.csv':
            numClasses += 1
            classNames.append(fname[:-4])
            with open(os.path.join(path, fname)) as fid:
                rows = fid.readlines()
                data = [float(r.strip().split(', ')[1]) for r in rows]
                for i in range(len(data)):
                    categories[i].append(data[i])

    ind = range(numClasses)
    width = .5

    plt.figure(1)
    p0 = plt.bar(ind, categories[0], width,color = 'k')
    p1 = plt.bar(ind, categories[1], width,color = 'r',bottom=categories[0])
    p2 = plt.bar(ind, categories[2], width,color = 'g',bottom=listsum(categories,[0,1]))
    p3 = plt.bar(ind, categories[3], width,color = 'b',bottom=listsum(categories,[0,1,2]))
    p4 = plt.bar(ind, categories[4], width,color = 'c',bottom=listsum(categories,[0,1,2,3]))
    plt.xticks([x + width/2. for x in ind], classNames, rotation='vertical')
    #plt.show()
    plt.ylim((0.,1.))
    plt.subplots_adjust(bottom=0.5)
    figpath = os.path.join(FileSystem.getResultsDir(),projectName,'distribution.pdf')
    plt.savefig(figpath)

if __name__ == '__main__':
    projectName = 'ForumTypes'
    run(projectName)
