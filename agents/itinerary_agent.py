"""
Itinerary Planning Agent - handles travel itinerary creation and management
"""

from . import TravelLlmAgent
from ..tools import ActivitySearchTool, DestinationInfoTool, TravelTipsTool
from google.adk.tools import FunctionTool
from typing import Dict, Any, List
from pydantic import Field
import re
from datetime import datetime


class ItineraryPlanningAgent(TravelLlmAgent):
    """Agent specialized in creating and managing travel itineraries"""
    current_itinerary: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self):
        # Instantiate raw tool classes as local variables (avoid Pydantic attributes)
        activity_tool = ActivitySearchTool()
        destination_tool = DestinationInfoTool()
        tips_tool = TravelTipsTool()

        # Wrap tool methods with uniquely named callables to avoid duplicate
        # function declarations in Google AI backend (each name must be unique)
        async def itin_activity_search(destination: str, interests: str = "") -> str:
            """Search for activities and attractions in a destination"""
            return await activity_tool.execute(destination, interests)

        async def itin_destination_info(destination: str, context: str = "") -> str:
            """Get general info about a destination"""
            return await destination_tool.execute(destination, context)

        async def itin_travel_tips(destination: str, travel_type: str = "general") -> str:
            """Get travel tips for a destination"""
            return await tips_tool.execute(destination, travel_type)

        activity_fn = FunctionTool(itin_activity_search)
        destination_fn = FunctionTool(itin_destination_info)
        tips_fn = FunctionTool(itin_travel_tips)

        super().__init__(
            name="itinerary_planner",
            description="Specialized agent for creating personalized travel itineraries",
            instruction="""You are an itinerary planner. When given a request string, extract
                          destination, dates/duration, travelers, budget, preferences. If needed,
                          use your tools to enrich with destination info and activities. Then return
                          a compact day-by-day plan (2-6 bullets per day) and a short summary.
                          Output should be plain text that can be shown directly to the user.""",
            tools=[activity_fn, destination_fn, tips_fn]
        )
        
        # State is declared as a Pydantic field (current_itinerary)
    
    async def create_itinerary(
        self, 
        destination: str, 
        duration: str,
        travelers: int,
        interests: List[str] = None,
        budget: str = "mid-range",
        special_requirements: Dict = None
    ) -> Dict[str, Any]:
        """Create a comprehensive travel itinerary"""
        
        # Extract number of days
        days_match = re.search(r'(\d+)', duration)
        num_days = int(days_match.group(1)) if days_match else 3
        
        # Gather information using tools (instantiate helpers locally)
        destination_info = await DestinationInfoTool().execute(destination, budget)
        
        interests_str = ",".join(interests) if interests else "culture,food"
        activities_info = await ActivitySearchTool().execute(destination, interests_str)
        
        travel_tips = await TravelTipsTool().execute(destination, budget)
        
        # Create structured itinerary
        itinerary = {
            "destination": destination,
            "duration": duration,
            "num_days": num_days,
            "travelers": travelers,
            "budget": budget,
            "interests": interests or [],
            "special_requirements": special_requirements or {},
            "destination_overview": destination_info,
            "activities": activities_info,
            "travel_tips": travel_tips,
            "created_at": datetime.now().isoformat()
        }
        
        # Generate day-by-day plan
        daily_plan = await self._generate_daily_plan(itinerary)
        itinerary["daily_plan"] = daily_plan
        
        # Store for modifications
        self.current_itinerary = itinerary
        
        return itinerary
    
    async def _generate_daily_plan(self, itinerary: Dict) -> List[Dict]:
        """Generate day-by-day plan based on gathered information"""
        daily_plans = []
        num_days = itinerary["num_days"]
        
        # This is a simplified version - in production this would use LLM reasoning
        for day in range(1, num_days + 1):
            day_plan = {
                "day": day,
                "theme": await self._get_day_theme(day, num_days, itinerary["interests"]),
                "activities": [
                    {
                        "time": "Morning",
                        "activity": f"Explore {itinerary['destination']} - Day {day} morning activities",
                        "description": "Based on your interests and recommendations"
                    },
                    {
                        "time": "Afternoon", 
                        "activity": f"Main attraction visit - Day {day}",
                        "description": "Featured activity for the day"
                    },
                    {
                        "time": "Evening",
                        "activity": "Local dining and culture",
                        "description": "Experience local cuisine and nightlife"
                    }
                ]
            }
            daily_plans.append(day_plan)
        
        return daily_plans
    
    async def _get_day_theme(self, day: int, total_days: int, interests: List[str]) -> str:
        """Get theme for each day based on interests"""
        if not interests:
            interests = ["culture", "food", "sightseeing"]
        
        # Rotate through interests
        theme_index = (day - 1) % len(interests)
        return interests[theme_index].title()
    
    async def modify_itinerary(self, changes: str) -> Dict[str, Any]:
        """Modify existing itinerary based on user feedback"""
        if not self.current_itinerary:
            return {"error": "No itinerary exists to modify"}
        
        # For prototype, we'll recreate with modified interests
        destination = self.current_itinerary["destination"]
        duration = self.current_itinerary["duration"]
        travelers = self.current_itinerary["travelers"]
        budget = self.current_itinerary["budget"]
        
        # Add changes to interests
        current_interests = self.current_itinerary.get("interests", [])
        modified_interests = current_interests + [changes]
        
        # Recreate itinerary
        modified = await self.create_itinerary(
            destination=destination,
            duration=duration,
            travelers=travelers,
            interests=modified_interests,
            budget=budget
        )
        
        modified["modification"] = changes
        return modified
    
    async def get_current_itinerary(self) -> Dict[str, Any]:
        """Get the current stored itinerary"""
        if not self.current_itinerary:
            return {"error": "No itinerary has been created yet"}
        
        return self.current_itinerary
