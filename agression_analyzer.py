import random

class Agression_analyzer():

	def analyze(self,tweets):
		
		results = [];
		
		for tweet in tweets:
			results.append((tweet,random.randrange(1,100)));

		return results
