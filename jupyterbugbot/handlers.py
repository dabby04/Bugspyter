import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from .chat import test
from .chat import request_api_key
from .chat import load_notebook
from .chat import analysis
import tornado
import os

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        # result=test()
        self.finish(json.dumps({
            "data": "This is /jupyterbugbot/get-example endpoint!",
            "result": test()
        }))

class ConfigHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data=self.get_json_body()
        data=input_data["key"]
        result=request_api_key(data)
        self.finish(json.dumps({
            "data": "This is /jupyterbugbot/get-example endpoint!",
            "result": result
        }))

class NotebookHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data=self.get_json_body()
        data=input_data["notebook_path"]
        result = json.loads(load_notebook(data))
        self.finish(json.dumps({
            "buggy_or_not": result["buggy_or_not"],
            "major_bug": result["major_bug"],
            "root_cause":result["root_cause"],
        }))
 
class AnalysisHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        result = analysis()
        self.finish(json.dumps({
            "result":result
        }))       

def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern1 = url_path_join(base_url, "jupyterbugbot", "get-example")
    route_pattern2=url_path_join(base_url,"jupyterbugbot","request_api")
    route_pattern3=url_path_join(base_url,"jupyterbugbot","load_notebook")
    route_pattern4=url_path_join(base_url,"jupyterbugbot","analysis")
    handlers = [(route_pattern1, RouteHandler),(route_pattern2, ConfigHandler),(route_pattern3, NotebookHandler),(route_pattern4, AnalysisHandler)]
    web_app.add_handlers(host_pattern, handlers)
    

