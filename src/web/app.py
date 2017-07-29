"""Web application module"""

import inspect
import cherrypy

class BaseController:
    """Base controller class"""

    def view(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        file_path = "web/views/{}.{}.html".format(type(self).__name__, calframe[1][3])
        return open(file_path)

class Home(BaseController):
    """Main application endpoint"""

    @cherrypy.expose
    def index(self):
        return self.view()
