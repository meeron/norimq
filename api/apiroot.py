"""Queues api module"""

import cherrypy

class Api:
    """Api root class"""

    def __init__(self):
        self.queues = Queues()

class Queues:
    """Queues class"""

    @cherrypy.expose
    def index(self):
        return "Queues"
