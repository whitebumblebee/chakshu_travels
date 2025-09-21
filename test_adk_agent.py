#!/usr/bin/env python3
"""
Test script to verify ADK agent setup and functionality
"""

import os
import sys
import asyncio
from datetime import datetime


def test_environment():
    """Test environment setup and API keys"""
    print("🔧 Testing Environment Setup...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check API keys
    serpapi_key = os.getenv('SERPAPI_KEY')
    google_ai_key = os.getenv('GOOGLE_AI_API_KEY') 
    
    if not serpapi_key:
        print("❌ SERPAPI_KEY not set")
        return False
    print("✅ SERPAPI_KEY configured")
    
    if not google_ai_key:
        print("❌ GOOGLE_AI_API_KEY not set")
        return False
    print("✅ GOOGLE_AI_API_KEY configured")
    
    return True


def test_imports():
    """Test that all modules can be imported"""
    print("\n🔧 Testing Imports...")
    
    try:
        from google.adk import LlmAgent, Tool
        print("✅ Google ADK imported")
    except ImportError as e:
        print(f"❌ ADK import failed: {e}")
        return False
    
    try:
        from config.settings import Config
        print("✅ Config imported")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from tools import FlightSearchTool, HotelSearchTool
        print("✅ Tools imported")
    except ImportError as e:
        print(f"❌ Tools import failed: {e}")
        return False
    
    try:
        from agents.orchestrator import TravelPlanningOrchestrator
        print("✅ Orchestrator imported")
    except ImportError as e:
        print(f"❌ Orchestrator import failed: {e}")
        return False
    
    try:
        from agent import agent
        print("✅ Root agent imported")
    except ImportError as e:
        print(f"❌ Root agent import failed: {e}")
        return False
    
    return True


async def test_agent_functionality():
    """Test basic agent functionality"""
    print("\n🔧 Testing Agent Functionality...")
    
    try:
        from agent import agent
        
        # Test agent properties
        print(f"✅ Agent name: {agent.name}")
        print(f"✅ Agent description: {agent.description[:50]}...")
        
        # Test basic message processing
        test_message = "Plan a 3-day trip to Paris"
        print(f"🧪 Testing message: '{test_message}'")
        
        result = await agent.process_travel_request(test_message)
        
        if isinstance(result, str) and len(result) > 0:
            print("✅ Agent processed message successfully")
            print(f"📤 Response preview: {result[:100]}...")
            return True
        else:
            print("❌ Agent returned invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Agent functionality test failed: {e}")
        return False


async def test_child_agents():
    """Test child agent coordination"""
    print("\n🔧 Testing Child Agent Coordination...")
    
    try:
        from agents.orchestrator import TravelPlanningOrchestrator
        from agents.itinerary_agent import ItineraryPlanningAgent
        from agents.data_aggregator import DataAggregationAgent
        
        orchestrator = TravelPlanningOrchestrator()
        
        # Test child agent access
        print(f"✅ Itinerary agent: {type(orchestrator.itinerary_agent).__name__}")
        print(f"✅ Data aggregator: {type(orchestrator.data_aggregator).__name__}")
        
        # Test intent parsing
        intent = await orchestrator._parse_travel_intent("Plan a week in Tokyo for 2 people")
        
        if intent and intent.get("destination"):
            print(f"✅ Intent parsing: destination = {intent['destination']}")
            return True
        else:
            print("❌ Intent parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Child agent test failed: {e}")
        return False


def test_adk_structure():
    """Test ADK project structure"""
    print("\n🔧 Testing ADK Project Structure...")
    
    required_files = [
        "agent.py",
        "adk.yaml",
        "agents/__init__.py",
        "agents/orchestrator.py",
        "agents/itinerary_agent.py",
        "agents/data_aggregator.py",
        "tools/__init__.py",
        "config/__init__.py",
        "config/settings.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True


async def main():
    """Run all tests"""
    print("🌍 ADK Travel Agent - System Tests")
    print("=" * 40)
    
    tests = [
        ("Environment", test_environment()),
        ("Project Structure", test_adk_structure()),
        ("Imports", test_imports()),
        ("Agent Functionality", test_agent_functionality()),
        ("Child Agent Coordination", test_child_agents())
    ]
    
    results = []
    for name, test_coro in tests:
        print(f"\n📋 Running: {name}")
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((name, result))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🚀 All tests passed! Your ADK Travel Agent is ready.")
        print("\n🔧 To start the agent:")
        print("   adk web     # Start web interface")
        print("   adk run     # Start in terminal mode")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        if not os.getenv('SERPAPI_KEY') or not os.getenv('GOOGLE_AI_API_KEY'):
            print("\n💡 Missing API keys? Set them with:")
            print("   export SERPAPI_KEY='your_serpapi_key'")
            print("   export GOOGLE_AI_API_KEY='your_google_ai_key'")


if __name__ == "__main__":
    asyncio.run(main())
