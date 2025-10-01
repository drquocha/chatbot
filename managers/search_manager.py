"""
SearchManager - Handles web search decision making and execution
"""

import openai
from web_search import WebSearcher
from .prompt_manager import PromptManager

class SearchManager:
    def __init__(self, openai_client=None):
        self.client = openai_client
        self.web_searcher = WebSearcher()
        self.prompt_manager = PromptManager()

        # Fallback keywords for when LLM decision fails
        self.search_keywords = [
            'hiện tại', 'bây giờ', 'mới nhất', 'cập nhật', 'tình hình',
            'tổng bí thư', 'chủ tịch nước', 'thủ tướng', 'lãnh đạo',
            'tin tức', 'tin mới', 'hôm nay', 'năm 2024', 'năm 2025',
            'ai đang', 'giờ có', 'giờ là', 'đang là', 'có bao nhiêu',
            'web search', 'tìm kiếm', 'search', 'ngày mấy'
        ]

    def needs_web_search(self, user_message: str) -> bool:
        """Use LLM to intelligently decide if web search is needed"""
        if not self.client:
            return self._keyword_based_decision(user_message)

        try:
            decision_prompt = self.prompt_manager.create_search_decision_prompt(user_message)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": decision_prompt}],
                max_tokens=10,
                temperature=0.1
            )

            decision = response.choices[0].message.content.strip().upper()
            needs_search = "CÓ" in decision

            print(f"DEBUG: LLM decision for '{user_message}': {decision} -> needs_search: {needs_search}")
            return needs_search

        except Exception as e:
            print(f"DEBUG: LLM decision failed, falling back to keywords: {e}")
            return self._keyword_based_decision(user_message)

    def _keyword_based_decision(self, user_message: str) -> bool:
        """Fallback keyword-based decision making"""
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in self.search_keywords)

    def perform_search(self, user_message: str) -> str:
        """Perform web search and return results"""
        print("🔍 Đang tìm kiếm thông tin mới nhất...")
        return self.web_searcher.search_and_summarize(user_message)

    def should_search_and_get_results(self, user_message: str):
        """Check if search is needed and return results if so"""
        needs_search = self.needs_web_search(user_message)
        search_results = ""

        if needs_search:
            search_results = self.perform_search(user_message)

        return needs_search, search_results