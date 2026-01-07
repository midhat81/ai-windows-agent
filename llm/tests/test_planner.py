"""
Test LLM Planner - End-to-End Voice Command Processing
This tests the REAL Llama 3.1 integration!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.planner import LLMPlanner, quick_plan
import json


def test_simple_command():
    """Test a simple command"""
    print("=" * 70)
    print("TEST 1: Simple Command - 'Open Chrome'")
    print("=" * 70)
    
    command = quick_plan("Open Chrome", verbose=True)
    
    if command:
        print("\n✅ SUCCESS!")
        print(f"📋 Final Command:")
        print(json.dumps(command.to_dict(), indent=2))
        return True
    else:
        print("\n❌ FAILED - Could not generate command")
        return False


def test_multi_step_command():
    """Test a multi-step command"""
    print("\n" + "=" * 70)
    print("TEST 2: Multi-Step Command - 'Open Chrome and search for Python'")
    print("=" * 70)
    
    command = quick_plan("Open Chrome and search for Python tutorials", verbose=True)
    
    if command:
        print("\n✅ SUCCESS!")
        print(f"📋 Command has {len(command.steps)} steps:")
        for i, step in enumerate(command.steps, 1):
            print(f"  Step {i}: {step.action}")
            print(f"    Params: {step.parameters}")
        return True
    else:
        print("\n❌ FAILED")
        return False


def test_file_operation():
    """Test file creation command"""
    print("\n" + "=" * 70)
    print("TEST 3: File Operation - 'Create a file called test.txt'")
    print("=" * 70)
    
    command = quick_plan("Create a file called test.txt in Documents", verbose=True)
    
    if command:
        print("\n✅ SUCCESS!")
        print(f"📋 Risk Level: {command.risk_level.value}")
        print(f"⚠️  Requires Confirmation: {command.requires_confirmation}")
        return True
    else:
        print("\n❌ FAILED")
        return False


def test_various_commands():
    """Test multiple different commands quickly"""
    print("\n" + "=" * 70)
    print("TEST 4: Batch Testing - Various Commands")
    print("=" * 70)
    
    test_commands = [
        "Open Notepad",
        "Close Chrome",
        "Find PDF files in Downloads",
        "Open VS Code",
    ]
    
    planner = LLMPlanner()
    results = []
    
    for cmd in test_commands:
        print(f"\n🎙️  Testing: '{cmd}'")
        command = planner.plan(cmd, verbose=False)
        
        if command:
            print(f"   ✅ Intent: {command.intent}")
            print(f"   ✅ Risk: {command.risk_level.value}")
            results.append(True)
        else:
            print(f"   ❌ Failed to process")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"\n📊 Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)})")
    
    return sum(results) == len(results)


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 70)
    print("TEST 5: Edge Cases")
    print("=" * 70)
    
    edge_cases = [
        ("Ambiguous command", "Do something"),
        ("Empty command", ""),
        ("Dangerous command", "Delete all files"),
    ]
    
    planner = LLMPlanner()
    
    for name, cmd in edge_cases:
        print(f"\n🧪 {name}: '{cmd}'")
        command = planner.plan(cmd, verbose=False)
        
        if command:
            print(f"   ℹ️  Intent: {command.intent}")
            print(f"   ℹ️  Explanation: {command.explanation}")
            if command.intent == "error":
                print(f"   ✅ Correctly identified as error/unclear")
        else:
            print(f"   ⚠️  No command generated (expected for invalid inputs)")


def interactive_test():
    """Interactive testing - type your own commands"""
    print("\n" + "=" * 70)
    print("🎤 INTERACTIVE MODE - Type your own commands!")
    print("=" * 70)
    print("Type 'quit' or 'exit' to stop\n")
    
    planner = LLMPlanner()
    
    while True:
        try:
            user_input = input("\n🎙️  Your command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print()
            command = planner.plan(user_input, verbose=True)
            
            if command:
                print("\n" + "=" * 70)
                print("📋 GENERATED COMMAND:")
                print("=" * 70)
                print(json.dumps(command.to_dict(), indent=2))
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 TESTING LLM PLANNER WITH REAL LLAMA 3.1")
    print("=" * 70)
    print("\nMake sure Ollama is running: ollama serve")
    print()
    
    # Run automated tests
    results = []
    
    try:
        results.append(test_simple_command())
        results.append(test_multi_step_command())
        results.append(test_file_operation())
        results.append(test_various_commands())
        test_edge_cases()  # Don't track pass/fail for edge cases
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 FINAL RESULTS")
        print("=" * 70)
        print(f"Tests passed: {sum(results)}/{len(results)}")
        
        if all(results):
            print("\n🎉 ALL TESTS PASSED! LLM Planner is working!")
        else:
            print("\n⚠️  Some tests failed - check logs above")
        
        # Offer interactive mode
        print("\n" + "=" * 70)
        response = input("\n🎤 Want to try interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_test()
        else:
            print("👋 Done!")
            
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        print("\nMake sure:")
        print("1. Ollama is running (ollama serve)")
        print("2. Llama 3.1 model is downloaded (ollama pull llama3.2:3b)")