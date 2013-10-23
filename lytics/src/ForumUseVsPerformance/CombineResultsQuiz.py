#! /usr/bin/env ipython

# CombineResultsQuiz.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from scipy.stats import linregress, spearmanr,histogram

NUMBINS = 100

def loadRegressionResults(path):
    with open(path) as fid:
        rows = fid.readlines()
        row1 = rows[1].rstrip().split(',')
        row2 = rows[2].rstrip().split(',')
        result = {'rhoActivity': float(row1[1]), \
                    'pValActivity': float(row1[2]), \
                    'corrActivity': float(row1[3]), \
                    'corrpValActivity': float(row1[4]), \
                    'rhoOriginal': float(row2[1]), \
                    'pValOriginal': float(row2[2]), \
                    'corrOriginal': float(row2[3]), \
                    'corrpValOriginal': float(row2[4])}
        return result

def loadCourseStats(path):
    with open(path) as fid:
        rows = [r.rstrip().split(', ')[1] for r in fid.readlines()]
        courseStats = { 'numRegisteredUsers': int(rows[0]), \
                        'numContributors': int(rows[1]), \
                        'numQuizSubmitters': int(rows[2])}
        return courseStats

def writeMergedCorrelationResults(results, outputPath):
    with open(outputPath,'wt') as fid:
        fid.write('Forum Activity vs. Quiz Score\n')
        fid.write('course, spearman_rho_activity, p_value_activity, ')
        fid.write('pearson_corr_activity, pearson_corr_p_value_activity, ')
        fid.write('spearman_rho_originalposts, p_value_originalposts, ')
        fid.write('pearson_corr_originalposts, pearson_corr_p_value_originalposts, ')
        fid.write('# forum contributors, # registered users\n')
        for result in results:
            course = result[0]
            info = result[1]
            courseStats = result[2]
            fid.write(course + ', ' \
                        + str(info['rhoActivity']) + ', ' \
                        + str(info['pValActivity']) + ', ' \
                        + str(info['corrActivity']) + ', ' \
                        + str(info['corrpValActivity']) + ', ' \
                        + str(info['rhoOriginal']) + ', ' \
                        + str(info['pValOriginal']) + ', ' \
                        + str(info['corrOriginal']) + ', ' \
                        + str(info['corrpValOriginal']) + ', ' \
                        + str(courseStats['numContributors']) + ', ' \
                        + str(courseStats['numRegisteredUsers']) + '\n')
    
def mergeCorrelationResults(projectName):
    courseList = FileSystem.loadCourseList()
    resultsDir = os.path.join(FileSystem.getResultsDir(),projectName)
    results = []
    for course in courseList:
        currDir = os.path.join(resultsDir,course)
        path = os.path.join(currDir,'ForumActivityVsQuizScore_regression.csv')
        pathStats = os.path.join(currDir,'CourseStats.csv')
        try:
            currResults = loadRegressionResults(path)
            currCourseStats = loadCourseStats(pathStats)
            results.append((course,currResults,currCourseStats))
        except IOError:
            continue
    outputPath = os.path.join(resultsDir,'mergedCorrelationResults.csv')
    writeMergedCorrelationResults(results, outputPath)

if __name__ == '__main__':
    projectName = 'ForumUseVsQuizPerformance'
    mergeCorrelationResults(projectName)

