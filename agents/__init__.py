"""
Base agent classes for the travel planning system following ADK patterns
"""

from google.adk.agents import LlmAgent, BaseAgent
from typing import Dict, List, Any, Optional


class TravelBaseAgent:
    """Base class for all travel agents with common functionality"""
    
    async def log_interaction(self, action: str, context: Dict):
        """Log agent interactions for debugging and optimization"""
        print(f"Agent action: {action}, context: {context}")


class TravelLlmAgent(LlmAgent, TravelBaseAgent):
    """Base LLM Agent for travel system"""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        instruction: str = "",
        model: str = "gemini-2.5-flash",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List[Any]] = None,
        **kwargs
    ):
        LlmAgent.__init__(
            self, 
            name=name,
            description=description,
            instruction=instruction,
            model=model,
            tools=tools or [],
            sub_agents=sub_agents or [],
            **kwargs
        )
        # Do not set arbitrary attributes here; BaseAgent is a Pydantic model


class TravelCustomAgent(BaseAgent, TravelBaseAgent):
    """Base Custom Agent for travel system"""
    
    def __init__(self, name: str, description: str, **kwargs):
        BaseAgent.__init__(
            self,
            name=name, 
            description=description,
            **kwargs
        )
        # Do not set arbitrary attributes here; BaseAgent is a Pydantic model
