from typing import Literal, Optional, TypedDict
import warnings
import sys

warnings.filterwarnings("ignore")
from pprint import pprint
import json
import os
import keyring
from pydantic import BaseModel, Field, model_validator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatCohere
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface import HuggingFacePipeline

from langchain_community.document_loaders import NotebookLoader

from langchain.tools import tool
from langchain.messages import HumanMessage, SystemMessage, ToolMessage, RemoveMessage
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,FewShotChatMessagePromptTemplate, MessagesPlaceholder

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph, END

from langgraph.graph.message import add_messages
from langchain_core.documents import Document

from IPython.display import display, Markdown
from .bandit import run_bandit
from .runtime_execution import create_JSON_report

# class AgentState(TypedDict):
#     """The state of the agent."""
#     messages: Annotated[Sequence[BaseMessage], add_messages]


llm = None
memory=MemorySaver()
config={"configurable": {"thread_id": "1"}}
app = None

class Route(BaseModel):
    step: Literal["runtime", "analysis"] = Field(
        None, description="The next step in the routing process"
    )

def get_router():
    """ Create a structured-output router"""
    return llm.with_structured_output(Route)

class State(TypedDict):
    input: str
    decision: str
    output: str
    summary: Optional[str]

LLM_ENV_KEYS = {
    "Anthropic": "ANTHROPIC_API_KEY",
    "Cohere": "COHERE_API_KEY",
    "Groq": "GROQ_API_KEY",
    "Nvidia": "NVIDIA_API_KEY",
    "Qwen": "HUGGINGFACEHUB_API_TOKEN",
    "Gemini": "GOOGLE_API_KEY"
}

def get_api_key_for_llm(selectedLLM, api_key=None):
    """
    Retrieves the API key from keyring, or prompts user if not available.
    """
    service_name = LLM_ENV_KEYS.get(selectedLLM)

    if api_key:
        # store in keyring for future sessions
        keyring.set_password("bugspyter", service_name, api_key)
        return api_key

    # Try keyring first
    stored_key = keyring.get_password("bugspyter", service_name)
    if stored_key:
        return stored_key

    # fallback
    return "LLM not initialised"

def clear_all_api_keys():
    results = {}
    for key_name in LLM_ENV_KEYS.values():
        try:
            keyring.delete_password("bugspyter", key_name)
            results[key_name] = "cleared"
        except Exception:
            results[key_name] = "not found"
    return results

