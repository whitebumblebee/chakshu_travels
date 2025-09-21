"""
Travel planning tools using SerpApi integration
"""

from google.adk.tools import FunctionTool
from typing import Dict, List, Any, Optional
import requests
from ..config.settings import Config


class SerpApiSearchTool:
    """Base tool for SerpApi search functionality"""
    
    def __init__(self):
        # No base class init; this is a plain helper object
        self.api_key = Config.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
    
    async def _make_search_request(self, query: str, params: Dict = None) -> Dict:
        """Make a search request to SerpApi"""
        search_params = {
            "q": query,
            "engine": "google",
            "api_key": self.api_key,
            "num": 10
        }
        
        if params:
            search_params.update(params)
        
        try:
            response = requests.get(self.base_url, params=search_params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "organic_results": []}


class FlightSearchTool(SerpApiSearchTool):
    """Tool for searching flight information"""
    
    def __init__(self):
        super().__init__()
        self.name = "flight_search"
        self.description = "Search for flight options between destinations"
    
    async def execute(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str,
        return_date: Optional[str] = None
    ) -> str:
        """Search for flights between two destinations"""
        query = f"flights from {origin} to {destination} {departure_date}"
        if return_date:
            query += f" return {return_date}"
        
        data = await self._make_search_request(query)
        
        if "error" in data:
            return f"Error searching flights: {data['error']}"
        
        results = []
        for result in data.get("organic_results", [])[:5]:
            results.append(f"✈️ {result.get('title', '')}\n   {result.get('snippet', '')[:100]}...\n   🔗 {result.get('link', '')}")
        
        return f"Found {len(results)} flight options for {origin} → {destination}:\n\n" + "\n\n".join(results)


class HotelSearchTool(SerpApiSearchTool):
    """Tool for searching hotel accommodations"""
    
    def __init__(self):
        super().__init__()
        self.name = "hotel_search"
        self.description = "Search for hotel accommodations in destinations"
    
    async def execute(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2
    ) -> str:
        """Search for hotels in a destination"""
        query = f"hotels in {destination} {check_in} to {check_out} {guests} guests"
        
        data = await self._make_search_request(query)
        
        if "error" in data:
            return f"Error searching hotels: {data['error']}"
        
        results = []
        for result in data.get("organic_results", [])[:5]:
            results.append(f"🏨 {result.get('title', '')}\n   {result.get('snippet', '')[:100]}...\n   🔗 {result.get('link', '')}")
        
        return f"Found {len(results)} hotel options in {destination}:\n\n" + "\n\n".join(results)


class ActivitySearchTool(SerpApiSearchTool):
    """Tool for searching activities and attractions"""
    
    def __init__(self):
        super().__init__()
        self.name = "activity_search"
        self.description = "Search for activities and attractions in destinations"
    
    async def execute(self, destination: str, interests: str = "") -> str:
        """Search for activities and attractions"""
        interests_str = interests if interests else "tourist attractions"
        query = f"things to do in {destination} {interests_str} activities attractions"
        
        data = await self._make_search_request(query)
        
        if "error" in data:
            return f"Error searching activities: {data['error']}"
        
        results = []
        for result in data.get("organic_results", [])[:8]:
            results.append(f"🎯 {result.get('title', '')}\n   {result.get('snippet', '')[:100]}...\n   🔗 {result.get('link', '')}")
        
        return f"Found {len(results)} activities in {destination}:\n\n" + "\n\n".join(results)


class DestinationInfoTool(SerpApiSearchTool):
    """Tool for getting destination information"""
    
    def __init__(self):
        super().__init__()
        self.name = "destination_info"
        self.description = "Get general information about travel destinations"
    
    async def execute(self, destination: str, context: str = "") -> str:
        """Get destination information"""
        query = f"{destination} travel guide best time to visit weather {context}"
        
        data = await self._make_search_request(query)
        
        if "error" in data:
            return f"Error getting destination info: {data['error']}"
        
        results = []
        for result in data.get("organic_results", [])[:5]:
            results.append(f"📍 {result.get('title', '')}\n   {result.get('snippet', '')[:150]}...\n   🔗 {result.get('link', '')}")
        
        return f"Here's information about {destination}:\n\n" + "\n\n".join(results)


class TravelTipsTool(SerpApiSearchTool):
    """Tool for getting travel tips and recommendations"""
    
    def __init__(self):
        super().__init__()
        self.name = "travel_tips"
        self.description = "Get travel tips and local recommendations"
    
    async def execute(self, destination: str, travel_type: str = "general") -> str:
        """Get travel tips for destination"""
        query = f"{destination} travel tips {travel_type} recommendations budget local culture"
        
        data = await self._make_search_request(query)
        
        if "error" in data:
            return f"Error getting travel tips: {data['error']}"
        
        results = []
        for result in data.get("organic_results", [])[:6]:
            results.append(f"💡 {result.get('title', '')}\n   {result.get('snippet', '')[:150]}...\n   🔗 {result.get('link', '')}")
        
        return f"Travel tips for {destination} ({travel_type}):\n\n" + "\n\n".join(results)
