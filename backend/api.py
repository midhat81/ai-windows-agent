"""
FastAPI Backend for AI Windows Agent
Provides REST and WebSocket endpoints for frontend communication
"""

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime

# Import our modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.planner import LLMPlanner
from executor.executor import CommandExecutor
from llm.command_schema import Command


# ============================================
# Pydantic Models (API Request/Response)
# ============================================

class VoiceCommandRequest(BaseModel):
    """Request model for voice command processing"""
    command: str
    dry_run: bool = False
    
class CommandResponse(BaseModel):
    """Response model for command execution"""
    success: bool
    command: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    llm_available: bool
    executor_ready: bool
    timestamp: str


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="AI Windows Agent API",
    description="Voice-controlled Windows automation with local LLM",
    version="1.0.0"
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Global State
# ============================================

class AppState:
    """Global application state"""
    def __init__(self):
        self.planner: Optional[LLMPlanner] = None
        self.executor: Optional[CommandExecutor] = None
        self.command_history: List[Dict] = []
        self.active_websockets: List[WebSocket] = []
        
    def initialize(self):
        """Initialize LLM and executor"""
        try:
            self.planner = LLMPlanner()
            self.executor = CommandExecutor(dry_run=False)
            print("✅ Backend initialized: LLM and Executor ready")
        except Exception as e:
            print(f"❌ Backend initialization failed: {e}")
            raise

state = AppState()


# ============================================
# Startup/Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize backend on startup"""
    print("🚀 Starting AI Windows Agent Backend...")
    try:
        state.initialize()
        print("✅ Backend ready!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down backend...")
    # Close all websocket connections
    for ws in state.active_websockets:
        await ws.close()


# ============================================
# REST Endpoints
# ============================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="running",
        llm_available=state.planner is not None,
        executor_ready=state.executor is not None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy" if state.planner and state.executor else "degraded",
        llm_available=state.planner is not None,
        executor_ready=state.executor is not None,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/command", response_model=CommandResponse)
async def process_command(request: VoiceCommandRequest):
    """
    Process a voice command
    
    Args:
        request: VoiceCommandRequest with command text
        
    Returns:
        CommandResponse with execution results
    """
    try:
        print(f"\n📥 Received command: '{request.command}'")
        
        # Plan command using LLM
        command = state.planner.plan(request.command)
        
        if not command:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse command"
            )
        
        print(f"✅ Planned: {command.intent}")
        
        # Execute command
        if request.dry_run:
            # Create dry-run executor
            executor = CommandExecutor(dry_run=True)
            result = executor.execute(command)
        else:
            result = state.executor.execute(command)
        
        # Store in history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": request.command,
            "intent": command.intent,
            "success": result.success,
            "dry_run": request.dry_run
        }
        state.command_history.append(history_entry)
        
        # Broadcast to websocket clients
        await broadcast_to_websockets({
            "type": "command_executed",
            "data": history_entry
        })
        
        return CommandResponse(
            success=result.success,
            command=command.to_dict(),
            result=result.__dict__,
            error=None if result.success else result.message,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error processing command: {e}")
        return CommandResponse(
            success=False,
            command=None,
            result=None,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/history")
async def get_history(limit: int = 50):
    """
    Get command execution history
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of recent commands
    """
    return {
        "history": state.command_history[-limit:],
        "total": len(state.command_history)
    }

@app.delete("/api/history")
async def clear_history():
    """Clear command history"""
    state.command_history.clear()
    return {"message": "History cleared", "success": True}


# ============================================
# WebSocket Endpoint (Real-time updates)
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time command updates
    
    Frontend can connect to receive live updates
    """
    await websocket.accept()
    state.active_websockets.append(websocket)
    
    print(f"✅ WebSocket connected (Total: {len(state.active_websockets)})")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to AI Windows Agent",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "command":
                # Execute command via websocket
                command_text = message.get("command")
                
                try:
                    command = state.planner.plan(command_text)
                    result = state.executor.execute(command)
                    
                    await websocket.send_json({
                        "type": "command_result",
                        "success": result.success,
                        "command": command.to_dict(),
                        "result": result.__dict__,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
    except WebSocketDisconnect:
        state.active_websockets.remove(websocket)
        print(f"❌ WebSocket disconnected (Remaining: {len(state.active_websockets)})")
    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        state.active_websockets.remove(websocket)


async def broadcast_to_websockets(message: Dict):
    """Broadcast message to all connected websocket clients"""
    for websocket in state.active_websockets:
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Failed to send to websocket: {e}")


# ============================================
# Additional Endpoints
# ============================================

@app.get("/api/capabilities")
async def get_capabilities():
    """Get list of available commands/actions"""
    from llm.command_schema import ActionType
    
    actions = [action.value for action in ActionType]
    
    return {
        "actions": actions,
        "examples": [
            "Open Chrome",
            "Create a file called notes.txt",
            "Search for PDFs in Documents",
            "Open Chrome and search for Python tutorials"
        ]
    }

@app.post("/api/dry-run")
async def dry_run_command(request: VoiceCommandRequest):
    """
    Preview a command without executing it
    
    Same as /api/command but always in dry-run mode
    """
    request.dry_run = True
    return await process_command(request)


# ============================================
# Run Server (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 AI Windows Agent Backend")
    print("="*60)
    print("📡 Starting server on http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )