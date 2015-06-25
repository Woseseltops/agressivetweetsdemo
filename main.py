import os
import sys
import cherrypy
import tweetlib
import time
import json
import random
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
PASSWORD_FILES_FOLDER = 'password_files/';
PASSWORD_FILES = [PASSWORD_FILES_FOLDER+file for file in os.listdir(PASSWORD_FILES_FOLDER)];

# Put this function here temporarily because of caching

def get_profile_image_url(user,api=None,passwords='passwords.txt'):

    import twython as t

    if api==None:
        passwords = tweetlib.get_passwords(passwords);
        api = t.Twython(passwords['app_key'], passwords['app_secret'],
            passwords['oauth_token'], passwords['oauth_token_secret']);        

    return api.show_user(screen_name=user)['profile_image_url'];

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

        aggresso_score = calculate_aggresso_score(user);

        table = results_to_html(user,0,20);		

        chosen_password_file = random.choice(PASSWORD_FILES);

        content = open(TEMPLATE_FOLDER+'result.html').read();
        variables = {'tweets':table,'user':'@'+user,
                     'profile_image_url':get_profile_image_url(user,passwords=chosen_password_file),
                     'aggresso_score':int(round(aggresso_score*100)),
                     'aggresso_margin':aggresso_score*600};        

        for key, value in variables.items():
            content = content.replace('{%'+key.upper()+'%}',str(value));

        return content;
    results.exposed = True;

    def analyze(self,user):
        """Starts the import and shows the progress""";

        def parrallel_analysis():
            chosen_password_file = random.choice(PASSWORD_FILES);

            try:
                tweets = tweetlib.get_all_tweets(user,passwords=chosen_password_file);
            except: #Any problem
                self.log('<span class="error">Ai, er is iets mis gegaan! Mogelijk vindt Twitter dat we teveel tweets opvragen,'+\
                         ' of bestaat het account niet. Kijk hier eens voor wat accounts die het altijd doen: '+\
                         '<a href="results/geertwilderspvv">geertwilderspvv</a>, <a href="results/sylviawitteman">sylviawitteman</a>, <a href="results/femkehalsema">femkehalsema</a>, <a href="results/willemhoIIeeder">willemhoIIeeder</a></span>',
                         logfile);

            tweet_str = [str(tweet) for tweet in tweets];

            filepath = DATA_FOLDER+user;

            open(filepath,'w').write('\n'.join(tweet_str));
            self.log('Import succesvol.',logfile);

            self.log('Tweets analyseren.',logfile);
            classifier = Classifier();
            results = tweetlib.classify_tweets(classifier,tweets,RESULT_FOLDER+user+'.txt');
            self.log('Analyse voltooid!',logfile);

        result_path = RESULT_FOLDER+user+'.txt';
        SECONDS_IN_A_MONTH = 2629743;

        if not os.path.isfile(result_path) or time.time() - os.path.getmtime(result_path) > SECONDS_IN_A_MONTH:
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

def calculate_aggresso_score(user):

    results = open(RESULT_FOLDER+user+'.txt').readlines();
    total_score = 0;

    for n,line in enumerate(results[:20]):
        score = float(line.split('\t')[-1]);
        simplified_score = int(round(score,2)*100);
        total_score += score;

    return total_score/20;

#Standalone
if len(sys.argv) > 1 and sys.argv[1] == '--standalone':
    cherrypy.quickstart(AggressiveTweetsDemo());

#Apache
else:
    print('To run this as standalone, add --standalone');

    cherrypy.config.update({'environment': 'embedded'});
    application = cherrypy.Application(AggressiveTweetsDemo(),script_name=None,config={'/static':{'tools.staticdir.on':True,'tools.staticdir.dir':STATIC_FOLDER}})
