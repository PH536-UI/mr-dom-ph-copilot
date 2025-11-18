"""
Memori Integration Module for Mr. DOM PH Copilot

This module provides integration with Memori SDK to enable persistent memory
and conscious context awareness for the AI agents. It allows the system to
maintain conversation history and provide contextualized responses.

Author: Phpereira
Date: 2025-11-17
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from memori import Memori
    MEMORI_AVAILABLE = True
except ImportError:
    MEMORI_AVAILABLE = False
    logging.warning("Memori SDK not installed. Install with: pip install memorisdk")

from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoriManager:
    """
    Manager class for Memori SDK integration.
    
    This class handles the initialization and management of Memori for
    persistent memory and conscious context awareness in conversations.
    """
    
    def __init__(self, conscious_ingest: bool = True, enable_logging: bool = True):
        """
        Initialize the Memori Manager.
        
        Args:
            conscious_ingest (bool): Enable conscious ingestion of context
            enable_logging (bool): Enable logging of memory operations
        """
        self.conscious_ingest = conscious_ingest
        self.enable_logging = enable_logging
        self.memori = None
        self.client = None
        self.conversation_history = []
        self.memory_enabled = False
        
        if MEMORI_AVAILABLE:
            self._initialize_memori()
        else:
            logger.warning("Memori SDK is not available. Memory features will be disabled.")
    
    def _initialize_memori(self) -> None:
        """Initialize Memori and OpenAI client."""
        try:
            self.memori = Memori(conscious_ingest=self.conscious_ingest)
            self.memori.enable()
            self.client = OpenAI()
            self.memory_enabled = True
            logger.info("✅ Memori SDK initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Memori: {str(e)}")
            self.memory_enabled = False
    
    def add_to_memory(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the memory system.
        
        Args:
            role (str): Role of the speaker (user, assistant, system)
            content (str): Content of the message
            metadata (Optional[Dict]): Additional metadata about the message
        """
        if not self.memory_enabled:
            logger.warning("Memory is not enabled. Cannot add to memory.")
            return
        
        try:
            message_entry = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
            self.conversation_history.append(message_entry)
            
            if self.enable_logging:
                logger.info(f"📝 Added to memory: {role} - {content[:100]}...")
        except Exception as e:
            logger.error(f"❌ Error adding to memory: {str(e)}")
    
    def get_contextualized_response(
        self,
        user_message: str,
        model: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Get a response from OpenAI with Memori context awareness.
        
        Memori automatically provides context from previous conversations,
        allowing the LLM to understand the full context of the interaction.
        
        Args:
            user_message (str): The user's message
            model (str): OpenAI model to use
            system_prompt (Optional[str]): System prompt for the model
            temperature (float): Temperature for response generation
        
        Returns:
            str: The LLM's response with context awareness
        """
        if not self.memory_enabled or not self.client:
            logger.warning("Memori or OpenAI client not available. Using basic response.")
            return "Memory system is not available."
        
        try:
            # Add user message to memory
            self.add_to_memory("user", user_message)
            
            # Build messages for OpenAI
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history for context
            for entry in self.conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": entry["role"],
                    "content": entry["content"]
                })
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to memory
            self.add_to_memory("assistant", assistant_message)
            
            if self.enable_logging:
                logger.info(f"🤖 Response generated: {assistant_message[:100]}...")
            
            return assistant_message
        
        except Exception as e:
            logger.error(f"❌ Error getting contextualized response: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation.
        
        Returns:
            Dict: Summary containing conversation metadata and statistics
        """
        return {
            "total_messages": len(self.conversation_history),
            "memory_enabled": self.memory_enabled,
            "last_message": self.conversation_history[-1] if self.conversation_history else None,
            "conversation_start": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "conversation_end": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
            "user_messages": sum(1 for m in self.conversation_history if m["role"] == "user"),
            "assistant_messages": sum(1 for m in self.conversation_history if m["role"] == "assistant")
        }
    
    def clear_memory(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("🗑️ Memory cleared")
    
    def export_conversation(self, filepath: str) -> None:
        """
        Export conversation history to a file.
        
        Args:
            filepath (str): Path to save the conversation
        """
        try:
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Conversation exported to {filepath}")
        except Exception as e:
            logger.error(f"❌ Error exporting conversation: {str(e)}")
    
    def get_memory_status(self) -> Dict[str, Any]:
        """
        Get the current status of the memory system.
        
        Returns:
            Dict: Status information about Memori
        """
        return {
            "memori_available": MEMORI_AVAILABLE,
            "memory_enabled": self.memory_enabled,
            "conscious_ingest": self.conscious_ingest,
            "conversation_messages": len(self.conversation_history),
            "logging_enabled": self.enable_logging
        }


# Global instance
_memori_manager: Optional[MemoriManager] = None


def get_memori_manager() -> MemoriManager:
    """
    Get or create the global Memori manager instance.
    
    Returns:
        MemoriManager: The global Memori manager instance
    """
    global _memori_manager
    if _memori_manager is None:
        _memori_manager = MemoriManager()
    return _memori_manager


def initialize_memori(conscious_ingest: bool = True, enable_logging: bool = True) -> MemoriManager:
    """
    Initialize the Memori manager with custom settings.
    
    Args:
        conscious_ingest (bool): Enable conscious ingestion
        enable_logging (bool): Enable logging
    
    Returns:
        MemoriManager: The initialized Memori manager
    """
    global _memori_manager
    _memori_manager = MemoriManager(conscious_ingest=conscious_ingest, enable_logging=enable_logging)
    return _memori_manager
