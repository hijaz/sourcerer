import os
import requests
import json
from langchain_core.messages import ToolMessage
from sourcerer.langgraph.state import AgentState
from sourcerer.langgraph.find_web_search import FindWebSearch
import logging
from langgraph.types import Command
logger = logging.getLogger("sourcerer.find_fact_check")

def FactCheckClaim(query: str, language_code: str = "en-US", review_publisher_site_filter: str = None, max_age_days: int = None, page_size: int = 10):
    """
    Tool function to search fact-checked claims using Google Fact Check Tools API.
    Returns the first claim if available, otherwise an empty dict.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": query, "key": api_key}
    params["languageCode"] = language_code
    if review_publisher_site_filter:
        params["reviewPublisherSiteFilter"] = review_publisher_site_filter
    if max_age_days is not None:
        params["maxAgeDays"] = str(max_age_days)
    params["pageSize"] = str(page_size)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        claims = data.get("claims", [])
        return claims[0] if claims else {}
    except requests.exceptions.RequestException as err:
        error_body = getattr(err.response, "text", str(err))
        raise RuntimeError(f"FactCheck API error: {err}, Response: {error_body}")

def fact_check_node(state: AgentState, config):
    """
    LangGraph node that handles FactCheckClaim tool calls and updates state.
    """
    messages = state.get("messages", [])
    if not messages:
        return Command(goto="chat", update={"messages": messages})
    ai_message = messages[-1]
    if not hasattr(ai_message, "tool_calls") or not ai_message.tool_calls:
        return Command(goto="chat", update={"messages": messages})
    tool_call = ai_message.tool_calls[0]
    if tool_call["name"] != "FactCheckClaim":
        return Command(goto="chat", update={"messages": messages})
    query = tool_call["args"].get("query")
    try:
        claim = FactCheckClaim(query)
        msg_args = {"claim": claim}
        if not claim:
            fallback = FindWebSearch(query)
            msg_args["fallback_results"] = fallback
    except Exception as e:
        msg_args = {"error": str(e)}
    call_id = tool_call.get("tool_call_id") or tool_call.get("id")
    content = json.dumps(msg_args)
    state["messages"].append(
        ToolMessage(content=content, name=tool_call["name"], args=msg_args, tool_call_id=call_id)
    )
    # Ensure response for every tool_call_id
    last = state["messages"][-1]
    if getattr(last, "tool_call_id", None) != call_id:
        logger.warning(f"[fact_check_node] missing response for call_id {call_id}, inserting fallback")
        fallback_msg = ToolMessage(content=json.dumps({"error":"no response"}), name=tool_call["name"], args={"error":"no response"}, tool_call_id=call_id)
        state["messages"].append(fallback_msg)
    return Command(goto="chat", update={"messages": messages})
