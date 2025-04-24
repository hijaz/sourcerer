"""
This is the main entry point for the Sourcerer AI.
It defines the workflow graph and the entry point for the agent.
"""
# pylint: disable=line-too-long, unused-import
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from sourcerer.langgraph.state import AgentState
from sourcerer.langgraph.chat import chat_node
from sourcerer.langgraph.find_web_search import find_web_search_node
from sourcerer.langgraph.find_fact_check import fact_check_node

# --- LangGraph Workflow Setup ---
memory = MemorySaver()
workflow = StateGraph(AgentState)
workflow.set_entry_point("chat")

workflow.add_node("chat", chat_node)
workflow.add_node("find_web_search", find_web_search_node)
workflow.add_node("fact_check", fact_check_node)

workflow.add_edge("chat", "find_web_search")
workflow.add_edge("find_web_search", "chat")
workflow.add_edge("chat", "fact_check")
workflow.add_edge("fact_check", "chat")
workflow.add_edge("chat", END)

graph = workflow.compile(checkpointer=memory)
