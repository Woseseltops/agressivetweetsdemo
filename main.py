import cherrypy
import tweetlib
from threading import Thread
from agression_analyzer import Agression_analyzer

template_folder = 'templates/';
log_folder = 'log/';
data_folder = 'tweets/';
result_folder = 'result/';

class agressive_tweets_demo(object):

    def index(self):
        """"Shows the mainpage""";

	return open(template_folder+'enter_user.html').read();

    index.exposed = True;

    def analyze(self,user):
        """Starts the import and shows the progress""";

	def parrallel_analysis():
	    tweets = tweetlib.get_all_tweets(user);
	    tweet_str = [str(tweet) for tweet in tweets];

            filepath = data_folder+user;

	    open(filepath,'w').write('\n'.join(tweet_str));
            self.log('Importing successful.',logfile);

            self.log('Analyzing tweets.',logfile);
            analyzer = Agression_analyzer();
            results = analyzer.analyze(tweets);
#            open(result_folder+user,'w').write();
            self.log('Analysis finished!',logfile);

        logfile = open(log_folder+user+'.txt','w',0);
        self.log('Importing all tweets from '+user,logfile)

        Thread(target=parrallel_analysis).start();

        return open(template_folder+'analyze.html').read();

    analyze.exposed = True;

    def log_file(self,user):
        """Returns the current logfile for the model creation of a user""";
        return open(log_folder+user+'.txt').read();
    log_file.exposed = True;

    def results(self,user):
        """Returns the result view""";
        return "These are the results for "+user;
    results.exposed = True;

    def log(self,message,logfile):
        print(message);
        logfile.write('<p>'+message+'</p>');


cherrypy.quickstart(agressive_tweets_demo());

#application = cherrypy.Application(agressivetweetsdemo(), script_name=None, config=None)
