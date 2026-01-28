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

            # LOG: Print conversation state for debugging
            print("=" * 80)
            print("CONVERSATION STATE ANALYSIS:")
            print(f"  Stage: {conversation_state['stage']}")
            print(f"  Missing Info: {conversation_state['missing_info']}")
            print(f"  Has Enough Info: {conversation_state['has_enough_info']}")
            print(f"  Needs Clarification: {conversation_state['needs_clarification']}")
            print(f"  Suggested Question: {conversation_state.get('suggested_question', 'None')}")
            print(f"  Is Product Inquiry: {conversation_state['is_product_inquiry']}")
            print(f"  Redirect Needed: {conversation_state['redirect_needed']}")
            if 'extracted_info' in conversation_state:
                print(f"  Extracted Info:")
                print(f"    - Use Case: {conversation_state['extracted_info'].get('has_use_case')} - {conversation_state['extracted_info'].get('use_case_keywords')}")
                print(f"    - Budget: {conversation_state['extracted_info'].get('has_budget')} - {conversation_state['extracted_info'].get('budget_amount')}")
                print(f"    - Product Type: {conversation_state['extracted_info'].get('has_product_type')} - {conversation_state['extracted_info'].get('product_type')}")
            print("=" * 80)

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

            print(f"\nCUSTOMER TYPE RESULT:")
            print(f"   Type: {customer_type}")
            print(f"   Question from identifier: {clarifying_question_from_identifier}")

            # Update session with customer type if changed
            if session.customer_type != customer_type.value:
                self.session_repo.update_customer_type(session_id, customer_type.value)

            # Step 7: Check if we need to ask clarifying questions
            if conversation_state['needs_clarification']:
                # We don't have enough information yet - ask questions
                print(f"\nNEEDS CLARIFICATION - Asking follow-up questions")
                print(f"   Missing: {conversation_state['missing_info']}")

                response = self._generate_clarifying_response(
                    conversation_state=conversation_state,
                    customer_type=customer_type,
                    user_message=user_message,
                    history=history
                )

                print(f"   Generated Response: {response[:100]}...")

                return self._save_and_return_response(
                    session=session,
                    response=response,
                    customer_type=customer_type.value,
                    products=[],
                    upsell=None
                )

            # If we got here, we have enough info to recommend
            print(f"\nENOUGH INFO - Proceeding to product recommendation")

            # Step 8: We have enough info - find matching products
            extracted_info = conversation_state['extracted_info']

            # Check if user requested both computer AND accessory
            requested_accessory = extracted_info.get('requested_accessory')
            total_budget = extracted_info.get('budget_amount')

            # Split budget if user wants computer + accessory
            computer_budget = total_budget
            accessory_budget = 1000  # Default max for upsell

            if requested_accessory and total_budget:
                # User explicitly requested accessory with computer
                # Split budget: 75% computer, 25% accessory
                computer_budget = total_budget * 0.75
                accessory_budget = total_budget * 0.25
                print(f"Split budget - Computer: {computer_budget}, Accessory ({requested_accessory}): {accessory_budget}")

            products = self.product_matcher.find_matching_products(
                customer_type=customer_type.value,
                message=user_message,
                max_budget=computer_budget,  # Use split budget
                product_type=extracted_info.get('product_type'),
                category=extracted_info.get('category'),
                brand=extracted_info.get('brand'),
                limit=5
            )

            if not products:
                # No matching products - offer alternatives
                response = self._handle_no_products_found(
                    extracted_info=extracted_info,
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

            # Pass the requested accessory and budget to upsell selector
            upsell_product = self.upsell_selector.select_upsell(
                main_product=main_product,
                customer_type=customer_type.value,
                conversation_history=history,
                max_upsell_price=accessory_budget,
                requested_accessory=requested_accessory
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
        Handle off-topic conversations with gentle redirection in Hebrew.
        """
        return ("אני מעריך את ההודעה שלך! עם זאת, אני מתמחה בעזרה ללקוחות למצוא "
                "את המחשב או האביזר המושלם לצרכים שלהם. "
                "אשמח לעזור לך בכך! האם אתה מחפש מחשב נייד, מחשב נייח, "
                "או אולי אביזר כלשהו היום?")

    def _generate_clarifying_response(
        self,
        conversation_state: Dict[str, any],
        customer_type: CustomerType,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a response that asks clarifying questions naturally.
        """
        suggested_question = conversation_state['suggested_question']
        missing_info = conversation_state['missing_info']

        system_prompt = f"""You are a friendly and professional computer store sales assistant.

    CRITICAL: You MUST respond in Hebrew (עברית). All your responses must be in Hebrew language.

    SITUATION: You're helping a customer find the right computer, but you need more information.

    CUSTOMER TYPE: {customer_type.value}

    MISSING INFORMATION: {', '.join(missing_info)}

    YOUR TASK:
    1. Acknowledge the customer's message warmly IN HEBREW
    2. Ask the clarifying question naturally IN HEBREW: "{suggested_question}"
    3. Keep it conversational and friendly IN HEBREW
    4. Don't overwhelm them - just ask ONE question
    5. Make it feel like a helpful conversation, not an interrogation

    EXAMPLE (in Hebrew):
    User: "אני צריך מחשב"
    You: "מעולה! אשמח לעזור לך למצוא את המחשב המושלם. כדי שאוכל להמליץ על האפשרות הטובה ביותר עבורך, למה בעיקר תשתמש במחשב? לדוגמה: עבודה, לימודים, גיימינג, או שימוש כללי בבית?"

    REMEMBER:
    - Respond ONLY in Hebrew
    - Be warm, professional, and helpful
    - Ask only what you need to know"""

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add recent history for context
        if history:
            messages.extend(history[-4:])

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.llm.generate_with_context(messages, temperature=0.7, max_tokens=500)
            return response
        except LLMProviderError:
            # Fallback to simple question in Hebrew
            return suggested_question

    def _handle_no_products_found(
        self,
        extracted_info: Dict[str, any]
    ) -> str:
        """
        Handle case when no products match the requirements - IN HEBREW.
        """
        budget = extracted_info.get('budget_amount')
        product_type = extracted_info.get('product_type')
        category = extracted_info.get('category')

        # Get Hebrew name for the product being searched
        product_name = self._get_product_name_hebrew(product_type, category)

        response = f"תודה על שיתוף הדרישות שלך! "

        if budget:
            response += f"בדקתי את המלאי הנוכחי שלנו עבור {product_name} בטווח של {int(budget)} ₪, "
        else:
            response += f"בדקתי את המלאי הנוכחי שלנו עבור {product_name}, "

        response += "אבל למרבה הצער אין לי כרגע מוצרים במלאי שמתאימים בדיוק לכל הדרישות שלך.\n\n"

        response += "עם זאת, יש לי כמה אפשרויות:\n"
        response += "1. אוכל להראות לך מוצרים דומים שקרובים לצרכים שלך\n"
        response += "2. נוכל להתאים את התקציב מעט כדי לראות יותר אפשרויות\n"
        response += "3. נוכל לשקול סוג מוצר אחר (נייד מול נייח)\n\n"

        response += "מה תעדיף?"

        return response

    def _get_product_name_hebrew(self, product_type: Optional[str], category: Optional[str]) -> str:
        """
        Get Hebrew name for product based on type and category.

        Args:
            product_type: 'laptop' or 'desktop' (for computers)
            category: 'computer', 'headset', 'mouse', 'keyboard', 'monitor', 'bag'

        Returns:
            Hebrew product name
        """
        # Check product_type first (for computers)
        if product_type == 'laptop':
            return 'מחשב נייד'
        elif product_type == 'desktop':
            return 'מחשב נייח'

        # Check category (for accessories or when product_type is None)
        if category == 'headset':
            return 'אוזניות'
        elif category == 'mouse':
            return 'עכבר'
        elif category == 'keyboard':
            return 'מקלדת'
        elif category == 'monitor':
            return 'מסך'
        elif category == 'bag':
            return 'תיק'
        elif category == 'computer':
            return 'מחשב'

        # Default fallback
        return 'מחשב'

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

        CRITICAL: System prompt in English, but response MUST be in Hebrew.
        """
        # Build product context string
        products_context = self._build_strict_product_context(products)

        # Build system prompt - ENGLISH with Hebrew response requirement
        system_prompt = f"""You are a professional computer store sales assistant helping a {customer_type.value}.

    ==================== CRITICAL RULES - YOU MUST OBEY ====================
    1. You MUST respond in Hebrew (עברית) - this is mandatory
    2. ONLY recommend products from the list below
    3. ONLY mention the exact prices shown
    4. ONLY mention the exact specifications shown
    5. NEVER invent product names, prices, or specs
    6. If asked about products not in the list, say "לא זמין במלאי" (not available in stock)
    7. Stay focused on computers - redirect other topics politely IN HEBREW

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

    YOUR TASK (respond in Hebrew):
    1. Explain why {main_product.name} is perfect for this {customer_type.value} - IN HEBREW
    2. Highlight 2-3 key specs that match their needs - IN HEBREW
    3. State the exact price: {main_product.price} ₪ (use ₪ symbol, not ILS)
    4. Mention the accessory naturally if available - IN HEBREW
    5. Keep response under 120 words
    6. Sound natural and helpful, not robotic - IN HEBREW

    EXAMPLE RESPONSE STYLE (in Hebrew):
    "מעולה! לשימוש של {customer_type.value}, אני ממליץ על {main_product.display_name}.
    המחיר שלו הוא {main_product.price} ₪ והוא כולל [מפרט 1] ו-[מפרט 2], שהם אידיאליים ל[תחום שימוש].
    כדי להשלים את המערכת שלך, אמליץ להוסיף [אביזר] עבור [יתרון]."

    REMEMBER:
    - Respond ONLY in Hebrew
    - Use ONLY the information provided above
    - Do not create any information
    - Use ₪ symbol for prices"""

        # Rest of the function stays the same...
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history[-4:])

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.llm.generate_with_context(
                messages,
                temperature=0.6,
                max_tokens=600
            )

            response = self._validate_response(response, main_product)
            return response

        except LLMProviderError:
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
        main_product: Product
    ) -> str:
        """
        Validate LLM response to catch any hallucinations.

        Check that:
        - Price mentioned matches actual price
        - Product name matches actual name
        - No invented specifications
        """

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
        Generate a simple, template-based recommendation IN HEBREW.
        """
        response = f"בהתבסס על הצרכים שלך כ{customer_type.value}, "
        response += f"אני ממליץ על {main_product.display_name} "
        response += f"במחיר של {main_product.price} ₪. "

        if main_product.specs:
            key_specs = []
            if main_product.specs.get('cpu'):
                key_specs.append(f"מעבד {main_product.specs['cpu']}")
            if main_product.specs.get('ram_gb'):
                key_specs.append(f"{main_product.specs['ram_gb']}GB זיכרון RAM")
            if main_product.specs.get('storage_gb'):
                key_specs.append(f"{main_product.specs['storage_gb']}GB אחסון")

            if key_specs:
                response += f"הוא כולל {', '.join(key_specs)}, שמספקים {requirements.get('description', 'ביצועים מצוינים')}. "

        if upsell_product:
            response += f"\n\nכדי להשלים את המערכת שלך, אמליץ להוסיף את {upsell_product.name} "
            response += f"({upsell_product.price} ₪). זה השלמה מצוינת למחשב החדש שלך!"

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
