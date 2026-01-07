"""
Command Executor
Executes Command objects by calling appropriate Windows functions
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import time

from llm.command_schema import Command, CommandStep
from executor.functions import get_function, ExecutionResult


@dataclass
class ExecutionReport:
    """Report of command execution"""
    command: Command
    success: bool
    results: List[ExecutionResult]
    duration: float
    errors: List[str]
    
    def __str__(self):
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return f"{status} - {len(self.results)} step(s) executed in {self.duration:.2f}s"


class CommandExecutor:
    """Executes commands safely"""
    
    def __init__(self, dry_run: bool = False, verbose: bool = True):
        """
        Initialize executor
        
        Args:
            dry_run: If True, only preview commands without executing
            verbose: Print execution details
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.execution_history: List[ExecutionReport] = []
    
    def execute(self, command: Command) -> ExecutionReport:
        """
        Execute a command
        
        Args:
            command: Command object to execute
        
        Returns:
            ExecutionReport with results
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🚀 EXECUTING COMMAND: {command.intent}")
            print(f"{'='*60}")
            print(f"📋 Steps: {len(command.steps)}")
            print(f"⚠️  Risk Level: {command.risk_level.value}")
            print(f"ℹ️  {command.explanation}")
        
        if self.dry_run:
            return self._dry_run_preview(command)
        
        # Execute for real
        start_time = time.time()
        results = []
        errors = []
        
        for i, step in enumerate(command.steps, 1):
            if self.verbose:
                print(f"\n📍 Step {i}/{len(command.steps)}: {step.action}")
            
            try:
                result = self._execute_step(step)
                results.append(result)
                
                if self.verbose:
                    print(f"   {result}")
                
                if not result.success:
                    errors.append(f"Step {i} failed: {result.message}")
                    
                    # Stop on failure
                    if self.verbose:
                        print(f"\n⚠️  Stopping execution due to error")
                    break
                    
            except Exception as e:
                error_msg = f"Step {i} error: {str(e)}"
                errors.append(error_msg)
                
                if self.verbose:
                    print(f"   ❌ {error_msg}")
                
                results.append(ExecutionResult(
                    success=False,
                    message=error_msg
                ))
                break
        
        duration = time.time() - start_time
        success = len(errors) == 0 and all(r.success for r in results)
        
        report = ExecutionReport(
            command=command,
            success=success,
            results=results,
            duration=duration,
            errors=errors
        )
        
        self.execution_history.append(report)
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"{report}")
            print(f"{'='*60}")
        
        return report
    
    def _execute_step(self, step: CommandStep) -> ExecutionResult:
        """
        Execute a single command step
        
        Args:
            step: CommandStep to execute
        
        Returns:
            ExecutionResult
        """
        # Get the function to call
        func = get_function(step.action)
        
        if not func:
            return ExecutionResult(
                success=False,
                message=f"Unknown action: {step.action}"
            )
        
        # Call function with parameters
        try:
            return func(**step.parameters)
        except TypeError as e:
            return ExecutionResult(
                success=False,
                message=f"Invalid parameters for {step.action}: {str(e)}"
            )
    
    def _dry_run_preview(self, command: Command) -> ExecutionReport:
        """
        Preview command without executing
        
        Args:
            command: Command to preview
        
        Returns:
            ExecutionReport with preview
        """
        print(f"\n{'='*60}")
        print(f"🔍 DRY RUN PREVIEW (Not Executing)")
        print(f"{'='*60}")
        print(f"📋 Intent: {command.intent}")
        print(f"⚠️  Risk Level: {command.risk_level.value}")
        print(f"ℹ️  {command.explanation}")
        print(f"\n📝 Steps to be executed:")
        
        results = []
        for i, step in enumerate(command.steps, 1):
            print(f"\n  {i}. {step.action.upper()}")
            for key, value in step.parameters.items():
                print(f"     • {key}: {value}")
            
            # Create dummy result
            results.append(ExecutionResult(
                success=True,
                message=f"[DRY RUN] Would execute: {step.action}",
                data=step.parameters
            ))
        
        print(f"\n{'='*60}")
        print(f"✅ Preview complete - No actions taken")
        print(f"{'='*60}")
        
        return ExecutionReport(
            command=command,
            success=True,
            results=results,
            duration=0.0,
            errors=[]
        )
    
    def get_history(self) -> List[ExecutionReport]:
        """Get execution history"""
        return self.execution_history
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()
    
    def set_dry_run(self, enabled: bool):
        """Enable or disable dry-run mode"""
        self.dry_run = enabled
        if self.verbose:
            mode = "ENABLED" if enabled else "DISABLED"
            print(f"🔍 Dry-run mode {mode}")
    
    def set_verbose(self, enabled: bool):
        """Enable or disable verbose output"""
        self.verbose = enabled


# Convenience function for quick testing
def quick_execute(command: Command, dry_run: bool = False) -> ExecutionReport:
    """
    Quick way to execute a command
    
    Args:
        command: Command to execute
        dry_run: Preview only
    
    Returns:
        ExecutionReport
    """
    executor = CommandExecutor(dry_run=dry_run)
    return executor.execute(command)