import sys
import cherrypy
import tweetlib
from threading import Thread

from ctypes import cdll 
for library in ['libticcutils.so.2','libfolia.so.3','libucto.so.2']:
	lib_path = '/var/www2/aggrestweets/live/virtualenv/aggrestweets/lib/'+library;
	print(lib_path);
	cdll.LoadLibrary(lib_path); 

from classify_aggression import Classifier

template_folder = 'templates/';
log_folder = 'log/';
data_folder = 'tweets/';
result_folder = 'result/';
static_folder = '/var/www2/aggrestweets/live/repo/aggrestweets/static/';

class Test(object):

	def index(self):
		return "hoi";
	index.exposed = True;

class AggressiveTweetsDemo(object):

    def index(self):
        """"Shows the mainpage""";

        return open(template_folder+'enter_user.html').read();
    index.exposed = True

    def static_old(self,filename):
        return open(static_folder+filename).read();
    static_old.exposed = True

    def results(self,user):
        """Returns the result view""";

        table = get_resulttable(user);

        return open(template_folder+'result.html').read().replace('{%TWEETS%}',table).replace('{%USER%}',user);
    results.exposed = True;

    def analyze(self,user):
        """Starts the import and shows the progress""";

        def parrallel_analysis():
            tweets = tweetlib.get_all_tweets(user);
            tweet_str = [str(tweet) for tweet in tweets];

            filepath = data_folder+user;

            open(filepath,'w').write('\n'.join(tweet_str));
            self.log('Import succesvol.',logfile);

            self.log('Tweets analyseren.',logfile);
            classifier = Classifier();
            results = tweetlib.classify_tweets(classifier,tweets,result_folder+user+'.txt');
            self.log('Analyse voltooid!',logfile);

        logfile = open(log_folder+user+'.txt','w',0);
        self.log('Alle tweets importeren van '+user,logfile)

        Thread(target=parrallel_analysis).start();

        return open(template_folder+'analyze.html').read();
    analyze.exposed = True

    def log_file(self,user):
        """Returns the current logfile for the model creation of a user""";
        try:
            return open(log_folder+user+'.txt').read();
        except IOError:
            return '';
    log_file.exposed = True

    def log(self,message,logfile):
        print(message);
        logstr = message+'\n';
        logfile.write(logstr.encode());

def get_resulttable(user):

    results = open(result_folder+user+'.txt');
    table = '<table>';

    for n,line in enumerate(results):
        tid,score = line.split('\t');
        table += '<tr><td>'+id_to_embedded_tweet(tid)+'</td><td>'+score+'</td></tr>';

        if n > 15:
	        break;

    table += '</table>';
    return table;

def id_to_embedded_tweet(tid):

	return '<blockquote class="twitter-tweet" lang="nl"><a href="https://twitter.com/antalvdb/status/'+tid+'"></a></blockquote>'

#Standalone
if len(sys.argv) > 1 and sys.argv[1] == '--standalone':
    cherrypy.quickstart(AggressiveTweetsDemo());

#Apache
else:
    print('To run this as standalone, add --standalone');

    cherrypy.config.update({'environment': 'embedded'});
    application = cherrypy.Application(AggressiveTweetsDemo(),script_name=None,config={'/static':{'tools.staticdir.on':True,'tools.staticdir.dir':static_folder}})
