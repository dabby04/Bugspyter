import warnings
import sys

warnings.filterwarnings("ignore")
from pprint import pprint

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders import NotebookLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain.output_parsers import BooleanOutputParser,ResponseSchema, StructuredOutputParser
from langchain_text_splitters import Language
import json
from langchain import hub
from langchain_core.messages import HumanMessage
import os
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,FewShotChatMessagePromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains import LLMChain
from langgraph.prebuilt import create_react_agent
from langgraph.errors import GraphRecursionError
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, model_validator
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from IPython.display import display, Markdown

llm = None

def test():
    return "Please work"

def request_api_key(api_key):
    """
    Makes sure users API key is received and LLM is initialised
    """
    if not api_key:
        return "API key not initialised"
    os.environ["GROQ_API_KEY"] = api_key
    try:
        global llm
        llm=ChatGroq(model="llama3-8b-8192",max_retries=3) #initialising llm
    except:
        return("Could not initialise LLM")
    return "LLM initialised"

def load_notebook(argument):
    """
    Load the notebook content into the LLM and run all request calls
    """
    argument = sys.argv[1]  # Name of notebook being passed
    path=f"../{argument}"
    loader = NotebookLoader(
    path,
    include_outputs=True,
    max_output_length=20
)
    docs=loader.load_and_split()
    content = docs
    
    workflow = StateGraph(state_schema=MessagesState)
    # Define the node and edge
    workflow.add_node("model", buggy_or_not)
    workflow.add_edge(START, "model")

    # Add simple in-memory checkpointer
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    config={"configurable": {"thread_id": "1"}}

    return("works")

def buggy_or_not(state: MessagesState):
       
    system_message= """You are a reviewer for computational notebooks.
    Answer all questions to the best of your ability concerning this notebook"""
    messages = [SystemMessage(content=system_message)] + state["messages"]
    response = llm.invoke(messages)

    return {"messages": response}

