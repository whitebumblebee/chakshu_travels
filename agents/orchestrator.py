"""
Travel Planning Orchestrator - Main root agent that coordinates all child agents
"""

from . import TravelLlmAgent
from .itinerary_agent import ItineraryPlanningAgent
from .data_aggregator import DataAggregationAgent
from google.adk.tools import AgentTool
from typing import Dict, Any, List, Optional
from pydantic import Field
from datetime import datetime
import re
import json


class TravelPlanningOrchestrator(TravelLlmAgent):
    """
    Main root agent that orchestrates the entire travel planning process.
    Coordinates child agents and manages the overall workflow.
    """
    
    def __init__(self):
        # Initialize child agents first so they can be registered with the root
        itinerary_agent = ItineraryPlanningAgent()
        data_aggregator = DataAggregationAgent()
        
        today = datetime.now().strftime('%Y-%m-%d')
        super().__init__(
            name="travel_orchestrator",
            description="""Master travel planning agent that coordinates all other agents 
                          to create comprehensive, personalized travel plans.""",
            instruction=f"""You are the root orchestrator. Stay in control and solve the task end-to-end.

                          Today is {today}. Use this to interpret dates/timing correctly.

                          Process:
                          1) If details are sufficient, call the tool `data_aggregator` with a concise
                             request string that includes destination, dates, travelers, budget and
                             any preferences. The tool will return structured JSON for
                             flights/hotels/activities/destination_info.
                          2) After receiving results, call the tool `itinerary_planner` with a concise
                             request string summarizing the trip and constraints to produce a day-by-day
                             itinerary.
                          3) Synthesize a final answer with concrete, actionable options and links.
                             Prefer bullet points and a short options summary. Avoid asking questions
                             unless required information is truly missing.

                          Important:
                          - Use these tools (AgentTools), not agent transfer. Keep control.
                          - When calling tools, pass a single `request` string that is clear and
                            self-contained.
                          - Prefer structured, concise final replies.

                          Clarification:
                          - If ANY of the following are missing, FIRST ask one compact question listing
                            all missing fields, then wait for the user before using tools:
                            destination, outbound date (and return date or duration), origin (for flights),
                            number of travelers, and budget.

                          Language:
                          - Detect the user's language from their message and respond in that language.
                            Keep proper nouns as-is. If unclear, default to English.

                          Booking links (no API calls):
                          - At the end of your final reply, include a section "Book on EaseMyTrip" with
                            direct links the user can click:
                            • Flights: https://www.easemytrip.com/flights.html
                            • Hotels: https://www.easemytrip.com/hotels/
                            • Holidays: https://www.easemytrip.com/holidays/
                          - If you have origin/destination/dates, you may suggest what to input on the page.
                          - Do NOT fabricate prices or confirm availability; provide links and summaries only.
                          """,
            tools=[
                AgentTool(itinerary_agent),
                AgentTool(data_aggregator),
            ],
            sub_agents=[itinerary_agent, data_aggregator]
        )
        
    
        # Keep references to child agents (attributes must exist in Pydantic model)
        # Access children via find_agent when needed to avoid arbitrary attributes
        
        # Avoid setting arbitrary attributes on Pydantic model here.
    
    async def process_travel_request(self, user_message: str, context: Dict = None) -> str:
        """
        Main entry point for processing travel requests.
        This orchestrates the entire workflow.
        """
        
        # Log the interaction
        await self.log_interaction("process_travel_request", {
            "message": user_message[:100],
            "context": context or {}
        })
        
        # Parse user intent and requirements
        intent = await self._parse_travel_intent(user_message)
        
        # Determine workflow strategy
        workflow = await self._plan_agent_workflow(intent, user_message)
        
        # Execute coordinated agent workflow
        result = await self._execute_workflow(workflow, intent, context or {})
        
        # Generate final user response
        response = await self._synthesize_response(result, intent, user_message)
        
        # Store in conversation history
        # Keep minimal history in local variable instead of setting attribute
        _history_item = {
            "user_message": user_message,
            "intent": intent,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    async def _parse_travel_intent(self, message: str) -> Dict[str, Any]:
        """Parse user message to extract travel requirements and intent"""
        
        intent = {
            "type": "unknown",
            "destination": None,
            "origin": None,
            "duration": None,
            "travelers": None,
            "interests": [],
            "budget": None,
            "dates": {},
            "special_requirements": [],
            "modification": False
        }
        
        message_lower = message.lower()
        
        # Determine intent type
        if any(word in message_lower for word in ["plan", "trip", "itinerary", "travel"]):
            intent["type"] = "plan_trip"
        elif any(word in message_lower for word in ["find", "search", "look"]):
            if "flight" in message_lower:
                intent["type"] = "search_flights"
            elif "hotel" in message_lower:
                intent["type"] = "search_hotels"
            elif "activities" in message_lower or "things to do" in message_lower:
                intent["type"] = "search_activities"
            else:
                intent["type"] = "general_search"
        elif any(word in message_lower for word in ["modify", "change", "update", "add", "remove"]):
            intent["type"] = "modify_plan"
            intent["modification"] = True
        else:
            intent["type"] = "general_inquiry"
        
        # Extract destination
        # Simple pattern matching - in production would use NLP
        destinations = [
            "tokyo", "japan", "paris", "france", "rome", "italy", "barcelona", "spain",
            "london", "uk", "new york", "nyc", "los angeles", "bali", "thailand",
            "amsterdam", "berlin", "prague", "vienna", "budapest"
        ]
        
        for dest in destinations:
            if dest in message_lower:
                intent["destination"] = dest.title()
                break
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(day|days|week|weeks)', message_lower)
        if duration_match:
            num = int(duration_match.group(1))
            unit = duration_match.group(2)
            if "week" in unit:
                intent["duration"] = f"{num} week{'s' if num > 1 else ''}"
            else:
                intent["duration"] = f"{num} day{'s' if num > 1 else ''}"
        
        # Extract number of travelers
        travelers_match = re.search(r'(\d+)\s*(people|person|travelers?|guests?)', message_lower)
        if travelers_match:
            intent["travelers"] = int(travelers_match.group(1))
        elif "solo" in message_lower or "alone" in message_lower:
            intent["travelers"] = 1
        
        # Extract interests
        interest_keywords = {
            "culture": ["culture", "cultural", "history", "historical", "museum", "art"],
            "food": ["food", "cuisine", "restaurant", "dining", "culinary"],
            "adventure": ["adventure", "hiking", "outdoor", "sports", "active"],
            "nightlife": ["nightlife", "bars", "clubs", "entertainment"],
            "relaxation": ["relax", "spa", "beach", "peaceful", "quiet"],
            "shopping": ["shopping", "markets", "stores"],
            "nature": ["nature", "parks", "wildlife", "scenery"]
        }
        
        for category, keywords in interest_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                intent["interests"].append(category)
        
        # Extract budget hints
        if any(word in message_lower for word in ["budget", "cheap", "affordable"]):
            intent["budget"] = "budget"
        elif any(word in message_lower for word in ["luxury", "high-end", "premium"]):
            intent["budget"] = "luxury"
        else:
            intent["budget"] = "mid-range"
        
        return intent
    
    async def _plan_agent_workflow(self, intent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Plan the optimal workflow based on intent and requirements"""
        
        workflow = {
            "steps": [],
            "parallel_tasks": [],
            "required_agents": set()
        }
        
        intent_type = intent["type"]
        
        if intent_type == "plan_trip":
            # Full trip planning workflow
            workflow["steps"] = [
                {"agent": "data_aggregator", "task": "gather_destination_data"},
                {"agent": "itinerary_agent", "task": "create_itinerary"},
                {"agent": "orchestrator", "task": "synthesize_plan"}
            ]
            workflow["required_agents"] = {"data_aggregator", "itinerary_agent"}
            
        elif intent_type in ["search_flights", "search_hotels", "search_activities"]:
            # Specific search workflow
            workflow["steps"] = [
                {"agent": "data_aggregator", "task": f"search_{intent_type.split('_')[1]}"}
            ]
            workflow["required_agents"] = {"data_aggregator"}
            
        elif intent_type == "modify_plan":
            # Modification workflow
            workflow["steps"] = [
                {"agent": "itinerary_agent", "task": "modify_existing"}
            ]
            workflow["required_agents"] = {"itinerary_agent"}
            
        else:
            # General inquiry workflow
            workflow["steps"] = [
                {"agent": "data_aggregator", "task": "general_search"}
            ]
            workflow["required_agents"] = {"data_aggregator"}
        
        self.active_workflow = workflow
        return workflow
    
    async def _execute_workflow(self, workflow: Dict, intent: Dict, context: Dict) -> Dict[str, Any]:
        """Execute the planned workflow by coordinating child agents"""
        
        results = {
            "workflow_results": [],
            "agent_outputs": {},
            "status": "success"
        }
        
        try:
            # Execute workflow steps
            for step in workflow["steps"]:
                agent_name = step["agent"]
                task = step["task"]
                
                if agent_name == "data_aggregator":
                    result = await self._coordinate_data_aggregator(task, intent)
                elif agent_name == "itinerary_agent":
                    result = await self._coordinate_itinerary_agent(task, intent)
                elif agent_name == "orchestrator":
                    result = await self._coordinate_self_task(task, intent, results)
                else:
                    result = {"error": f"Unknown agent: {agent_name}"}
                
                results["agent_outputs"][agent_name] = result
                results["workflow_results"].append({
                    "agent": agent_name,
                    "task": task,
                    "result": result
                })
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _coordinate_data_aggregator(self, task: str, intent: Dict) -> Dict[str, Any]:
        """Coordinate with the data aggregation agent"""
        
        if task == "gather_destination_data":
            # Prepare request for data aggregator
            travel_request = {
                "destination": intent.get("destination"),
                "origin": intent.get("origin"),
                "travelers": intent.get("travelers", 2),
                "interests": ",".join(intent.get("interests", [])),
                "budget": intent.get("budget", "mid-range"),
                "timestamp": datetime.now().isoformat()
            }
            data_agent = self.find_agent("data_aggregator")
            result = await data_agent.aggregate_travel_data(travel_request) if data_agent else {"error": "data_aggregator not found"}
            return result
        
        elif task.startswith("search_"):
            # Specific search task
            search_type = task.split("search_")[1]
            destination = intent.get("destination", "")
            
            if search_type == "flights":
                # Use aggregator API instead of accessing private attributes
                data_agent = self.find_agent("data_aggregator")
                travel_request = {
                    "destination": destination,
                    "origin": intent.get("origin", ""),
                    "departure_date": intent.get("dates", {}).get("departure", ""),
                    "return_date": intent.get("dates", {}).get("return", None),
                    "timestamp": datetime.now().isoformat(),
                }
                result = await data_agent.aggregate_travel_data(travel_request) if data_agent else {"error": "data_aggregator not found"}
                return result
            
            # Default general search
            travel_request = {
                "destination": destination,
                "interests": ",".join(intent.get("interests", [])),
                "timestamp": datetime.now().isoformat()
            }
            data_agent = self.find_agent("data_aggregator")
            return await data_agent.aggregate_travel_data(travel_request) if data_agent else {"error": "data_aggregator not found"}
        
        else:
            return {"error": f"Unknown data aggregator task: {task}"}
    
    async def _coordinate_itinerary_agent(self, task: str, intent: Dict) -> Dict[str, Any]:
        """Coordinate with the itinerary planning agent"""
        
        if task == "create_itinerary":
            # Create new itinerary
            itinerary_agent = self.find_agent("itinerary_planner")
            result = await itinerary_agent.create_itinerary(
                destination=intent.get("destination", "Unknown"),
                duration=intent.get("duration", "3 days"),
                travelers=intent.get("travelers", 2),
                interests=intent.get("interests", []),
                budget=intent.get("budget", "mid-range")
            ) if itinerary_agent else {"error": "itinerary_planner not found"}
            return result
        
        elif task == "modify_existing":
            # Modify existing itinerary
            # Ask itinerary agent to modify based on request
            itinerary_agent = self.find_agent("itinerary_planner")
            if itinerary_agent and getattr(itinerary_agent, "current_itinerary", None):
                result = await itinerary_agent.modify_itinerary(
                    intent.get("modification_request", "general improvements")
                )
                return result
            else:
                return {"error": "No existing itinerary to modify"}
        
        else:
            return {"error": f"Unknown itinerary agent task: {task}"}
    
    async def _coordinate_self_task(self, task: str, intent: Dict, current_results: Dict) -> Dict[str, Any]:
        """Handle tasks that the orchestrator performs itself"""
        
        if task == "synthesize_plan":
            # Synthesize information from multiple agents into final plan
            data_result = current_results["agent_outputs"].get("data_aggregator", {})
            itinerary_result = current_results["agent_outputs"].get("itinerary_agent", {})
            
            synthesis = {
                "plan_summary": f"Complete travel plan for {intent.get('destination', 'your destination')}",
                "itinerary": itinerary_result,
                "supporting_data": data_result,
                "recommendations": self._generate_final_recommendations(data_result, itinerary_result)
            }
            
            return synthesis
        
        else:
            return {"error": f"Unknown orchestrator task: {task}"}
    
    def _generate_final_recommendations(self, data_result: Dict, itinerary_result: Dict) -> List[str]:
        """Generate final recommendations based on all agent results"""
        recommendations = []
        
        # Add recommendations based on results
        if itinerary_result and not itinerary_result.get("error"):
            recommendations.append("📋 Detailed itinerary created with daily activities")
        
        if data_result and data_result.get("recommendations"):
            recommendations.extend(data_result["recommendations"])
        
        # Add general travel advice
        recommendations.extend([
            "💡 Book accommodations early for better rates",
            "📱 Download offline maps and translation apps",
            "🌍 Check visa requirements and travel advisories"
        ])
        
        return recommendations
    
    async def _synthesize_response(self, workflow_result: Dict, intent: Dict, original_message: str) -> str:
        """Synthesize the final response to the user"""
        
        if workflow_result["status"] == "error":
            return f"I apologize, but I encountered an error while processing your request: {workflow_result.get('error')}"
        
        response_parts = []
        
        # Add greeting and acknowledgment
        destination = intent.get("destination", "your destination")
        intent_type = intent["type"]
        
        if intent_type == "plan_trip":
            response_parts.append(f"🌍 I've created a comprehensive travel plan for {destination}!")
            
            # Add itinerary information
            itinerary_result = workflow_result["agent_outputs"].get("itinerary_agent", {})
            if itinerary_result and not itinerary_result.get("error"):
                duration = itinerary_result.get("duration", "your trip")
                travelers = itinerary_result.get("travelers", 2)
                response_parts.append(f"📅 Duration: {duration} for {travelers} traveler{'s' if travelers > 1 else ''}")
                
                if itinerary_result.get("daily_plan"):
                    response_parts.append("\n📋 **Your Itinerary:**")
                    for day_plan in itinerary_result["daily_plan"][:3]:  # Show first 3 days
                        day_num = day_plan["day"]
                        theme = day_plan.get("theme", "Exploration")
                        response_parts.append(f"**Day {day_num} - {theme}:**")
                        for activity in day_plan.get("activities", []):
                            time = activity.get("time")
                            activity_name = activity.get("activity")
                            response_parts.append(f"  • {time}: {activity_name}")
            
            # Add supporting data
            data_result = workflow_result["agent_outputs"].get("data_aggregator", {})
            if data_result and data_result.get("recommendations"):
                response_parts.append("\n💡 **Recommendations:**")
                for rec in data_result["recommendations"][:3]:
                    response_parts.append(f"• {rec}")
        
        elif intent_type.startswith("search_"):
            search_type = intent_type.split("_")[1]
            response_parts.append(f"🔍 Here's what I found for {search_type} in {destination}:")
            
            data_result = workflow_result["agent_outputs"].get("data_aggregator", {})
            if data_result and data_result.get("data"):
                for key, value in data_result["data"].items():
                    if isinstance(value, str) and not value.startswith("Error"):
                        response_parts.append(f"\n{value[:500]}...")  # Truncate for readability
        
        elif intent_type == "modify_plan":
            response_parts.append("✅ I've updated your travel plan based on your request!")
            
            itinerary_result = workflow_result["agent_outputs"].get("itinerary_agent", {})
            if itinerary_result and not itinerary_result.get("error"):
                modification = itinerary_result.get("modification", "your changes")
                response_parts.append(f"🔄 Modification: {modification}")
        
        else:
            response_parts.append(f"ℹ️ Here's information about {destination}:")
            
            data_result = workflow_result["agent_outputs"].get("data_aggregator", {})
            if data_result and data_result.get("data", {}).get("destination_info"):
                info = data_result["data"]["destination_info"]
                if isinstance(info, str):
                    response_parts.append(info[:500] + "...")
        
        # Add call to action
        response_parts.append("\n❓ Would you like me to provide more details on any specific aspect or make modifications?")
        
        return "\n".join(response_parts)
