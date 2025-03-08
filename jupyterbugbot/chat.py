# Class that handles all AI calls
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

# Things to consider:
# I want to initialise

def request_api_key():
    """
    Makes sure users API key is received and LLM is initialised
    """
    api_key_file='api.txt'
    with open(api_key_file,'r') as file:
        api_key=file.read().strip()
    
    if not api_key:
        return "Error: No API key found in the file."
    
    os.environ["GROQ_API_KEY"] = api_key
    llm=ChatGroq(model="llama3-8b-8192",max_retries=3) #initialising llm
    return llm,"LLM initialised"

def load_notebook(llm, argument):
    """
    Load the notebook content into the LLM and run all request calls
    """
    argument = sys.argv[1]  # Name of notebook being passed
    path=f"../{argument}"
    loader = GenericLoader.from_filesystem(
        path, #need to get name of notebook and pass it here
        glob="*",
        suffixes=[".ipynb"],
        parser=LanguageParser(),
    )
    docs = loader.load()
    return("works")
    
    


    
