from enum import Enum

class AgentType(Enum):
    """
    Enum defining the different specialized agents within the Casey AI system.
    The hierarchy reflects the processing flow: Intent Analysis -> Orchestration -> Specialized Agents
    """
    
    # Intent Analysis Layer
    INTENT_ANALYZER = "intent_analyzer"
    
    # Conversation Agents
    CASUAL_CHAT = "casual_chat"  # Handles everyday conversation