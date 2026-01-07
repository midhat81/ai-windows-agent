"""
Windows Command Execution Functions
Core functions that perform actual Windows operations
"""

import os
import subprocess
import webbrowser
import psutil
import pathlib
import glob
from typing import List, Dict, Any, Optional
import shutil


class ExecutionResult:
    """Result of a command execution"""
    def __init__(self, success: bool, message: str, data: Any = None):
        self.success = success
        self.message = message
        self.data = data
    
    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.message}"


# ============================================
# APPLICATION MANAGEMENT
# ============================================

def open_app(app_name: str, args: Optional[str] = None) -> ExecutionResult:
    """
    Open an application
    
    Args:
        app_name: Name of application (e.g., 'chrome', 'notepad')
        args: Optional command-line arguments
    
    Returns:
        ExecutionResult with success status
    """
    try:
        # Common application paths
        app_paths = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'msedge': 'msedge.exe',
            'edge': 'msedge.exe',
            'notepad': 'notepad.exe',
            'notepad++': 'notepad++.exe',
            'code': 'code.cmd',  # VS Code
            'vscode': 'code.cmd',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'winword': 'WINWORD.EXE',  # Word
            'excel': 'EXCEL.EXE',
            'outlook': 'OUTLOOK.EXE',
            'teams': 'Teams.exe',
            'discord': 'Discord.exe',
            'slack': 'slack.exe',
            'spotify': 'Spotify.exe',
            'vlc': 'vlc.exe',
        }
        
        # Get executable path
        exe_path = app_paths.get(app_name.lower(), f"{app_name}.exe")
        
        # Build command
        cmd = [exe_path]
        if args:
            cmd.append(args)
        
        # Start process
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        
        return ExecutionResult(
            success=True,
            message=f"Opened {app_name}",
            data={'app': app_name, 'args': args}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to open {app_name}: {str(e)}"
        )


def close_app(app_name: str) -> ExecutionResult:
    """
    Close an application by name
    
    Args:
        app_name: Name of application to close
    
    Returns:
        ExecutionResult with success status
    """
    try:
        # Map common names to process names
        process_names = {
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'msedge': 'msedge.exe',
            'notepad': 'notepad.exe',
            'code': 'Code.exe',
            'vscode': 'Code.exe',
            'explorer': 'explorer.exe',
        }
        
        process_name = process_names.get(app_name.lower(), f"{app_name}.exe")
        
        # Find and kill processes
        killed = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed > 0:
            return ExecutionResult(
                success=True,
                message=f"Closed {killed} instance(s) of {app_name}",
                data={'app': app_name, 'instances': killed}
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"{app_name} is not running"
            )
            
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to close {app_name}: {str(e)}"
        )


# ============================================
# FILE OPERATIONS
# ============================================

def open_file(file_path: str) -> ExecutionResult:
    """
    Open a file with default application
    
    Args:
        file_path: Path to file
    
    Returns:
        ExecutionResult with success status
    """
    try:
        file_path = os.path.expandvars(file_path)
        
        if not os.path.exists(file_path):
            return ExecutionResult(
                success=False,
                message=f"File not found: {file_path}"
            )
        
        os.startfile(file_path)
        
        return ExecutionResult(
            success=True,
            message=f"Opened {os.path.basename(file_path)}",
            data={'path': file_path}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to open file: {str(e)}"
        )


def create_file(path: str, content: str = "") -> ExecutionResult:
    """
    Create a new file
    
    Args:
        path: File path
        content: Initial file content
    
    Returns:
        ExecutionResult with success status
    """
    try:
        path = os.path.expandvars(path)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return ExecutionResult(
            success=True,
            message=f"Created {os.path.basename(path)}",
            data={'path': path, 'size': len(content)}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to create file: {str(e)}"
        )


