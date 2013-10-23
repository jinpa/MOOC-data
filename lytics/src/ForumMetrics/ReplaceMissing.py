# ReplaceMissing.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
import numpy as np
import numpy.ma as ma

def loadResults(path):
    fid = open(path)
    rows = fid.readlines()
    fid.close()
    arr = []
    nanmask = []
    for r in rows:
        row = r.strip().split(', ')
        arrLine = []
        maskLine = []
        for val in row[1:]:
            if val == 'None':
                arrLine.append(float('nan'))
                maskLine.append(1)
            else:
                arrLine.append(float(val))
                maskLine.append(0)
        arr.append(arrLine)
        nanmask.append(maskLine)
    return arr, nanmask

def writeCorrMat(C, path):
    s = ''
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            if str(C[i,j]) == '--':
                s += 'nan' + ', '
            else:
                s += str(C[i,j]) + ', '
        s += '\n'
    with open(path,'wt') as fid:
        fid.write(s)

def run():
    projectName = 'ForumMetrics'
    path = os.path.join(FileSystem.getResultsDir(),projectName,'results.csv')
    outputPath = os.path.join(FileSystem.getResultsDir(),projectName,'corrMat.csv')
    
    arr, nanmask = loadResults(path)
    X = ma.array(arr,mask = nanmask)
    C = np.ma.corrcoef(np.transpose(X))

    writeCorrMat(C, outputPath)
    

if __name__ == '__main__':
    run()
















