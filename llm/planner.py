"""
LLM Planner Module
Converts voice commands into structured JSON using local Llama 3.1
"""

import json
import os
import re
from typing import Optional, Dict, Any
import ollama

from llm.command_schema import Command, CommandStep
from llm.prompt_templates import get_full_prompt, normalize_app_name


class LLMPlanner:
    """Converts natural language to structured commands using LLM"""
    
    def __init__(
        self, 
        model_name: str = "llama3.2:3b",
        temperature: float = 0.1,
        max_retries: int = 3
    ):
        """
        Initialize the LLM planner
        
        Args:
            model_name: Ollama model to use
            temperature: Lower = more deterministic (0.0-1.0)
            max_retries: How many times to retry on failures
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.username = os.getenv('USERNAME', 'User')
        
        # Verify Ollama is running
        self._check_ollama()
    
    def _check_ollama(self):
        """Check if Ollama is running and model is available"""
        try:
            # Test connection
            result = ollama.list()
            print(f"✅ Ollama connected")
            
            # Extract model names - Ollama returns Pydantic objects
            # Each model has a 'model' attribute (not 'name')
            models = [m.model for m in result.models]
            
            print(f"🔍 Available models: {models}")
            
            if not any(self.model_name in m for m in models):
                print(f"⚠️  Model {self.model_name} not found")
                print(f"📥 Downloading {self.model_name}...")
                ollama.pull(self.model_name)
                print(f"✅ Model downloaded")
            else:
                print(f"✅ Model {self.model_name} available")
                
        except Exception as e:
            raise RuntimeError(
                f"❌ Ollama not running or not accessible: {e}\n"
                f"Please start Ollama with: ollama serve"
            )
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call Ollama API with the prompt (DEBUG VERSION)
        
        Args:
            prompt: Full prompt to send to LLM
            
        Returns:
            Raw LLM response text
        """
        try:
            print("🔍 DEBUG: Calling ollama.generate()...")
            
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'top_p': 0.9,
                    'top_k': 40,
                }
            )
            
            # DEBUG: Show response structure
            print(f"🔍 Response type: {type(response)}")
            
            # Try to extract content
            if isinstance(response, dict):
                print(f"🔍 It's a dict, keys: {list(response.keys())}")
                content = response.get('response', '')
            else:
                print(f"🔍 It's an object, checking attributes...")
                available_attrs = [a for a in dir(response) if not a.startswith('_')]
                print(f"🔍 Available attributes: {available_attrs}")
                
                if hasattr(response, 'response'):
                    content = response.response
                elif hasattr(response, 'content'):
                    content = response.content
                elif hasattr(response, 'text'):
                    content = response.text
                else:
                    raise RuntimeError(f"Cannot find response content. Available: {available_attrs}")
            
            print(f"🔍 Extracted content (first 100 chars): {str(content)[:100]}...")
            return str(content).strip()
                
        except Exception as e:
            print(f"❌ LLM API call failed: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"LLM API call failed: {e}")
    
    def _extract_json(self, llm_response: str) -> str:
        """
        Extract JSON from LLM response (handles extra text)
        
        Args:
            llm_response: Raw response from LLM
            
        Returns:
            Cleaned JSON string
        """
        # Try to find JSON in the response
        # LLM might add extra text like "Here's the JSON:" or markdown
        
        # Remove markdown code blocks
        llm_response = re.sub(r'```json\s*', '', llm_response)
        llm_response = re.sub(r'```\s*', '', llm_response)
        
        # Find JSON object (starts with {, ends with })
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If no JSON found, return original
        return llm_response.strip()
    
    def _normalize_command(self, command_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize app names and paths in the command
        
        Args:
            command_dict: Raw command dictionary from LLM
            
        Returns:
            Normalized command dictionary
        """
        # Normalize app names in steps
        for step in command_dict.get('steps', []):
            if step.get('action') in ['open_app', 'close_app']:
                app_name = step.get('parameters', {}).get('app_name', '')
                if app_name:
                    step['parameters']['app_name'] = normalize_app_name(app_name)
            
            # Replace {username} in paths
            for key, value in step.get('parameters', {}).items():
                if isinstance(value, str) and '{username}' in value:
                    step['parameters'][key] = value.replace('{username}', self.username)
        
        return command_dict
    
    def plan(self, voice_command: str, verbose: bool = False) -> Optional[Command]:
        """
        Convert voice command to structured Command object
        
        Args:
            voice_command: Transcribed voice command from STT
            verbose: Print detailed logs
            
        Returns:
            Command object if successful, None if failed
        """
        if verbose:
            print(f"\n🎙️  Voice command: '{voice_command}'")
        
        # Build the prompt
        full_prompt = get_full_prompt(voice_command, self.username)
        
        if verbose:
            print(f"📝 Prompt length: {len(full_prompt)} chars")
        
        # Try multiple times if needed
        for attempt in range(self.max_retries):
            try:
                if verbose and attempt > 0:
                    print(f"🔄 Retry attempt {attempt + 1}/{self.max_retries}")
                
                # Call LLM
                if verbose:
                    print(f"🤖 Calling LLM ({self.model_name})...")
                
                llm_response = self._call_llm(full_prompt)
                
                if verbose:
                    print(f"📥 LLM response: {llm_response[:200]}...")
                
                # Extract JSON
                json_str = self._extract_json(llm_response)
                
                if verbose:
                    print(f"🔍 Extracted JSON: {json_str[:200]}...")
                
                # Parse JSON
                try:
                    command_dict = json.loads(json_str)
                except json.JSONDecodeError as e:
                    if verbose:
                        print(f"❌ JSON parse error: {e}")
                    continue
                
                # Normalize
                command_dict = self._normalize_command(command_dict)
                
                # Convert to Command object
                command = Command.from_dict(command_dict)
                
                # Validate
                if not command.validate():
                    if verbose:
                        print(f"❌ Command validation failed")
                    continue
                
                if verbose:
                    print(f"✅ Command created successfully!")
                    print(f"   Intent: {command.intent}")
                    print(f"   Steps: {len(command.steps)}")
                    print(f"   Risk: {command.risk_level.value}")
                
                return command
                
            except Exception as e:
                if verbose:
                    print(f"❌ Attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    print(f"❌ All {self.max_retries} attempts failed")
                    return None
        
        return None
    
    def plan_with_details(self, voice_command: str) -> Dict[str, Any]:
        """
        Plan command and return detailed results including raw outputs
        
        Args:
            voice_command: Voice command to process
            
        Returns:
            Dictionary with command, raw_response, and metadata
        """
        full_prompt = get_full_prompt(voice_command, self.username)
        
        try:
            # Call LLM
            llm_response = self._call_llm(full_prompt)
            json_str = self._extract_json(llm_response)
            
            # Parse and normalize
            command_dict = json.loads(json_str)
            command_dict = self._normalize_command(command_dict)
            
            # Create command
            command = Command.from_dict(command_dict)
            
            return {
                'success': True,
                'command': command,
                'raw_response': llm_response,
                'json_str': json_str,
                'is_valid': command.validate(),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'command': None,
                'raw_response': llm_response if 'llm_response' in locals() else None,
                'json_str': None,
                'is_valid': False,
                'error': str(e)
            }


# Convenience function for quick testing
def quick_plan(voice_command: str, verbose: bool = True) -> Optional[Command]:
    """
    Quick way to test planning without creating planner instance
    
    Args:
        voice_command: Command to plan
        verbose: Show detailed output
        
    Returns:
        Command object or None
    """
    planner = LLMPlanner()
    return planner.plan(voice_command, verbose=verbose)