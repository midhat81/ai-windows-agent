"""
Test Command Executor
Tests the complete flow: Voice → LLM → Executor → Action
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.planner import LLMPlanner
from executor.executor import CommandExecutor
import time


def test_dry_run():
    """Test dry-run mode (safe, no actual execution)"""
    print("=" * 70)
    print("TEST 1: Dry-Run Mode (Preview Only)")
    print("=" * 70)
    
    planner = LLMPlanner()
    executor = CommandExecutor(dry_run=True, verbose=True)
    
    # Test command
    voice_cmd = "Open Chrome and search for Python tutorials"
    
    print(f"\n🎙️  Voice Command: '{voice_cmd}'")
    print("\n🤖 Planning...")
    
    command = planner.plan(voice_cmd, verbose=False)
    
    if command:
        print(f"✅ Plan created: {command.intent}")
        
        print("\n🔍 Executing in DRY-RUN mode...")
        report = executor.execute(command)
        
        return report.success
    else:
        print("❌ Failed to create plan")
        return False


def test_safe_execution():
    """Test actual execution with safe commands"""
    print("\n" + "=" * 70)
    print("TEST 2: Safe Command Execution (REAL)")
    print("=" * 70)
    
    planner = LLMPlanner()
    executor = CommandExecutor(dry_run=False, verbose=True)
    
    # Test with a safe command
    voice_cmd = "Open Notepad"
    
    print(f"\n🎙️  Voice Command: '{voice_cmd}'")
    print("\n🤖 Planning...")
    
    command = planner.plan(voice_cmd, verbose=False)
    
    if command:
        print(f"✅ Plan created: {command.intent}")
        
        # Ask for confirmation
        print("\n⚠️  This will ACTUALLY open Notepad!")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n🚀 Executing...")
            report = executor.execute(command)
            
            if report.success:
                print("\n✅ SUCCESS! Notepad should be open now.")
                print("\n💡 Check your screen - did Notepad open?")
                return True
            else:
                print(f"\n❌ Execution failed: {report.errors}")
                return False
        else:
            print("❌ Cancelled by user")
            return False
    else:
        print("❌ Failed to create plan")
        return False


def test_file_creation():
    """Test file creation (creates a real file in temp)"""
    print("\n" + "=" * 70)
    print("TEST 3: File Creation")
    print("=" * 70)
    
    planner = LLMPlanner()
    executor = CommandExecutor(dry_run=False, verbose=True)
    
    # Create a test file in temp directory
    import tempfile
    temp_dir = tempfile.gettempdir()
    
    voice_cmd = f"Create a file called test_ai_agent.txt in {temp_dir}"
    
    print(f"\n🎙️  Voice Command: '{voice_cmd}'")
    print("\n🤖 Planning...")
    
    command = planner.plan(voice_cmd, verbose=False)
    
    if command:
        print(f"✅ Plan created: {command.intent}")
        
        print("\n⚠️  This will create a real file!")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n🚀 Executing...")
            report = executor.execute(command)
            
            if report.success:
                print("\n✅ File created!")
                
                # Verify file exists
                test_file = os.path.join(temp_dir, "test_ai_agent.txt")
                if os.path.exists(test_file):
                    print(f"✅ Verified: {test_file}")
                    
                    # Clean up
                    cleanup = input("\nDelete test file? (y/n): ").strip().lower()
                    if cleanup == 'y':
                        os.remove(test_file)
                        print("🗑️  Test file deleted")
                    
                    return True
                else:
                    print("❌ File not found (unexpected)")
                    return False
            else:
                print(f"\n❌ Execution failed: {report.errors}")
                return False
        else:
            print("❌ Cancelled by user")
            return False
    else:
        print("❌ Failed to create plan")
        return False


def test_complete_flow():
    """Test the complete end-to-end flow"""
    print("\n" + "=" * 70)
    print("TEST 4: Complete End-to-End Flow")
    print("=" * 70)
    
    planner = LLMPlanner()
    executor = CommandExecutor(dry_run=False, verbose=True)
    
    test_commands = [
        "Open Notepad",
        "Open Calculator",
    ]
    
    print("\n📋 Will test these commands:")
    for i, cmd in enumerate(test_commands, 1):
        print(f"  {i}. {cmd}")
    
    confirm = input("\n⚠️  This will ACTUALLY execute these commands. Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled by user")
        return False
    
    results = []
    
    for cmd in test_commands:
        print(f"\n{'='*70}")
        print(f"🎙️  Testing: '{cmd}'")
        print(f"{'='*70}")
        
        # Plan
        command = planner.plan(cmd, verbose=False)
        
        if not command:
            print(f"❌ Failed to plan: {cmd}")
            results.append(False)
            continue
        
        # Execute
        report = executor.execute(command)
        results.append(report.success)
        
        # Small delay between commands
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Total commands: {len(results)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    return all(results)


def interactive_mode():
    """Interactive testing mode"""
    print("\n" + "=" * 70)
    print("🎤 INTERACTIVE EXECUTOR MODE")
    print("=" * 70)
    print("\nCommands:")
    print("  - Type a voice command to execute")
    print("  - Type 'dry' to toggle dry-run mode")
    print("  - Type 'quit' or 'exit' to stop")
    print()
    
    planner = LLMPlanner()
    executor = CommandExecutor(dry_run=True, verbose=True)  # Start in dry-run
    
    print("🔍 Starting in DRY-RUN mode (safe, no execution)")
    
    while True:
        try:
            user_input = input("\n🎙️  Your command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'dry':
                executor.set_dry_run(not executor.dry_run)
                mode = "DRY-RUN" if executor.dry_run else "LIVE EXECUTION"
                print(f"🔄 Switched to {mode} mode")
                continue
            
            if not user_input:
                continue
            
            # Warn if in live mode
            if not executor.dry_run:
                print("⚠️  LIVE MODE - This will ACTUALLY execute!")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("❌ Cancelled")
                    continue
            
            # Plan
            print("\n🤖 Planning...")
            command = planner.plan(user_input, verbose=False)
            
            if not command:
                print("❌ Failed to understand command")
                continue
            
            # Execute
            print()
            report = executor.execute(command)
            
            if report.success:
                print("\n🎉 Command executed successfully!")
            else:
                print(f"\n❌ Execution failed")
                for error in report.errors:
                    print(f"   • {error}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 TESTING COMMAND EXECUTOR")
    print("=" * 70)
    print("\n⚠️  IMPORTANT:")
    print("  • Test 1 (Dry-Run) is SAFE - no actual execution")
    print("  • Tests 2-4 will ACTUALLY execute commands")
    print("  • You'll be asked to confirm before each execution")
    print()
    
    results = []
    
    # Test 1: Always safe
    results.append(test_dry_run())
    
    # Ask about real execution tests
    print("\n" + "=" * 70)
    response = input("\nRun REAL execution tests? (y/n): ").strip().lower()
    
    if response == 'y':
        results.append(test_safe_execution())
        results.append(test_file_creation())
        results.append(test_complete_flow())
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    print(f"Tests run: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    # Offer interactive mode
    print("\n" + "=" * 70)
    response = input("\n🎤 Try interactive mode? (y/n): ").strip().lower()
    
    if response == 'y':
        interactive_mode()
    else:
        print("\n👋 Done! Your executor is working!")