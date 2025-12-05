"""
Tests for conversation management
"""
import pytest
from datetime import datetime
from src.api.conversation_manager import (
    ConversationMessage,
    Conversation,
    ConversationManager
)


class TestConversationMessage:
    """Test ConversationMessage class"""
    
    def test_message_creation(self):
        """Test basic message creation"""
        msg = ConversationMessage("user", "Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)
        assert msg.metadata == {}
    
    def test_message_with_metadata(self):
        """Test message with metadata"""
        metadata = {"task_type": "password_reset", "user": "john"}
        msg = ConversationMessage("assistant", "Done", metadata=metadata)
        assert msg.metadata == metadata
    
    def test_message_to_dict(self):
        """Test message to_dict conversion"""
        msg = ConversationMessage("user", "Hello", metadata={"key": "value"})
        msg_dict = msg.to_dict()
        
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Hello"
        assert msg_dict["metadata"] == {"key": "value"}
        assert "timestamp" in msg_dict
    
    def test_message_from_dict(self):
        """Test message from_dict creation"""
        msg_dict = {
            "role": "user",
            "content": "Hello",
            "timestamp": "2024-01-01T12:00:00",
            "metadata": {"key": "value"}
        }
        msg = ConversationMessage.from_dict(msg_dict)
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.metadata == {"key": "value"}


class TestConversation:
    """Test Conversation class"""
    
    def test_conversation_creation(self):
        """Test basic conversation creation"""
        conv = Conversation()
        assert conv.session_id is not None
        assert isinstance(conv.created_at, datetime)
        assert len(conv.messages) == 0
    
    def test_conversation_with_session_id(self):
        """Test conversation with custom session ID"""
        conv = Conversation(session_id="test-123")
        assert conv.session_id == "test-123"
    
    def test_add_message(self):
        """Test adding messages to conversation"""
        conv = Conversation()
        conv.add_message("user", "Hello")
        conv.add_message("assistant", "Hi there")
        
        assert len(conv.messages) == 2
        assert conv.messages[0].role == "user"
        assert conv.messages[1].role == "assistant"
    
    def test_get_messages(self):
        """Test getting messages"""
        conv = Conversation()
        conv.add_message("user", "Message 1")
        conv.add_message("user", "Message 2")
        conv.add_message("user", "Message 3")
        
        all_messages = conv.get_messages()
        assert len(all_messages) == 3
        
        limited = conv.get_messages(limit=2)
        assert len(limited) == 2
        assert limited[0].content == "Message 2"
        assert limited[1].content == "Message 3"
    
    def test_get_context(self):
        """Test getting conversation context"""
        conv = Conversation()
        conv.add_message("user", "Hello")
        conv.add_message("assistant", "Hi there")
        conv.add_message("user", "How are you?")
        
        context = conv.get_context()
        assert "USER: Hello" in context
        assert "ASSISTANT: Hi there" in context
        assert "USER: How are you?" in context
    
    def test_get_context_with_limit(self):
        """Test getting context with message limit"""
        conv = Conversation()
        for i in range(5):
            conv.add_message("user", f"Message {i}")
        
        context = conv.get_context(max_messages=2)
        # Should only include last 2 messages
        assert "Message 3" in context
        assert "Message 4" in context
        assert "Message 0" not in context
    
    def test_conversation_to_dict(self):
        """Test conversation to_dict conversion"""
        conv = Conversation(session_id="test-123")
        conv.add_message("user", "Hello")
        
        conv_dict = conv.to_dict()
        assert conv_dict["session_id"] == "test-123"
        assert len(conv_dict["messages"]) == 1
        assert "created_at" in conv_dict
    
    def test_conversation_from_dict(self):
        """Test conversation from_dict creation"""
        conv_dict = {
            "session_id": "test-123",
            "created_at": "2024-01-01T12:00:00",
            "metadata": {"key": "value"},
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2024-01-01T12:00:00", "metadata": {}}
            ]
        }
        conv = Conversation.from_dict(conv_dict)
        
        assert conv.session_id == "test-123"
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"


