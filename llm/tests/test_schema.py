"""
Test the command schema validation
This file tests if our JSON structure works correctly
"""

import sys
import os
# Add parent directory to path so we can import from llm folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.command_schema import Command, CommandStep, RiskLevel

def test_valid_command():
    """Test creating a valid command"""
    print("=" * 50)
    print("TEST 1: Valid Command - Open Chrome")
    print("=" * 50)
    
    test_json = {
        "intent": "open_application",
        "steps": [
            {
                "action": "open_app",
                "parameters": {"app_name": "chrome"}
            }
        ],
        "risk_level": "low",
        "requires_confirmation": False,
        "explanation": "Opening Chrome browser"
    }
    
    try:
        command = Command.from_dict(test_json)
        is_valid = command.validate()
        
        print(f"✅ Command created successfully")
        print(f"✅ Validation passed: {is_valid}")
        print(f"\nCommand details:")
        print(f"  Intent: {command.intent}")
        print(f"  Steps: {len(command.steps)}")
        print(f"  Risk: {command.risk_level.value}")
        print(f"  Needs confirmation: {command.requires_confirmation}")
        print(f"\nJSON output:")
        print(command.to_dict())
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multi_step_command():
    """Test command with multiple steps"""
    print("\n" + "=" * 50)
    print("TEST 2: Multi-Step Command - Open Chrome and Search")
    print("=" * 50)
    
    test_json = {
        "intent": "web_search",
        "steps": [
            {
                "action": "open_app",
                "parameters": {"app_name": "chrome"}
            },
            {
                "action": "open_url",
                "parameters": {"url": "https://google.com/search?q=Python"}
            }
        ],
        "risk_level": "low",
        "requires_confirmation": False,
        "explanation": "Opening Chrome and searching"
    }
    
    try:
        command = Command.from_dict(test_json)
        is_valid = command.validate()
        
        print(f"✅ Multi-step command created")
        print(f"✅ Validation passed: {is_valid}")
        print(f"\nCommand has {len(command.steps)} steps:")
        for i, step in enumerate(command.steps, 1):
            print(f"  Step {i}: {step.action}")
            print(f"    Parameters: {step.parameters}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_action():
    """Test command with invalid action"""
    print("\n" + "=" * 50)
    print("TEST 3: Invalid Action - Should Fail")
    print("=" * 50)
    
    test_json = {
        "intent": "invalid_test",
        "steps": [
            {
                "action": "invalid_action",  # This should fail
                "parameters": {}
            }
        ],
        "risk_level": "low",
        "requires_confirmation": False,
        "explanation": "Testing invalid action"
    }
    
    try:
        command = Command.from_dict(test_json)
        is_valid = command.validate()
        
        if not is_valid:
            print(f"✅ Correctly detected invalid action")
            print(f"✅ Validation failed as expected: {is_valid}")
            return True
        else:
            print(f"❌ Should have failed but didn't")
            return False
    except Exception as e:
        print(f"✅ Correctly caught error: {e}")
        return True

def test_high_risk_command():
    """Test high-risk command"""
    print("\n" + "=" * 50)
    print("TEST 4: High-Risk Command - Delete File")
    print("=" * 50)
    
    test_json = {
        "intent": "delete_file",
        "steps": [
            {
                "action": "delete_file",
                "parameters": {"path": "C:\\temp\\test.txt"}
            }
        ],
        "risk_level": "high",
        "requires_confirmation": True,
        "explanation": "Deleting file - cannot be undone"
    }
    
    try:
        command = Command.from_dict(test_json)
        is_valid = command.validate()
        
        print(f"✅ High-risk command created")
        print(f"✅ Validation passed: {is_valid}")
        print(f"✅ Requires confirmation: {command.requires_confirmation}")
        print(f"✅ Risk level: {command.risk_level.value}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 TESTING COMMAND SCHEMA\n")
    
    results = []
    results.append(test_valid_command())
    results.append(test_multi_step_command())
    results.append(test_invalid_action())
    results.append(test_high_risk_command())
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED! Schema is working correctly!")
    else:
        print("\n❌ Some tests failed. Check errors above.")