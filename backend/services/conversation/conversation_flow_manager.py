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

        # IMPORTANT: Extract info from CURRENT message first, then supplement from history
        # This ensures the latest message takes precedence (e.g., new budget overrides old)
        current_info = self._extract_conversation_info(current_message.lower())

        # If critical info is missing from current message, check full history
        if not current_info['has_budget'] or not current_info['has_use_case'] or not current_info['has_product_type'] or not current_info['has_category']:
            history_info = self._extract_conversation_info(all_user_text)

            # Fill in gaps from history, but DON'T override current message info
            if not current_info['has_budget'] and history_info['has_budget']:
                current_info['budget_amount'] = history_info['budget_amount']
                current_info['has_budget'] = True

            if not current_info['has_use_case'] and history_info['has_use_case']:
                current_info['use_case_keywords'] = history_info['use_case_keywords']
                current_info['has_use_case'] = True

            if not current_info['has_product_type'] and history_info['has_product_type']:
                current_info['product_type'] = history_info['product_type']
                current_info['has_product_type'] = True

            if not current_info['has_category'] and history_info['has_category']:
                current_info['category'] = history_info['category']
                current_info['has_category'] = True

            if not current_info['has_brand_preference'] and history_info['has_brand_preference']:
                current_info['brand'] = history_info['brand']
                current_info['has_brand_preference'] = True

        extracted_info = current_info

        # LOG: Print extracted info for debugging
        print(f"\nEXTRACTED INFO FROM MESSAGE:")
        print(f"   Has Use Case: {extracted_info['has_use_case']} - Keywords: {extracted_info['use_case_keywords']}")
        print(f"   Has Budget: {extracted_info['has_budget']} - Amount: {extracted_info.get('budget_amount')}")
        print(f"   Has Product Type: {extracted_info['has_product_type']} - Type: {extracted_info.get('product_type')}")
        print(f"   Has Category: {extracted_info['has_category']} - Category: {extracted_info.get('category')}")

        # Determine what's missing
        missing_info = self._identify_missing_info(extracted_info)
        print(f"   Missing Info: {missing_info}")

        # Determine conversation stage
        stage = self._determine_stage(extracted_info, conversation_history)

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

        Strategy:
        1. Check ONLY the current message for product keywords
        2. Also accept messages with only numbers (likely answering our budget/spec questions)
        3. If neither found, the user has gone off-topic - redirect them
        """
        import re

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
            'gaming', 'work', 'study', 'office', 'development', 'music', 'entertainment',
            'גיימינג', 'עבודה', 'לימודים', 'משרד', 'פיתוח', 'מוזיקה', 'בידור',

            # Price/budget
            'price', 'cost', 'budget', 'cheap', 'expensive',
            'מחיר', 'תקציב', 'זול', 'יקר',

            # Accessories
            'mouse', 'keyboard', 'monitor', 'headset', 'bag', 'headphones',
            'עכבר', 'מקלדת', 'מסך', 'אוזניות', 'תיק', 'אזניות'
        ]

        # Check ONLY the current message to detect topic changes
        current_message_lower = current_message.lower()

        # First check: Does it have product keywords?
        if any(keyword in current_message_lower for keyword in product_keywords):
            return True

        # Second check: Is it just a number (likely answering our question)?
        # Match numbers like: "5000", "5000 שקל", "5,000", "16GB", etc.
        # This handles cases where user answers "What's your budget?" with just "5000"
        number_pattern = r'\d{3,6}'  # 3-6 digit numbers (typical for budgets/specs)
        if re.search(number_pattern, current_message):
            return True

        # No keywords and no numbers - likely off-topic
        return False

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
            'has_category': False,
            'category': None,
            'has_specific_specs': False,
            'spec_requirements': {}
        }

        # Extract use case
        use_case_patterns = {
            'student': ['student', 'university', 'college', 'study', 'homework', 'סטודנט', 'לימודים', 'אוניברסיטה', 'מכללה'],
            'gaming': ['gaming', 'gamer', 'games', 'fps', 'fortnite', 'גיימר', 'משחקים', 'גיימינג', 'חזק'],
            'work':   ['work', 'office', 'business', 'professional', 'עבודה', 'משרד', 'עסק', 'זום', 'פגישות'],
            'development': ['developer', 'programming', 'coding', 'engineer', 'מפתח', 'תכנות', 'מהנדס', 'פיתוח', 'דוקר', 'docker']
        }

        for use_case, keywords in use_case_patterns.items():
            if any(kw in text for kw in keywords):
                info['has_use_case'] = True
                info['use_case_keywords'].append(use_case)

        currency = r'(?:₪|שח|ש"ח|ש״ח|שקל|shekel|nis|ils)'
        # IMPORTANT: Try longer numbers first to avoid matching only part of a number
        # For example, "5000" should match as 5000, not as 500
        # Support both large numbers (1000+) and smaller amounts (50-999) for accessories
        num = r'(\d{4,6}|\d{1,3}(?:[,\.\s]\d{3})+|\d{2,3})'  # Matches 50-999999 or formatted numbers

        # Extract budget using regex
        budget_patterns = [
            rf'תקציב.*?{num}',
            rf'עד\s*{num}',
            rf'בערך\s*{num}',
            rf'סביב(?:ות|)s*\s*{num}',
            rf'מקס(?:ימום|)\s*{num}',
            rf'{num}\s*{currency}',
            rf'{num}\s*ומעלה',  # Support "200 ומעלה" pattern
            rf'{num}\s*שקל',
        ]

        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw = match.group(1)
                budget_str = raw.replace(',', '').replace('.', '').replace(' ', '')
                try:
                    budget_value = float(budget_str)
                    info['budget_amount'] = budget_value
                    info['has_budget'] = True

                    # Check if this is a minimum budget (e.g., "200 ומעלה" / "200 and up")
                    if 'ומעלה' in text or 'and up' in text.lower() or 'minimum' in text.lower():
                        # For minimum budget, set a high max so we show expensive items
                        # Set max to 10x the minimum or 10000, whichever is higher
                        info['budget_amount'] = max(budget_value * 10, 10000)
                        info['is_minimum_budget'] = True
                        print(f"Detected minimum budget: {budget_value}+ (setting max to {info['budget_amount']})")

                    break
                except ValueError:
                    pass

        # If we found numbers but no explicit budget, check if it's a reasonable budget number
        if not info['has_budget']:
            numbers = re.findall(r'\b(\d{2,6})\b', text)  # 2-6 digit numbers
            if numbers:
                # Assume it's a budget if in reasonable range (50-50000 ILS)
                # Skip if it's clearly a tech spec (RAM, storage)
                is_tech_spec = any(keyword in text.lower() for keyword in
                                  ['gb', 'ram', 'ראם', 'גיגה', 'tb', 'ssd', 'hdd'])
                if not is_tech_spec:
                    for num in numbers:
                        num_val = int(num)
                        if 50 <= num_val <= 50000:
                            info['budget_amount'] = float(num_val)
                            info['has_budget'] = True
                            break

        # Extract product type preference
        if any(k in text for k in ['laptop', 'notebook', 'portable', 'נייד', 'לפטופ', 'מחשב נייד']):
            info['has_product_type'] = True
            info['product_type'] = 'laptop'
        elif any(k in text for k in ['desktop', 'tower', 'pc', 'נייח', 'שולחני', 'מחשב נייח', 'מגדל']):
            info['has_product_type'] = True
            info['product_type'] = 'desktop'

        # Extract category preference (computer vs accessories)
        computer_keywords = [
            'computer', 'computers', 'pc',  # English
            'מחשב', 'מחשבים', 'קומפיוטר'  # Hebrew
        ]
        has_computer_request = any(k in text for k in computer_keywords)

        # Extract accessory category
        detected_accessory = None
        if any(k in text for k in ['headset', 'headphones', 'אוזניות', 'אזניות']):
            detected_accessory = 'headset'
        elif any(k in text for k in ['mouse', 'עכבר']):
            detected_accessory = 'mouse'
        elif any(k in text for k in ['keyboard', 'מקלדת']):
            detected_accessory = 'keyboard'
        elif any(k in text for k in ['monitor', 'screen', 'מסך', 'צג']):
            detected_accessory = 'monitor'
        elif any(k in text for k in ['bag', 'backpack', 'תיק', 'תרמיל']):
            detected_accessory = 'bag'

        # Priority: If user wants computer, that's the main product
        # Any accessory they mention will be offered as upsell
        if has_computer_request:
            info['has_category'] = True
            info['category'] = 'computer'
            if detected_accessory:
                info['requested_accessory'] = detected_accessory
                print(f"Detected combined request: computer + {detected_accessory} as upsell")
        elif detected_accessory:
            # Only accessory (no computer)
            info['has_category'] = True
            info['category'] = detected_accessory

        # Extract brand preference
        if any(k in text for k in ['lenovo', 'לנובו']):
            info['has_brand_preference'] = True
            info['brand'] = 'Lenovo'
        elif any(k in text for k in ['dell', 'דל']):
            info['has_brand_preference'] = True
            info['brand'] = 'Dell'
        elif any(k in text for k in ['hp', 'אייץ פי', 'הפ']):
            info['has_brand_preference'] = True
            info['brand'] = 'HP'
        elif any(k in text for k in ['asus', 'אסוס']):
            info['has_brand_preference'] = True
            info['brand'] = 'ASUS'

        # Extract specific specs
        specs = {}

        # RAM requirements: "16GB RAM" / "RAM 16GB" / "16 גיגה ראם"
        ram_match = re.search(r'(\d+)\s*(?:gb|גיגה)\s*(?:ram|ראם)|(?:ram|ראם)\s*(\d+)\s*(?:gb|גיגה)', text, re.IGNORECASE)
        if ram_match:
            ram_val = int(ram_match.group(1) or ram_match.group(2))
            specs['min_ram'] = ram_val
            info['has_specific_specs'] = True

        # GPU requirements
        if any(k in text for k in ['rtx', 'nvidia', 'radeon', 'כרטיס מסך', 'גרפיקה', 'gpu']):
            specs['needs_gpu'] = True
            info['has_specific_specs'] = True

        info['spec_requirements'] = specs
        return info

    def _identify_missing_info(self, extracted_info: Dict[str, any]) -> List[str]:
        """
        Identify what critical information is still missing.

        For computers, we need:
        1. Use case (what will they use it for?)
        2. Budget (how much can they spend?)
        3. Product type preference (laptop or desktop?)

        For accessories, we need:
        1. Use case (gaming, music, work?) - helps filter appropriate accessories
        2. Budget (price range varies significantly) - helps filter by price
        We DON'T need product_type since they're not buying a computer.
        """
        missing = []

        # Check if this is an accessory-only request
        category = extracted_info.get('category')
        is_accessory_only = category in ['mouse', 'keyboard', 'headset', 'bag', 'monitor']

        if is_accessory_only:
            # For accessories, we still need budget and use_case to filter properly
            # but we don't need product_type
            if not extracted_info['has_use_case']:
                missing.append('use_case')

            if not extracted_info['has_budget']:
                missing.append('budget')

            return missing

        # For computers, we need all the info
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
        conversation_history: List[Dict[str, str]]) -> ConversationStage:
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
            (('recommend' in msg['content'].lower()) or ('ממליץ' in msg['content']) or ('המלצה' in msg['content']))
            and msg['role'] == 'assistant'
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
        """
        # Check if this is an accessory-only request
        category = extracted_info.get('category')
        is_accessory_only = category in ['mouse', 'keyboard', 'headset', 'bag', 'monitor']

        # Priority 1: Understand the use case
        if 'use_case' in missing_info:
            if is_accessory_only:
                # Customize question based on accessory type
                if category == 'headset':
                    return ("אשמח לעזור לך למצוא את האוזניות המושלמות! "
                           "למה בעיקר תשתמש באוזניות? לדוגמה: גיימינג, האזנה למוזיקה, שיחות עבודה, או שימוש כללי.")
                elif category == 'mouse':
                    return ("אשמח לעזור לך למצוא את העכבר המושלם! "
                           "למה בעיקר תשתמש בעכבר? לדוגמה: גיימינג, עבודה משרדית, עיצוב גרפי, או שימוש כללי.")
                elif category == 'keyboard':
                    return ("אשמח לעזור לך למצוא את המקלדת המושלמת! "
                           "למה בעיקר תשתמש במקלדת? לדוגמה: גיימינג, תכנות, כתיבה, או שימוש כללי.")
                elif category == 'monitor':
                    return ("אשמח לעזור לך למצוא את המסך המושלם! "
                           "למה בעיקר תשתמש במסך? לדוגמה: גיימינג, עיצוב גרפי, עבודה משרדית, או שימוש כללי.")
                elif category == 'bag':
                    return ("אשמח לעזור לך למצוא את התיק המושלם! "
                           "למה בעיקר תשתמש בתיק? לדוגמה: נסיעות, לימודים, עבודה, או שימוש יומיומי.")
            else:
                # Computer question
                return ("אשמח לעזור לך למצוא את המחשב המושלם! "
                       "כדי לתת לך את ההמלצה הטובה ביותר, תוכל לספר לי למה בעיקר תשתמש במחשב? "
                       "לדוגמה: לימודים, עבודה, גיימינג, או שימוש כללי בבית.")

        # Priority 2: Get product type preference (only for computers)
        if 'product_type' in missing_info:
            # Tailor the question based on use case if we know it
            if extracted_info['use_case_keywords']:
                use_case = extracted_info['use_case_keywords'][0]
                if use_case == 'student':
                    return "האם תעדיף מחשב נייד לניידות בין שיעורים, או מחשב נייח לחדר הלימודים שלך?"
                elif use_case == 'gaming':
                    return "האם אתה מחפש מחשב נייד לגיימינג או מחשב נייח לגיימינג (יותר כוח תמורת הכסף)?"
                else:
                    return "האם תעדיף מחשב נייד או מחשב נייח (נייח אבל חזק יותר)?"
            else:
                return "האם תרצה מחשב נייד או מחשב שולחני?"

        # Priority 3: Get budget
        if 'budget' in missing_info:
            if is_accessory_only:
                return f"מה טווח התקציב שלך ל{self._get_accessory_name_hebrew(category)}? זה יעזור לי להראות לך את האפשרויות הטובות ביותר."
            else:
                return "מה טווח התקציב שלך לרכישה? זה יעזור לי להראות לך את האפשרויות הטובות ביותר הזמינות."

        # If we somehow get here (shouldn't happen), ask a general question
        if is_accessory_only:
            return f"האם יש משהו ספציפי שאתה מחפש ב{self._get_accessory_name_hebrew(category)}? תכונות או דרישות מיוחדות?"
        else:
            return "האם יש משהו ספציפי שאתה מחפש במחשב? תכונות או דרישות מיוחדות?"

    def _get_accessory_name_hebrew(self, category: Optional[str]) -> str:
        """Get Hebrew name for accessory category."""
        names = {
            'headset': 'אוזניות',
            'mouse': 'עכבר',
            'keyboard': 'מקלדת',
            'monitor': 'מסך',
            'bag': 'תיק'
        }
        return names.get(category, 'מוצר')
