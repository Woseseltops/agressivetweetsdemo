import cherrypy

template_folder = 'templates/';

class agressive_tweets_demo(object):

    def index(self):
        """"Shows the mainpage""";

	return open(template_folder+'enter_user.html').read();

    index.exposed = True

    def log_file(self,user):
        """Returns the current logfile for the model creation of a user""";
        return open(maindir+'/logs/create_model_'+user+'.txt').read();
    log_file.exposed = True;

cherrypy.quickstart(agressive_tweets_demo());

#application = cherrypy.Application(agressivetweetsdemo(), script_name=None, config=None)
