# Combine.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
#import statsmodels.formula.api as smf

datatypes = {'MedianFirstResponseTime': np.float64, 'MedianNumVotes': np.float64, 'AvgNumVotes': np.float64, 'MedianNumResponses': np.float64, 'AvgNumResponses': np.float64, 'NumOpenThreads': np.float64, 'FracOpenThreads': np.float64, 'FracLecsViewed': np.float64, 'FracQuizSubmissions': np.float64}

def run(projectName):
    path = os.path.join(FileSystem.getResultsDir(),projectName,'results.csv')
    df = pd.read_csv(path,sep = ', ')
        #,usecols=['MedianFirstResponseTime','AvgNumVotes','AvgNumResponses','FracOpenThreads','FracLecsViewed'])

    df = pd.read_csv(path,sep = ', ', dtype = datatypes)

    colname = 'MedianFirstResponseTime'
    #MedianFirstResponseTimeSeries = squeeze(df,colname,mu=.000005)
    MedianFirstResponseTimeSeries = squeeze(df,colname,mu=.00000005)
    MedianFirstResponseTimeSeries = logmap(df,colname)

    colname = 'FracOpenThreads'
    FracOpenThreadsSeries = df[colname]
    #series = MedianFirstResponseTimeSeries

    colname = 'AvgNumResponses'
    AvgNumResponsesSeries = squeeze(df,colname,mu=.5)
    #AvgNumResponsesSeries = df[colname]
    #AvgNumResponsesSeries = logmap(df,colname)
    #series = AvgNumResponses

    colname = 'MedianNumVotes'
    MedianNumVotesSeries = squeeze(df,colname,mu=.5)
    MedianNumVotesSeries = df[colname]
    #series = MedianNumVotes

    processedDF = pd.DataFrame({'MedianFirstResponseTime': \
                                MedianFirstResponseTimeSeries, \
            'FracOpenThreads': FracOpenThreadsSeries, \
            'AvgNumResponses': AvgNumResponsesSeries, \
            'MedianNumVotes': MedianNumVotesSeries, \
            'FracLecsViewed': df['FracLecsViewed'], \
            'FracQuizSubmissions': df['FracQuizSubmissions'] })
    #seriesHist(series)
    processedDF = killOutliers(processedDF)
    processedDF['NumOpenThreads'] = df['NumOpenThreads']
    processedDF['ANRsq'] = processedDF['AvgNumResponses']**2
    processedDF['MFRTsq'] = processedDF['MedianFirstResponseTime']**2
    processedDF['FOTANR'] = processedDF['FracOpenThreads']*processedDF['AvgNumResponses']
    X = sm.add_constant(processedDF)
    endog = 'FracLecsViewed'
    results = sm.OLS(X[endog], \
        X[['MedianFirstResponseTime', \
            'FracOpenThreads', \
            'AvgNumResponses', \
            'FOTANR']]).fit()
    print results.summary()    

    #print(seriesHist(df['FracLecsViewed']))

    pred = .0267*X['MedianFirstResponseTime'] - .191*X['FracOpenThreads'] + .3039*X['AvgNumResponses'] + .0389*X['FOTANR']
    dfToCorrelate = pd.DataFrame({'MedianFirstResponseTime': \
                                MedianFirstResponseTimeSeries, \
            'FracOpenThreads': FracOpenThreadsSeries, \
            'AvgNumResponses': AvgNumResponsesSeries, \
            'MedianNumVotes': MedianNumVotesSeries, \
            'FracQuizSubmissions': df['FracQuizSubmissions'], \
            'FracLecsViewed': df['FracLecsViewed']})
    dfToCorrelate = processedDF[['MedianFirstResponseTime', \
                    'FracOpenThreads','AvgNumResponses',\
                    'FracLecsViewed','FracQuizSubmissions']]
    dfToCorrelate = processedDF[['FracLecsViewed','FracQuizSubmissions']]
    #dfToCorrelate['prediction'] = pred
    correlateData(dfToCorrelate)

def seriesHist(series):
    floor = np.percentile(series,5)
    ceil = np.percentile(series,95)
    histbins = np.linspace(floor,ceil,50)
    plt.figure();
    series.hist(bins = histbins)
    plt.show()
    print(series.describe())

def correlateData(df):
    #plt.figure()
    pd.scatter_matrix(df, alpha=0.2, figsize=(6, 6), diagonal='kde')
    plt.show()

def killOutliers(df):
    cols = df.columns.tolist()
    crit = {}
    for col in cols:
        floor = np.percentile(df[col],5)
        ceil = np.percentile(df[col],95)
        crit[col] = df[col].map(lambda x: x>= floor and x<=ceil)
    critcat = crit[cols[0]]
    for col in cols[1:]:
        critcat = critcat & crit[col]
    return df[critcat]

def logmap(df,colname):
    f = lambda x: np.log(max(.0001,min(x,3600*24*28)))
    return df[colname].map(f)

def squeeze(df,colname, mu):
    f = lambda x: 1.0-np.e**(-mu*float(x))
    return df[colname].map(f)

if __name__ == '__main__':
    projectName = 'EngagementVsSatisfaction'
    run(projectName)






