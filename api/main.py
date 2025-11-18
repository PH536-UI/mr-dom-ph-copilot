from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from ..agents.main_agno_agent import run_main_agno_agent
from ..integrations.memori_integration import get_memori_manager, initialize_memori

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mr. DOM PH Copilot API",
    description="API para orquestração de agentes LangChain/LangGraph com memória persistente via Memori.",
    version="0.2.0"
)

# Initialize Memori on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Memori when the API starts."""
    memori_manager = initialize_memori(conscious_ingest=True, enable_logging=True)
    logger.info("✅ Memori initialized on API startup")
    logger.info(f"Memory Status: {memori_manager.get_memory_status()}")


# Request/Response Models
class MessageRequest(BaseModel):
    """Request model for message processing."""
    message: str
    user_id: str = "default_user"
    context: Optional[Dict[str, Any]] = None
    enable_memory: bool = True


class MessageResponse(BaseModel):
    """Response model for message processing."""
    status: str
    user_id: str
    input_message: str
    agent_response: str
    agent_used: str
    memory_enabled: bool
    conversation_id: Optional[str] = None


class MemoryStatusResponse(BaseModel):
    """Response model for memory status."""
    memori_available: bool
    memory_enabled: bool
    conscious_ingest: bool
    conversation_messages: int
    logging_enabled: bool


class ConversationSummaryResponse(BaseModel):
    """Response model for conversation summary."""
    total_messages: int
    memory_enabled: bool
    user_messages: int
    assistant_messages: int
    conversation_start: Optional[str]
    conversation_end: Optional[str]


# Endpoints
@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint."""
    return {
        "message": "Mr. DOM PH Copilot API está online!",
        "version": "0.2.0",
        "features": ["Agno Framework", "LangGraph", "Memori Memory", "Vtiger CRM", "Mautic Marketing"]
    }


@app.post("/process_message", response_model=MessageResponse, tags=["Messages"])
def process_message(request: MessageRequest):
    """
    Main endpoint to process incoming messages from N8N/Messaging systems.
    
    Orchestrates the appropriate LangChain agent and maintains conversation
    history using Memori for persistent memory and context awareness.
    
    Args:
        request (MessageRequest): The incoming message request
    
    Returns:
        MessageResponse: The agent's response with memory status
    """
    try:
        memori_manager = get_memori_manager()
        
        # Add context to memory if provided
        if request.context:
            memori_manager.add_to_memory("system", f"Context: {str(request.context)}", metadata=request.context)
        
        # Add user message to memory
        if request.enable_memory:
            memori_manager.add_to_memory("user", request.message, metadata={"user_id": request.user_id})
        
        # Process message through Agno Agent
        agent_response = run_main_agno_agent(request.message)
        
        # Add agent response to memory
        if request.enable_memory:
            memori_manager.add_to_memory("assistant", agent_response, metadata={"agent": "Agno Main Agent"})
        
        return MessageResponse(
            status="success",
            user_id=request.user_id,
            input_message=request.message,
            agent_response=agent_response,
            agent_used="Agno Main Agent (via LangGraph + Memori)",
            memory_enabled=request.enable_memory,
            conversation_id=f"{request.user_id}_{len(memori_manager.conversation_history)}"
        )
    
    except Exception as e:
        logger.error(f"❌ Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/memory/status", response_model=MemoryStatusResponse, tags=["Memory"])
def get_memory_status():
    """
    Get the current status of the Memori system.
    
    Returns:
        MemoryStatusResponse: The current memory system status
    """
    try:
        memori_manager = get_memori_manager()
        return MemoryStatusResponse(**memori_manager.get_memory_status())
    except Exception as e:
        logger.error(f"❌ Error getting memory status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting memory status: {str(e)}")


@app.get("/memory/conversation", response_model=ConversationSummaryResponse, tags=["Memory"])
def get_conversation_summary():
    """
    Get a summary of the current conversation.
    
    Returns:
        ConversationSummaryResponse: Summary of the conversation
    """
    try:
        memori_manager = get_memori_manager()
        summary = memori_manager.get_conversation_summary()
        return ConversationSummaryResponse(
            total_messages=summary["total_messages"],
            memory_enabled=summary["memory_enabled"],
            user_messages=summary["user_messages"],
            assistant_messages=summary["assistant_messages"],
            conversation_start=summary["conversation_start"],
            conversation_end=summary["conversation_end"]
        )
    except Exception as e:
        logger.error(f"❌ Error getting conversation summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation summary: {str(e)}")


@app.post("/memory/clear", tags=["Memory"])
def clear_memory():
    """
    Clear the conversation history and memory.
    
    Returns:
        Dict: Confirmation of memory clear operation
    """
    try:
        memori_manager = get_memori_manager()
        memori_manager.clear_memory()
        return {
            "status": "success",
            "message": "Memory cleared successfully"
        }
    except Exception as e:
        logger.error(f"❌ Error clearing memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")


@app.post("/memory/export", tags=["Memory"])
def export_conversation(filepath: str = "conversation_export.json"):
    """
    Export the conversation history to a file.
    
    Args:
        filepath (str): Path to save the conversation
    
    Returns:
        Dict: Confirmation of export operation
    """
    try:
        memori_manager = get_memori_manager()
        memori_manager.export_conversation(filepath)
        return {
            "status": "success",
            "message": f"Conversation exported to {filepath}"
        }
    except Exception as e:
        logger.error(f"❌ Error exporting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting conversation: {str(e)}")


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint."""
    memori_manager = get_memori_manager()
    return {
        "status": "healthy",
        "api_version": "0.2.0",
        "memori_status": memori_manager.get_memory_status(),
        "endpoints": {
            "process_message": "/process_message (POST)",
            "memory_status": "/memory/status (GET)",
            "conversation_summary": "/memory/conversation (GET)",
            "clear_memory": "/memory/clear (POST)",
            "export_conversation": "/memory/export (POST)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
