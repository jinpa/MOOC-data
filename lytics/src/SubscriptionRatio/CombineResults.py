#! /usr/bin/env ipython

# CombineResults.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from numpy import mean, std


def loadResults(resultsDir):
    resultsMean = []
    resultsStd = []
    for k in range(100):
        path = os.path.join(resultsDir, 'results' + str(k) + '.csv')
        ratioList = []
        with open(path) as fid:
            rows = fid.readlines()
            for r in rows:
                ratioList.append(float(r.rstrip().split(', ')[-1]))
        resultsMean.append(mean(ratioList))
        resultsStd.append(std(ratioList))
    return resultsMean, resultsStd

def writeResults(path, resultsMean, resultsStd):
    with open(path,'wt') as fid:
        fid.write('t, mean of ratios, std of ratios\n')
        for (k,m,s) in zip(range(100),resultsMean,resultsStd):
            fid.write(str(k) + ', ' + str(m) + ', ' + str(s) + '\n')

resultsDir = os.path.join(FileSystem.getResultsDir(),'SubscriptionRatio')
outputPath = os.path.join(resultsDir,'combinedResults.csv')
resultsMean, resultsStd = loadResults(resultsDir)
writeResults(outputPath, resultsMean, resultsStd)