def delete_file(path: str) -> ExecutionResult:
    """
    Delete a file
    
    Args:
        path: File path
    
    Returns:
        ExecutionResult with success status
    """
    try:
        path = os.path.expandvars(path)
        
        if not os.path.exists(path):
            return ExecutionResult(
                success=False,
                message=f"File not found: {path}"
            )
        
        os.remove(path)
        
        return ExecutionResult(
            success=True,
            message=f"Deleted {os.path.basename(path)}",
            data={'path': path}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to delete file: {str(e)}"
        )


def move_file(source: str, destination: str) -> ExecutionResult:
    """
    Move a file to new location
    
    Args:
        source: Source file path
        destination: Destination path
    
    Returns:
        ExecutionResult with success status
    """
    try:
        source = os.path.expandvars(source)
        destination = os.path.expandvars(destination)
        
        if not os.path.exists(source):
            return ExecutionResult(
                success=False,
                message=f"Source file not found: {source}"
            )
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        shutil.move(source, destination)
        
        return ExecutionResult(
            success=True,
            message=f"Moved {os.path.basename(source)} to {destination}",
            data={'source': source, 'destination': destination}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to move file: {str(e)}"
        )


def search_files(directory: str, pattern: str) -> ExecutionResult:
    """
    Search for files matching pattern
    
    Args:
        directory: Directory to search
        pattern: File pattern (e.g., '*.txt', '*.pdf')
    
    Returns:
        ExecutionResult with list of matching files
    """
    try:
        directory = os.path.expandvars(directory)
        
        if not os.path.exists(directory):
            return ExecutionResult(
                success=False,
                message=f"Directory not found: {directory}"
            )
        
        # Search for files
        search_path = os.path.join(directory, pattern)
        files = glob.glob(search_path, recursive=False)
        
        return ExecutionResult(
            success=True,
            message=f"Found {len(files)} file(s) matching '{pattern}'",
            data={'files': files, 'count': len(files)}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to search files: {str(e)}"
        )


# ============================================
# WEB OPERATIONS
# ============================================

def open_url(url: str) -> ExecutionResult:
    """
    Open URL in default browser
    
    Args:
        url: URL to open
    
    Returns:
        ExecutionResult with success status
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        webbrowser.open(url)
        
        return ExecutionResult(
            success=True,
            message=f"Opened {url}",
            data={'url': url}
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to open URL: {str(e)}"
        )


# ============================================
# EMAIL (Placeholder - will implement later)
# ============================================

def send_email(to: str, subject: str, body: str, **kwargs) -> ExecutionResult:
    """
    Send email (placeholder for future implementation)
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        **kwargs: Additional options (cc, bcc, attachments)
    
    Returns:
        ExecutionResult with success status
    """
    # TODO: Implement actual email sending (Day 8)
    return ExecutionResult(
        success=False,
        message="Email functionality not yet implemented (coming in Week 2)"
    )


# ============================================
# SYSTEM COMMANDS
# ============================================

def run_command(command: str, args: Optional[str] = None, working_dir: Optional[str] = None) -> ExecutionResult:
    """
    Execute a system command (DANGEROUS - use with caution)
    
    Args:
        command: Command to execute
        args: Command arguments
        working_dir: Working directory
    
    Returns:
        ExecutionResult with command output
    """
    try:
        # Build full command
        full_cmd = command
        if args:
            full_cmd = f"{command} {args}"
        
        # Execute
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=30
        )
        
        return ExecutionResult(
            success=result.returncode == 0,
            message=f"Command executed: {command}",
            data={
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        )
        
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            message=f"Command timed out: {command}"
        )
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Failed to execute command: {str(e)}"
        )


# ============================================
# FUNCTION REGISTRY
# ============================================

# Map action names to functions
FUNCTION_REGISTRY = {
    'open_app': open_app,
    'close_app': close_app,
    'open_file': open_file,
    'open_url': open_url,
    'create_file': create_file,
    'delete_file': delete_file,
    'move_file': move_file,
    'search_files': search_files,
    'send_email': send_email,
    'run_command': run_command,
}


def get_function(action_name: str):
    """Get function by action name"""
    return FUNCTION_REGISTRY.get(action_name)