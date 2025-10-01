"""
PromptManager - Handles all prompt creation and template management
"""

class PromptManager:
    def __init__(self):
        self.web_search_template = """Dựa trên thông tin tìm kiếm mới nhất từ web:

{search_results}

Hãy trả lời câu hỏi: {question}

Lưu ý: Ưu tiên thông tin từ kết quả tìm kiếm nếu có, kết hợp với ngữ cảnh cuộc trò chuyện trước đó, và trả lời bằng tiếng Việt một cách chính xác, cập nhất."""

        self.search_decision_template = """Câu hỏi này có cần tìm kiếm thông tin CẬP NHẬT trên Internet không?

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

Câu hỏi: "{question}"

Trả lời:"""

    def create_web_search_prompt(self, question: str, search_results: str) -> str:
        """Create enhanced prompt with web search results"""
        return self.web_search_template.format(
            search_results=search_results,
            question=question
        )

    def create_search_decision_prompt(self, question: str) -> str:
        """Create prompt for LLM to decide if web search is needed"""
        return self.search_decision_template.format(question=question)

    def create_standard_prompt(self, history: list) -> list:
        """Create standard conversation prompt"""
        return history

    def add_system_message(self, messages: list, system_content: str) -> list:
        """Add system message to conversation"""
        return [{"role": "system", "content": system_content}] + messages