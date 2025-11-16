# 🌍 AI Travel Agent - Chakshu

A **Google ADK travel planning agent** with multi-agent orchestration, following official ADK patterns and best practices.

## 🏗️ Architecture

### Root Agent Orchestrator Pattern

```
TravelPlanningOrchestrator (Root Agent)
├── ItineraryPlanningAgent (Child Agent)
│   └── Tools: ActivitySearch, DestinationInfo, TravelTips
├── DataAggregationAgent (Child Agent)
│   └── Tools: FlightSearch, HotelSearch, ActivitySearch
└── Coordination Logic & Workflow Management
```

### ADK Project Structure

```
exchange/
├── agent.py                    # Root agent entry point
├── adk.yaml                   # ADK configuration
├── agents/
│   ├── __init__.py            # Base agent classes
│   ├── orchestrator.py        # Root orchestrator agent
│   ├── itinerary_agent.py     # Itinerary planning child agent
│   └── data_aggregator.py     # Data aggregation child agent
├── tools/
│   └── __init__.py            # SerpApi tool implementations
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration management
├── requirements.txt           # Minimal ADK dependencies
├── test_adk_agent.py         # ADK agent testing
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google ADK installed: `pip install google-adk`
- SerpApi account (free tier)
- Google AI Studio API key (free)

### 1. Setup Environment

```bash
cd <dir>/exchange

# Install dependencies
pip install -r requirements.txt

# Set required API keys
export SERPAPI_KEY="your_serpapi_key_here"
export GOOGLE_AI_API_KEY="your_google_ai_key_here"
```

### 2. Verify Setup

```bash
# Test ADK agent structure and functionality
python test_adk_agent.py
```

### 3. Run with ADK Commands

```bash
# Start web interface (recommended)
adk web

# Or run in terminal mode
adk run

# Or run specific queries
adk run "Plan a 5-day trip to Tokyo for 2 people"
```

## 🤖 Agent Architecture Details

### Root Orchestrator Agent

The `TravelPlanningOrchestrator` is the root agent that:

- Parses user intent and requirements
- Plans optimal workflows using child agents
- Coordinates multi-agent execution
- Synthesizes results into coherent responses
- Maintains conversation state and context

### Child Agent Coordination

- **ItineraryPlanningAgent**: Creates detailed day-by-day travel plans
- **DataAggregationAgent**: Aggregates data from multiple sources in parallel
- **Tool Integration**: Each agent uses specialized tools for specific tasks

### ADK Patterns Used

✅ **LlmAgent inheritance** with proper initialization  
✅ **Tool classes** extending ADK Tool base class  
✅ **Agent coordination** through the orchestrator pattern  
✅ **Async workflow** execution with proper error handling  
✅ **Configuration management** following ADK conventions  
✅ **Project structure** matching ADK standards

## 🛠️ How It Works

### 1. User Request Processing

```python
# User: "Plan a week in Paris for art lovers"
intent = await orchestrator._parse_travel_intent(message)
# → {type: "plan_trip", destination: "Paris", duration: "1 week", interests: ["culture", "art"]}
```

### 2. Workflow Planning

```python
workflow = await orchestrator._plan_agent_workflow(intent)
# → Determines which child agents to use and in what order
```

### 3. Agent Coordination

```python
# Orchestrator coordinates child agents:
data_result = await data_aggregator.aggregate_travel_data(travel_request)
itinerary_result = await itinerary_agent.create_itinerary(params)
```

### 4. Response Synthesis

```python
response = await orchestrator._synthesize_response(results, intent)
# → Creates comprehensive, personalized travel plan
```

## 🎯 Example Interactions

### Complete Trip Planning

```
User: "Plan a 5-day trip to Tokyo for 2 people interested in culture and food"

Agent Response:
🌍 I've created a comprehensive travel plan for Tokyo!
📅 Duration: 5 days for 2 travelers

📋 Your Itinerary:
Day 1 - Culture:
  • Morning: Explore Tokyo - Traditional temples and shrines
  • Afternoon: Main cultural attraction visit
  • Evening: Local dining and culture

Day 2 - Food:
  • Morning: Tokyo food markets and street food
  • Afternoon: Cooking class or food tour
  • Evening: Traditional restaurant experience

[...continues with full itinerary...]

