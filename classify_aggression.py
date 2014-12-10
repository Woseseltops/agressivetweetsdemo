from sklearn.externals import joblib
import ucto
import re

class Classifier:

    def __init__(self):
        self.clf = joblib.load("model.joblib.pkl")
        self.vocabulary = {}
        vocabularyfile = open("vocabulary.txt",mode = "r",encoding = "utf-8")
        for i,line in enumerate(vocabularyfile.readlines()):
            self.vocabulary[line.strip()] = i
        vocabularyfile.close()
        self.vocab_size = len(self.vocabulary.keys())
        self.tokenizer = ucto.Tokenizer("/vol/customopt/uvt-ru/etc/ucto/tokconfig-nl-twitter")

    #extract uni-, bi- and trigrams
    def tweet_2_features(self,texts):
        vectors = []
        vectorframe = [float(0)] * self.vocab_size
        for text in texts:
            self.tokenizer.process(text)
            tokens = [x.text for x in self.tokenizer]
            for i,token in enumerate(tokens):
                if token[0] == "@":
                    tokens[i] = "USER"
                if re.search(r"^http",token):
                    tokens[i] == "URL"
            ngrams = tokens + ["_".join(x) for x in zip(tokens, tokens[1:])] + ["_".join(x) for x in zip(tokens, tokens[1:], tokens[2:])]
        #    print(ngrams)
            vector = vectorframe[:]
            for feature in ngrams:
                try:
                    vector[self.vocabulary[feature]] = float(1)
                except KeyError:
         #           print("KeyError",feature)
                    continue
          #  print(vector)
            vectors.append((text,vector))
        return vectors

    def classify_aggression(self,texts):
        outcome = []
        instances = self.tweet_2_features(texts)
        for instance in instances:
            classification = self.clf.predict(instance[1])
            proba = self.clf.predict_proba(instance[1])
            outcome.append((instance[0],classification[0],proba.tolist()[0][-1]))
        return outcome

    def main(self,texts):
        return self.classify_aggression(texts)
