# Correlations.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')

from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


def getHistList(df,X,Y,numbins):
    bins = getBins(df,X,numbins)
    binSpacing = bins[1] - bins[0]
    hist = {}
    avg = {}
    for rowIdx, row in df.iterrows():
        xVal = row[X]
        yVal = row[Y]
        if xVal < bins[0] or xVal>= bins[-1]:
            continue
        binIdx = int((xVal-bins[0])/float(binSpacing))
        try:
            hist[binIdx] +=1
            avg[binIdx] += yVal
        except KeyError:
            hist[binIdx] = 1
            avg[binIdx] = yVal
    xvals = sorted(hist.keys())
    yvals = [avg[x]*1./max(1.,hist[x]) for x in xvals]
    hvals = [hist[x] for x in xvals]
    binCenters = [(x+y)/2 for x,y in zip(bins[1:],bins[:-1])]
    return (xvals,yvals,hvals,binCenters)

# get bin boundaries
def getBins(df,X,numbins):
    floor = np.percentile(df[X],0)
    ceil = np.percentile(df[X],100)
    return np.linspace(floor,ceil,numbins + 1)

def getCorr(df,X,Y):
    (rho, pval) = spearmanr(df[X],df[Y])    
    return (rho,pval)

def reportCorrelation(result,X,Y):
    print('Correlation between ' + X + \
            ' and ' + Y + ': ' + str(result[0]) + \
            ', (p=' + str(result[1]) + ').')

def plotCorr(figId,df,X,Y,numbins):
    plt.figure(figId)
    fig,y1 = plt.subplots()
    xvals, yvals, hvals,binCenters = getHistList(df,X,Y,numbins)
    y1.scatter(df[X],df[Y],c=(0,.7,.8,.3),)
    y1.plot(binCenters,yvals,'r-',lw = 3)
    y1.set_xlabel(X)
    y1.set_ylabel(Y, color='r')
    plt.xlim((binCenters[0],binCenters[-1]))
    plt.savefig(X + 'v' + Y + '.png')

def killOutliers(df):
    cols = df.columns.tolist()
    crit = {}
    for col in cols[1:]:
        floor = np.percentile(df[col],0)
        ceil = np.percentile(df[col],95)
        crit[col] = df[col].map(lambda x: x>= floor and x<ceil)
    critcat = crit[cols[1]]
    for col in cols[2:]:
        critcat = critcat & crit[col]
    return df[critcat]

def run(projectName):
    path = os.path.join(FileSystem.getResultsDir(),projectName,'results.csv')
    df = pd.read_csv(path,sep = ', ')
    df = killOutliers(df)

    X = 'MedianFirstResponseTime'
    Y = 'FracLecsViewed'
    corrResult = getCorr(df,X,Y)
    reportCorrelation(corrResult,X,Y)

    X = 'FracOpenThreads'
    Y = 'FracLecsViewed'
    corrResult = getCorr(df,X,Y)
    reportCorrelation(corrResult,X,Y)

    X = 'FracOpenThreads'
    Y = 'FracQuizSubmissions'
    corrResult = getCorr(df,X,Y)
    reportCorrelation(corrResult,X,Y)

    X = 'AvgNumResponses'
    Y = 'FracLecsViewed'
    corrResult = getCorr(df,X,Y)
    reportCorrelation(corrResult,X,Y)

    X = 'MedianNumVotes'
    Y = 'FracLecsViewed'
    corrResult = getCorr(df,X,Y)
    reportCorrelation(corrResult,X,Y)

    X = 'FracQuizSubmissions'
    Y = 'FracLecsViewed'
    corrResult = getCorr(df,X,Y)
    reportCorrelation(corrResult,X,Y)

    return

    X = 'AvgNumResponses'
    Y = 'FracLecsViewed'
    figId = 1
    plotCorr(figId,df,X,Y,15)

    X = 'AvgNumResponses'
    Y = 'FracQuizSubmissions'
    figId = 2
    plotCorr(figId,df,X,Y,15)

    X = 'MedianFirstResponseTime'
    Y = 'FracLecsViewed'
    figId = 3
    plotCorr(figId,df,X,Y,5)




if __name__ == '__main__':
    projectName = 'EngagementVsSatisfaction'
    run(projectName)