def request_api_key(selectedLLM,selectedModel,api_key):
    """
    Makes sure users API key is received and LLM is initialised
    """
    api_key = get_api_key_for_llm(selectedLLM, api_key)
    global llm
    
    try:
        if selectedLLM=='Anthropic':
            llm = ChatAnthropic(
                model=selectedModel,
                api_key = api_key,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        
        elif selectedLLM=='Cohere':
            llm = ChatCohere(
                temperature=0,
                api_key = api_key,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        elif selectedLLM=='Groq':
            llm = ChatGroq(
                model=selectedModel,
                api_key = api_key,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        elif selectedLLM=='Nvidia':
            llm = ChatNVIDIA(
                model=selectedModel,
                api_key = api_key,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
        elif selectedLLM=='Qwen':
            model = HuggingFacePipeline.from_model_id(
                model_id=selectedModel,
                api_key = api_key,
                task="text-generation",
                device_map="auto",
                model_kwargs={
                    "low_cpu_mem_usage": True,
                    "torch_dtype": "auto"
                }
            )
            llm = ChatHuggingFace(llm=model, max_retries=3) #initialising llm
            llm.invoke("Hello")
        else:
            llm = ChatGoogleGenerativeAI(
                model=selectedModel,
                api_key = api_key,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=3,
                ) #initialising llm
            llm.invoke("Hello")
    except:
            return("Could not initialise LLM")
    
    return "LLM initialised"

def load_notebook_content(notebook_path):
    """
    Load the notebook content into the LLM and run all request calls
    """
    path=f"{notebook_path}"
    loader = NotebookLoader(
    path,
    include_outputs=True,
    max_output_length=20
)
    docs=loader.load_and_split()
    docs_as_dict = [
        {
            "page_content": d.page_content,
            "metadata": d.metadata
        }
        for d in docs
    ]
    bandit_report= run_bandit(notebook_path)
    result = json.dumps({"docs":docs_as_dict,"bandit_report":bandit_report})
    return result

def build_memory(system_message:str):
    """Building Langgraph conversational memory"""
    def llm_node(state: MessagesState):
        """
        Sets up conversational memory with LLM
        """
        messages = [SystemMessage(content=system_message)] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": response}
    
    workflow = StateGraph(state_schema=MessagesState)
    # Define the node and edge
    workflow.add_node("model", llm_node)
    workflow.add_edge(START, "model")

    # compile with memory
    return workflow.compile(checkpointer=memory)

def load_notebook( docs, bandit_report):
    """Pass notebook and bandit report to the LLM"""
    global app
    app = build_memory("""You are a reviewer for computational notebooks. 
                           Answer all questions to the best of your ability concerning this notebook.""")
    docs_reconstructed = [
        Document(
            page_content=d["page_content"],
            metadata=d["metadata"]
        )
        for d in docs
    ]
    for contentChunks in docs_reconstructed:
        app.invoke({"messages":[HumanMessage(content=contentChunks.page_content)]
                    },config,)
    app.invoke({"messages": [HumanMessage(content=f"This is a security report produced by Bandit for the notebook: {bandit_report}")]},config)
    
def buggy_or_not(runtime_json: Optional[str]=None):
    """Determine if the notebook is buggy, what is the bug type, and root cause"""
    buggy=app.invoke({"messages":[
                                HumanMessage(content=f"This is a runtime execution report (JSON); this runtime report could be empty; if it is empty, find it irrelevant: {runtime_json}"),
                                HumanMessage(content="Is the notebook I provided earlier buggy? Please answer my question only with Yes or No. Please make sure that the answer provided is only in one word")
                                ]},config)["messages"][-1].content
        
#     res=app.invoke({"messages":[HumanMessage(content="""If you said the notebook was buggy, out of these bugs, what is the major bug in this computational notebook?
# List of bugs: Kernel, Conversion, Portability, Environments and Settings, Connection, Processing, Cell Defect, and Implementation
# Please respond only with one bug out of the list if the notebook is buggy""")]},config,)["messages"][-1].content
#     major_bug=res
    res=app.invoke({"messages":[HumanMessage(content="""If you said the notebook was buggy, out of these bugs, what is the major bug in this computational notebook?
List of bugs: Attribute Error, Data Value Violation, Feature name mismatch, Index error, Invalid argument, IO Error, Key Error, Model Initialization Error, Module not found, Runtime error, Tensor shape mismatch, Type error, Unsupported Broadcast, Value Error, and Variable Not Found
Please respond only with one bug out of the list if the notebook is buggy""")]},config,)["messages"][-1].content
    major_bug=res

#     res=app.invoke({"messages":[HumanMessage(content="""You specifically identify the root causes for bugs in computational notebooks.
# The root causes you choose are from this list: Install and Configuration problems, Version problems, Deprecation, Permission denied
# , Time Out, Memory error, Coding error, Logic error, Hardware software limitations, and  Unknown
# If you said the notebook was buggy, please respond only with a root cause from this list and the reason why in a sentence.""")]},config,)["messages"][-1].content
#     root_cause=res
    res=app.invoke({"messages":[HumanMessage(content="""You specifically identify the root causes for bugs in computational notebooks.
The root causes you choose are from this list: API misuse, data confusion, NB specific, implementation error, ML model confusion, and library cause
If you said the notebook was buggy, please respond only with a root cause from this list and the reason why in a sentence.""")]},config,)["messages"][-1].content
    root_cause=res
    
    result=json.dumps({"buggy_or_not": buggy,"major_bug":major_bug,"root_cause":root_cause})
    return(result)

def summarize_conversation(state: State):
    """Generate a summary of the conversation"""
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt
    if summary:

        # A summary already exists
        summary_message = (
            f"This is a summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )

    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

def runtime_execution(notebook_path:str):
    """Call runtime execution tool on notebook and produce JSON runtime report"""
    report = create_JSON_report(notebook_path)
    return report

def llm_call_router(state: State):
    """Route the input to the appropriate node"""

    # Run the augmented LLM with structured output to serve as routing logic
    router = get_router()
    decision = router.invoke(
        [
            SystemMessage(
                content="From the notebook information and bandit report, decide if you need more information in finding the bug by running the runtime execution tool or routing to the analysis tools. Route this input to runtime or analysis based on your decision."
            ),
            HumanMessage(content=state["input"]),
        ],config
    )
    return {"decision": decision.step}

def route_decision(state: State):
    # Return the node name you want to visit next
    if state["decision"] == "runtime":
        return "runtime_execution"
    elif state["decision"] == "analysis":
        return "analysis"
    
    
def router_workflow(decision:str, notebook_path:str):
    max_cycle = 3
    cycle = 0
    runtime_json = None
    
    while decision == "runtime" and cycle<max_cycle:
        runtime_json = runtime_execution(notebook_path)
        decision = llm_call_router({
            "input": "Re-route after runtime execution using latest runtime context."
        })["decision"]
        cycle+=1
    
    buggy_questions= buggy_or_not(runtime_json)
    tools = analysis()

    # Normalize analysis content to a plain string for robust UI rendering
    def _normalize_to_string(value: object) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, list):
            return "\n\n".join(_normalize_to_string(v) for v in value if v is not None)

        if isinstance(value, dict):
            for key in ("analysis", "content", "text", "message"):
                if key in value:
                    return _normalize_to_string(value[key])

            return "\n".join(
                f"**{k}**:\n{_normalize_to_string(v)}"
                for k, v in value.items()
                if k not in ("extras", "signature")
            )

        return str(value)

    analysis_text = _normalize_to_string(tools)

    result= json.dumps({"buggy_questions": buggy_questions, "analysis": analysis_text})
    return result
    
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

