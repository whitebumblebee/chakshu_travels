"""
Data Aggregation Agent - handles data collection from multiple travel APIs
"""

from . import TravelLlmAgent
from ..tools import FlightSearchTool, HotelSearchTool, ActivitySearchTool, DestinationInfoTool
from google.adk.tools import FunctionTool
from typing import Dict, List, Any, Optional
from pydantic import Field
import json
import asyncio


class DataAggregationAgent(TravelLlmAgent):
    """Agent specialized in aggregating data from multiple travel sources"""
    # No arbitrary attributes; declare state if needed
    
    def __init__(self):
        # Instantiate tool helpers as local closures (avoid Pydantic attributes)
        flight_tool = FlightSearchTool()
        hotel_tool = HotelSearchTool()
        activity_tool = ActivitySearchTool()
        destination_tool = DestinationInfoTool()

        # Wrap with uniquely named callables to avoid duplicate function names
        async def agg_flight_search(origin: str, destination: str, departure_date: str, return_date: Optional[str] = None) -> str:
            """Search for flight options between destinations"""
            return await flight_tool.execute(origin, destination, departure_date, return_date)

        async def agg_hotel_search(destination: str, check_in: str, check_out: str, guests: int = 2) -> str:
            """Search for hotel accommodations in a destination"""
            return await hotel_tool.execute(destination, check_in, check_out, guests)

        async def agg_activity_search(destination: str, interests: str = "") -> str:
            """Search for activities and attractions in a destination"""
            return await activity_tool.execute(destination, interests)

        async def agg_destination_info(destination: str, context: str = "") -> str:
            """Get general information about a destination"""
            return await destination_tool.execute(destination, context)

        flight_fn = FunctionTool(agg_flight_search)
        hotel_fn = FunctionTool(agg_hotel_search)
        activity_fn = FunctionTool(agg_activity_search)
        destination_fn = FunctionTool(agg_destination_info)

        super().__init__(
            name="data_aggregator",
            description="Orchestrates data collection from multiple travel APIs and sources",
            instruction="""You are a data aggregation agent. When given a request string,
                            extract destination, dates (outbound and return or duration), origin (for flights),
                            number of travelers, budget, and preferences. If any of these are missing,
                            first ask the user one compact question listing ONLY the missing fields, then wait.

                            Always use your SerpApi-backed tools to fetch real information:
                            - agg_flight_search for flights
                            - agg_hotel_search for hotels
                            - agg_activity_search for activities
                            - agg_destination_info for destination basics

                            Return a compact JSON dict with keys: flights, hotels, activities, destination_info.
                            Each value should be a short summary or bullet list with real links. Keep output concise.""",
            tools=[flight_fn, hotel_fn, activity_fn, destination_fn]
        )
    
    async def aggregate_travel_data(self, travel_request: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate all travel data for a request"""
        
        destination = travel_request.get("destination")
        origin = travel_request.get("origin")
        departure_date = travel_request.get("departure_date")
        return_date = travel_request.get("return_date")
        check_in = travel_request.get("check_in")
        check_out = travel_request.get("check_out")
        travelers = travel_request.get("travelers", 2)
        interests = travel_request.get("interests", "")
        
        # Determine what data is needed
        needs = self._analyze_data_needs(travel_request)
        
        # Execute parallel data collection
        results = await self._execute_parallel_searches(
            destination=destination,
            origin=origin,
            departure_date=departure_date,
            return_date=return_date,
            check_in=check_in,
            check_out=check_out,
            travelers=travelers,
            interests=interests,
            needs=needs
        )
        
        # Aggregate and normalize results
        aggregated_data = await self._aggregate_results(results, travel_request)
        # Return structured dict to the orchestrator
        return aggregated_data
    
    def _analyze_data_needs(self, request: Dict[str, Any]) -> Dict[str, bool]:
        """Analyze what data is needed based on the request"""
        needs = {
            "flights": False,
            "hotels": False,
            "activities": True,  # Always include activities
            "destination_info": True  # Always include destination info
        }
        
        # Check if flight data is needed
        if request.get("origin") and request.get("departure_date"):
            needs["flights"] = True
        
        # Check if hotel data is needed  
        if request.get("check_in") and request.get("check_out"):
            needs["hotels"] = True
        
        return needs
    
    async def _execute_parallel_searches(
        self,
        destination: str,
        origin: Optional[str] = None,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        travelers: int = 2,
        interests: str = "",
        needs: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """Execute multiple searches in parallel"""
        
        if needs is None:
            needs = {"flights": True, "hotels": True, "activities": True, "destination_info": True}
        
        # Prepare tasks for parallel execution
        tasks = []
        task_names = []
        # Instantiate helpers locally
        flight_tool = FlightSearchTool()
        hotel_tool = HotelSearchTool()
        activity_tool = ActivitySearchTool()
        destination_tool = DestinationInfoTool()
        
        if needs.get("flights") and origin and departure_date:
            tasks.append(flight_tool.execute(origin, destination, departure_date, return_date))
            task_names.append("flights")
        
        if needs.get("hotels") and check_in and check_out:
            tasks.append(hotel_tool.execute(destination, check_in, check_out, travelers))
            task_names.append("hotels")
        
        if needs.get("activities"):
            tasks.append(activity_tool.execute(destination, interests))
            task_names.append("activities")
        
        if needs.get("destination_info"):
            tasks.append(destination_tool.execute(destination, interests))
            task_names.append("destination_info")
        
        # Execute all tasks in parallel
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Map results back to names
                result_dict = {}
                for i, (task_name, result) in enumerate(zip(task_names, results)):
                    if isinstance(result, Exception):
                        result_dict[task_name] = {"error": str(result)}
                    else:
                        result_dict[task_name] = {"data": result, "success": True}
                
                return result_dict
                
            except Exception as e:
                return {"error": f"Failed to execute parallel searches: {str(e)}"}
        else:
            return {"message": "No searches were needed based on the request"}
    
    async def _aggregate_results(
        self, 
        results: Dict[str, Any], 
        original_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate and normalize results from different sources"""
        
        aggregated = {
            "destination": original_request.get("destination"),
            "search_timestamp": original_request.get("timestamp"),
            "request_summary": {
                "travelers": original_request.get("travelers", 2),
                "interests": original_request.get("interests", ""),
                "budget": original_request.get("budget", "mid-range")
            },
            "data": {},
            "summary": {},
            "recommendations": []
        }
        
        # Process each data type
        for data_type, result in results.items():
            if result.get("success"):
                aggregated["data"][data_type] = result["data"]
                aggregated["summary"][data_type] = self._summarize_result(data_type, result["data"])
            else:
                aggregated["data"][data_type] = {"error": result.get("error", "Unknown error")}
        
        # Generate cross-data recommendations
        aggregated["recommendations"] = await self._generate_recommendations(aggregated["data"])
        
        return aggregated
    
    def _summarize_result(self, data_type: str, data: Any) -> Dict[str, Any]:
        """Create a summary for each data type"""
        if isinstance(data, str):
            # Count mentions and extract key info
            lines = data.split('\n')
            summary = {
                "total_lines": len(lines),
                "key_points": [line.strip() for line in lines[:3] if line.strip()],
                "data_type": data_type
            }
        else:
            summary = {
                "data_type": data_type,
                "status": "processed"
            }
        
        return summary
    
    async def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate cross-data recommendations"""
        recommendations = []
        
        # Simple rule-based recommendations for prototype
        if "flights" in data and not data["flights"].get("error"):
            recommendations.append("✈️ Flight options are available - book early for better prices")
        
        if "hotels" in data and not data["hotels"].get("error"):
            recommendations.append("🏨 Multiple accommodation options found - compare amenities")
        
        if "activities" in data and not data["activities"].get("error"):
            recommendations.append("🎯 Great activities available - plan 2-3 per day for best experience")
        
        if "destination_info" in data and not data["destination_info"].get("error"):
            recommendations.append("📍 Check local weather and cultural events during your visit")
        
        return recommendations