class TestConversationManager:
    """Test ConversationManager class"""
    
    def test_create_conversation(self):
        """Test creating a new conversation"""
        manager = ConversationManager()
        conv = manager.create_conversation()
        
        assert conv.session_id is not None
        assert conv.session_id in manager.conversations
    
    def test_create_conversation_with_id(self):
        """Test creating conversation with custom ID"""
        manager = ConversationManager()
        conv = manager.create_conversation(session_id="custom-123")
        
        assert conv.session_id == "custom-123"
        assert manager.get_conversation("custom-123") == conv
    
    def test_get_conversation(self):
        """Test getting existing conversation"""
        manager = ConversationManager()
        conv = manager.create_conversation(session_id="test-123")
        
        retrieved = manager.get_conversation("test-123")
        assert retrieved == conv
        
        not_found = manager.get_conversation("nonexistent")
        assert not_found is None
    
    def test_get_or_create_conversation(self):
        """Test get_or_create functionality"""
        manager = ConversationManager()
        
        # Create new
        conv1 = manager.get_or_create_conversation(session_id="test-123")
        assert conv1.session_id == "test-123"
        
        # Get existing
        conv2 = manager.get_or_create_conversation(session_id="test-123")
        assert conv2 == conv1
        
        # Create without ID
        conv3 = manager.get_or_create_conversation()
        assert conv3.session_id is not None
    
    def test_add_message(self):
        """Test adding message to conversation"""
        manager = ConversationManager()
        conv = manager.create_conversation(session_id="test-123")
        
        success = manager.add_message("test-123", "user", "Hello")
        assert success is True
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hello"
        
        # Add to nonexistent session
        success = manager.add_message("nonexistent", "user", "Hello")
        assert success is False
    
    def test_get_context(self):
        """Test getting conversation context"""
        manager = ConversationManager()
        conv = manager.create_conversation(session_id="test-123")
        manager.add_message("test-123", "user", "Hello")
        manager.add_message("test-123", "assistant", "Hi")
        
        context = manager.get_context("test-123")
        assert context is not None
        assert "Hello" in context
        assert "Hi" in context
        
        # Nonexistent session
        context = manager.get_context("nonexistent")
        assert context is None
    
    def test_clear_conversation(self):
        """Test clearing conversation messages"""
        manager = ConversationManager()
        conv = manager.create_conversation(session_id="test-123")
        manager.add_message("test-123", "user", "Hello")
        
        success = manager.clear_conversation("test-123")
        assert success is True
        assert len(conv.messages) == 0
        
        # Nonexistent session
        success = manager.clear_conversation("nonexistent")
        assert success is False
    
    def test_delete_conversation(self):
        """Test deleting conversation"""
        manager = ConversationManager()
        manager.create_conversation(session_id="test-123")
        
        success = manager.delete_conversation("test-123")
        assert success is True
        assert "test-123" not in manager.conversations
        
        # Nonexistent session
        success = manager.delete_conversation("nonexistent")
        assert success is False
    
    def test_list_conversations(self):
        """Test listing all conversations"""
        manager = ConversationManager()
        manager.create_conversation(session_id="test-1")
        manager.create_conversation(session_id="test-2")
        manager.create_conversation(session_id="test-3")
        
        sessions = manager.list_conversations()
        assert len(sessions) == 3
        assert "test-1" in sessions
        assert "test-2" in sessions
        assert "test-3" in sessions
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        manager = ConversationManager()
        conv = manager.create_conversation(session_id="test-123", metadata={"user": "john"})
        manager.add_message("test-123", "user", "Hello")
        manager.add_message("test-123", "assistant", "Hi")
        
        summary = manager.get_conversation_summary("test-123")
        assert summary is not None
        assert summary["session_id"] == "test-123"
        assert summary["message_count"] == 2
        assert summary["metadata"]["user"] == "john"
        
        # Nonexistent session
        summary = manager.get_conversation_summary("nonexistent")
        assert summary is None

