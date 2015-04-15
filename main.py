import sys
import cherrypy
import tweetlib
import time
import json
from threading import Thread

from ctypes import cdll 
for library in ['libticcutils.so.2','libfolia.so.3','libucto.so.2']:
	lib_path = '/var/www2/aggrestweets/live/virtualenv/aggrestweets/lib/'+library;
	print(lib_path);
	cdll.LoadLibrary(lib_path); 

from classify_aggression import Classifier

TEMPLATE_FOLDER = 'templates/';
LOG_FOLDER = 'log/';
DATA_FOLDER = 'tweets/';
RESULT_FOLDER = 'result/';
CORRECTIONS_FOLDER = 'corrections/';
STATIC_FOLDER = '/var/www2/aggrestweets/live/repo/aggrestweets/static/';
THRESHOLD_HIGH = 0.6;
THRESHOLD_MEDIUM = 0.4;

class AggressiveTweetsDemo(object):

    def index(self):
        """"Shows the mainpage""";

        return open(TEMPLATE_FOLDER+'enter_user.html').read();
    index.exposed = True

    def static_old(self,filename):
        return open(STATIC_FOLDER+filename).read();
    static_old.exposed = True

    def results(self,user):
        """Returns the result view""";

        table = results_to_html(user,0,20);

        return open(TEMPLATE_FOLDER+'result.html').read().replace('{%TWEETS%}',table).replace('{%USER%}','@'+user);
    results.exposed = True;

    def analyze(self,user):
        """Starts the import and shows the progress""";

        def parrallel_analysis():
            tweets = tweetlib.get_all_tweets(user);
            tweet_str = [str(tweet) for tweet in tweets];

            filepath = DATA_FOLDER+user;

            open(filepath,'w').write('\n'.join(tweet_str));
            self.log('Import succesvol.',logfile);

            self.log('Tweets analyseren.',logfile);
            classifier = Classifier();
            results = tweetlib.classify_tweets(classifier,tweets,RESULT_FOLDER+user+'.txt');
            self.log('Analyse voltooid!',logfile);

        logfile = open(LOG_FOLDER+user+'.txt','w',0);
        self.log('Alle tweets importeren van '+user,logfile)

        Thread(target=parrallel_analysis).start();

        return open(TEMPLATE_FOLDER+'analyze.html').read();
    analyze.exposed = True

    def log_file(self,user):
        """Returns the current logfile for the model creation of a user""";
        try:
            return open(LOG_FOLDER+user+'.txt').read();
        except IOError:
            return '';
    log_file.exposed = True

    def correct(self,user,tweet_id,our_prediction,timestamp,correction=None):

        if correction == None:

            home_link = 'results/'+user;

            prediction_to_number = {'low_aggressive':'0','medium_aggressive':'1','high_aggressive':'2'};

            content = open(TEMPLATE_FOLDER+'correct.html').read();

            for placeholder, replacement in [('{%TWEET_ID%}',tweet_id),
                                             ('{%OUR_CLASSIFICATION%}',prediction_to_number[our_prediction]),
                                             ('{%HOME_LINK%}',home_link)
                                             ]:

                content = content.replace(placeholder,replacement);

            return content;

        else:

            dict_with_all_info = {'twitterID':user,
                                  'tweetID':tweet_id,
                                  'ourClassification':our_prediction,
                                  'theirClassification':correction,
                                  'ourClassificationTimeStamp':timestamp};

            json.dump(dict_with_all_info,open(CORRECTIONS_FOLDER+user+'.'+tweet_id+'.'+timestamp+'.json','w'));

            return open(TEMPLATE_FOLDER+'thanks.html').read().replace('{%TWITTER_USER%}',user);

    correct.exposed = True

    def log(self,message,logfile):
        print(message);
        logstr = message+'\n';
        logfile.write(logstr.encode());

def results_to_html(user,fro,to):

    results = open(RESULT_FOLDER+user+'.txt').readlines();
    html = '';
    timestamp = str(time.time());

    for n,line in enumerate(results[fro:to]):
        tid,score = line.split('\t');
        score = float(score);
        simplified_score = int(round(score,2)*100);
       

        if score > THRESHOLD_HIGH:
            aggression_group = "high_aggressive";
        elif score > THRESHOLD_MEDIUM:
            aggression_group = "medium_aggressive";
        else:
            aggression_group = "low_aggressive";

        html += '<div class="tweet" id="'+ tid +'"></div><div class="aggression_score aggression_resultfield '+aggression_group+'">'+str(simplified_score)+'</div><div class="correct_text"><a href="../correct?user=' + user + '&tweet_id=' + tid + '&our_prediction=' + aggression_group + '&timestamp=' + timestamp + '">Dit klopt niet!</a></div>';

    return html;

#Standalone
if len(sys.argv) > 1 and sys.argv[1] == '--standalone':
    cherrypy.quickstart(AggressiveTweetsDemo());

#Apache
else:
    print('To run this as standalone, add --standalone');

    cherrypy.config.update({'environment': 'embedded'});
    application = cherrypy.Application(AggressiveTweetsDemo(),script_name=None,config={'/static':{'tools.staticdir.on':True,'tools.staticdir.dir':STATIC_FOLDER}})
