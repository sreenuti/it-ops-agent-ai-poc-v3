"""
Conversation management for maintaining context and history
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class ConversationMessage:
    """Represents a single message in a conversation"""
    
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize conversation message
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            timestamp: Message timestamp (defaults to now)
            metadata: Additional metadata
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        """Create message from dictionary"""
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data.get("timestamp"), str) else data.get("timestamp")
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp,
            metadata=data.get("metadata", {})
        )


class Conversation:
    """Represents a conversation session"""
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize conversation
        
        Args:
            session_id: Unique session identifier (generated if not provided)
            created_at: Creation timestamp (defaults to now)
            metadata: Additional metadata
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
        self.messages: List[ConversationMessage] = []
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to the conversation
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Additional metadata
        """
        message = ConversationMessage(role, content, metadata=metadata)
        self.messages.append(message)
    
    def get_messages(self, limit: Optional[int] = None) -> List[ConversationMessage]:
        """
        Get conversation messages
        
        Args:
            limit: Maximum number of messages to return (None for all)
            
        Returns:
            List of messages
        """
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()
    
    def get_context(self, max_messages: int = 10) -> str:
        """
        Get conversation context as formatted string
        
        Args:
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted context string
        """
        recent_messages = self.get_messages(limit=max_messages)
        context_parts = []
        
        for msg in recent_messages:
            context_parts.append(f"{msg.role.upper()}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create conversation from dictionary"""
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at")
        conv = cls(
            session_id=data["session_id"],
            created_at=created_at,
            metadata=data.get("metadata", {})
        )
        conv.messages = [ConversationMessage.from_dict(msg) for msg in data.get("messages", [])]
        return conv


class ConversationManager:
    """Manages conversation sessions and history"""
    
    def __init__(self):
        """Initialize conversation manager"""
        self.conversations: Dict[str, Conversation] = {}
    
    def create_conversation(self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """
        Create a new conversation session
        
        Args:
            session_id: Optional session ID (generated if not provided)
            metadata: Optional metadata
            
        Returns:
            New conversation instance
        """
        conversation = Conversation(session_id=session_id, metadata=metadata)
        self.conversations[conversation.session_id] = conversation
        return conversation
    
    def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """
        Get conversation by session ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation instance or None if not found
        """
        return self.conversations.get(session_id)
    
    def get_or_create_conversation(self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """
        Get existing conversation or create new one
        
        Args:
            session_id: Optional session ID
            metadata: Optional metadata
            
        Returns:
            Conversation instance
        """
        if session_id and session_id in self.conversations:
            return self.conversations[session_id]
        return self.create_conversation(session_id, metadata)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add message to conversation
        
        Args:
            session_id: Session identifier
            role: Message role
            content: Message content
            metadata: Optional metadata
            
        Returns:
            True if message added, False if session not found
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return False
        
        conversation.add_message(role, content, metadata)
        return True
    
    def get_context(self, session_id: str, max_messages: int = 10) -> Optional[str]:
        """
        Get conversation context
        
        Args:
            session_id: Session identifier
            max_messages: Maximum number of messages to include
            
        Returns:
            Context string or None if session not found
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return None
        
        return conversation.get_context(max_messages)
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear all messages from a conversation
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleared, False if session not found
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return False
        
        conversation.messages = []
        return True
    
    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete a conversation session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if session not found
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False
    
    def list_conversations(self) -> List[str]:
        """
        List all conversation session IDs
        
        Returns:
            List of session IDs
        """
        return list(self.conversations.keys())
    
    def get_conversation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of a conversation
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summary dictionary or None if session not found
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return None
        
        return {
            "session_id": conversation.session_id,
            "created_at": conversation.created_at.isoformat(),
            "message_count": len(conversation.messages),
            "metadata": conversation.metadata
        }

