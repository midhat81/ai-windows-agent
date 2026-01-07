"""
Command Schema Definition
Defines the structure for LLM outputs and valid actions
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """Risk levels for commands"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ActionType(Enum):
    """All possible actions the agent can perform"""
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    OPEN_FILE = "open_file"
    OPEN_URL = "open_url"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    MOVE_FILE = "move_file"
    SEARCH_FILES = "search_files"
    SEND_EMAIL = "send_email"
    RUN_COMMAND = "run_command"

@dataclass
class CommandStep:
    """Single action step in a command"""
    action: str
    parameters: Dict
    
    def validate(self) -> bool:
        """Check if action is valid"""
        try:
            ActionType(self.action)
            return True
        except ValueError:
            return False

@dataclass
class Command:
    """Complete command structure from LLM"""
    intent: str
    steps: List[CommandStep]
    risk_level: RiskLevel
    requires_confirmation: bool
    explanation: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Command':
        """Create Command from LLM JSON output"""
        return cls(
            intent=data.get('intent', 'unknown'),
            steps=[
                CommandStep(
                    action=step['action'],
                    parameters=step.get('parameters', {})
                )
                for step in data.get('steps', [])
            ],
            risk_level=RiskLevel(data.get('risk_level', 'medium')),
            requires_confirmation=data.get('requires_confirmation', True),
            explanation=data.get('explanation', '')
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'intent': self.intent,
            'steps': [
                {
                    'action': step.action,
                    'parameters': step.parameters
                }
                for step in self.steps
            ],
            'risk_level': self.risk_level.value,
            'requires_confirmation': self.requires_confirmation,
            'explanation': self.explanation
        }
    
    def validate(self) -> bool:
        """Validate entire command structure"""
        if not self.intent or not self.steps:
            return False
        return all(step.validate() for step in self.steps)


# What parameters each action needs
ACTION_SCHEMAS = {
    ActionType.OPEN_APP: {
        "required": ["app_name"],
        "optional": ["args"]
    },
    ActionType.CLOSE_APP: {
        "required": ["app_name"],
        "optional": []
    },
    ActionType.OPEN_FILE: {
        "required": ["file_path"],
        "optional": []
    },
    ActionType.OPEN_URL: {
        "required": ["url"],
        "optional": []
    },
    ActionType.CREATE_FILE: {
        "required": ["path"],
        "optional": ["content"]
    },
    ActionType.DELETE_FILE: {
        "required": ["path"],
        "optional": []
    },
    ActionType.MOVE_FILE: {
        "required": ["source", "destination"],
        "optional": []
    },
    ActionType.SEARCH_FILES: {
        "required": ["directory", "pattern"],
        "optional": []
    },
    ActionType.SEND_EMAIL: {
        "required": ["to", "subject", "body"],
        "optional": ["cc", "bcc", "attachments"]
    },
    ActionType.RUN_COMMAND: {
        "required": ["command"],
        "optional": ["args", "working_dir"]
    }
}