import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from chat import request_api_key
from chat import load_notebook

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        result=request_api_key()
        self.finish(json.dumps({
            "data": "This is /jupyterbugbot/get-example endpoint!",
            "result": result
        }))
        
    
    # @tornado.web.authenticated
    # def post(self):
    #     # input_data is a dictionary with a key "name"
    #     input_data = self.get_json_body()
    #     data = input_data["name"]

    #     self.finish(json.dumps(data))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "jupyterbugbot", "get-example")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
    

