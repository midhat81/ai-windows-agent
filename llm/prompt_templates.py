"""
Prompt Templates for LLM
Teaches the LLM how to convert voice commands into structured JSON
"""

# System prompt - tells LLM its role and rules
SYSTEM_PROMPT = """You are an AI assistant that converts natural language voice commands into structured JSON for a Windows PC automation agent.

Your task:
1. Understand the user's intent from their voice command
2. Break it down into specific, executable actions
3. Output ONLY valid JSON in the exact format specified
4. Assess the risk level of the command
5. Determine if user confirmation is needed

CRITICAL RULES:
- Output ONLY valid JSON, no extra text or explanations outside the JSON
- Use only the allowed actions listed below
- Always include all required fields
- Set appropriate risk levels
- Be conservative with risk assessment (when in doubt, mark as higher risk)

ALLOWED ACTIONS:
1. open_app - Opens an application
   Required: app_name (string)
   Optional: args (string)
   Risk: low
   Example: {"action": "open_app", "parameters": {"app_name": "chrome"}}

2. close_app - Closes an application
   Required: app_name (string)
   Risk: low
   Example: {"action": "close_app", "parameters": {"app_name": "notepad"}}

3. open_file - Opens a file with default application
   Required: file_path (string)
   Risk: low
   Example: {"action": "open_file", "parameters": {"file_path": "C:\\\\Documents\\\\report.pdf"}}

4. open_url - Opens a URL in browser
   Required: url (string)
   Risk: low
   Example: {"action": "open_url", "parameters": {"url": "https://google.com"}}

5. create_file - Creates a new file
   Required: path (string)
   Optional: content (string)
   Risk: medium
   Example: {"action": "create_file", "parameters": {"path": "C:\\\\Documents\\\\notes.txt", "content": "Hello"}}

6. delete_file - Deletes a file (DANGEROUS)
   Required: path (string)
   Risk: high
   Example: {"action": "delete_file", "parameters": {"path": "C:\\\\temp\\\\old.txt"}}

7. move_file - Moves a file to new location
   Required: source (string), destination (string)
   Risk: medium
   Example: {"action": "move_file", "parameters": {"source": "C:\\\\Downloads\\\\file.txt", "destination": "C:\\\\Documents\\\\file.txt"}}

8. search_files - Searches for files
   Required: directory (string), pattern (string)
   Risk: low
   Example: {"action": "search_files", "parameters": {"directory": "C:\\\\Documents", "pattern": "*.pdf"}}

9. send_email - Sends an email
   Required: to (string), subject (string), body (string)
   Optional: cc, bcc, attachments
   Risk: medium
   Example: {"action": "send_email", "parameters": {"to": "user@example.com", "subject": "Test", "body": "Hello"}}

10. run_command - Executes a command line command (VERY DANGEROUS)
    Required: command (string)
    Optional: args, working_dir
    Risk: high
    Example: {"action": "run_command", "parameters": {"command": "dir"}}

RISK LEVELS:
- low: Safe operations (open apps, view files, search)
- medium: Operations that modify system but are recoverable (create files, send emails)
- high: Dangerous operations (delete files, run commands)

OUTPUT FORMAT (you must output valid JSON exactly like this):
{
  "intent": "brief description of what user wants",
  "steps": [
    {
      "action": "action_name",
      "parameters": {
        "param_name": "param_value"
      }
    }
  ],
  "risk_level": "low|medium|high",
  "requires_confirmation": true|false,
  "explanation": "human-readable explanation of what will happen"
}

IMPORTANT:
- For multi-step commands, list steps in execution order
- Use Windows paths with double backslashes (C:\\\\Users\\\\...)
- If command is ambiguous, choose the most likely interpretation
- If command is impossible or unclear, set intent to "error" and explain in explanation field"""

