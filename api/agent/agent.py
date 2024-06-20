from langchain_openai import ChatOpenAI
from typing import Annotated, List, Tuple, Union
from langchain.tools import BaseTool, StructuredTool, Tool
from langchain_experimental.tools import PythonREPLTool
from .tools import  get_requisition_details, get_supplier_data, get_procurement_data, get_invoice_data
from .agent_creator import create_agent, agent_node
from .supervisor_chain import supervisor_chain as SC
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import functools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from icecream import ic
from langserve import add_routes


# This executes code locally, which can be unsafe
python_repl_tool = PythonREPLTool()

llm = ChatOpenAI()

#import tools
tools = [get_supplier_data, get_requisition_details, get_procurement_data, get_invoice_data]

members, supervisor_chain = SC(llm)


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


# lotto_agent = create_agent(llm, tools, "You are a senior lotto manager. you run the lotto and get random numbers")
# lotto_node = functools.partial(agent_node, agent=lotto_agent, name="Lotto_Manager")

Suppliers_agent = create_agent(llm, tools, "You are an agent that manages and tracks the suppliers details for an organization")
Suppliers_node = functools.partial(agent_node, agent=Suppliers_agent, name="Suppliers_Manager")

requisition_agent = create_agent(llm, tools, "You are an AI sourcing assistant that helps us manage requisitions by providing status updates, details, based on the requisition number provided")
requisition_node = functools.partial(agent_node, agent=requisition_agent, name="requisition_Manager")

procurement_agent = create_agent(llm, tools, "You are an AI assistant that helps us manage procurement reports based on the report IDs, report names, or generated dates provided")
procurement_node = functools.partial(agent_node, agent=procurement_agent, name="procurement_Manager")

invoice_agent = create_agent(llm, tools, "You are an AI assistant that helps us manage invoice reports based on the invoice IDs or supplier id provided")
invoice_node = functools.partial(agent_node, agent=invoice_agent, name="invoice_Manager")

##NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
# code_agent = create_agent(llm, [python_repl_tool], "You may generate safe python code to analyze data and generate charts using matplotlib.")
# code_node = functools.partial(agent_node, agent=code_agent, name="Coder")

workflow = StateGraph(AgentState)
# workflow.add_node("Lotto_Manager", lotto_node)
workflow.add_node("requisition_Manager", requisition_node)
workflow.add_node("Suppliers_Manager", Suppliers_node)
workflow.add_node("procurement_Manager", procurement_node)
workflow.add_node("invoice_Manager", invoice_node)
workflow.add_node("supervisor", supervisor_chain)

##Create edges

for member in members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor") # add one edge for each of the agents

# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.set_entry_point("supervisor")

graph = workflow.compile()

#run it

# config = {"recursion_limit": 20} #a config dictionary is defined for recursion limit
config = {"recursion_limit": 20} #a config dictionary is defined for recursion limit

# for s in graph.stream(
#     {
#         "messages": [
#             HumanMessage(content="Get the staff detail for the staff named Babatunde")
#         ]
#     }, config=config
# ):
#     if "__end__" not in s:
#         print(s)
#         print("----")


def getResponse(query=""):
    final_response = graph.invoke(
    {
        "messages": [
            SystemMessage(content=query)
        ]
    }, config=config
        )

    res = final_response['messages'][1].content
    ic(final_response)

    return res

# def defineRoute(app, query):

#     add_routes(
#     app,
#     graph.invoke(
#     {
#         "messages": [
#             SystemMessage(content=query)
#         ]
#     }, config=config
#         ),
#     path="/AI/chat"
# )


#     return graph
