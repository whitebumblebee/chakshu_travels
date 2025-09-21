#!/usr/bin/env python3
"""
Simple test script to verify the Travel Agent setup
"""

import os
import asyncio
from datetime import datetime

def test_imports():
    """Test that all required imports work"""
    print("🧪 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config module imported")
        
        from serpapi_tool import SerpApiTool
        print("✅ SerpApi tool imported")
        
        from travel_agent import TravelPlanningAgent
        print("✅ Travel agent imported")
        
        from google.adk import Agent, tool
        print("✅ Google ADK imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration and API keys"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config
        
        # Test API keys
        serpapi_key = os.getenv('SERPAPI_KEY')
        google_ai_key = os.getenv('GOOGLE_AI_API_KEY')
        
        if serpapi_key:
            print(f"✅ SERPAPI_KEY configured (length: {len(serpapi_key)})")
        else:
            print("❌ SERPAPI_KEY not found")
            
        if google_ai_key:
            print(f"✅ GOOGLE_AI_API_KEY configured (length: {len(google_ai_key)})")
        else:
            print("❌ GOOGLE_AI_API_KEY not found")
        
        # Test validation
        if serpapi_key and google_ai_key:
            Config.validate()
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_agent():
    """Test agent initialization and basic functionality"""
    print("\n🧪 Testing agent...")
    
    try:
        from travel_agent import TravelPlanningAgent
        
        agent = TravelPlanningAgent()
        print("✅ Travel agent initialized")
        
        # Test tool availability
        tools = [attr for attr in dir(agent) if hasattr(getattr(agent, attr), '__tool_metadata__')]
        print(f"✅ Found {len(tools)} agent tools: {', '.join(tools)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

async def test_serpapi_connection():
    """Test SerpApi connectivity (if keys are available)"""
    print("\n🧪 Testing SerpApi connection...")
    
    try:
        from serpapi_tool import SerpApiTool
        
        if not os.getenv('SERPAPI_KEY'):
            print("⚠️  SERPAPI_KEY not set, skipping connection test")
            return True
        
        tool = SerpApiTool()
        
        # Test with a simple query
        result = await tool.search_destination_info("Paris", "travel guide")
        
        if 'error' in result:
            print(f"❌ SerpApi connection failed: {result['error']}")
            return False
        elif result.get('destination_info'):
            print(f"✅ SerpApi connection successful, found {len(result['destination_info'])} results")
            return True
        else:
            print("⚠️  SerpApi connection succeeded but returned no results")
            return True
            
    except Exception as e:
        print(f"❌ SerpApi test failed: {e}")
        return False

async def test_web_app():
    """Test that the web app can be imported and configured"""
    print("\n🧪 Testing web application...")
    
    try:
        from app import app
        print("✅ FastAPI app imported")
        
        # Check if templates directory exists
        import os
        if os.path.exists('templates'):
            template_files = os.listdir('templates')
            print(f"✅ Templates found: {', '.join(template_files)}")
        else:
            print("❌ Templates directory not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web app test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🌍 AI Travel Agent - System Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports()),
        ("Configuration", test_configuration()),
        ("Agent", test_agent()),
        ("SerpApi", test_serpapi_connection()),
        ("Web App", test_web_app())
    ]
    
    results = []
    for name, test_coro in tests:
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
        print("\n🚀 All tests passed! Your Travel Agent is ready to run.")
        print("   Start with: python app.py")
        print("   Or use: python run.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        if not os.getenv('SERPAPI_KEY') or not os.getenv('GOOGLE_AI_API_KEY'):
            print("\n💡 Missing API keys? Set them with:")
            print("   export SERPAPI_KEY='your_serpapi_key'")
            print("   export GOOGLE_AI_API_KEY='your_google_ai_key'")

if __name__ == "__main__":
    asyncio.run(main())
