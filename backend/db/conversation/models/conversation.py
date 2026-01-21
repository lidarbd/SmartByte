"""
Conversation Models

Contains all models related to customer conversations:
- ChatSession: A complete conversation with a customer
- ChatMessage: Individual messages within a conversation
- Recommendation: Product recommendations made during conversations
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class ChatSession(Base):
    """
    Represents a complete conversation with a customer.
    Every time a customer starts chatting, we create a new session.
    
    Attributes:
        id: Internal database ID
        session_id: External ID (what the frontend stores in localStorage)
        customer_type: Identified customer type (Student, Engineer, Gamer, Other)
        started_at: When the conversation began
        ended_at: When the conversation ended (NULL if still active)
        messages: All messages in this session (relationship)
        recommendations: All recommendations given in this session (relationship)
    """
    __tablename__ = 'chat_sessions'
    
    # Internal database ID
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # External session ID - unique and indexed for fast lookups
    # This is what the frontend sends in every request
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Customer type identified during conversation
    customer_type = Column(String(50), nullable=True)
    
    # Timestamps for session lifecycle
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships to other tables
    # back_populates creates a two-way relationship
    # cascade="all, delete-orphan" means: if we delete a session, delete all its messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', customer_type='{self.customer_type}')>"


class ChatMessage(Base):
    """
    Represents a single message in a conversation.
    Can be from the user or from the AI assistant.
    
    Attributes:
        id: Unique message ID
        session_id: Which session this message belongs to (foreign key)
        role: Who sent the message - "user" or "assistant"
        content: The actual message text
        timestamp: When the message was sent
        session: Reference back to the parent session (relationship)
    """
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key linking to chat_sessions table
    # Indexed because we'll frequently query "all messages for session X"
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False, index=True)
    
    # Role - either "user" or "assistant"
    role = Column(String(20), nullable=False)
    
    # Message content - can be long, so we use Text
    content = Column(Text, nullable=False)
    
    # Timestamp with index for chronological sorting
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship back to the session
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        """
        Show only first 30 characters of content to keep output readable
        """
        return f"<ChatMessage(id={self.id}, role='{self.role}', content='{self.content[:30]}...')>"


class Recommendation(Base):
    """
    Represents a product recommendation given to a customer.
    Includes both the main recommended product and an optional upsell product.
    
    Attributes:
        id: Unique recommendation ID
        session_id: Which session this recommendation was made in
        product_id: The main product that was recommended
        upsell_product_id: An additional product for upselling (optional)
        recommendation_text: The full recommendation text from the LLM
        created_at: When the recommendation was made
        product: Reference to the main Product object (relationship)
        upsell_product: Reference to the upsell Product object (relationship)
        session: Reference back to the ChatSession (relationship)
    """
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to the session where this recommendation was made
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False, index=True)
    
    # Foreign key to the main recommended product
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # Foreign key to the upsell product (optional)
    upsell_product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    
    # The full recommendation text generated by the LLM
    recommendation_text = Column(Text, nullable=True)
    
    # Timestamp indexed for analytics (daily recommendations chart)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships to products
    # We specify foreign_keys because there are multiple FKs to products table
    product = relationship("Product", foreign_keys=[product_id])
    upsell_product = relationship("Product", foreign_keys=[upsell_product_id])
    
    # Relationship back to session
    session = relationship("ChatSession", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, product_id={self.product_id}, upsell={self.upsell_product_id})>"