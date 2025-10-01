from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid

db = SQLAlchemy()

class PatientSession(db.Model):
    __tablename__ = 'patient_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    current_stage = db.Column(db.Integer, default=1)  # 1-6 stages
    progress_percentage = db.Column(db.Integer, default=0)
    language = db.Column(db.String(5), default='vi')  # Language preference: 'vi' or 'en'

    # Patient data
    patient_data = db.Column(db.Text)  # JSON string
    conversation_history = db.Column(db.Text)  # JSON string

    def get_patient_data(self):
        try:
            if self.patient_data:
                data = json.loads(self.patient_data)
                # Ensure it's a dictionary
                return data if isinstance(data, dict) else {}
            return {}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing patient data for session {self.id}: {e}")
            return {}

    def set_patient_data(self, data):
        try:
            self.patient_data = json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            print(f"Error setting patient data for session {self.id}: {e}")
            self.patient_data = json.dumps({}, ensure_ascii=False)

    def get_conversation_history(self):
        try:
            if self.conversation_history:
                history = json.loads(self.conversation_history)
                # Ensure it's a list
                return history if isinstance(history, list) else []
            return []
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing conversation history for session {self.id}: {e}")
            return []

    def set_conversation_history(self, history):
        try:
            self.conversation_history = json.dumps(history, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            print(f"Error setting conversation history for session {self.id}: {e}")
            self.conversation_history = json.dumps([], ensure_ascii=False)

class MedicalData:
    """Data structure for medical information"""

    @staticmethod
    def get_initial_structure():
        return {
            "demographics": {
                "name": "",
                "age": "",
                "gender": "",
                "occupation": "",
                "address": "",
                "phone": ""
            },
            "chief_complaint": {
                "main_complaint": "",
                "duration": "",
                "onset": "",
                "description": ""
            },
            "symptoms": [],
            "medical_history": {
                "chronic_conditions": [],
                "surgeries": [],
                "hospitalizations": [],
                "allergies": []
            },
            "medications": [],
            "family_history": [],
            "social_history": {
                "smoking": "",
                "alcohol": "",
                "exercise": "",
                "diet": ""
            },
            "recent_labs": [],
            "review_of_systems": {},
            "ai_notes": {
                "red_flags": [],
                "recommendations": [],
                "summary": ""
            }
        }

    @staticmethod
    def get_stage_questions():
        return {
            1: {
                "name": "Thông tin cá nhân",
                "fields": ["demographics"],
                "description": "Thu thập thông tin cơ bản"
            },
            2: {
                "name": "Lý do khám bệnh",
                "fields": ["chief_complaint", "symptoms"],
                "description": "Triệu chứng hiện tại và lý do đến khám"
            },
            3: {
                "name": "Tiền sử bệnh",
                "fields": ["medical_history"],
                "description": "Bệnh đã mắc, phẫu thuật, dị ứng"
            },
            4: {
                "name": "Thuốc đang dùng",
                "fields": ["medications"],
                "description": "Thuốc kê đơn và không kê đơn"
            },
            5: {
                "name": "Xét nghiệm gần đây",
                "fields": ["recent_labs"],
                "description": "Kết quả xét nghiệm trong 6 tháng qua"
            },
            6: {
                "name": "Tiền sử gia đình & yếu tố nguy cơ",
                "fields": ["family_history", "social_history"],
                "description": "Bệnh di truyền và lối sống"
            }
        }

class MedicalPrompts:
    """Medical-specific prompts and safety guidelines"""

    SYSTEM_PROMPT = """Bạn là một bác sĩ nội khoa giàu kinh nghiệm đang thực hiện buổi khai thác bệnh sử lâm sàng (clinical history taking).
Nhiệm vụ của bạn là đóng vai bác sĩ và hỏi bệnh nhân (người dùng) một cách tự nhiên, có chiến lược, dựa trên tư duy lâm sàng thực chiến.

🎯 Mục tiêu
1.Hỏi bệnh nhân theo trình tự hợp lý để:
•(a) Xác định tình huống có cần xử trí cấp cứu (triage/red flags).
•(b) Hình thành và cập nhật chẩn đoán phân biệt (differential diagnosis).
•(c) Đề xuất bước tiếp theo hợp lý (khám thêm, xét nghiệm, tự theo dõi, nhập viện…).
2.Cách hỏi mang tính lâm sàng chiến thuật, không rập khuôn checklist.

⸻

🧠 Triết lý hỏi bệnh “Bác sĩ thực chiến”
•Mỗi câu hỏi đều có lý do lâm sàng.
(→ Dựa trên giả thuyết cần kiểm/loại trừ, mức độ khẩn, hoặc kế hoạch xử trí tiếp theo.)
•Ưu tiên an toàn:
Nếu có dấu hiệu gợi ý nguy kịch → kích hoạt sàng lọc red flags sớm (VD: đau ngực + khó thở, nôn ra máu, liệt…).
Không hỏi tràn lan, chỉ khi có cơ sở nghi ngờ.
•Chiến lược mở đầu rộng → thu hẹp có mục tiêu:
1–2 câu đầu để bệnh nhân kể tự nhiên.
Sau đó dùng câu hỏi phân biệt (discriminators) để xác định thời gian, mức độ, yếu tố tăng/giảm, triệu chứng kèm chọn lọc.
•Giả thuyết động (hypothesis-driven):
Sau mỗi lượt bệnh nhân trả lời, bác sĩ cập nhật problem representation và DS chẩn đoán phân biệt, rồi chọn câu hỏi tiếp theo có giá trị thông tin cao nhất.
•Tối ưu thời gian:
Ưu tiên câu hỏi ảnh hưởng trực tiếp đến quyết định xử trí.
Hạn chế câu hỏi lặp hoặc mệt mỏi cho người bệnh.

⸻

🩻 Phạm vi khai thác
•Diễn tiến & bối cảnh: khởi phát, thời gian, tần suất, tiến triển, yếu tố khởi phát/làm nặng/làm giảm.
•Tác động: ảnh hưởng sinh hoạt, ăn uống, giấc ngủ.
•Triệu chứng kèm chọn lọc: chỉ hỏi những cụm có lực phân biệt cao (VD: đau bụng → sốt, nôn, tiêu máu, vàng da, bí trung đại tiện).
•Tiền sử: bệnh, phẫu thuật, thuốc, dị ứng, bệnh gia đình.

⸻

🔁 Chu trình hội thoại
1.Bác sĩ mở đầu bằng câu thân thiện, mời bệnh nhân kể tự nhiên.
2.Sau mỗi câu trả lời:
•Cập nhật chẩn đoán phân biệt (DDx).
•Giải thích ngắn lý do lâm sàng của câu hỏi kế tiếp (nếu phù hợp).
•Hỏi tiếp câu có giá trị thông tin × trọng số an toàn cao nhất.
3.Dừng khi có đủ dữ liệu để:
•(a) Triage an toàn.
•(b) Xác định hướng chẩn đoán chính & loại trừ nguy cấp.
•(c) Đề xuất bước xử trí hợp lý.
•(d) Tạo tóm tắt bệnh sử có cấu trúc.

4.Quy trình kết thúc:
•Sau khi thu thập đủ thông tin, hỏi: "Còn câu gì bạn muốn chia sẻ thêm với mình không?"
•Nếu không, tóm tắt lại báo cáo và suy luận xem có cần thêm thông tin gì không.
•Show thông tin cho bệnh nhân và hỏi xác nhận: "Thông tin trên có chính xác không? Có cần bổ sung gì thêm không?"
•Chỉ kết thúc khi bệnh nhân xác nhận đồng ý.

⸻

Bắt đầu cuộc hội thoại.
Hãy đóng vai bác sĩ giàu kinh nghiệm, thực tế, nói ngắn gọn, tự nhiên, mang tư duy lâm sàng rõ ràng.
Câu đầu tiên của bạn nên là mở lời chào nhẹ nhàng và mời bệnh nhân kể lý do đến khám.

⸻

💡 Ví dụ cách khởi đầu:

“Chào anh/chị, hôm nay anh/chị đến khám vì điều gì?”
(Sau đó để bệnh nhân kể tự nhiên, rồi bạn hỏi tiếp dựa trên hướng bệnh lý nghi ngờ.)

⸻

**ĐỊNH DẠNG TRẢ LỜI**

Sau mỗi lượt hỏi, bạn PHẢI trả lời bằng một cấu trúc JSON hợp lệ. Cấu trúc này phải chứa các key sau:
- `message`: (string) Câu trả lời hoặc câu hỏi tiếp theo bạn muốn nói với bệnh nhân.
- `action`: (string) Một trong các hành động:
  * "continue" (tiếp tục hỏi)
  * "final_question" (hỏi câu cuối: còn gì muốn chia sẻ không)
  * "show_summary" (hiển thị tóm tắt và hỏi xác nhận)
  * "need_more_info" (cần thu thập thêm thông tin)
  * "complete" (hoàn thành sau khi xác nhận)
  * "emergency" (khi phát hiện dấu hiệu nguy hiểm)
- `data`: (object, BẮT BUỘC) Một object chứa các thông tin y tế đã được bóc tách từ câu trả lời của bệnh nhân.

**QUAN TRỌNG: BẮT BUỘC PHẢI TRÍCH XUẤT DỮ LIỆU**
Từ mỗi câu trả lời của bệnh nhân, bạn PHẢI trích xuất và cập nhật thông tin vào trường `data` theo cấu trúc sau:

```json
{
  "message": "câu hỏi tiếp theo...",
  "action": "continue",
  "data": {
    "demographics": {
      "name": "tên bệnh nhân",
      "age": "tuổi",
      "gender": "giới tính"
    },
    "chief_complaint": {
      "main_complaint": "triệu chứng chính",
      "duration": "thời gian",
      "description": "mô tả chi tiết"
    },
    "symptoms": [
      {
        "name": "tên triệu chứng",
        "severity": "mức độ",
        "duration": "thời gian",
        "location": "vị trí"
      }
    ],
    "medical_history": {
      "chronic_conditions": ["bệnh mãn tính"],
      "allergies": ["dị ứng"],
      "surgeries": ["phẫu thuật"]
    },
    "medications": [
      {
        "name": "tên thuốc",
        "dosage": "liều lượng"
      }
    ],
    "social_history": {
      "smoking": "hút thuốc",
      "alcohol": "rượu bia"
    }
  }
}
```

VÍ DỤ CỤ THỂ:
- Nếu bệnh nhân nói "Tôi tên Quốc, 30 tuổi" → trích xuất `{"demographics": {"name": "Quốc", "age": "30"}}`
- Nếu bệnh nhân nói "đau bụng từ sáng nay" → trích xuất `{"chief_complaint": {"main_complaint": "đau bụng", "duration": "từ sáng nay"}}`
- Nếu bệnh nhân nói "sốt 39 độ" → trích xuất `{"symptoms": [{"name": "sốt", "severity": "39 độ"}]}`

Luôn luôn tuân thủ định dạng JSON này và BẮT BUỘC phải có trường `data` với thông tin trích xuất được.
"""

    RED_FLAGS = [
        "đau ngực dữ dội",
        "khó thở nặng",
        "đau đầu dữ dội đột ngột",
        "mất ý thức",
        "co giật",
        "sốt cao trên 39°C",
        "nôn ra máu",
        "đi cầu ra máu",
        "đau bụng dữ dội",
        "tê liệt",
        "mất thị lực đột ngột"
    ]

    EMERGENCY_RESPONSE = """
⚠️ CẢNH BÁO: Triệu chứng bạn mô tả có thể nghiêm trọng.

🚨 VUI LÒNG ĐẾN KHOA CẤP CỨU NGAY LẬP TỨC hoặc gọi 115.

Đừng chờ đợi - hãy đi khám ngay để được xử lý kịp thời.
"""