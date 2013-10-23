# Combine.py
# author = Jonathan Huang
import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from numpy import mean, std, percentile

employmentOptions = {'employed full-time (35 or more hours per week)': 'employedfulltime', \
        'employed part-time (less than 35 hours per week)': 'employedparttime', \
        'unemployed and looking for work': 'unemployedlooking', \
        'unemployed and not looking for work': 'unemployednotlooking', \
        'unable to work': 'unabletowork', \
        'homemaker, taking care of a family member, or on maternity/paternity leave': 'homemaker', \
        'retired': 'retired', \
        'self-employed (35 or more hours per week)': 'selffulltime', \
        'self-employed (less than 35 hours per week)': 'selfparttime', \
        '': ''}


def summarizeBuckets(buckets, oldies, path, ageMin, ageMax, sizeBucket):
    with open(path,'wt') as fid:
        for bucket,idx in zip(buckets,range(len(buckets))):
            avgNumPosts = mean(bucket)
            numPts = len(bucket)
            bucketMin = ageMin + idx*sizeBucket
            bucketMax = bucketMin + sizeBucket
            fid.write(str(bucketMin) + ', ' + str(bucketMax) + ', ' \
                    + str(avgNumPosts) + ', ' + str(numPts) + '\n')
            avgNumPosts = mean(oldies)
        numPts = len(oldies)
        bucketMin = ageMax
        fid.write(str(bucketMin) + ', ' + '120' + ', ' \
                + str(avgNumPosts) + ', ' + str(numPts) + '\n')



def run(projectName):
    path = os.path.join(FileSystem.getResultsDir(),projectName,'results.csv')
    fid = open(path)
    rows = fid.readlines()
    fid.close()
    buckets = []
    bucketsByGender = {}
    bucketsByGender['male'] = []
    bucketsByGender['female'] = []
    bucketsByEmployment = {}
    for key in employmentOptions:
        bucketsByEmployment[employmentOptions[key]] = []   
    ageMax = 75
    ageMin = 15
    sizeBucket = 5
    oldies = []
    oldiesByGender = {}
    oldiesByGender['male'] = []
    oldiesByGender['female'] = []
    oldiesByEmployment = {}
    for key in employmentOptions:
        oldiesByEmployment[employmentOptions[key]] = []   
    for i in range((ageMax-ageMin)/sizeBucket):
        buckets.append([])
        bucketsByGender['male'].append([])
        bucketsByGender['female'].append([])
        for key in employmentOptions:
            bucketsByEmployment[employmentOptions[key]].append([])
    
    for r in rows:
        row = r.strip().split(', ')
        age = int(row[1])
        gender = row[2]
        employment = row[3]
        studentStatus = row[4]
        grade = int(row[5])
        numPosts = int(row[6])
        if age >= ageMin and age < ageMax:
            bin = (age - ageMin) / sizeBucket
            buckets[bin].append(numPosts)
            if gender == 'male' or gender == 'female':
                bucketsByGender[gender][bin].append(numPosts)
            bucketsByEmployment[employment][bin].append(numPosts)
        if age >= ageMax:
            oldies.append(numPosts)
            if gender == 'male' or gender == 'female':
                oldiesByGender[gender].append(numPosts)
            oldiesByEmployment[employment].append(numPosts)
    
    path = os.path.join(FileSystem.getResultsDir(),projectName,'aggregatedAgeVsForumPosts.csv')
    pathMale = os.path.join(FileSystem.getResultsDir(),projectName,'maleAgeVsForumPosts.csv')
    pathFemale = os.path.join(FileSystem.getResultsDir(),projectName,'femaleAgeVsForumPosts.csv')
    summarizeBuckets(buckets,oldies,path,ageMin, ageMax, sizeBucket)
    summarizeBuckets(bucketsByGender['male'],oldiesByGender['male'],pathMale,ageMin, ageMax, sizeBucket)
    summarizeBuckets(bucketsByGender['female'],oldiesByGender['female'],pathFemale,ageMin, ageMax, sizeBucket)
    for key in employmentOptions:
        if len(key) > 0:
            path = os.path.join(FileSystem.getResultsDir(), projectName, employmentOptions[key] + 'AgeVsForumPosts.csv')
            summarizeBuckets(bucketsByEmployment[employmentOptions[key]], \
                        oldiesByEmployment[employmentOptions[key]],path,ageMin,ageMax,sizeBucket)


if __name__ == '__main__':
    projectName = 'AgeVsForumPosts'    
    run(projectName)