# Few-shot examples to teach the LLM
FEW_SHOT_EXAMPLES = """
EXAMPLE 1:
User: "Open Chrome"
Output:
{
  "intent": "open_application",
  "steps": [
    {
      "action": "open_app",
      "parameters": {
        "app_name": "chrome"
      }
    }
  ],
  "risk_level": "low",
  "requires_confirmation": false,
  "explanation": "Opening Google Chrome browser"
}

EXAMPLE 2:
User: "Create a file called todo.txt in my Documents folder"
Output:
{
  "intent": "create_document",
  "steps": [
    {
      "action": "create_file",
      "parameters": {
        "path": "C:\\\\Users\\\\{username}\\\\Documents\\\\todo.txt",
        "content": ""
      }
    }
  ],
  "risk_level": "medium",
  "requires_confirmation": true,
  "explanation": "Creating a new text file in Documents folder"
}

EXAMPLE 3:
User: "Open Chrome and search for Python tutorials"
Output:
{
  "intent": "web_search",
  "steps": [
    {
      "action": "open_app",
      "parameters": {
        "app_name": "chrome"
      }
    },
    {
      "action": "open_url",
      "parameters": {
        "url": "https://www.google.com/search?q=Python+tutorials"
      }
    }
  ],
  "risk_level": "low",
  "requires_confirmation": false,
  "explanation": "Opening Chrome and performing Google search for Python tutorials"
}

EXAMPLE 4:
User: "Delete old files from Downloads"
Output:
{
  "intent": "error",
  "steps": [],
  "risk_level": "high",
  "requires_confirmation": true,
  "explanation": "Command is too vague. Please specify which files to delete or provide a pattern (e.g., 'delete all .txt files from Downloads')"
}

EXAMPLE 5:
User: "Open Notepad and write Hello World"
Output:
{
  "intent": "create_document_with_content",
  "steps": [
    {
      "action": "open_app",
      "parameters": {
        "app_name": "notepad"
      }
    }
  ],
  "risk_level": "low",
  "requires_confirmation": false,
  "explanation": "Opening Notepad. Note: Cannot automatically type text, user will need to type 'Hello World' manually"
}

EXAMPLE 6:
User: "Find all PDF files in Documents"
Output:
{
  "intent": "search_files",
  "steps": [
    {
      "action": "search_files",
      "parameters": {
        "directory": "C:\\\\Users\\\\{username}\\\\Documents",
        "pattern": "*.pdf"
      }
    }
  ],
  "risk_level": "low",
  "requires_confirmation": false,
  "explanation": "Searching for all PDF files in Documents folder"
}"""

def create_user_prompt(voice_command: str, username: str = "User") -> str:
    """
    Creates the user prompt by inserting the voice command
    
    Args:
        voice_command: The user's voice command transcribed by STT
        username: Windows username (for path substitution)
    
    Returns:
        Formatted prompt ready to send to LLM
    """
    user_prompt = f"""Now convert this voice command to JSON:

User: "{voice_command}"

Remember:
- Output ONLY valid JSON, no other text
- Replace {{username}} with: {username}
- Use Windows paths with double backslashes
- Choose appropriate risk level
- List steps in execution order

Output:"""
    
    return user_prompt

def get_full_prompt(voice_command: str, username: str = "User") -> str:
    """
    Combines system prompt, examples, and user command into complete prompt
    
    Args:
        voice_command: The user's voice command
        username: Windows username
    
    Returns:
        Complete prompt ready for LLM
    """
    return f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}

{create_user_prompt(voice_command, username)}"""

# Common app name mappings (helps LLM understand variations)
APP_NAME_MAPPINGS = {
    # Browsers
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "brave": "brave",
    
    # Text editors
    "notepad": "notepad",
    "note pad": "notepad",
    "notepad++": "notepad++",
    "vs code": "code",
    "visual studio code": "code",
    "vscode": "code",
    "sublime": "sublime_text",
    
    # Office
    "word": "winword",
    "microsoft word": "winword",
    "excel": "excel",
    "microsoft excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    
    # Media
    "vlc": "vlc",
    "spotify": "spotify",
    "windows media player": "wmplayer",
    
    # Communication
    "discord": "discord",
    "slack": "slack",
    "teams": "teams",
    "microsoft teams": "teams",
    "zoom": "zoom",
    
    # Development
    "git bash": "bash",
    "terminal": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    
    # File management
    "explorer": "explorer",
    "file explorer": "explorer",
    "this pc": "explorer",
}

def normalize_app_name(app_name: str) -> str:
    """
    Normalizes application names to their executable names
    
    Args:
        app_name: Application name from voice command
    
    Returns:
        Normalized executable name
    """
    app_name_lower = app_name.lower().strip()
    return APP_NAME_MAPPINGS.get(app_name_lower, app_name_lower)