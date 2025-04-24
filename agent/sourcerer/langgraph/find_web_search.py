import os
import json
import requests
from langchain_core.messages import ToolMessage
from sourcerer.langgraph.state import AgentState
from langgraph.types import Command


def FindWebSearch(query: str):
    """
    Tool function to perform web search using the Tavily API.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set")
    headers = {"Authorization": f"Bearer {api_key}"}
    # Send JSON payload for Tavily search (using 'query' field)
    headers["Content-Type"] = "application/json"
    payload = {"query": query}
    try:
        response = requests.post("https://api.tavily.com/search", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        # Log and raise detailed error for diagnostics
        error_body = None
        if hasattr(err, 'response') and err.response is not None:
            try:
                error_body = err.response.text
            except Exception:
                error_body = str(err)
        raise RuntimeError(f"Tavily API error: {err}, Response: {error_body}")


def find_web_search_node(state: AgentState, config):
    """
    LangGraph node that handles web search tool calls and updates state.
    """
    messages = state.get("messages", [])
    if not messages:
        return Command(goto="chat", update={"messages": messages})
    ai_message = messages[-1]
    if not hasattr(ai_message, "tool_calls") or not ai_message.tool_calls:
        return Command(goto="chat", update={"messages": messages})
    tool_call = ai_message.tool_calls[0]
    if tool_call["name"] != "FindWebSearch":
        return Command(goto="chat", update={"messages": messages})
    query = tool_call["args"].get("query")
    try:
        results = FindWebSearch(query)
        msg_args = {"results": results}
    except Exception as e:
        # Return an error message instead of failing
        msg_args = {"error": str(e)}
    # Attach function response with call_id for API compliance
    call_id = tool_call.get("tool_call_id") or tool_call.get("id")
    content = json.dumps(msg_args)
    state["messages"].append(ToolMessage(content=content, name=tool_call["name"], args=msg_args, tool_call_id=call_id))
    return Command(goto="chat", update={"messages": messages})
