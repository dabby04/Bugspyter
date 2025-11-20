import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
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
        self.finish(json.dumps({
            "data": "This is /bugspyter/get-example endpoint!",
        }))

class ConfigHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data=self.get_json_body()
        selectedLLM=input_data["selectedLLM"]
        selectedModel= input_data["selectedModel"]
        key=input_data["key"]
        result=request_api_key(selectedLLM,selectedModel,key)
        self.finish(json.dumps({
            "data": "This is /bugspyter/get-example endpoint!",
            "result": result
        }))

class NotebookHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data=self.get_json_body()
        data=input_data["notebook_path"]
        result = json.loads(load_notebook(data))
        self.finish(json.dumps({
            "buggy_or_not_final": result["buggy_or_not_final"],
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
    route_pattern1 = url_path_join(base_url, "bugspyter", "get-example")
    route_pattern2=url_path_join(base_url,"bugspyter","request_api")
    route_pattern3=url_path_join(base_url,"bugspyter","load_notebook")
    route_pattern4=url_path_join(base_url,"bugspyter","analysis")
    handlers = [(route_pattern1, RouteHandler),(route_pattern2, ConfigHandler),(route_pattern3, NotebookHandler),(route_pattern4, AnalysisHandler)]
    web_app.add_handlers(host_pattern, handlers)
    

