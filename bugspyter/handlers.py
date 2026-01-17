import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from .chat import llm_call_router, request_api_key, router_workflow
from .chat import load_notebook
from .chat import analysis, load_notebook_content, build_memory, get_router
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
        key=input_data.get("key")
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
        # result = json.loads(load_notebook(data))
        
        result=json.loads(load_notebook_content(data))
        docs = result["docs"]
        bandit_report= result["bandit_report"]
        # app = build_memory("""You are a reviewer for computational notebooks. 
                        #    Answer all questions to the best of your ability concerning this notebook.""")
        load_notebook(docs, bandit_report)
        
        decision = llm_call_router({
            "input": "Decide if runtime or analysis is required."
            })["decision"]
        
        self.finish(json.dumps({
                "status": "Notebook loaded",
                "decision": decision,
            }))
        
class RouterHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        input_data=self.get_json_body()
        notebook_path = input_data["notebook_path"]
        decision = input_data["decision"]
        
        if not decision:
            decision = llm_call_router({"input": "Continue routing based on current memory and reports."})["decision"]
            
        result_json = json.loads(router_workflow(decision, notebook_path))
        buggy_questions = json.loads(result_json["buggy_questions"])
        analysis = result_json["analysis"]
        self.finish(json.dumps({
            "buggy_or_not": buggy_questions["buggy_or_not"],
            "major_bug": buggy_questions["major_bug"],
            "root_cause":buggy_questions["root_cause"],
            "analysis":analysis
        }))
        
 
# class AnalysisHandler(APIHandler):
#     @tornado.web.authenticated
#     def get(self):
#         result = analysis()
#         self.finish(json.dumps({
#             "result":result
#         }))       

def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern1 = url_path_join(base_url, "bugspyter", "get-example")
    route_pattern2=url_path_join(base_url,"bugspyter","request_api")
    route_pattern3=url_path_join(base_url,"bugspyter","load_notebook")
    route_pattern4=url_path_join(base_url,"bugspyter","router_workflow")
    handlers = [(route_pattern1, RouteHandler),(route_pattern2, ConfigHandler),(route_pattern3, NotebookHandler),(route_pattern4, RouterHandler)]
    web_app.add_handlers(host_pattern, handlers)
    

