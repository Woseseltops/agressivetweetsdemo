import cherrypy
import tweetlib

template_folder = 'templates/';
log_folder = 'log/';
data_folder = 'tweets/';

class agressive_tweets_demo(object):

    def index(self):
        """"Shows the mainpage""";

	return open(template_folder+'enter_user.html').read();

    index.exposed = True;

    def analyze(self,user):
        """Starts the import and shows the progress""";

        tweets = tweetlib.get_all_tweets(user);
        tweet_str = [str(tweet) for tweet in tweets];
        open(data_folder+'user','w').write('\n'.join(tweet_str));

        return open(template_folder+'analyze.html').read();

    analyze.exposed = True;

    def log_file(self,user):
        """Returns the current logfile for the model creation of a user""";
        return open(maindir+'/logs/create_model_'+user+'.txt').read();
    log_file.exposed = True;

cherrypy.quickstart(agressive_tweets_demo());

#application = cherrypy.Application(agressivetweetsdemo(), script_name=None, config=None)
