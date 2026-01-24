"""
Recommendation Service

Main orchestrator for generating product recommendations with natural conversation flow.

Key improvements over previous version:
1. Uses ConversationFlowManager for better conversation guidance
2. More sophisticated handling of incomplete information
3. Better off-topic detection and redirection
4. Stronger guardrails against inventing information
5. Natural progression through conversation stages
"""

import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from db.conversation.models import Product, ChatSession
from db.conversation.repositories import (
    ProductRepository,
    ChatSessionRepository,
    ChatMessageRepository,
    RecommendationRepository
)
from llm import get_llm_provider, LLMProviderError

from .customer_identifier import CustomerIdentifier, CustomerType
from .product_matcher import ProductMatcher
from .upsell_selector import UpsellSelector
from .conversation_flow_manager import ConversationFlowManager, ConversationStage
from .exceptions import RecommendationError


class RecommendationService:
    """
    Main service for generating product recommendations with natural conversation flow.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.session_repo = ChatSessionRepository(db)
        self.message_repo = ChatMessageRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        
        # Initialize service components
        self.customer_identifier = CustomerIdentifier()
        self.product_matcher = ProductMatcher(db)
        self.upsell_selector = UpsellSelector(db)
        self.flow_manager = ConversationFlowManager()
        
        # Get LLM provider
        try:
            self.llm = get_llm_provider()
        except Exception as e:
            raise RecommendationError(f"Failed to initialize LLM: {str(e)}")
    
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate appropriate response.
        
        This is the main entry point that orchestrates the entire conversation flow.
        
        The key difference from the previous version: we now use ConversationFlowManager
        to understand where we are in the conversation and what to do next.
        
        Args:
            session_id: Unique session identifier
            user_message: User's message
        
        Returns:
            Dictionary with response structure matching API requirements
        """
        try:
            # Step 1: Get or create session
            session = self._get_or_create_session(session_id)
            
            # Step 2: Save user message
            self.message_repo.create_message(
                session_id=session.id,
                role='user',
                content=user_message
            )
            
            # Step 3: Get conversation history
            history = self._get_conversation_history(session.id)
            
            # Step 4: Analyze conversation state using flow manager
            # This is the key improvement - we understand where we are in the conversation
            conversation_state = self.flow_manager.analyze_conversation_state(
                current_message=user_message,
                conversation_history=history,
                identified_customer_type=session.customer_type
            )
            
            # Step 5: Handle based on conversation state
            if conversation_state['redirect_needed']:
                # Off-topic conversation - redirect politely
                response = self._handle_off_topic(user_message)
                return self._save_and_return_response(
                    session=session,
                    response=response,
                    customer_type=session.customer_type or "Other",
                    products=[],
                    upsell=None
                )
            
            # Step 6: Identify or update customer type
            customer_type_result = self.customer_identifier.identify_from_conversation(
                current_message=user_message,
                conversation_history=[msg['content'] for msg in history if msg['role'] == 'user']
            )
            customer_type, requirements, clarifying_question_from_identifier = customer_type_result
            
            # Update session with customer type if changed
            if session.customer_type != customer_type.value:
                self.session_repo.update_customer_type(session_id, customer_type.value)
            
            # Step 7: Check if we need to ask clarifying questions
            if conversation_state['needs_clarification']:
                # We don't have enough information yet - ask questions
                response = self._generate_clarifying_response(
                    conversation_state=conversation_state,
                    customer_type=customer_type,
                    user_message=user_message,
                    history=history
                )
                
                return self._save_and_return_response(
                    session=session,
                    response=response,
                    customer_type=customer_type.value,
                    products=[],
                    upsell=None
                )
            
            # Step 8: We have enough info - find matching products
            extracted_info = conversation_state['extracted_info']
            
            products = self.product_matcher.find_matching_products(
                customer_type=customer_type.value,
                message=user_message,
                max_budget=extracted_info.get('budget_amount'),
                limit=5
            )
            
            if not products:
                # No matching products - offer alternatives
                response = self._handle_no_products_found(
                    customer_type=customer_type,
                    extracted_info=extracted_info,
                    user_message=user_message
                )
                
                return self._save_and_return_response(
                    session=session,
                    response=response,
                    customer_type=customer_type.value,
                    products=[],
                    upsell=None
                )
            
            # Step 9: Select primary recommendation and upsell
            main_product = products[0]
            upsell_product = self.upsell_selector.select_upsell(
                main_product=main_product,
                customer_type=customer_type.value
            )
            
            # Step 10: Generate recommendation response with strong guardrails
            recommendation_text = self._generate_recommendation_with_guardrails(
                user_message=user_message,
                customer_type=customer_type,
                requirements=requirements,
                products=products[:3],  # Top 3 for context
                main_product=main_product,
                upsell_product=upsell_product,
                history=history
            )
            
            # Step 11: Save recommendation to database
            self.recommendation_repo.create_recommendation(
                session_id=session.id,
                product_id=main_product.id,
                recommendation_text=recommendation_text,
                upsell_product_id=upsell_product.id if upsell_product else None
            )
            
            # Step 12: Return formatted response
            return self._save_and_return_response(
                session=session,
                response=recommendation_text,
                customer_type=customer_type.value,
                products=[main_product],
                upsell=upsell_product
            )
        
        except Exception as e:
            # Log error and return user-friendly message
            print(f"Error in process_message: {str(e)}")
            raise RecommendationError(f"Failed to process message: {str(e)}")
    
    def _handle_off_topic(self, message: str) -> str:
        """
        Handle off-topic conversations with gentle redirection.
        
        The goal is to be polite but firm - we're here to help with computers,
        not other topics.
        """
        return ("I appreciate your message! However, I specialize in helping customers find "
                "the perfect computer or accessory for their needs. "
                "I'd love to help you with that! Are you looking for a laptop, desktop, "
                "or perhaps an accessory today?")
    
    def _generate_clarifying_response(
        self,
        conversation_state: Dict[str, any],
        customer_type: CustomerType,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a response that asks clarifying questions naturally.
        
        This uses the LLM to create natural-sounding questions that guide
        the conversation forward while gathering needed information.
        """
        suggested_question = conversation_state['suggested_question']
        missing_info = conversation_state['missing_info']
        
        # Build system prompt that instructs LLM to ask questions
        system_prompt = f"""You are a friendly and professional computer store sales assistant.

SITUATION: You're helping a customer find the right computer, but you need more information.

CUSTOMER TYPE: {customer_type.value}

MISSING INFORMATION: {', '.join(missing_info)}

YOUR TASK:
1. Acknowledge the customer's message warmly
2. Ask the clarifying question naturally: "{suggested_question}"
3. Keep it conversational and friendly
4. Don't overwhelm them - just ask ONE question
5. Make it feel like a helpful conversation, not an interrogation

EXAMPLE:
User: "I need a computer"
You: "Great! I'd love to help you find the perfect computer. To make sure I recommend the best option for you, what will you mainly use it for? For example: work, studies, gaming, or general home use?"

Remember: Be warm, professional, and helpful. Ask only what you need to know."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history for context
        if history:
            messages.extend(history[-4:])
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.llm.generate_with_context(messages, temperature=0.7, max_tokens=150)
            return response
        except LLMProviderError:
            # Fallback to simple question
            return suggested_question
    
    def _handle_no_products_found(
        self,
        customer_type: CustomerType,
        extracted_info: Dict[str, any],
        user_message: str
    ) -> str:
        """
        Handle case when no products match the requirements.
        
        Important: We never invent products! We honestly say we don't have
        exactly what they want, and offer to help find alternatives.
        """
        budget = extracted_info.get('budget_amount')
        product_type = extracted_info.get('product_type', 'computer')
        
        response = f"Thank you for sharing your requirements! "
        
        if budget:
            response += f"I've checked our current inventory for {product_type}s within {int(budget)} ILS, "
        else:
            response += f"I've checked our current inventory for {product_type}s, "
        
        response += "but unfortunately I don't have any products in stock that exactly match all your requirements at the moment.\n\n"
        
        response += "However, I have a few options:\n"
        response += "1. I can show you similar products that are close to your needs\n"
        response += "2. We could adjust the budget slightly to see more options\n"
        response += "3. We could consider a different product type (laptop vs desktop)\n\n"
        
        response += "What would you prefer?"
        
        return response
    
    def _generate_recommendation_with_guardrails(
        self,
        user_message: str,
        customer_type: CustomerType,
        requirements: Dict[str, any],
        products: List[Product],
        main_product: Product,
        upsell_product: Optional[Product],
        history: List[Dict[str, str]]
    ) -> str:
        """
        Generate recommendation with VERY strong guardrails.
        
        This is the most critical function - it must ensure the LLM:
        1. Only recommends products that exist
        2. Only mentions prices that are real
        3. Only mentions stock that's available
        4. Doesn't invent specifications
        5. Stays on topic
        """
        # Build product context string
        products_context = self._build_strict_product_context(products)
        
        # Build system prompt with extremely strong guardrails
        system_prompt = f"""You are a professional computer store sales assistant helping a {customer_type.value}.

==================== CRITICAL RULES - YOU MUST OBEY ====================
1. ONLY recommend products from the list below
2. ONLY mention the exact prices shown
3. ONLY mention the exact specifications shown
4. NEVER invent product names, prices, or specs
5. If asked about products not in the list, say "not available in stock"
6. Stay focused on computers - redirect other topics politely

AVAILABLE PRODUCTS IN STOCK:
{products_context}

YOUR PRIMARY RECOMMENDATION:
Product: {main_product.display_name}
SKU: {main_product.sku}
Price: {main_product.price} ILS (exactly this price - do not round or change)
Stock: {main_product.stock} units available
Specifications:
{json.dumps(main_product.specs, indent=2, ensure_ascii=False) if main_product.specs else 'Standard specifications'}

SUGGESTED ACCESSORY (optional upsell):
{self._format_upsell_for_prompt(upsell_product) if upsell_product else 'No accessory available'}

CUSTOMER REQUIREMENTS:
{requirements.get('description', 'General use')}

YOUR TASK:
1. Explain why {main_product.name} is perfect for this {customer_type.value}
2. Highlight 2-3 key specs that match their needs
3. State the exact price: {main_product.price} ILS
4. Mention the accessory naturally if available
5. Keep response under 120 words
6. Sound natural and helpful, not robotic

EXAMPLE RESPONSE STYLE:
"Perfect! For {customer_type.value} use, I recommend the {main_product.display_name}. 
It's priced at {main_product.price} ILS and features [spec 1] and [spec 2], which are ideal for [use case].
To complete your setup, I'd suggest adding [accessory] for [benefit]."

REMEMBER: Use ONLY the information provided above. Do not create any information."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history
        if history:
            messages.extend(history[-4:])
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.llm.generate_with_context(
                messages,
                temperature=0.6,  # Lower temperature for more deterministic output
                max_tokens=250
            )
            
            # Post-process to ensure no hallucinations
            response = self._validate_response(response, products, main_product)
            
            return response
        
        except LLMProviderError:
            # Fallback to template-based response (guaranteed accurate)
            return self._generate_template_recommendation(
                main_product=main_product,
                upsell_product=upsell_product,
                customer_type=customer_type,
                requirements=requirements
            )
    
    def _build_strict_product_context(self, products: List[Product]) -> str:
        """Build product context with all details for LLM"""
        lines = []
        for i, p in enumerate(products, 1):
            specs_str = json.dumps(p.specs, ensure_ascii=False) if p.specs else "N/A"
            lines.append(
                f"{i}. {p.sku} - {p.display_name}\n"
                f"   Price: {p.price} ILS | Stock: {p.stock} units\n"
                f"   Specs: {specs_str}"
            )
        return "\n".join(lines)
    
    def _format_upsell_for_prompt(self, product: Product) -> str:
        """Format upsell product for LLM prompt"""
        return (f"{product.display_name}\n"
                f"Price: {product.price} ILS\n"
                f"Stock: {product.stock} units\n"
                f"Category: {product.category}")
    
    def _validate_response(
        self,
        response: str,
        valid_products: List[Product],
        main_product: Product
    ) -> str:
        """
        Validate LLM response to catch any hallucinations.
        
        Check that:
        - Price mentioned matches actual price
        - Product name matches actual name
        - No invented specifications
        """
        # This is a simple validation - you could make it more sophisticated
        # For now, we just ensure the main product price is mentioned correctly
        
        if str(main_product.price) not in response:
            # LLM changed the price - fix it
            response = response.replace(
                re.search(r'\d+(?:,\d{3})*(?:\.\d+)?\s*ILS', response).group(0),
                f"{main_product.price} ILS"
            ) if re.search(r'\d+(?:,\d{3})*(?:\.\d+)?\s*ILS', response) else response
        
        return response
    
    def _generate_template_recommendation(
        self,
        main_product: Product,
        upsell_product: Optional[Product],
        customer_type: CustomerType,
        requirements: Dict[str, any]
    ) -> str:
        """
        Generate a simple, template-based recommendation.
        
        This is used as a fallback when LLM fails. It's less natural
        but guaranteed to be accurate.
        """
        response = f"Based on your needs as a {customer_type.value}, "
        response += f"I recommend the {main_product.display_name} "
        response += f"for {main_product.price} ILS. "
        
        if main_product.specs:
            key_specs = []
            if main_product.specs.get('cpu'):
                key_specs.append(f"{main_product.specs['cpu']} processor")
            if main_product.specs.get('ram_gb'):
                key_specs.append(f"{main_product.specs['ram_gb']}GB RAM")
            if main_product.specs.get('storage_gb'):
                key_specs.append(f"{main_product.specs['storage_gb']}GB storage")
            
            if key_specs:
                response += f"It features {', '.join(key_specs)}, which provides {requirements.get('description', 'excellent performance')}. "
        
        if upsell_product:
            response += f"\n\nTo complete your setup, I'd recommend adding the {upsell_product.name} "
            response += f"({upsell_product.price} ILS). It's a great complement to your new computer!"
        
        return response
    
    def _get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            session = self.session_repo.create_session(session_id)
        return session
    
    def _get_conversation_history(self, internal_session_id: int) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM"""
        messages = self.message_repo.get_session_messages(internal_session_id)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def _save_and_return_response(
        self,
        session: ChatSession,
        response: str,
        customer_type: str,
        products: List[Product],
        upsell: Optional[Product]
    ) -> Dict[str, Any]:
        """
        Save assistant message and return formatted response.
        
        This ensures consistency in how we return data to the API layer.
        """
        # Save assistant message
        self.message_repo.create_message(
            session_id=session.id,
            role='assistant',
            content=response
        )
        
        # Format response
        return {
            "assistant_message": response,
            "customer_type": customer_type,
            "recommended_items": [p.to_dict() for p in products],
            "upsell_item": upsell.to_dict() if upsell else None
        }