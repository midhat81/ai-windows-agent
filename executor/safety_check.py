"""
Safety Verification System
Validates commands before execution to prevent dangerous operations
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from llm.command_schema import Command, RiskLevel, ActionType


class SafetyChecker:
    """Validates commands for safety before execution"""
    
    # Protected system paths that should never be modified
    PROTECTED_PATHS = [
        r"C:\Windows",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\System32",
        r"C:\ProgramData",
    ]
    
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        r"format\s+[a-z]:",  # format drive
        r"del\s+/s\s+/q",     # recursive delete
        r"rd\s+/s\s+/q",      # remove directory recursively
        r"reg\s+delete",       # registry delete
        r"bcdedit",            # boot config
        r"diskpart",           # disk partition
        r"cipher\s+/w",        # secure wipe
    ]
    
    # High-risk file extensions
    HIGH_RISK_EXTENSIONS = [
        '.exe', '.dll', '.sys', '.bat', '.cmd', 
        '.ps1', '.vbs', '.msi', '.reg'
    ]
    
    def __init__(self):
        self.blocked_commands: List[str] = []
        self.warnings: List[str] = []
    
    def validate_command(self, command: Command) -> Tuple[bool, List[str]]:
        """
        Validate entire command for safety
        
        Returns:
            (is_safe, list_of_issues)
        """
        self.warnings = []
        
        # 1. Validate command structure
        if not command.validate():
            self.warnings.append("Invalid command structure")
            return False, self.warnings
        
        # 2. Check risk level consistency
        if not self._validate_risk_level(command):
            return False, self.warnings
        
        # 3. Validate each step
        for i, step in enumerate(command.steps):
            if not self._validate_step(step, i + 1):
                return False, self.warnings
        
        # If we have warnings but command is structurally safe
        is_safe = len(self.warnings) == 0
        return is_safe, self.warnings
    
    def _validate_risk_level(self, command: Command) -> bool:
        """Ensure risk level matches actions"""
        high_risk_actions = [
            ActionType.DELETE_FILE.value,
            ActionType.RUN_COMMAND.value
        ]
        
        has_high_risk = any(
            step.action in high_risk_actions 
            for step in command.steps
        )
        
        if has_high_risk and command.risk_level != RiskLevel.HIGH:
            self.warnings.append(
                f"High-risk action detected but risk_level is {command.risk_level.value}"
            )
            return False
        
        return True
    
    def _validate_step(self, step, step_num: int) -> bool:
        """Validate individual step"""
        action = step.action
        params = step.parameters
        
        # Route to specific validator
        if action == ActionType.DELETE_FILE.value:
            return self._validate_delete_file(params, step_num)
        
        elif action == ActionType.RUN_COMMAND.value:
            return self._validate_run_command(params, step_num)
        
        elif action == ActionType.MOVE_FILE.value:
            return self._validate_move_file(params, step_num)
        
        elif action == ActionType.CREATE_FILE.value:
            return self._validate_create_file(params, step_num)
        
        # Default: safe actions need no special validation
        return True
    
    def _validate_delete_file(self, params: Dict, step_num: int) -> bool:
        """Validate file deletion"""
        path = params.get('path', '')
        
        # Check if path exists
        if not path:
            self.warnings.append(f"Step {step_num}: No path specified for delete")
            return False
        
        # Normalize path
        path = os.path.normpath(path)
        
        # Check protected paths
        if self._is_protected_path(path):
            self.warnings.append(
                f"Step {step_num}: Cannot delete from protected system directory: {path}"
            )
            return False
        
        # Check if trying to delete system files
        if self._is_system_file(path):
            self.warnings.append(
                f"Step {step_num}: Cannot delete system file: {path}"
            )
            return False
        
        return True
    
    def _validate_run_command(self, params: Dict, step_num: int) -> bool:
        """Validate command execution"""
        command = params.get('command', '')
        
        if not command:
            self.warnings.append(f"Step {step_num}: Empty command")
            return False
        
        # Check for dangerous patterns
        command_lower = command.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command_lower):
                self.warnings.append(
                    f"Step {step_num}: Dangerous command pattern detected: {pattern}"
                )
                return False
        
        return True
    
    def _validate_move_file(self, params: Dict, step_num: int) -> bool:
        """Validate file move operation"""
        source = params.get('source', '')
        destination = params.get('destination', '')
        
        if not source or not destination:
            self.warnings.append(
                f"Step {step_num}: Missing source or destination"
            )
            return False
        
        # Normalize paths
        source = os.path.normpath(source)
        destination = os.path.normpath(destination)
        
        # Check protected paths
        if self._is_protected_path(source) or self._is_protected_path(destination):
            self.warnings.append(
                f"Step {step_num}: Cannot move files to/from protected directories"
            )
            return False
        
        return True
    
    def _validate_create_file(self, params: Dict, step_num: int) -> bool:
        """Validate file creation"""
        path = params.get('path', '')
        
        if not path:
            self.warnings.append(f"Step {step_num}: No path specified")
            return False
        
        # Normalize path
        path = os.path.normpath(path)
        
        # Check if trying to create in protected location
        if self._is_protected_path(path):
            self.warnings.append(
                f"Step {step_num}: Cannot create file in protected directory: {path}"
            )
            return False
        
        # Check file extension
        ext = Path(path).suffix.lower()
        if ext in self.HIGH_RISK_EXTENSIONS:
            self.warnings.append(
                f"Step {step_num}: Creating executable file ({ext}). Please confirm."
            )
            # This is a warning, not a blocker
        
        return True
    
    def _is_protected_path(self, path: str) -> bool:
        """Check if path is in protected system directory"""
        path = os.path.normpath(path).lower()
        
        return any(
            path.startswith(protected.lower())
            for protected in self.PROTECTED_PATHS
        )
    
    def _is_system_file(self, path: str) -> bool:
        """Check if file is a critical system file"""
        path = path.lower()
        
        system_patterns = [
            r'\\system32\\',
            r'\\syswow64\\',
            r'\\windows\\system',
            'ntoskrnl.exe',
            'kernel32.dll',
            'user32.dll',
        ]
        
        return any(
            pattern in path or path.endswith(pattern)
            for pattern in system_patterns
        )
    
    def get_confirmation_message(self, command: Command) -> str:
        """Generate human-readable confirmation message"""
        risk_emoji = {
            RiskLevel.LOW: "✅",
            RiskLevel.MEDIUM: "⚠️",
            RiskLevel.HIGH: "🚨"
        }
        
        emoji = risk_emoji.get(command.risk_level, "⚠️")
        
        msg = f"\n{emoji} CONFIRM ACTION\n"
        msg += "=" * 60 + "\n"
        msg += f"Risk Level: {command.risk_level.value.upper()}\n"
        msg += f"Intent: {command.intent}\n"
        msg += f"\n{command.explanation}\n"
        msg += "\nSteps:\n"
        
        for i, step in enumerate(command.steps, 1):
            msg += f"  {i}. {step.action.upper()}\n"
            for key, value in step.parameters.items():
                msg += f"     • {key}: {value}\n"
        
        msg += "\n" + "=" * 60
        msg += f"\nProceed with this {command.risk_level.value}-risk action? (y/n): "
        
        return msg


def require_confirmation(command: Command) -> bool:
    """
    Check if command requires user confirmation
    
    Returns:
        True if confirmation needed, False otherwise
    """
    # Always confirm high-risk
    if command.risk_level == RiskLevel.HIGH:
        return True
    
    # Confirm if explicitly marked
    if command.requires_confirmation:
        return True
    
    # Confirm medium-risk by default
    if command.risk_level == RiskLevel.MEDIUM:
        return True
    
    return False


def get_user_confirmation(command: Command) -> bool:
    """
    Get user confirmation for command execution
    
    Returns:
        True if user confirms, False otherwise
    """
    checker = SafetyChecker()
    message = checker.get_confirmation_message(command)
    
    try:
        response = input(message).strip().lower()
        return response in ['y', 'yes']
    except (KeyboardInterrupt, EOFError):
        print("\n❌ Cancelled by user")
        return False