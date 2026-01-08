"""
Test FastAPI Backend
Tests REST endpoints and WebSocket connections
"""

import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"🧪 {text}")
    print("="*70)


def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Status: {data['status']}")
        print(f"LLM Available: {data['llm_available']}")
        print(f"Executor Ready: {data['executor_ready']}")
        
        if response.status_code == 200 and data['llm_available']:
            print("✅ TEST PASSED: Backend is healthy")
            return True
        else:
            print("❌ TEST FAILED: Backend not ready")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_capabilities():
    """Test capabilities endpoint"""
    print_header("TEST 2: Get Capabilities")
    
    try:
        response = requests.get(f"{BASE_URL}/api/capabilities")
        data = response.json()
        
        print(f"Available Actions: {len(data['actions'])}")
        print(f"Actions: {', '.join(data['actions'][:5])}...")
        print(f"\nExample Commands:")
        for example in data['examples']:
            print(f"  • {example}")
        
        print("✅ TEST PASSED: Capabilities retrieved")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_dry_run_command():
    """Test dry-run command execution"""
    print_header("TEST 3: Dry-Run Command")
    
    try:
        payload = {
            "command": "Open Chrome",
            "dry_run": True
        }
        
        print(f"🎙️  Command: '{payload['command']}'")
        print(f"🔍 Dry-run: {payload['dry_run']}")
        
        response = requests.post(
            f"{BASE_URL}/api/command",
            json=payload
        )
        
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Success: {data['success']}")
        
        if data['command']:
            cmd = data['command']
            print(f"Intent: {cmd['intent']}")
            print(f"Steps: {len(cmd['steps'])}")
            print(f"Risk Level: {cmd['risk_level']}")
        
        if response.status_code == 200 and data['success']:
            print("✅ TEST PASSED: Dry-run executed")
            return True
        else:
            print(f"❌ TEST FAILED: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_real_command():
    """Test real command execution"""
    print_header("TEST 4: Real Command Execution")
    
    print("⚠️  This will ACTUALLY open Notepad!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("⏭️  Skipped by user")
        return True
    
    try:
        payload = {
            "command": "Open Notepad",
            "dry_run": False
        }
        
        print(f"\n🎙️  Command: '{payload['command']}'")
        
        response = requests.post(
            f"{BASE_URL}/api/command",
            json=payload,
            timeout=30  # Longer timeout for execution
        )
        
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Success: {data['success']}")
        
        if data['result']:
            print(f"Result: {data['result']['message']}")
        
        if response.status_code == 200 and data['success']:
            print("✅ TEST PASSED: Command executed (Check if Notepad opened!)")
            return True
        else:
            print(f"❌ TEST FAILED: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_history():
    """Test command history"""
    print_header("TEST 5: Command History")
    
    try:
        response = requests.get(f"{BASE_URL}/api/history?limit=10")
        data = response.json()
        
        print(f"Total Commands: {data['total']}")
        print(f"Retrieved: {len(data['history'])}")
        
        if data['history']:
            print("\nRecent Commands:")
            for i, entry in enumerate(data['history'][-3:], 1):
                print(f"  {i}. {entry['command']} - {entry['intent']}")
                print(f"     Success: {entry['success']}, Dry-run: {entry['dry_run']}")
        
        print("✅ TEST PASSED: History retrieved")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_websocket():
    """Test WebSocket connection"""
    print_header("TEST 6: WebSocket Connection")
    
    try:
        import websocket
        
        ws_url = "ws://localhost:8000/ws"
        print(f"Connecting to: {ws_url}")
        
        ws = websocket.create_connection(ws_url)
        
        # Receive welcome message
        welcome = json.loads(ws.recv())
        print(f"✅ Connected: {welcome['message']}")
        
        # Send ping
        ws.send(json.dumps({"type": "ping"}))
        pong = json.loads(ws.recv())
        print(f"✅ Ping-Pong: {pong['type']}")
        
        ws.close()
        print("✅ TEST PASSED: WebSocket works")
        return True
        
    except ImportError:
        print("⚠️  websocket-client not installed")
        print("   Install: pip install websocket-client")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 TESTING AI WINDOWS AGENT BACKEND API")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n⚠️  IMPORTANT:")
    print("  1. Make sure Ollama is running: ollama serve")
    print("  2. Make sure backend is running: python backend/api.py")
    print("  3. Wait for backend to initialize (10-15 seconds)")
    
    input("\nPress Enter when ready...")
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Capabilities", test_capabilities),
        ("Dry-Run Command", test_dry_run_command),
        ("Real Command", test_real_command),
        ("History", test_history),
        ("WebSocket", test_websocket),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"\n❌ TEST ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend is working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} tests failed - check backend logs")
    
    return passed == total


if __name__ == "__main__":
    success = main()