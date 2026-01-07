"""
Test prompt template generation
Shows what prompts we're sending to the LLM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.prompt_templates import (
    get_full_prompt, 
    create_user_prompt,
    normalize_app_name,
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES
)

def test_simple_command():
    """Test prompt for simple command"""
    print("=" * 60)
    print("TEST 1: Simple Command - 'Open Chrome'")
    print("=" * 60)
    
    voice_command = "Open Chrome"
    full_prompt = get_full_prompt(voice_command, username="MuhammadMidhat")
    
    print("\n📝 FULL PROMPT (what we send to LLM):")
    print("-" * 60)
    print(full_prompt)
    print("-" * 60)
    print(f"\n✅ Prompt length: {len(full_prompt)} characters")
    print(f"✅ Username inserted: MuhammadMidhat")

def test_complex_command():
    """Test prompt for complex command"""
    print("\n" + "=" * 60)
    print("TEST 2: Complex Command - Multi-step")
    print("=" * 60)
    
    voice_command = "Open Chrome and search for AI tutorials"
    user_prompt = create_user_prompt(voice_command, username="MuhammadMidhat")
    
    print("\n📝 USER PROMPT ONLY:")
    print("-" * 60)
    print(user_prompt)
    print("-" * 60)
    print(f"✅ Voice command: {voice_command}")

def test_app_name_normalization():
    """Test app name normalization"""
    print("\n" + "=" * 60)
    print("TEST 3: App Name Normalization")
    print("=" * 60)
    
    test_names = [
        "Chrome",
        "Google Chrome",
        "VS Code",
        "Visual Studio Code",
        "notepad",
        "Microsoft Word",
        "Discord",
        "unknown app"
    ]
    
    print("\n📱 APP NAME MAPPINGS:")
    print("-" * 60)
    for name in test_names:
        normalized = normalize_app_name(name)
        print(f"{name:30} → {normalized}")
    print("-" * 60)

def show_prompt_structure():
    """Show the structure of our prompts"""
    print("\n" + "=" * 60)
    print("PROMPT STRUCTURE BREAKDOWN")
    print("=" * 60)
    
    print("\n1️⃣ SYSTEM PROMPT (teaches LLM its role)")
    print(f"   Length: {len(SYSTEM_PROMPT)} characters")
    print(f"   Contains: Rules, allowed actions, output format")
    
    print("\n2️⃣ FEW-SHOT EXAMPLES (teaches by example)")
    print(f"   Length: {len(FEW_SHOT_EXAMPLES)} characters")
    print(f"   Contains: 6 example voice commands → JSON outputs")
    
    print("\n3️⃣ USER COMMAND (the actual voice input)")
    print(f"   Format: 'User: [voice_command]'")
    print(f"   Ends with: 'Output:' to prompt JSON response")
    
    print("\n📊 TOTAL PROMPT SIZE:")
    example_full = get_full_prompt("Open Chrome")
    print(f"   ~{len(example_full)} characters")
    print(f"   ~{len(example_full.split())} words")

if __name__ == "__main__":
    print("\n🧪 TESTING PROMPT TEMPLATES\n")
    
    show_prompt_structure()
    test_simple_command()
    test_complex_command()
    test_app_name_normalization()
    
    print("\n" + "=" * 60)
    print("✅ ALL PROMPT TESTS COMPLETE!")
    print("=" * 60)
    print("\nNext: These prompts will be sent to Llama 3.1")
    print("to generate the JSON commands we tested in Step 2!")