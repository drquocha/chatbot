import openai
import os
from typing import List, Dict
from web_search import WebSearcher

class SimpleChatbot:
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.conversation_history: List[Dict[str, str]] = []
        self.web_searcher = WebSearcher()

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def needs_web_search(self, user_message: str) -> bool:
        """Check if user message needs web search for current information"""
        search_keywords = [
            'hiện tại', 'bây giờ', 'mới nhất', 'cập nhật', 'tình hình',
            'tổng bí thư', 'chủ tịch nước', 'thủ tướng', 'lãnh đạo',
            'tin tức', 'tin mới', 'hôm nay', 'năm 2024', 'năm 2025',
            'ai đang', 'giờ có', 'giờ là', 'đang là', 'có bao nhiêu',
            'web search', 'tìm kiếm', 'search', 'ngày mấy'
        ]
        message_lower = user_message.lower()
        result = any(keyword in message_lower for keyword in search_keywords)
        print(f"DEBUG: Message '{user_message}' needs search: {result}")
        return result

    def get_response(self, user_message: str) -> str:
        self.add_message("user", user_message)

        try:
            # Check if we need web search for current information
            if self.needs_web_search(user_message):
                print("🔍 Đang tìm kiếm thông tin mới nhất...")
                search_results = self.web_searcher.search_and_summarize(user_message)

                # Create enhanced prompt with search results
                enhanced_prompt = f"""Dựa trên thông tin tìm kiếm mới nhất từ web:

{search_results}

Hãy trả lời câu hỏi: {user_message}

Lưu ý: Ưu tiên thông tin từ kết quả tìm kiếm nếu có, và trả lời bằng tiếng Việt một cách chính xác, cập nhật nhất."""

                messages = [
                    {"role": "system", "content": "Bạn là một trợ lý AI thông minh, luôn cung cấp thông tin chính xác và cập nhật nhất."},
                    {"role": "user", "content": enhanced_prompt}
                ]
            else:
                messages = self.conversation_history

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            assistant_message = response.choices[0].message.content
            self.add_message("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            return f"Lỗi: {str(e)}"

    def clear_history(self):
        self.conversation_history = []

def main():
    print("🤖 Chatbot Demo - Nhập 'quit' để thoát")
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