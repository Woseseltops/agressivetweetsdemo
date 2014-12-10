from sklearn.externals import joblib
import random
import codecs
import classify_aggression

class Agression_analyzer():

        def analyze(self,tweets,resultpath):
                #load classifier
                clf = classify_aggression.Classifier()
                
                #Get a score for all tweets
                tweets_text = [t.text for t in tweets]
                results = sorted(clf.main(tweets_text),key=lambda x: x[2],reverse=True);
                print(results)

                #Write the results away
                results = [(txt,str(classification),str(score)) for txt,classification,score in results]
                lines = ['\t'.join(line) for line in results]
                open(resultpath,'w').write('\n'.join(lines))
