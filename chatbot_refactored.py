"""
Refactored SimpleChatbot following Single Responsibility Principle
"""

import openai
import os
from typing import List, Dict

from managers.history_manager import HistoryManager
from managers.search_manager import SearchManager
from managers.prompt_manager import PromptManager

class SimpleChatbot:
    """
    Refactored chatbot that acts as a coordinator between specialized managers.
    Each manager handles a specific responsibility:
    - HistoryManager: Conversation history with sliding window
    - SearchManager: Web search decision making and execution
    - PromptManager: Prompt creation and template management
    """

    def __init__(self, api_key: str = None, max_history: int = 20):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

        # Initialize specialized managers
        self.history_manager = HistoryManager(max_messages=max_history)
        self.search_manager = SearchManager(openai_client=self.client)
        self.prompt_manager = PromptManager()

    def get_response(self, user_message: str) -> str:
        """
        Main orchestration method - coordinates between managers
        """
        try:
            # 1. Add user message to history
            self.history_manager.add_message("user", user_message)

            # 2. Check if web search is needed and get results
            needs_search, search_results = self.search_manager.should_search_and_get_results(user_message)

            # 3. Prepare messages for API based on search results
            if needs_search:
                # Get history without the last message for context preservation
                messages_for_api = self.history_manager.get_history_except_last()

                # Create enhanced prompt with search results
                enhanced_prompt = self.prompt_manager.create_web_search_prompt(
                    user_message, search_results
                )

                # Add enhanced prompt and update history
                messages_for_api.append({"role": "user", "content": enhanced_prompt})
                self.history_manager.update_last_message("user", enhanced_prompt)
            else:
                # Use standard conversation flow
                messages_for_api = self.history_manager.get_history()

            # 4. Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages_for_api,
                max_tokens=500,
                temperature=0.7
            )

            # 5. Add assistant response to history and return
            assistant_message = response.choices[0].message.content
            self.history_manager.add_message("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            error_message = f"Lỗi: {str(e)}"
            self.history_manager.add_message("assistant", error_message)
            return error_message

    # Convenience methods for external access
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.history_manager.add_message(role, content)

    def clear_history(self):
        """Clear conversation history"""
        self.history_manager.clear()

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history"""
        return self.history_manager.get_history()

    def get_message_count(self) -> int:
        """Get total number of messages in history"""
        return self.history_manager.get_message_count()

# For backward compatibility and testing
def main():
    print("🤖 Refactored Chatbot Demo - Nhập 'quit' để thoát")
    print("-" * 40)

    chatbot = SimpleChatbot()

    while True:
        user_input = input("\nBạn: ").strip()

        if user_input.lower() in ['quit', 'exit', 'thoát']:
            print("Tạm biệt! 👋")
            break

        if user_input.lower() == 'clear':
            chatbot.clear_history()
            print("Đã xóa lịch sử hội thoại.")
            continue

        if not user_input:
            continue

        print("Bot: ", end="")
        response = chatbot.get_response(user_input)
        print(response)

if __name__ == "__main__":
    main()