"""
Customer Identifier Service

Identifies customer type based on conversation context.

Customer Types:
- Student: Looking for value, portability, basic performance
- Engineer: Needs strong CPU, RAM, professional tools
- Gamer: Needs GPU, high performance, cooling
- Other: Doesn't fit other categories
"""
"""
Customer Identifier Service - Enhanced Version

Identifies customer type and needs through natural conversation flow.

Key improvements:
1. Natural conversation approach - doesn't ask "what type are you?"
2. Maps use cases to technical requirements
3. Handles incomplete information gracefully
4. Provides clarifying questions when needed
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum


class CustomerType(str, Enum):
    """Customer types with their typical use cases"""
    STUDENT = "Student"
    ENGINEER = "Engineer"
    GAMER = "Gamer"
    BUSINESS = "Business"
    HOME_USER = "Home User"
    OTHER = "Other"


class CustomerIdentifier:
    """
    Identifies customer type and requirements through conversation analysis.
    """
    
    # Keyword mappings for identification
    USE_CASE_KEYWORDS = {
        CustomerType.STUDENT: {
            'strong': ['student', 'university', 'college', 'studies', 'homework', 'assignment',
                      'סטודנט', 'אוניברסיטה', 'לימודים', 'שיעורי בית'],
            'medium': ['school', 'class', 'lecture', 'exam', 'notes', 'research',
                      'בית ספר', 'הרצאה', 'מבחן']
        },
        CustomerType.ENGINEER: {
            'strong': ['engineer', 'developer', 'programmer', 'architect', 'designer',
                      'מהנדס', 'מפתח', 'תכנתן', 'אדריכל'],
            'medium': ['coding', 'programming', 'development', 'software', 'cad', 'autocad',
                      '3d modeling', 'rendering', 'simulation', 'compile',
                      'תכנות', 'פיתוח', 'רינדור']
        },
        CustomerType.GAMER: {
            'strong': ['gaming', 'gamer', 'games', 'fortnite', 'valorant', 'csgo', 'warzone',
                      'גיימר', 'משחקים', 'גיימינג'],
            'medium': ['fps', 'streaming', 'twitch', 'discord', 'graphics', 'rtx',
                      'frame rate', 'hz', 'rgb']
        },
        CustomerType.BUSINESS: {
            'strong': ['business', 'office', 'work', 'company', 'employee',
                      'עסק', 'משרד', 'עבודה', 'חברה'],
            'medium': ['excel', 'powerpoint', 'word', 'email', 'meetings', 'zoom',
                      'אקסל', 'וורד', 'פגישות']
        },
        CustomerType.HOME_USER: {
            'strong': ['home', 'family', 'personal use', 'browsing', 'netflix',
                      'בית', 'משפחה', 'שימוש אישי'],
            'medium': ['internet', 'youtube', 'email', 'photos', 'videos',
                      'אינטרנט', 'תמונות', 'סרטונים']
        }
    }
    
    # Technical requirement mappings
    REQUIREMENTS_MAP = {
        CustomerType.STUDENT: {
            'cpu_priority': 'medium',
            'ram_min': 8,
            'ram_recommended': 16,
            'gpu_needed': False,
            'storage_min': 256,
            'storage_recommended': 512,
            'portability': 'important',
            'budget_sensitive': True,
            'description': 'Students need portable, affordable laptops for office work, research, and note-taking'
        },
        CustomerType.ENGINEER: {
            'cpu_priority': 'high',
            'ram_min': 16,
            'ram_recommended': 32,
            'gpu_needed': 'depends',  # Depends on engineering field
            'storage_min': 512,
            'storage_recommended': 1024,
            'portability': 'medium',
            'budget_sensitive': False,
            'description': 'Engineers need powerful CPUs and RAM for development, compilation, and professional tools'
        },
        CustomerType.GAMER: {
            'cpu_priority': 'high',
            'ram_min': 16,
            'ram_recommended': 32,
            'gpu_needed': True,
            'storage_min': 512,
            'storage_recommended': 1024,
            'portability': 'low',
            'budget_sensitive': False,
            'description': 'Gamers need dedicated GPUs, good cooling, and high-performance components'
        },
        CustomerType.BUSINESS: {
            'cpu_priority': 'medium',
            'ram_min': 8,
            'ram_recommended': 16,
            'gpu_needed': False,
            'storage_min': 256,
            'storage_recommended': 512,
            'portability': 'medium',
            'budget_sensitive': True,
            'description': 'Business users need reliable, secure computers for office applications and communication'
        },
        CustomerType.HOME_USER: {
            'cpu_priority': 'low',
            'ram_min': 8,
            'ram_recommended': 8,
            'gpu_needed': False,
            'storage_min': 256,
            'storage_recommended': 256,
            'portability': 'medium',
            'budget_sensitive': True,
            'description': 'Home users need basic, affordable computers for browsing, email, and multimedia'
        },
        CustomerType.OTHER: {
            'cpu_priority': 'medium',
            'ram_min': 8,
            'ram_recommended': 16,
            'gpu_needed': False,
            'storage_min': 256,
            'storage_recommended': 512,
            'portability': 'medium',
            'budget_sensitive': True,
            'description': 'General-purpose computing with balanced specifications'
        }
    }
    
    def identify_from_conversation(
        self,
        current_message: str,
        conversation_history: List[str]
    ) -> Tuple[CustomerType, Dict[str, any], Optional[str]]:
        """
        Identify customer type and return requirements + clarifying question if needed.
        
        Args:
            current_message: Latest user message
            conversation_history: Previous user messages
        
        Returns:
            Tuple of (customer_type, requirements_dict, clarifying_question)
            - customer_type: Identified CustomerType enum
            - requirements_dict: Technical requirements based on type
            - clarifying_question: Question to ask if more info needed, or None
        
        Example:
            customer_type, reqs, question = identifier.identify_from_conversation(
                "I need a computer",
                []
            )
            # Returns: (CustomerType.OTHER, {...}, "What will you primarily use it for?")
        """
        # Combine all messages for analysis
        all_text = " ".join(conversation_history + [current_message]).lower()
        
        # Score each customer type
        scores = self._score_customer_types(all_text)
        
        # Get best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # If score is too low, we need more information
        if best_score < 2:
            # Not enough information to identify
            question = self._get_clarifying_question(current_message, all_text)
            return CustomerType.OTHER, self.REQUIREMENTS_MAP[CustomerType.OTHER], question
        
        # Get requirements for this customer type
        requirements = self.REQUIREMENTS_MAP[best_type]
        
        # Check if we have enough specifics (budget, product type preference)
        needs_clarification = self._check_missing_info(all_text)
        question = needs_clarification if needs_clarification else None
        
        return best_type, requirements, question
    
    def _score_customer_types(self, text: str) -> Dict[CustomerType, int]:
        """
        Score each customer type based on keyword matches.
        
        Strong keywords: 3 points
        Medium keywords: 1 point
        """
        scores = {ct: 0 for ct in CustomerType}
        
        for customer_type, keyword_sets in self.USE_CASE_KEYWORDS.items():
            # Strong keywords
            for keyword in keyword_sets['strong']:
                if keyword.lower() in text:
                    scores[customer_type] += 3
            
            # Medium keywords
            for keyword in keyword_sets['medium']:
                if keyword.lower() in text:
                    scores[customer_type] += 1
        
        return scores
    
    def _get_clarifying_question(self, message: str, full_context: str) -> Optional[str]:
        """
        Generate appropriate clarifying question based on what we know.
        
        IMPORTANT: Questions must be in Hebrew.
        """
        # Check what information we're missing
        has_use_case = any(word in full_context for word in [
            'student', 'gaming', 'work', 'engineer', 'business', 'home',
            'סטודנט', 'גיימינג', 'עבודה', 'מהנדס', 'עסק', 'בית'])
        
        has_product_type = any(word in full_context for word in [
            'laptop', 'desktop', 'notebook', 'pc', 'tower',
            'נייד', 'נייח', 'לפטופ'])
        
        has_budget = any(word in full_context for word in [
            'budget', 'price', 'cost', 'shekel', 'nis', 'ils',
            'תקציב', 'מחיר', 'שקל']) or any(char.isdigit() for char in full_context)
        
        # Ask the most relevant question in Hebrew
        if not has_use_case:
            return ("מעולה! אשמח לעזור לך למצוא את המחשב המושלם. "
                "למה בעיקר תשתמש במחשב? לדוגמה: לימודים, עבודה, גיימינג, או שימוש כללי בבית?")
        
        elif not has_product_type:
            return ("תודה על המידע! האם תעדיף מחשב נייד (נייד) או מחשב נייח (יותר כוח תמורת המחיר)?")
        
        elif not has_budget:
            return ("מעולה! מה טווח התקציב שלך? זה יעזור לי להראות לך את האפשרויות הטובות ביותר הזמינות.")
        
        else:
            # We have enough info, no question needed
            return None

    def _check_missing_info(self, text: str) -> Optional[str]:
        """
        Check if critical information is missing and return appropriate question in Hebrew.
        """
        has_budget = any(word in text for word in [
            'budget', 'price', 'cost', 'תקציב', 'מחיר']) or any(char.isdigit() for char in text)
        
        has_product_type = any(word in text for word in [
            'laptop', 'desktop', 'notebook', 'pc', 'נייד', 'נייח'])
        
        # If customer type is identified but we're missing budget or product type
        if not has_product_type:
            return "האם תעדיף מחשב נייד או מחשב נייח?"
        
        if not has_budget:
            return "מה טווח התקציב שלך לרכישה?"
        
        return None

    
    def get_requirements(self, customer_type: CustomerType) -> Dict[str, any]:
        """Get technical requirements for a customer type"""
        return self.REQUIREMENTS_MAP.get(customer_type, self.REQUIREMENTS_MAP[CustomerType.OTHER])