💡 Recommendations:
• ✈️ Flight options are available - book early for better prices
• 🏨 Multiple accommodation options found - compare amenities
• 🎯 Great activities available - plan 2-3 per day for best experience
```

### Specific Searches

```
User: "Find flights from NYC to Tokyo"

Agent Response:
🔍 Here's what I found for flights in Tokyo:
✈️ JetBlue Airways - New York to Tokyo
   Compare prices across 500+ travel sites to find...
   🔗 https://www.jetblue.com/...

✈️ American Airlines - JFK to NRT
   Find the best deals on flights from New York to Tokyo...
   🔗 https://www.aa.com/...
```

### Plan Modifications

```
User: "Add more museums to my Tokyo itinerary"

Agent Response:
✅ I've updated your travel plan based on your request!
🔄 Modification: museums

[Updated itinerary with more cultural attractions...]
```

## 🧪 Testing & Validation

### Run Tests

```bash
# Complete system test
python test_adk_agent.py

# Expected output:
🌍 ADK Travel Agent - System Tests
=====================================
✅ Environment: PASS
✅ Project Structure: PASS
✅ Imports: PASS
✅ Agent Functionality: PASS
✅ Child Agent Coordination: PASS

🎯 Overall: 5/5 tests passed
🚀 All tests passed! Your ADK Travel Agent is ready.
```

### Manual Testing

```bash
# Test with various queries
adk run "What are the best activities in Barcelona?"
adk run "Find budget hotels in Rome for next week"
adk run "Create a cultural itinerary for Prague"
```

## 📊 ADK Configuration

### adk.yaml

```yaml
name: ai-travel-agent
version: 1.0.0
description: Intelligent travel planning assistant using Google ADK

agent:
  module: agent
  class: agent

environment:
  python_version: ">=3.8"

env_vars:
  - SERPAPI_KEY
  - GOOGLE_AI_API_KEY

web:
  port: 8000
  host: "0.0.0.0"
```

## 🔧 Development

### Adding New Agents

```python
# 1. Create new agent class
class NewTravelAgent(TravelLlmAgent):
    def __init__(self):
        super().__init__(
            name="new_agent",
            description="Specialized agent for X"
        )

# 2. Add to orchestrator
self.new_agent = NewTravelAgent()

# 3. Include in workflow coordination
```

### Adding New Tools

```python
# 1. Extend SerpApiSearchTool
class NewSearchTool(SerpApiSearchTool):
    def __init__(self):
        super().__init__()
        self.name = "new_search"

    async def execute(self, query: str) -> str:
        # Tool implementation
        pass

# 2. Add to relevant agent's tools list
```

## 🚨 Troubleshooting

### Common Issues

**"Configuration Error" on startup:**

```bash
# Ensure API keys are set
export SERPAPI_KEY='your_key_here'
export GOOGLE_AI_API_KEY='your_key_here'
```

**"Module not found" errors:**

```bash
# Ensure ADK is installed
pip install google-adk

# Check project structure
python test_adk_agent.py
```

**Agent not responding:**

```bash
# Verify agent structure
adk validate  # If available

# Check logs
adk run --debug "test message"
```

### Debug Mode

```bash
# Run with verbose logging
adk web --debug --log-level=debug

# Test individual components
python -c "from agent import agent; print(agent.name)"
```

## 🎖️ Good Stuff about the implementation

### Follows ADK Best Practices

✅ **Proper agent inheritance** using `LlmAgent` base class  
✅ **Tool pattern** with ADK `Tool` base class  
✅ **Root agent orchestrator** coordinates child agents  
✅ **Async patterns** for proper workflow execution  
✅ **Configuration structure** matching ADK conventions  
✅ **Project layout** following ADK standards

### Multi-Agent Coordination

✅ **Clear separation of concerns** between agents  
✅ **Workflow orchestration** through the root agent  
✅ **Parallel execution** of independent tasks  
✅ **State management** and conversation context  
✅ **Error handling** and graceful degradation

### Production Ready Features

✅ **Proper testing** and validation framework  
✅ **Configuration management** with environment variables  
✅ **Comprehensive documentation** and examples  
✅ **ADK command support** (`adk web`, `adk run`)  
✅ **Extensible architecture** for adding new capabilities

---

