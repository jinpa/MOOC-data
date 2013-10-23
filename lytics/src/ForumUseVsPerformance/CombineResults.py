#! /usr/bin/env ipython

# CombineResults.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from scipy.stats import linregress, spearmanr,histogram

NUMBINS = 100

def loadResults(path):
    forumActivities = []
    finalGrades = []
    with open(path) as fid:
        rows = fid.readlines()
        for r in rows:
            splitRow = r.rstrip().split(', ')
            forumActivities.append(float(splitRow[0]))
            finalGrades.append(float(splitRow[-1]))
    return forumActivities, finalGrades

def writeResults(forumActivities, finalGrades, path):
    with open(path,'wt') as fid:
        for (forumActivity, finalGrade) in zip(forumActivities, finalGrades):
            fid.write(str(forumActivity) + ', ' + str(finalGrade) + '\n')

def writeRegressionResults(forumActivities, finalGrades, path):
    slope, intercept, rValue, pValue, stdErr = \
                    linregress(forumActivities,finalGrades)
    rho, pValueSpearman = spearmanr(forumActivities, finalGrades)
    with open(path,'wt') as fid:
            fid.write('slope, intercept, R^2, p_value, std_err\n')
            fid.write(str(slope) + ', ' \
                    + str(intercept) + ', ' \
                    + str(rValue**2) + ', ' \
                    + str(pValue) + ', ' \
                    + str(stdErr) + '\n\n')
            fid.write('spearman rho, p_value\n')
            fid.write(str(rho) + ', ' + str(pValueSpearman))

def writeHistogram(x,path,limits = None):
    hist, lowRange, binSize, extra = histogram(x,numbins = NUMBINS, defaultlimits = limits)
    with open(path,'wt') as fid:
        low = lowRange
        hi = lowRange + binSize
        for freq in hist:
            fid.write(str(low) + ', ' + str(hi) + ', ' + str(freq) + '\n')
            low += binSize
            hi += binSize

def combineResults(projectName):
    courseList = FileSystem.loadCourseList()
    resultsDir = os.path.join(FileSystem.getResultsDir(),projectName)
    forumActivities = []
    finalGrades = []
    forumActivities2 = []
    lecturesViewed = []
    for course in courseList:
        currDir = os.path.join(resultsDir, course)
        pathScore = os.path.join(currDir,'allForumVsFinalScore.csv')
        try:
            forumActivity, finalGrade = loadResults(pathScore)
            forumActivities += forumActivity
            finalGrades += finalGrade
        except IOError:
            continue
        pathLectures = os.path.join(currDir,'allForumVsLecturesViewed.csv')
        try:
            forumActivity, numLectures = loadResults(pathLectures)
            forumActivities2 += forumActivity
            lecturesViewed += numLectures
        except IOError:
            continue

    outputPathScore = os.path.join(resultsDir,'allForumVsFinalScore.csv')
    regressOutputPathScore = os.path.join(resultsDir,'allForumVsFinalScore_regression.csv')
    outputPathLectures = os.path.join(resultsDir,'allForumVsLectures.csv')
    regressOutputPathLectures = os.path.join(resultsDir,'allForumVsLectures_regression.csv')
    forumActivitiesHistPath = os.path.join(resultsDir,'allForum_hist.csv')
    finalGradesHistPath = os.path.join(resultsDir,'finalScore_hist.csv')
    lecturesHistPath = os.path.join(resultsDir,'lecturesViewed_hist.csv')
    
    writeResults(forumActivities, finalGrades, outputPathScore) 
    writeRegressionResults(forumActivities, finalGrades, regressOutputPathScore)   
    writeResults(forumActivities, lecturesViewed, outputPathLectures) 
    writeRegressionResults(forumActivities2, lecturesViewed, regressOutputPathLectures)   
    writeHistogram(forumActivities, forumActivitiesHistPath, limits = (-3.0,3.0))    
    writeHistogram(finalGrades, finalGradesHistPath, limits = (-3.0, 3.0))
    writeHistogram(lecturesViewed, lecturesHistPath, limits = (-3.0, 3.0))

def loadRegressionResults(path):
    with open(path) as fid:
        rows = fid.readlines()
        row = rows[1].rstrip().split(',')
        values = [float(x) for x in row]
        result = {'slope': values[0], \
                    'intercept': values[1], \
                    'R^2': values[2], \
                    'p_value': values[3],\
                    'std_err': values[4], \
                    'rho': values[5], \
                    'p_value_spearman': values[6]}
        return result

def writeMergedCorrelationResults(resultsScore, resultsLectures, outputPath):
    with open(outputPath,'wt') as fid:
        fid.write('Forum Activity vs. Score\n')
        fid.write('course, slope, intercept, R^2, p_value, std_err, spearman rho, p_value_spearman\n')
        for result in resultsScore:
            course = result[0]
            info = result[1]
            fid.write(course + ', ' \
                        + str(info['slope']) + ', ' \
                        + str(info['intercept']) + ', ' \
                        + str(info['R^2']) + ', ' \
                        + str(info['p_value']) + ', ' \
                        + str(info['std_err']) + ', ' \
                        + str(info['rho']) + ', ' \
                        + str(info['p_value_spearman']) + '\n')
        fid.write('Forum Activity vs. Lectures Viewed\n')
        fid.write('course, slope, intercept, R^2, p_value, std_err, spearman rho, p_value_spearman\n')
        for result in resultsLectures:
            course = result[0]
            info = result[1]
            fid.write(course + ', ' \
                        + str(info['slope']) + ', ' \
                        + str(info['intercept']) + ', ' \
                        + str(info['R^2']) + ', ' \
                        + str(info['p_value']) + ', ' \
                        + str(info['std_err']) + ', ' \
                        + str(info['rho']) + ', ' \
                        + str(info['p_value_spearman']) + '\n')

def mergeCorrelationResults(projectName):
    courseList = FileSystem.loadCourseList()
    resultsDir = os.path.join(FileSystem.getResultsDir(),projectName)
    resultsScore = []
    resultsLectures = []
    for course in courseList:
        currDir = os.path.join(resultsDir,course)
        pathScore = os.path.join(currDir,'allForumVsFinalScore_regression.csv')
        pathLectures = os.path.join(currDir,'allForumVsLecturesViewed_regression.csv')
        try:
            currResults = loadRegressionResults(pathScore)
            resultsScore.append((course,currResults))
        except IOError:
            continue
        try:
            currResults = loadRegressionResults(pathLectures)
            resultsLectures.append((course,currResults))
        except IOError:
            continue
    outputPath = os.path.join(resultsDir,'mergedCorrelationResults.csv')
    writeMergedCorrelationResults(resultsScore,resultsLectures,outputPath)

if __name__ == '__main__':
    projectName = 'ForumUseVsEngagement'
    combineResults(projectName)
    mergeCorrelationResults(projectName)



