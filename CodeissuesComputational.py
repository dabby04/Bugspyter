#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

api_key_file='../api.txt'

with open(api_key_file,'r') as file:
    api_key=file.read().strip()

os.environ["GROQ_API_KEY"] = api_key

llm=ChatGroq(model="llama3-8b-8192",max_retries=3) #initialising llm

argument = sys.argv[1]  # Name of notebook being passed



# In[2]:

path=f"../{argument}"
loader = GenericLoader.from_filesystem(
   path, #need to get name of notebook and pass it here
    glob="*",
    suffixes=[".ipynb"],
    parser=LanguageParser(),
)
docs = loader.load()


# In[3]:


content=docs[0].page_content


# In[4]:


loader2 = NotebookLoader(
    path,
    include_outputs=True,
    max_output_length=20
)
docs2=loader2.load_and_split()


# In[5]:


content2 = docs2

# In[6]:
workflow = StateGraph(state_schema=MessagesState)

# @tool
# def buggy_or_not(notebook:str)->str:
    # """ Identifies if the notebook is buggy """
 
def buggy_or_not(state: MessagesState):
       
    system_message= """You are a reviewer for computational notebooks.
    Answer all questions to the best of your ability concerning this notebook"""
    messages = [SystemMessage(content=system_message)] + state["messages"]
    response = llm.invoke(messages)

    return {"messages": response}

# Define the node and edge
workflow.add_node("model", buggy_or_not)
workflow.add_edge(START, "model")

# Add simple in-memory checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config={"configurable": {"thread_id": "1"}}

# In[7]:
display(Markdown("<b>Is the notebook buggy?</b>"))
for content in content2:
    app.invoke({"messages":[HumanMessage(content=content.page_content)]
                    },config,)
res=app.invoke({"messages":[HumanMessage(content="Is the notebook I provided earlier buggy? Please answer my question only with Yes or No. Please make sure that the answer provided is only in one word")]
                },config,)["messages"][-1].content
print(res)
# boolean_parser=BooleanOutputParser()
# chain = prompt.pipe(llm)| boolean_parser


display(Markdown("<b>What major bug type is in the notebook?</b>"))

res=app.invoke({"messages":[HumanMessage(content="""If you said the notebook was buggy, out of these bugs, what is the major bug in this computational notebook?
List of bugs: Kernel, Conversion, Portability, Environments and Settings, Connection, Processing, Cell Defect, and Implementation
Please respond only with one bug out of the list if the notebook is buggy""")]},config,)["messages"][-1].content
print(res)


# response_schema = [
#     ResponseSchema(name="answer", description="answer to the user's question in a single word or two"),
# ]
# output_parser = StructuredOutputParser.from_response_schemas(response_schema)
# format_instructions = output_parser.get_format_instructions()

# """ Identifies which of the bugs are present in the notebooks """
# system_message= """You are a reviewer for computational notebooks.
# Out of these bugs, what is the major bug in this computational notebook?
# List of bugs: Kernel, Conversion, Portability, Environments and Settings, Connection, Processing, Cell Defect, and Implementation
# You respond only with one bug out of the list"""

# prompt=ChatPromptTemplate.from_messages([("system",system_message),
#             ("human","{input}")])
# # formatted_prompt=prompt.format_prompt(human_message="{input}",format_instructions = output_parser.get_format_instructions())

# chain = prompt.pipe(llm) 
# response=chain.invoke({"input":content2})
# print(response)

# In[8]:
display(Markdown("<b>What is the root cause of bugs in the notebook?</b>"))

res=app.invoke({"messages":[HumanMessage(content="""You specifically identify the root causes for bugs in computational notebooks.
The root causes you choose are from this list:
1. Install and Configuration problems
2. Version problems
3. Deprecation
4. Permission denied
5. Time Out
6. Memory error
7. Coding error
8. Logic error
9. Hardware software limitations
10. Unknown
If you said the notebook was buggy, please respond only with a root cause from this list and the reason why in a sentence.""")]},config,)["messages"][-1].content
print(res)

# system_message= """You are a reviewer for computational notebooks.
# You specifically identify the root causes for bugs in computational notebooks.
# The root causes you choose are from this list:
# 1. Install and Configuration problems
# 2. Version problems
# 3. Deprecation
# 4. Permission denied
# 5. Time Out
# 6. Memory error
# 7. Coding error
# 8. Logic error
# 9. Hardware software limitations
# 10. Unknown
# You respond only with a root cause from this list and the reason why."""

# prompt=ChatPromptTemplate.from_messages([("system",system_message),
#             ("human","{input}")])

# chain = prompt.pipe(llm)
# response=chain.invoke({"input":content2})
# print(response)

# In[9]:


@tool
def code_quality(notebook:str) -> str:
    """Returns suggestions on code quality issues to improve in the noteboook"""
    system_message= """You are a reviewer for computational notebooks.
    You specifically review code smells, code defects, and cell defects within these notebooks.
    For code smells, you look at things such as lack of visualisations, inadequate visualisations for data cleaning or exploration, wrong library usage, algorithm errors.
    For code defects, you look for syntax errors, semantic errors, and debugging errors.
    For cell defects you look at issues such as having markdown in code blocks, layout bugs, and indentation errors.
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response


# In[10]:


@tool
def security_and_confidentiality(notebook:str) -> str:
    """Returns suggestions on security issues to improve in the noteboook"""
    system_message= """You are a reviewer for computational notebooks.
    You specifically handle the security and confidentiality issues for notebooks which include information leakage and input validation and sanitisation.
    For issues in information leakage, you might look at security issues and lack of data confidentiality.
    For input validation and sanitisation, you might look at wrong dataset file paths.
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response


# In[11]:


@tool
#Need a tool that handles resources
def resource_management(notebook:str) -> str:
    """Returns suggestions on possible leaks in the noteboook"""
    system_message= """You are a reviewer for computational notebooks.
    You specifically handle resource management of the notebook such as file handle leaks, socket handle leaks, memory leaks, and resource exhaustion. 
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response


# In[12]:


@tool
# Need a tool that handles exceptions and errors
def exception_error(notebook:str) -> str:
    """Returns suggestions on possible leaks in the noteboook"""
    system_message= """You are a reviewer for computational notebooks. 
    You specifically manage exception and error handling such as inadequate error handling or exceptions logic.
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response


# In[13]:


@tool
# Need a tool that manages the dependency and environment
def dependency_env(notebook:str) -> str:
    """Returns suggestions on possible leaks in the noteboook"""
    system_message= """You are a reviewer for computational notebooks.
    You handle dependency issues and environment management issues in the notebook. 
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response


# In[14]:


# Create the agent with tools
tools=[code_quality,security_and_confidentiality,resource_management,exception_error,dependency_env]
agent= langgraph_agent_executor = create_react_agent(
    llm, tools,checkpointer=memory)


# In[15]:


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


# In[ ]:


query= f"I asked you earlier if the notebook was buggy, what was your reply? If your reply was yes, conduct a bug and vulnerability analysis using the tools (not limited to): code_quality,security_and_confidentiality,resource_management,exception_error,dependency_env. Also provide code fixes where necessary"
inputs={"messages":[("user",query)]}
message=agent.invoke(inputs,config)["messages"][-1].content
display(Markdown(message))
# print_stream(agent.stream(inputs, stream_mode="values"))

