import random

class Agression_analyzer():

	def analyze(self,tweets,resultpath):
		
		results = [];
		
		#Get a score for all tweets
		for tweet in tweets:
			results.append((tweet.text,random.randrange(1,100)));

		results = sorted(results,key=lambda x: x[1],reverse=True);
		print(results);

		#Write the results away
		results = [(txt,str(score)) for txt,score in results];
		lines = ['\t'.join(line) for line in results];
		open(resultpath,'w').write('\n'.join(lines));
