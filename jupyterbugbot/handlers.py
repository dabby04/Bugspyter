import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from .chat import test
from .chat import request_api_key
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
        
    
    # @tornado.web.authenticated
    # def post(self):
    #     # input_data is a dictionary with a key "name"
    #     input_data = self.get_json_body()
    #     data = input_data["name"]

    #     self.finish(json.dumps(data))

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

def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern1 = url_path_join(base_url, "jupyterbugbot", "get-example")
    route_pattern2=url_path_join(base_url,"jupyterbugbot","request_api")
    handlers = [(route_pattern1, RouteHandler),(route_pattern2, ConfigHandler)]
    web_app.add_handlers(host_pattern, handlers)
    

