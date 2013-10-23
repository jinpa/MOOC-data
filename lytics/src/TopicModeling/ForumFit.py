#! /usr/bin/env ipython

# ForumFit.py
# author = Jonathan Huang



import sys
import os.path
sys.path.append('../../util')
from FileSystem import FileSystem
sys.path.append(FileSystem.getRootDir())
sys.path.append(FileSystem.getSiteDir())
from  DBSetup import DBSetup
from lyticssite.classModels.models import *
import logging
from operator import itemgetter
from Text import Text
from RunExternal import RunExternal
import nltk
from nltk.tokenize import word_tokenize, wordpunct_tokenize
from nltk.corpus import stopwords
import enchant

PREPROCESSPARAMS = {
    'minNumWords': 5,
    'minWordLen': 3,
    'minTokensPerThread': 10,
    'language': 'en',
}

TOPICMODELPARAMS = {
    'numTopics': 50,
    'numIters': 2000,
    'twords' : 100,
    'maxRunTime': 14000,
}

class ForumFit(object):
    
    def loadThreadTextsRaw(self):
        logging.info('loadThreadTextsRaw: ' + self.currDB)
        posts = ForumPosts.objects.all().values('thread_id','post_text')
        self.threads = {}
        for post in posts:
            threadId = post['thread_id']
            text = Text(post['post_text'])
            try:
                self.threads[threadId].append(text)
            except KeyError:
                self.threads[threadId] = [text]
   
    def formLexicon(self, preprocessParams):
        logging.info('formLexicon: ' + self.currDB)
        tokens = []
        for threadId, cnt in zip(self.threads, range(len(self.threads))):
            if cnt % 100 == 0:
                logging.info('\t+Reading ' + str(cnt) + ' of ' \
                            + str(len(self.threads)) + ' threads...')
            for post in self.threads[threadId]:
                tokens += self.toBOW(post, filterOption = False)
        self.lex = {}
        self.lexFiltered = {}
        for t in tokens:
            try:
                self.lex[t] += 1
            except KeyError:
                self.lex[t] = 1
        lexLanguageSet = self.filterForLanguage(preprocessParams['language'])
        for word in lexLanguageSet:
            if self.lex[word] > preprocessParams['minNumWords'] \
                and len(word) >= preprocessParams['minWordLen']:
                self.lexFiltered[word] = self.lex[word]

    def toBOW(self, text, filterOption = False):
        tokens = text.getTokens()
        if filterOption == True:
            tokens_nostop = [t for t in tokens \
                    if not t in stopwords.words('english') \
                    and len(t)>1 and t in self.lexFiltered]
        else:
            tokens_nostop = [t for t in tokens \
                    if not t in stopwords.words('english') and len(t)>1]
        return tokens_nostop

    def filterForLanguage(self, language = 'en_US'):
        if language == '':
            return [word for word in self.lex if 1]
        logging.info('filterForLanguage: ' + self.currDB)
        return [word for word in self.lex if self.langDict.check(word)]

    def writeLex(self, lex, path):
        sortedLex = sorted(lex.iteritems(), key = itemgetter(1), reverse=True)
        strLex = ''
        for w, freq in sortedLex:
            strLex += w + '\t' + str(freq) + '\n'
        with open(path, 'wt') as fid:
            fid.write(strLex)

    def writeThreadsAsBOW(self, preprocessParams):
        logging.info('writeThreadsAsBOW: ' + self.currDB)
        tokens = {}
        for threadId, cnt in zip(self.threads, range(len(self.threads))):
            if cnt % 100 == 0:
                logging.info('\t+Writing ' + str(cnt) + ' of ' \
                    + str(len(self.threads)) + ' threads...')
            tokens[threadId] = []
            for post in self.threads[threadId]:
                tokens[threadId] += self.toBOW(post, filterOption = True)
        self.longThreadIds = [threadId for threadId in tokens \
                if len(tokens[threadId]) > preprocessParams['minTokensPerThread']]
        s = str(len(self.longThreadIds)) + '\n'
        for threadId in self.longThreadIds:
            s += ''.join([t + ' ' for t in tokens[threadId]]) + '\n'
        with open(self.tokensPath,'wt') as fid:
            fid.write(s)
        with open(self.longThreadsPath,'wt') as fid:
            for threadId in self.longThreadIds:
                fid.write(str(threadId) + '\n')
    
    def preprocessText(self, forcePreprocessOption):
        if os.path.exists(self.tokensPath) and not forcePreprocessOption:
            logging.info('	skipping preprocessing: ' + self.currDB)
            return
        logging.info('preprocessText: ' + self.currDB)
        self.formLexicon(self.preprocessParams)
        self.writeLex(self.lex, self.lexPath)
        self.writeLex(self.lexFiltered, self.lexFilteredPath)
        self.writeThreadsAsBOW(self.preprocessParams)

    def trainTopicModel(self, topicModelParams, forceTrainOption):
        if os.path.exists(self.modelParamsPath + '.twords') and not forceTrainOption:
            logging.info('  skipping training: ' + self.currDB)
            return
        logging.info('trainTopicModel: ' + self.currDB)
        LDAcmd = [self.trainExecutablePath, '-est', \
                    '-ntopics', str(topicModelParams['numTopics']), \
                    '-niters', str(topicModelParams['numIters']), \
                    '-twords', str(topicModelParams['twords']), \
                    '-dfile', self.tokensPath]
        timeout = topicModelParams['maxRunTime']
        runner = RunExternal(LDAcmd, timeout, pipeOption = False)
        runner.run()

    def createWordleForm(self, topicModelParams):
        logging.info('createWordleForm: ' + self.currDB)
        numTopics = topicModelParams['numTopics']
        numWords = topicModelParams['twords']
        twordsPath = self.modelParamsPath + '.twords'
        with open(twordsPath) as fid:
            rows = fid.readlines()
        i = 0
        fid = open(self.wordlesPath,'wt')
        fid.write('<html><body>')
        for t in range(numTopics):
            i += 1
            fid.write('<b>Topic ' + str(t) + '</b>\n' \
                    '<form action="http://www.wordle.net/advanced" method="POST" target="_blank">' \
                    + '<textarea name="wordcounts" style="display:none">\n')
            for word in range(numWords):
                tmp = rows[i].lstrip('\t').rstrip('\n').split(' ')
                i += 1
                fid.write(tmp[0] + ':' + tmp[-1] + '\n')
            fid.write('</textarea><input type="submit"></form>\n')
        fid.write('</body></html>')
        fid.close()

    def createTopicSummary(self, topicModelParams):
        logging.info('creatTopicSummary: ' + self.currDB)
        numTopics = topicModelParams['numTopics']
        numWords = topicModelParams['twords']
        twordsPath = self.modelParamsPath + '.twords'
        with open(twordsPath) as fid:
            rows = fid.readlines()
        i = 0
        fid = open(self.topicSummaryPath,'wt')
        for t in range(numTopics):
            i += 1
            fid.write('Topic ' + str(t) + ':\n')
            for word in range(numWords):
                tmp = rows[i].lstrip('\t').rstrip('\n').split(' ')
                i += 1
                if word < 25:
                    fid.write('\t' + tmp[0] + '\n')
            fid.write('\n')
        fid.close()

    def setCurrPaths(self):
        self.tokensPath = os.path.join(self.currDataDir, 'QNATokens.csv')
        self.lexPath = os.path.join(self.currDataDir, 'Lex.csv')
        self.longThreadsPath = os.path.join(self.currDataDir, 'LongThreadIds.csv')
        self.lexFilteredPath = os.path.join(self.currDataDir, 'LexFiltered.csv')
        self.modelParamsPath = os.path.join(self.currDataDir, 'model-final')
        self.wordlesPath = os.path.join(self.currResultDir, 'wordles.html')
        self.topicSummaryPath = os.path.join(self.currResultDir, 'topicSummary.txt')

    def createResultDir(self):
        resultsDir = os.path.join(self.resultsDir, self.currDB)
        return FileSystem.createDir(resultsDir)

    def createDataDir(self):
        dataDir = os.path.join(self.dataDir, self.currDB)
        return FileSystem.createDir(dataDir)

    def __init__(self):
        self.projectName = 'TopicModel'
        FileSystem.startLogger(self.projectName, 'log')
        self.dbNames = FileSystem.loadForumList()
        self.dataDir = FileSystem.createDataDir(self.projectName)
        self.resultsDir = FileSystem.createResultsDir(self.projectName)
        self.trainExecutablePath = os.path.join(FileSystem.getBinDir(), 'lda')
        self.preprocessParams = PREPROCESSPARAMS
        self.topicModelParams = TOPICMODELPARAMS
        self.langDict = enchant.Dict(self.preprocessParams['language'])

    def run(self, forcePreprocessOption, forceTrainOption):
        for dbName in self.dbNames:
            self.currDB = dbName
            DBSetup.switch(self.currDB)

            self.currResultDir = self.createResultDir()
            self.currDataDir = self.createDataDir()
            self.setCurrPaths()

            self.loadThreadTextsRaw()
            self.preprocessText(forcePreprocessOption)
            self.trainTopicModel(self.topicModelParams, forceTrainOption)
            self.createWordleForm(self.topicModelParams)
            self.createTopicSummary(self.topicModelParams)


if __name__ == '__main__':
    forcePreprocessOption = False
    forceTrainOption = False
    if len(sys.argv) >= 2:
        for arg in sys.argv[1:]:
            if arg == '-fpreprocess':
                forcePreprocessOption = True
            if arg == '-ftrain':
                forceTrainOption = True
    ForumFit().run(forcePreprocessOption, forceTrainOption)




