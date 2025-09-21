"""
Root Agent for Travel Planning System using Google ADK
This is the main entry point that ADK will use when running the agent.
"""

from .agents.orchestrator import TravelPlanningOrchestrator
from .config.settings import Config


# This is the root agent that ADK will instantiate
root_agent = TravelPlanningOrchestrator()


def create_agent():
    """
    Factory function to create the root agent.
    This is called by ADK when initializing the agent system.
    """
    try:
        # Validate configuration
        Config.validate()
        
        # Return the orchestrator as the main agent
        return root_agent
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set required environment variables:")
        print("export SERPAPI_KEY='your_serpapi_key'")
        print("export GOOGLE_AI_API_KEY='your_google_ai_key'")
        raise


# Main agent instance that ADK will use
agent = create_agent()


# Optional: Define agent metadata for ADK
AGENT_METADATA = {
    "name": "AI Travel Agent",
    "version": "1.0.0", 
    "description": "Intelligent travel planning assistant using Google ADK",
    "author": "Travel Agent Team",
    "capabilities": [
        "Travel itinerary creation",
        "Flight and hotel search", 
        "Activity recommendations",
        "Multi-agent coordination",
        "Real-time travel information"
    ],
    "requirements": {
        "apis": ["SerpApi", "Google AI"],
        "python_version": ">=3.8"
    }
}
