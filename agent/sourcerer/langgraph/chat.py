from typing import List, cast, Literal
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.types import Command
from langgraph.graph import END
from copilotkit.langgraph import copilotkit_customize_config
from sourcerer.langgraph.state import AgentState
from sourcerer.langgraph.find_web_search import FindWebSearch
from sourcerer.langgraph.find_fact_check import FactCheckClaim
from langchain.tools import Tool

import logging

async def chat_node(state, config: RunnableConfig) -> Command[Literal["chat", "find_web_search", "fact_check", END]]:
    """
    Generic chat node powered by web search.
    For each user query, perform web searches with FindWebSearch and provide answers with source citations.
    """
    logger = logging.getLogger("sourcerer.chat")
    logging.basicConfig(level=logging.INFO, force=True)
    logger.info(f"[chat_node] Incoming state: {state}")

    # Initialize messages
    if "messages" not in state or state["messages"] is None:
        state["messages"] = []
    msgs = state["messages"]
    last_msg = msgs[-1] if msgs else None

    # Initialize LLM and tools for decision and final steps
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    tools = [
        Tool(name="FactCheckClaim", func=FactCheckClaim, description="Verify factual claims using Google Fact Check Tools API"),
        Tool(name="FindWebSearch", func=FindWebSearch, description="Perform web search using Tavily API")
    ]

    # If last message is a ToolMessage, generate final AI response
    if isinstance(last_msg, ToolMessage):
        logger.info("[chat_node] Found ToolMessage, generating final AI answer")
        system_final = (
            "You are a knowledgeable web search assistant. Use the provided search results below to craft a clear, accurate answer with citations."
        )
        # Only include non-AI messages and AI messages that made tool calls in final prompt
        filtered_msgs = [
            m for m in msgs if not isinstance(m, AIMessage) or getattr(m, 'tool_calls', None)
        ]
        # Final consolidation: no further tool definitions
        response = await llm.ainvoke(
            [SystemMessage(content=system_final), *filtered_msgs],
            config
        )
        ai_message = cast(AIMessage, response)
        return Command(goto=END, update={"messages": msgs + [ai_message]})

    # If last message is an AIMessage
    if isinstance(last_msg, AIMessage):
        # Route to tool if there are pending calls
        if getattr(last_msg, "tool_calls", None):
            tool_name = last_msg.tool_calls[0]["name"]
            if tool_name == "FactCheckClaim":
                logger.info("[chat_node] AIMessage has FactCheckClaim, routing to fact_check")
                return Command(goto="fact_check", update={"messages": msgs})
            elif tool_name == "FindWebSearch":
                logger.info("[chat_node] AIMessage has FindWebSearch, routing to find_web_search")
                return Command(goto="find_web_search", update={"messages": msgs})
        # Otherwise end chat
        logger.info("[chat_node] AIMessage has no tool_calls, ending chat")
        return Command(goto=END, update={"messages": msgs})

    # Otherwise it's a new user query: invoke LLM to select a tool
    config = copilotkit_customize_config(config)
    # Initial decision: let model pick a tool
    system_prompt = (
        "You are a knowledgeable assistant capable of verifying claims and performing web searches. "
        "For each user query, call exactly one tool: FactCheckClaim or FindWebSearch. "
        "Return only the tool call in this response."
    )
    response = await llm.bind_tools(tools, tool_choice="auto").ainvoke(
        [SystemMessage(content=system_prompt), *msgs],
        config
    )
    ai_message = cast(AIMessage, response)
    new_msgs = msgs + [ai_message]
    if getattr(ai_message, "tool_calls", None):
        tool_name = ai_message.tool_calls[0]["name"]
        goto = "fact_check" if tool_name == "FactCheckClaim" else "find_web_search"
    else:
        goto = END
    return Command(goto=goto, update={"messages": new_msgs})