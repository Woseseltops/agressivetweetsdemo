# 2015.03.23 15:28:24 CET
# Embedded file name: /www/aggressivetweets/live/repo/aggrestweets/classify_aggression.py
from sklearn.externals import joblib
import ucto
import re
import cPickle
import codecs
from collections import defaultdict

class Classifier:

    def __init__(self):
        clfmodel = open('model.joblib.pkl', 'rb')
        self.clf = cPickle.load(clfmodel)
        self.tokenizer = ucto.Tokenizer('/vol/customopt/uvt-ru/etc/ucto/tokconfig-nl-twitter')
        self.vocabulary = {}
        vocabularyfile = codecs.open('vocabulary.txt', 'r', 'utf-8')
        for i, line in enumerate(vocabularyfile.readlines()):
            self.vocabulary[line.strip()] = i

        vocabularyfile.close()
        self.vocab_size = len(self.vocabulary.keys())
        self.idf = {}
        idffile = codecs.open('log/test.txt', 'r', 'utf-8')
        for line in idffile.readlines():
            tokens = line.strip().split('\t')
            self.idf[int(tokens[0])] = float(tokens[1])

        idffile.close()

    def tweet_2_features(self, texts):
        vectors = []
        vectorframe = [float(0)] * self.vocab_size
        for text in texts:
            self.tokenizer.process(unicode(text.decode('cp1252', 'ignore').lower()))
            tokens = [ x.text for x in self.tokenizer ]
            for i, token in enumerate(tokens):
                if token[0] == '@':
                    tokens[i] = 'USER'
                if re.search('^http', token):
                    tokens[i] == 'URL'

            tokens_n = ['<s>'] + tokens + ['<s>']
            ngrams = tokens + [ '_'.join(x) for x in zip(tokens_n, tokens_n[1:]) ] + [ '_'.join(x) for x in zip(tokens_n, tokens_n[1:], tokens_n[2:]) ]
            print ngrams
            vector = vectorframe[:]
            feature_freq = defaultdict(int)
            for feature in ngrams:
                try:
                    feature_index = self.vocabulary[feature]
                    if re.search('kutwijf', feature):
                        print (feature, feature_index)
                    feature_freq[feature_index] += 1
                except KeyError:
                    continue

            for feature in sorted(feature_freq.keys()):
                vector[feature] = feature_freq[feature] * self.idf[feature]

            vectors.append((text, vector))

        return vectors

    def classify_aggression(self, texts):
        outcome = []
        instances = self.tweet_2_features(texts)
        for instance in instances:
            classification = self.clf.predict(instance[1])
            proba = self.clf.predict_proba(instance[1])
            outcome.append((instance[0], classification[0], proba.tolist()[0][-1]))

        return outcome

    def main(self, texts):
        return self.classify_aggression(texts)
