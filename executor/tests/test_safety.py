"""
Test Safety Checker
Validates that dangerous operations are blocked
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from llm.command_schema import Command, CommandStep, RiskLevel
from executor.safety_check import SafetyChecker, require_confirmation


def test_safe_command():
    """Test that safe commands pass validation"""
    print("\n" + "="*70)
    print("TEST 1: Safe Command - Open Chrome")
    print("="*70)
    
    command = Command(
        intent="open_application",
        steps=[
            CommandStep(
                action="open_app",
                parameters={"app_name": "chrome"}
            )
        ],
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        explanation="Opening Chrome browser"
    )
    
    checker = SafetyChecker()
    is_safe, warnings = checker.validate_command(command)
    
    print(f"✅ Command: {command.intent}")
    print(f"✅ Risk Level: {command.risk_level.value}")
    print(f"✅ Validation result: {'SAFE' if is_safe else 'BLOCKED'}")
    print(f"✅ Warnings: {len(warnings)}")
    
    if is_safe:
        print("✅ TEST PASSED: Safe command allowed")
    else:
        print(f"❌ TEST FAILED: Safe command blocked! Warnings: {warnings}")
    
    return is_safe


def test_dangerous_delete():
    """Test that deleting system files is blocked"""
    print("\n" + "="*70)
    print("TEST 2: Dangerous Command - Delete System File")
    print("="*70)
    
    command = Command(
        intent="delete_system_file",
        steps=[
            CommandStep(
                action="delete_file",
                parameters={"path": "C:\\Windows\\System32\\kernel32.dll"}
            )
        ],
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        explanation="Attempting to delete system file"
    )
    
    checker = SafetyChecker()
    is_safe, warnings = checker.validate_command(command)
    
    print(f"🚨 Command: {command.intent}")
    print(f"🚨 Target: C:\\Windows\\System32\\kernel32.dll")
    print(f"🚨 Validation result: {'SAFE' if is_safe else 'BLOCKED'}")
    print(f"🚨 Warnings: {warnings}")
    
    if not is_safe:
        print("✅ TEST PASSED: Dangerous command blocked correctly")
    else:
        print("❌ TEST FAILED: Dangerous command was allowed!")
    
    return not is_safe


def test_dangerous_command():
    """Test that dangerous shell commands are blocked"""
    print("\n" + "="*70)
    print("TEST 3: Dangerous Shell Command")
    print("="*70)
    
    command = Command(
        intent="format_drive",
        steps=[
            CommandStep(
                action="run_command",
                parameters={"command": "format c: /q"}
            )
        ],
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        explanation="Format drive command"
    )
    
    checker = SafetyChecker()
    is_safe, warnings = checker.validate_command(command)
    
    print(f"🚨 Command: format c: /q")
    print(f"🚨 Validation result: {'SAFE' if is_safe else 'BLOCKED'}")
    print(f"🚨 Warnings: {warnings}")
    
    if not is_safe:
        print("✅ TEST PASSED: Dangerous shell command blocked")
    else:
        print("❌ TEST FAILED: Format command was allowed!")
    
    return not is_safe


def test_protected_path():
    """Test that protected directories are blocked"""
    print("\n" + "="*70)
    print("TEST 4: Protected Path - Program Files")
    print("="*70)
    
    command = Command(
        intent="delete_from_program_files",
        steps=[
            CommandStep(
                action="delete_file",
                parameters={"path": "C:\\Program Files\\important.exe"}
            )
        ],
        risk_level=RiskLevel.HIGH,
        requires_confirmation=True,
        explanation="Delete from Program Files"
    )
    
    checker = SafetyChecker()
    is_safe, warnings = checker.validate_command(command)
    
    print(f"🚨 Path: C:\\Program Files\\important.exe")
    print(f"🚨 Validation result: {'SAFE' if is_safe else 'BLOCKED'}")
    print(f"🚨 Warnings: {warnings}")
    
    if not is_safe:
        print("✅ TEST PASSED: Protected path blocked")
    else:
        print("❌ TEST FAILED: Protected path was allowed!")
    
    return not is_safe


def test_safe_user_file():
    """Test that safe user file operations are allowed"""
    print("\n" + "="*70)
    print("TEST 5: Safe Operation - Create File in Documents")
    print("="*70)
    
    command = Command(
        intent="create_document",
        steps=[
            CommandStep(
                action="create_file",
                parameters={
                    "path": "C:\\Users\\TestUser\\Documents\\notes.txt",
                    "content": "Hello World"
                }
            )
        ],
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        explanation="Create text file in Documents"
    )
    
    checker = SafetyChecker()
    is_safe, warnings = checker.validate_command(command)
    
    print(f"✅ Path: C:\\Users\\TestUser\\Documents\\notes.txt")
    print(f"✅ Validation result: {'SAFE' if is_safe else 'BLOCKED'}")
    print(f"✅ Warnings: {warnings}")
    
    if is_safe:
        print("✅ TEST PASSED: Safe user operation allowed")
    else:
        print(f"❌ TEST FAILED: Safe operation blocked! Warnings: {warnings}")
    
    return is_safe


def test_confirmation_required():
    """Test confirmation requirement logic"""
    print("\n" + "="*70)
    print("TEST 6: Confirmation Requirements")
    print("="*70)
    
    test_cases = [
        (RiskLevel.LOW, False, False, "Low risk, no explicit requirement"),
        (RiskLevel.MEDIUM, False, True, "Medium risk (default confirm)"),
        (RiskLevel.HIGH, False, True, "High risk (always confirm)"),
        (RiskLevel.LOW, True, True, "Low risk but explicitly required"),
    ]
    
    passed = 0
    for risk, explicit, expected, description in test_cases:
        command = Command(
            intent="test",
            steps=[CommandStep(action="open_app", parameters={})],
            risk_level=risk,
            requires_confirmation=explicit,
            explanation="Test"
        )
        
        result = require_confirmation(command)
        status = "✅" if result == expected else "❌"
        
        print(f"{status} {description}: {result} (expected {expected})")
        if result == expected:
            passed += 1
    
    print(f"\n{'✅' if passed == len(test_cases) else '❌'} Passed {passed}/{len(test_cases)} confirmation tests")
    return passed == len(test_cases)


def main():
    print("\n" + "="*70)
    print("🔒 TESTING SAFETY SYSTEM")
    print("="*70)
    
    tests = [
        ("Safe Command", test_safe_command),
        ("Block System Delete", test_dangerous_delete),
        ("Block Format Command", test_dangerous_command),
        ("Block Protected Path", test_protected_path),
        ("Allow User File", test_safe_user_file),
        ("Confirmation Logic", test_confirmation_required),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
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
        print("\n🎉 ALL SAFETY TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)