from typing import Literal
import warnings
import sys

warnings.filterwarnings("ignore")
from pprint import pprint
import json
import os
from pydantic import BaseModel, Field, model_validator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatCohere
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_anthropic import ChatAnthropic

from langchain_community.document_loaders import NotebookLoader

from langchain.tools import tool
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,FewShotChatMessagePromptTemplate, MessagesPlaceholder

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph, END

from langgraph.graph.message import add_messages

from IPython.display import display, Markdown
from .bandit import run_bandit

# class AgentState(TypedDict):
#     """The state of the agent."""
#     messages: Annotated[Sequence[BaseMessage], add_messages]


llm = None
memory=MemorySaver()
config={"configurable": {"thread_id": "1"}}

def request_api_key(selectedLLM,selectedModel,api_key):
    """
    Makes sure users API key is received and LLM is initialised
    """
    if not api_key:
        return "API key not initialised"
    
    global llm
    if selectedLLM=='Anthropic':
        os.environ["ANTHROPIC_API_KEY"] = api_key
        try:
            llm = ChatAnthropic(
                model=selectedModel,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        except:
            return("Could not initialise LLM")
    elif selectedLLM=='Cohere':
        os.environ["COHERE_API_KEY"] = api_key
        try:
            llm = ChatCohere(
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        except:
            return("Could not initialise LLM")
    elif selectedLLM=='Groq':
        os.environ["GROQ_API_KEY"] = api_key
        try:
            llm = ChatGroq(
                model=selectedModel,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        except:
            return("Could not initialise LLM")
    elif selectedLLM=='Nvidia':
        os.environ["NVIDIA_API_KEY"] = api_key
        try:
            llm = ChatNVIDIA(
                model=selectedModel,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        except:
            return("Could not initialise LLM")
    else:
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            llm = ChatGoogleGenerativeAI(
                model=selectedModel,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        except:
            return("Could not initialise LLM")
    
    return "LLM initialised"

def load_notebook(argument):
    """
    Load the notebook content into the LLM and run all request calls
    """
    path=f"{argument}"
    loader = NotebookLoader(
    path,
    include_outputs=True,
    max_output_length=20
)
    docs=loader.load_and_split()
    content = docs
    
    bandit_report= run_bandit(argument)
    
    def buggy_or_not(state: MessagesState):
        """
        Sets up conversational memory with LLM
        """
        
        system_message= """You are a reviewer for computational notebooks.
        Answer all questions to the best of your ability concerning this notebook"""
        messages = [SystemMessage(content=system_message)] + state["messages"]
        response = llm.invoke(messages)

        return {"messages": response}
    
    workflow = StateGraph(state_schema=MessagesState)
    # Define the node and edge
    workflow.add_node("model", buggy_or_not)
    workflow.add_edge(START, "model")

    # compile with memory
    app = workflow.compile(checkpointer=memory)
    
    for contentChunks in content:
        app.invoke({"messages":[HumanMessage(content=contentChunks.page_content)]
                    },config,)
    res=app.invoke({"messages":[HumanMessage(content="Is the notebook I provided earlier buggy? Please answer my question only with Yes or No. Please make sure that the answer provided is only in one word")]
                },config,)["messages"][-1].content
   
    buggy=res
    
    buggy2=app.invoke({"messages":[HumanMessage(content=f"This is a security report produced by Bandit: {bandit_report}"),
                                   HumanMessage(content="Is the notebook I provided earlier buggy? Please answer my question only with Yes or No. Please make sure that the answer provided is only in one word")
                                   ]},config)["messages"][-1].content   
    
    
    res=app.invoke({"messages":[HumanMessage(content="""If you said the notebook was buggy, out of these bugs, what is the major bug in this computational notebook?
List of bugs: Kernel, Conversion, Portability, Environments and Settings, Connection, Processing, Cell Defect, and Implementation
Please respond only with one bug out of the list if the notebook is buggy""")]},config,)["messages"][-1].content
    major_bug=res
    
    res=app.invoke({"messages":[HumanMessage(content="""You specifically identify the root causes for bugs in computational notebooks.
The root causes you choose are from this list: Install and Configuration problems, Version problems, Deprecation, Permission denied
, Time Out, Memory error, Coding error, Logic error, Hardware software limitations, and  Unknown
If you said the notebook was buggy, please respond only with a root cause from this list and the reason why in a sentence.""")]},config,)["messages"][-1].content
    
    root_cause=res
    result=json.dumps({"buggy_or_not": buggy,"buggy_or_not_final":buggy2,"major_bug":major_bug,"root_cause":root_cause})
    return(result)

def analysis():
    """
    Runs the analysis using agent tools
    """
    tools=[code_quality,security_and_confidentiality,resource_management,exception_error,dependency_env]
    tools_by_name = {tool.name: tool for tool in tools}
    llm_with_tools = llm.bind_tools(tools)
    
    # Nodes
    def llm_call(state: MessagesState):
        """LLM decides whether to call a tool or not"""

        return {
            "messages": [
                llm_with_tools.invoke(
                    [
                        SystemMessage(
                            # content="""
                            # You are a helpful assistant who identifies and fixes code bugs in computational notebooks, providing both explanations and corrected code.
                            # """
                            content="""
                            You are a notebook diagnostics assistant.
                            You have access to these tools: code_quality, security_and_confidentiality, resource_management, exception_error, dependency_env.
                            Rules:
                            - Call ONLY the tools strictly relevant to the current user query and available context.
                            - Do NOT call a tool if its domain is not clearly implicated.
                            - Maximum 2 tools per turn unless absolutely necessary.
                            If no tool is needed, just answer directly.
                            """
                        )
                    ]
                    + state["messages"]
                )
            ]
        }
    
    # Custom ToolNode
    def tool_node(state: dict):
        """Performs the tool call"""

        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        return {"messages": result}
    
    # Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
    def should_continue(state: MessagesState) -> Literal["tool_node", END]:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM makes a tool call, then perform an action
        if last_message.tool_calls:
            return "tool_node"

        # Otherwise, we stop (reply to the user)
        return END
    
    # Build workflow
    agent_builder = StateGraph(MessagesState)

    # Add nodes
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)

    # Add edges to connect nodes
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call",
        should_continue,
        ["tool_node", END]
    )
    agent_builder.add_edge("tool_node", "llm_call")

    # Compile the agent
    agent = agent_builder.compile(checkpointer=memory)
    
    # query= f"Use tools to answer. I asked you earlier if the notebook was buggy, what was your reply? If your reply was yes, on the same notebook, conduct a bug and vulnerability analysis using the tools (not limited to): code_quality, security_and_confidentiality,resource_management,exception_error,dependency_env. Also provide code fixes where necessary."
    query= """Using the notebook and any supporting information available (including summaries, security reports, or a runtime execution report if one exists), determine whether you previously assessed the notebook as buggy. 
    If you did, produce a detailed bug and vulnerability analysis. 
    Address any issues you identify across relevant dimensions such as correctness, security, confidentiality, resource handling, error management, and dependency or environment consistency. 
    Only analyze areas that are applicable based on the information available. 
    Provide explanations and corrected or improved code where appropriate."""
    messages = [HumanMessage(content=query)]
    messages = agent.invoke({"messages": messages},config)
    return(messages["messages"][-1].content)


@tool
def code_quality(notebook:str) -> str:
    """Returns suggestions on code quality issues to improve in the notebook"""
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

@tool
def security_and_confidentiality(notebook:str) -> str:
    """Returns suggestions on security issues/vulnerabilities to improve in the notebook"""
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

@tool
#Need a tool that handles resources
def resource_management(notebook:str) -> str:
    """Returns suggestions on possible leaks in the notebook"""
    system_message= """You are a reviewer for computational notebooks.
    You specifically handle resource management of the notebook such as file handle leaks, socket handle leaks, memory leaks, and resource exhaustion. 
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response

@tool
# Need a tool that handles exceptions and errors
def exception_error(notebook:str) -> str:
    """Returns suggestions on possible exceptions and errors in the notebook"""
    system_message= """You are a reviewer for computational notebooks. 
    You specifically manage exception and error handling such as inadequate error handling or exceptions logic.
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response

@tool
# Need a tool that manages the dependency and environment
def dependency_env(notebook:str) -> str:
    """Returns suggestions on possible dependency problems in the notebook"""
    system_message= """You are a reviewer for computational notebooks.
    You handle dependency issues and environment management issues in the notebook. 
    You respond only with feedback and suggestions to fix."""

    prompt=ChatPromptTemplate.from_messages([("system",system_message),
              ("human","{input}")])

    chain = prompt.pipe(llm)
    response=chain.invoke({"input":notebook})
    return response

