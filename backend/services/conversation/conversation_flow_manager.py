"""
Conversation Flow Manager

Manages the natural flow of customer conversations.

This is the "brain" that decides:
- What stage of the conversation are we in?
- What information are we still missing?
- What question should we ask next?
- Are we ready to recommend products?

The goal is to make conversations feel natural, not like filling out a form.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum


class ConversationStage(str, Enum):
    """
    Stages in a typical sales conversation.
    
    Each stage represents a point in the customer journey where
    we need different information or take different actions.
    """
    GREETING = "greeting"              # Initial contact, no info yet
    UNDERSTANDING_NEEDS = "understanding_needs"  # Gathering use case info
    CLARIFYING_BUDGET = "clarifying_budget"      # Getting budget constraints
    CLARIFYING_PREFERENCES = "clarifying_preferences"  # Product type, brand, etc.
    READY_TO_RECOMMEND = "ready_to_recommend"    # Have enough info to suggest products
    RECOMMENDATION_GIVEN = "recommendation_given"  # Already recommended, handling follow-up
    OFF_TOPIC = "off_topic"            # Customer is discussing unrelated topics


class ConversationFlowManager:
    """
    Manages conversation flow and determines next steps.
    
    This class is like a conversation director - it knows what information
    we need and guides the conversation toward getting that information naturally.
    """
    
    def __init__(self):
        """Initialize the conversation flow manager"""
        pass
    
    def analyze_conversation_state(
        self,
        current_message: str,
        conversation_history: List[Dict[str, str]],
        identified_customer_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze the current state of the conversation and determine next steps.
        
        This is the main function that decides "what should we do now?"
        
        Args:
            current_message: Latest message from user
            conversation_history: Full conversation so far (list of {"role": "...", "content": "..."})
            identified_customer_type: Customer type if already identified
        
        Returns:
            Dictionary with analysis:
            {
                "stage": ConversationStage enum,
                "missing_info": ["budget", "product_type"],  # What we still need
                "has_enough_info": False,
                "suggested_question": "What's your budget?",
                "is_product_inquiry": True,
                "needs_clarification": True
            }
        
        Example usage:
            flow = ConversationFlowManager()
            state = flow.analyze_conversation_state(
                current_message="I need a computer",
                conversation_history=[],
                identified_customer_type=None
            )
            # Returns: stage=UNDERSTANDING_NEEDS, missing_info=['use_case', 'budget', 'product_type']
        """
        # Extract all user messages
        user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        user_messages.append(current_message)
        all_user_text = " ".join(user_messages).lower()
        
        # Check if this is about products at all
        is_product_inquiry = self._is_product_related(current_message, all_user_text)
        
        if not is_product_inquiry:
            return {
                "stage": ConversationStage.OFF_TOPIC,
                "missing_info": [],
                "has_enough_info": False,
                "suggested_question": None,
                "is_product_inquiry": False,
                "needs_clarification": False,
                "redirect_needed": True
            }
        
        # Extract what information we have
        extracted_info = self._extract_conversation_info(all_user_text)
        
        # Determine what's missing
        missing_info = self._identify_missing_info(extracted_info)
        
        # Determine conversation stage
        stage = self._determine_stage(extracted_info, conversation_history, identified_customer_type)
        
        # Generate appropriate question if needed
        suggested_question = None
        if missing_info:
            suggested_question = self._generate_clarifying_question(missing_info, extracted_info)
        
        # Do we have enough to recommend?
        has_enough = len(missing_info) == 0
        
        return {
            "stage": stage,
            "missing_info": missing_info,
            "has_enough_info": has_enough,
            "suggested_question": suggested_question,
            "is_product_inquiry": is_product_inquiry,
            "needs_clarification": len(missing_info) > 0,
            "extracted_info": extracted_info,
            "redirect_needed": False
        }
    
    def _is_product_related(self, current_message: str, full_context: str) -> bool:
        """
        Check if conversation is about computer products.
        
        Why is this important? We want to catch off-topic conversations early
        and redirect gently before spending time on product matching.
        """
        product_keywords = [
            # Computer related
            'computer', 'laptop', 'desktop', 'pc', 'notebook', 'tower',
            'מחשב', 'לפטופ', 'נייד', 'נייח',
            
            # Purchase related
            'buy', 'purchase', 'need', 'looking for', 'want', 'recommend',
            'קנייה', 'צריך', 'מחפש', 'רוצה', 'המלצה',
            
            # Specs related
            'ram', 'cpu', 'gpu', 'processor', 'graphics', 'storage',
            'זיכרון', 'מעבד', 'כרטיס מסך',
            
            # Use cases
            'gaming', 'work', 'study', 'office', 'development',
            'גיימינג', 'עבודה', 'לימודים', 'משרד', 'פיתוח',
            
            # Price/budget
            'price', 'cost', 'budget', 'cheap', 'expensive',
            'מחיר', 'תקציב', 'זול', 'יקר',
            
            # Accessories
            'mouse', 'keyboard', 'monitor', 'headset', 'bag',
            'עכבר', 'מקלדת', 'מסך', 'אוזניות', 'תיק'
        ]
        
        # Check both current message and full context
        text_to_check = (current_message + " " + full_context).lower()
        
        return any(keyword in text_to_check for keyword in product_keywords)
    
    def _extract_conversation_info(self, text: str) -> Dict[str, any]:
        """
        Extract structured information from conversation text.
        
        This function looks for specific pieces of information that we need
        to make a good recommendation. Think of it as filling out a form,
        but from natural conversation instead of form fields.
        """
        import re
        
        info = {
            'has_use_case': False,
            'use_case_keywords': [],
            'has_budget': False,
            'budget_amount': None,
            'has_product_type': False,
            'product_type': None,
            'has_brand_preference': False,
            'brand': None,
            'has_specific_specs': False,
            'spec_requirements': {}
        }
        
        # Extract use case
        use_case_patterns = {
            'student': ['student', 'university', 'college', 'study', 'homework', 'סטודנט', 'לימודים'],
            'gaming': ['gaming', 'gamer', 'games', 'fps', 'fortnite', 'גיימר', 'משחקים'],
            'work': ['work', 'office', 'business', 'professional', 'עבודה', 'משרד'],
            'development': ['developer', 'programming', 'coding', 'engineer', 'מפתח', 'תכנות', 'מהנדס']
        }
        
        for use_case, keywords in use_case_patterns.items():
            if any(kw in text for kw in keywords):
                info['has_use_case'] = True
                info['use_case_keywords'].append(use_case)
        
        # Extract budget using regex
        # Look for patterns like "5000", "5,000", "around 3000", "budget is 4500"
        budget_patterns = [
            r'budget.*?(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:shekel|nis|ils|שקל)',
            r'up to\s*(\d{1,3}(?:,\d{3})*)',
            r'around\s*(\d{1,3}(?:,\d{3})*)',
            r'maximum\s*(\d{1,3}(?:,\d{3})*)',
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace(',', '')
                try:
                    info['budget_amount'] = float(budget_str)
                    info['has_budget'] = True
                    break
                except ValueError:
                    pass
        
        # If we found numbers but no explicit budget, check if it's a reasonable budget number
        if not info['has_budget']:
            numbers = re.findall(r'\b(\d{4,5})\b', text)  # 4-5 digit numbers
            if numbers:
                # Assume it's a budget if it's in reasonable range (1000-20000 ILS)
                for num in numbers:
                    num_val = int(num)
                    if 1000 <= num_val <= 20000:
                        info['budget_amount'] = float(num_val)
                        info['has_budget'] = True
                        break
        
        # Extract product type preference
        if 'laptop' in text or 'notebook' in text or 'portable' in text or 'נייד' in text:
            info['has_product_type'] = True
            info['product_type'] = 'laptop'
        elif 'desktop' in text or 'tower' in text or 'נייח' in text:
            info['has_product_type'] = True
            info['product_type'] = 'desktop'
        
        # Extract brand preference
        if 'lenovo' in text:
            info['has_brand_preference'] = True
            info['brand'] = 'Lenovo'
        elif 'dell' in text:
            info['has_brand_preference'] = True
            info['brand'] = 'Dell'
        
        # Extract specific specs
        specs = {}
        
        # RAM requirements
        ram_match = re.search(r'(\d+)\s*gb.*?ram|ram.*?(\d+)\s*gb', text, re.IGNORECASE)
        if ram_match:
            ram_val = int(ram_match.group(1) or ram_match.group(2))
            specs['min_ram'] = ram_val
            info['has_specific_specs'] = True
        
        # GPU requirements
        if 'rtx' in text or 'nvidia' in text or 'dedicated graphics' in text or 'כרטיס מסך' in text:
            specs['needs_gpu'] = True
            info['has_specific_specs'] = True
        
        info['spec_requirements'] = specs
        
        return info
    
    def _identify_missing_info(self, extracted_info: Dict[str, any]) -> List[str]:
        """
        Identify what critical information is still missing.
        
        We need at least:
        1. Use case (what will they use it for?)
        2. Budget (how much can they spend?)
        3. Product type preference (laptop or desktop?)
        
        Without these, we can't make a good recommendation.
        """
        missing = []
        
        if not extracted_info['has_use_case']:
            missing.append('use_case')
        
        if not extracted_info['has_budget']:
            missing.append('budget')
        
        if not extracted_info['has_product_type']:
            missing.append('product_type')
        
        return missing
    
    def _determine_stage(
        self,
        extracted_info: Dict[str, any],
        conversation_history: List[Dict[str, str]],
        identified_customer_type: Optional[str]
    ) -> ConversationStage:
        """
        Determine what stage of the conversation we're in.
        
        This helps us understand the context and respond appropriately.
        For example, if we're at GREETING stage, we should be welcoming.
        If we're at READY_TO_RECOMMEND, we should suggest products.
        """
        # Check if this is the first message
        if len(conversation_history) == 0:
            return ConversationStage.GREETING
        
        # Check if we've already given recommendations
        has_recommended = any(
            'recommend' in msg['content'].lower() and msg['role'] == 'assistant'
            for msg in conversation_history
        )
        
        if has_recommended:
            return ConversationStage.RECOMMENDATION_GIVEN
        
        # Check what info we have
        missing_info = self._identify_missing_info(extracted_info)
        
        if len(missing_info) == 0:
            return ConversationStage.READY_TO_RECOMMEND
        
        # Determine which stage based on what's missing
        if 'use_case' in missing_info:
            return ConversationStage.UNDERSTANDING_NEEDS
        
        if 'budget' in missing_info:
            return ConversationStage.CLARIFYING_BUDGET
        
        if 'product_type' in missing_info:
            return ConversationStage.CLARIFYING_PREFERENCES
        
        return ConversationStage.UNDERSTANDING_NEEDS
    
    def _generate_clarifying_question(
        self,
        missing_info: List[str],
        extracted_info: Dict[str, any]
    ) -> str:
        """
        Generate a natural clarifying question based on what's missing.
        
        The questions are ordered by priority:
        1. Use case (most important - tells us what they need)
        2. Product type (laptop vs desktop - affects everything)
        3. Budget (helps us filter appropriately)
        
        Why this order? Because knowing the use case helps us ask better
        questions about product type and budget.
        """
        # Priority 1: Understand the use case
        if 'use_case' in missing_info:
            return ("I'd be happy to help you find the perfect computer! "
                   "To give you the best recommendation, could you tell me what you'll mainly use it for? "
                   "For example: studies, work, gaming, or general home use.")
        
        # Priority 2: Get product type preference
        if 'product_type' in missing_info:
            # Tailor the question based on use case if we know it
            if extracted_info['use_case_keywords']:
                use_case = extracted_info['use_case_keywords'][0]
                if use_case == 'student':
                    return "Would you prefer a laptop for portability between classes, or a desktop for your study space?"
                elif use_case == 'gaming':
                    return "Are you looking for a gaming laptop (portable) or a gaming desktop (more power for the money)?"
                else:
                    return "Do you prefer a laptop (portable) or a desktop (stationary but more powerful)?"
            else:
                return "Would you like a laptop or a desktop computer?"
        
        # Priority 3: Get budget
        if 'budget' in missing_info:
            return "What's your budget range for this purchase? This will help me show you the best options available."
        
        # If we somehow get here (shouldn't happen), ask a general question
        return "Is there anything specific you're looking for in a computer? Any particular features or requirements?"