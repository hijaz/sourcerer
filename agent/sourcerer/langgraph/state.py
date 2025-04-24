"""
State definition for the Sourcerer AI.
Defines the agent's and conversation's state for budgeting purposes.
"""
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """Conversation state containing only messages."""
    pass
