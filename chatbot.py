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
        """Use LLM to intelligently decide if web search is needed"""
        try:
            decision_prompt = f"""Câu hỏi này có cần tìm kiếm thông tin CẬP NHẬT trên Internet không?

Chỉ trả lời: "CÓ" hoặc "KHÔNG"

CẦN tìm kiếm khi:
- Hỏi về lãnh đạo hiện tại, chính phủ hiện tại
- Giá cả hiện tại, thống kê mới nhất
- Tin tức, sự kiện đang diễn ra
- Thời tiết hôm nay/hiện tại

KHÔNG cần tìm kiếm khi:
- Hỏi CÁCH LÀM gì đó (nấu ăn, sửa chữa, học tập)
- Hỏi CÔNG THỨC món ăn
- Giải thích khái niệm, định nghĩa
- Kiến thức tổng quát không đổi theo thời gian

Câu hỏi: "{user_message}"

Trả lời:"""

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
            # Fallback to keyword-based approach if LLM fails
            search_keywords = [
                'hiện tại', 'bây giờ', 'mới nhất', 'cập nhật', 'tình hình',
                'tổng bí thư', 'chủ tịch nước', 'thủ tướng', 'lãnh đạo',
                'tin tức', 'tin mới', 'hôm nay', 'năm 2024', 'năm 2025',
                'ai đang', 'giờ có', 'giờ là', 'đang là', 'có bao nhiêu',
                'web search', 'tìm kiếm', 'search', 'ngày mấy'
            ]
            message_lower = user_message.lower()
            return any(keyword in message_lower for keyword in search_keywords)

    def get_response(self, user_message: str) -> str:
        self.add_message("user", user_message)

        try:
            # Check if we need web search for current information
            needs_search = self.needs_web_search(user_message)

            if needs_search:
                print("🔍 Đang tìm kiếm thông tin mới nhất...")
                search_results = self.web_searcher.search_and_summarize(user_message)

                # CRITICAL FIX: Preserve conversation history and enhance the last message
                # Get all conversation history except the last user message
                messages_for_api = self.conversation_history[:-1].copy()

                # Create enhanced prompt that includes search results
                enhanced_prompt = f"""Dựa trên thông tin tìm kiếm mới nhất từ web:

{search_results}

Hãy trả lời câu hỏi: {user_message}

Lưu ý: Ưu tiên thông tin từ kết quả tìm kiếm nếu có, kết hợp với ngữ cảnh cuộc trò chuyện trước đó, và trả lời bằng tiếng Việt một cách chính xác, cập nhất."""

                # Add the enhanced prompt as the new user message
                messages_for_api.append({"role": "user", "content": enhanced_prompt})
                messages = messages_for_api

                # Update conversation history to reflect what was actually sent to the API
                self.conversation_history[-1] = {"role": "user", "content": enhanced_prompt}
            else:
                # Use normal conversation history
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