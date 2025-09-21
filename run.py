#!/usr/bin/env python3
"""
ADK Travel Agent Runner - Proper Google ADK startup script
"""

import os
import sys
import subprocess
import pkg_resources

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['google-adk', 'requests', 'python-dotenv']
    
    missing = []
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("🔧 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("✅ All dependencies are installed")
    
    return True

def check_api_keys():
    """Check if required API keys are set"""
    serpapi_key = os.getenv('SERPAPI_KEY')
    google_ai_key = os.getenv('GOOGLE_AI_API_KEY')
    
    issues = []
    
    if not serpapi_key:
        issues.append("SERPAPI_KEY not set")
        print("❌ SERPAPI_KEY environment variable not found")
        print("   Get your key at: https://serpapi.com/")
    else:
        print("✅ SERPAPI_KEY is configured")
    
    if not google_ai_key:
        issues.append("GOOGLE_AI_API_KEY not set")
        print("❌ GOOGLE_AI_API_KEY environment variable not found")
        print("   Get your key at: https://aistudio.google.com/")
    else:
        print("✅ GOOGLE_AI_API_KEY is configured")
    
    if issues:
        print("\n🔧 To set environment variables:")
        print("   export SERPAPI_KEY='your_key_here'")
        print("   export GOOGLE_AI_API_KEY='your_key_here'")
        print("\nOr add them to your shell profile (~/.bashrc, ~/.zshrc)")
        return False
    
    return True

def check_adk_structure():
    """Check if ADK project structure is correct"""
    required_files = [
        "agent.py",
        "adk.yaml",
        "agents/__init__.py", 
        "agents/orchestrator.py",
        "tools/__init__.py",
        "config/settings.py"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing ADK files: {', '.join(missing)}")
        return False
    else:
        print("✅ ADK project structure is correct")
        return True

def main():
    """Main runner function"""
    print("🌍 ADK Travel Agent - Startup Checker")
    print("=" * 45)
    
    # Check all prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_adk_structure():
        print("❌ ADK project structure is incomplete")
        sys.exit(1)
    
    if not check_api_keys():
        print("\n❌ Setup incomplete. Please configure API keys and try again.")
        sys.exit(1)
    
    print("\n🚀 All checks passed! Starting ADK Travel Agent...")
    print("=" * 45)
    
    # Provide startup options
    print("🛠️  Choose how to start the agent:")
    print("   1. adk web      # Web interface (recommended)")
    print("   2. adk run      # Terminal mode")
    print("   3. Test setup   # Run system tests")
    print("\n💡 Example queries to try:")
    print("   • 'Plan a 5-day trip to Tokyo for 2 people'")
    print("   • 'Find budget hotels in Barcelona'")
    print("   • 'What are the best activities in Paris?'")
    print("   • 'Create Rome itinerary focusing on history'")
    
    choice = input("\nEnter choice (1-3) or press Enter for web mode: ").strip()
    
    try:
        if choice == "3":
            print("\n🧪 Running system tests...")
            subprocess.run([sys.executable, "test_adk_agent.py"])
        elif choice == "2":
            print("\n🔧 Starting ADK in terminal mode...")
            subprocess.run(["adk", "run"])
        else:
            print("\n🌐 Starting ADK web interface...")
            print("   Open http://localhost:8000 in your browser")
            print("   Press Ctrl+C to stop")
            subprocess.run(["adk", "web"])
            
    except KeyboardInterrupt:
        print("\n👋 Travel Agent stopped. See you next time!")
    except FileNotFoundError:
        print("\n❌ ADK command not found. Make sure google-adk is installed:")
        print("   pip install google-adk")
    except Exception as e:
        print(f"\n❌ Error starting agent: {e}")
        print("\nTry running tests first:")
        print("   python test_adk_agent.py")

if __name__ == "__main__":
    main()
