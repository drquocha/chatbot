import openai
import os
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from models import MedicalData, MedicalPrompts, PatientSession, db

class MedicalChatbot:
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.prompts = MedicalPrompts()

    def create_session(self) -> str:
        """Create new patient session"""
        session = PatientSession()
        session.set_patient_data(MedicalData.get_initial_structure())
        session.set_conversation_history([])

        db.session.add(session)
        db.session.commit()

        return session.id

    def get_session(self, session_id: str) -> Optional[PatientSession]:
        """Get patient session by ID"""
        return PatientSession.query.get(session_id)

    def check_red_flags(self, message: str) -> bool:
        """Check for emergency symptoms"""
        message_lower = message.lower()
        for flag in self.prompts.RED_FLAGS:
            if flag in message_lower:
                return True
        return False

    def get_clinical_prompt(self, patient_data: Dict, conversation: List) -> str:
        """Get adaptive clinical reasoning prompt"""

        # Analyze current clinical picture
        chief_complaint = patient_data.get('chief_complaint', {}).get('main_complaint', '')
        symptoms = patient_data.get('symptoms', [])
        demographics = patient_data.get('demographics', {})

        # Recent conversation context
        recent_messages = [msg for msg in conversation[-6:] if msg.get('role') in ['user', 'assistant']]

        prompt = f"""
TÌNH HÌNH LÂM SÀNG HIỆN TẠI:
Bệnh nhân: {demographics.get('name', '')}, {demographics.get('age', '')}, {demographics.get('gender', '')}
Vấn đề chính: {chief_complaint}
Triệu chứng: {', '.join([s.get('name', '') if isinstance(s, dict) else str(s) for s in symptoms])}

DỮ LIỆU ĐÃ THU THẬP:
{json.dumps(patient_data, ensure_ascii=False, indent=2)}

CUỘC TRÒ CHUYỆN GẦN ĐÂY:
{json.dumps(recent_messages[-4:], ensure_ascii=False, indent=2)}

CLINICAL REASONING:
Dựa vào thông tin hiện có, hãy quyết định câu hỏi tiếp theo theo nguyên tắc:
1. An toàn trước tiên - kiểm tra red flags nếu cần
2. Giá trị thông tin cao - hỏi để phân biệt chẩn đoán
3. Hiệu quả - tránh hỏi lại hoặc không liên quan

DISCRIMINATING QUESTIONS dựa vào chief complaint:
- Nếu đau bụng: vị trí, lan tỏa, sốt, nôn, đại tiện
- Nếu đau đầu: đột ngột/dần, vị trí, kèm buồn nôn/nhìn mờ
- Nếu ho: khô/có đờm, máu, sốt, khó thở
- Nếu đau ngực: tính chất, lan tỏa, khó thở, đổ mồ hôi

CHỈ hỏi tiền sử/thuốc/gia đình khi LIÊN QUAN trực tiếp đến vấn đề hiện tại.

RESPONSE FORMAT: JSON hợp lệ với message, action, clinical_reasoning
"""
        return prompt

    def process_message(self, session_id: str, user_message: str) -> Dict:
        """Process user message and return response"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        # Check for emergency symptoms
        if self.check_red_flags(user_message):
            return {
                "message": self.prompts.EMERGENCY_RESPONSE,
                "action": "emergency",
                "emergency": True
            }

        # Get current data and conversation
        patient_data = session.get_patient_data()
        conversation = session.get_conversation_history()

        # Add user message to conversation
        conversation.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # Build AI prompt using clinical reasoning
        clinical_prompt = self.get_clinical_prompt(patient_data, conversation)

        # Include recent conversation for better context
        context_messages = []
        if len(conversation) > 1:
            # Add last few exchanges for context
            recent_conv = conversation[-4:]  # Last 4 messages
            for msg in recent_conv:
                if msg.get('role') in ['user', 'assistant']:
                    context_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })

        messages = [
            {"role": "system", "content": self.prompts.SYSTEM_PROMPT},
            {"role": "system", "content": clinical_prompt}
        ]

        # Add context messages
        messages.extend(context_messages)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            try:
                ai_response = json.loads(response.choices[0].message.content)
            except:
                # Fallback if JSON parsing fails
                ai_response = {
                    "message": response.choices[0].message.content,
                    "action": "continue"
                }

            # Adaptive clinical decision making
            message_lower = user_message.lower()

            # Check for completion signals
            conversation_length = len(conversation)
            demographics = patient_data.get('demographics', {})

            # Check for user frustration - always respect this
            frustration_keywords = ["hỏi lại", "mấy lần", "rồi đó", "được chưa", "!!!", "mắc mệt", "qua lẹ", "qua đi", "mất thời gian", "ăn chửi", "đủ rồi", "xong chưa"]
            if any(keyword in message_lower for keyword in frustration_keywords):
                ai_response["action"] = "complete"
                ai_response["message"] = "Cảm ơn bạn đã cung cấp thông tin. Tôi sẽ tổng hợp lại để tạo báo cáo bệnh sử. Bạn có thể tải báo cáo ở bên dưới."

            # Auto-complete if conversation too long
            elif conversation_length > 15:
                ai_response["action"] = "complete"
                ai_response["message"] = "Cảm ơn bạn đã cung cấp đầy đủ thông tin. Chúng ta đã hoàn thành quá trình thu thập bệnh sử. Bạn có thể tải báo cáo ở bên dưới."

            # Legacy compatibility check (can be removed later)
            if session.current_stage == 1:
                has_name = demographics.get('name') or any(word in message_lower for word in ['quốc', 'hà', 'tên'])
                has_gender = demographics.get('gender') or any(word in message_lower for word in ['nam', 'nữ'])

                if has_name and has_gender:
                    force_next_stage = True

            # Stage 2: Chief complaint - must ask about symptoms before moving
            elif session.current_stage == 2:
                chief_complaint = patient_data.get('chief_complaint', {})
                has_symptoms = chief_complaint.get('main_complaint') or any(word in message_lower for word in ['đau', 'khó', 'mệt', 'sốt', 'ho', 'chóng mặt'])

                # Count questions about symptoms
                symptom_questions = len([msg for msg in conversation[-6:] if msg.get('role') == 'assistant' and any(word in msg.get('content', '').lower() for word in ['triệu chứng', 'đau', 'khó', 'lý do khám'])])

                # Only move if we asked about symptoms OR user gave symptom info
                if symptom_questions >= 1 or has_symptoms:
                    # But give them chance to answer if they haven't provided symptoms yet
                    if not has_symptoms and symptom_questions < 2:
                        pass  # Don't force progression yet
                    else:
                        force_next_stage = True

            # Check for repetitive negative responses
            recent_user_messages = [msg.get("content", "").lower() for msg in conversation[-5:] if msg.get("role") == "user"]
            negative_responses = ["không", "không có", "chưa có", "không nhớ"]

            if any(neg in message_lower for neg in negative_responses):
                negative_count = sum(1 for msg in recent_user_messages if any(neg in msg for neg in negative_responses))
                if negative_count >= 2:
                    force_next_stage = True

            # Check for user frustration
            frustration_keywords = ["hỏi lại", "mấy lần", "rồi đó", "được chưa", "!!!", "mắc mệt", "qua lẹ", "qua đi", "mất thời gian", "ăn chửi"]
            if any(keyword in message_lower for keyword in frustration_keywords):
                force_next_stage = True

            # Force completion if conversation is too long
            if len(conversation) > 20:
                force_next_stage = True
                session.current_stage = 7  # Force completion

            # Override AI decision if needed
            if force_next_stage:
                ai_response["action"] = "next_stage"
                if len(conversation) > 25 or session.current_stage >= 7:
                    ai_response["message"] = "Cảm ơn bạn đã cung cấp thông tin. Chúng ta đã hoàn thành quá trình thu thập bệnh sử. Bạn có thể tải báo cáo ở bên dưới."
                elif session.current_stage == 1:
                    ai_response["message"] = "Cảm ơn bạn. Bây giờ hãy cho tôi biết lý do bạn đến khám và các triệu chứng hiện tại?"
                elif session.current_stage == 2:
                    ai_response["message"] = "Cảm ơn bạn. Bây giờ tôi hỏi về tiền sử bệnh. Bạn có từng mắc bệnh gì trước đây không? Hoặc có đang điều trị bệnh mãn tính nào không?"
                elif session.current_stage == 3:
                    ai_response["message"] = "Cảm ơn bạn. Bây giờ hỏi về thuốc. Bạn hiện tại có đang dùng thuốc gì không? Kể cả thuốc kê đơn hay thuốc tự mua?"
                elif session.current_stage == 4:
                    ai_response["message"] = "Cảm ơn bạn. Về xét nghiệm, bạn có làm xét nghiệm nào trong 6 tháng gần đây không?"
                elif session.current_stage == 5:
                    ai_response["message"] = "Cuối cùng, tôi hỏi về gia đình. Có ai trong gia đình bạn mắc bệnh di truyền hoặc bệnh mãn tính không?"
                elif session.current_stage == 6:
                    ai_response["message"] = "Cảm ơn bạn đã cung cấp thông tin. Chúng ta đã hoàn thành quá trình thu thập bệnh sử. Bạn có thể tải báo cáo ở bên dưới."
                elif session.current_stage == 7:
                    ai_response["message"] = "Cảm ơn bạn đã cung cấp thông tin. Chúng ta đã hoàn thành quá trình thu thập bệnh sử. Bạn có thể tải báo cáo ở bên dưới."
                else:
                    ai_response["message"] = "Cảm ơn bạn. Chúng ta chuyển sang phần tiếp theo nhé."

            # Add AI response to conversation
            conversation.append({
                "role": "assistant",
                "content": ai_response.get("message", ""),
                "timestamp": datetime.now().isoformat(),
                "action": ai_response.get("action"),
                "data": ai_response.get("data")
            })

            # Update patient data if provided
            if ai_response.get("data"):
                self.update_patient_data(patient_data, ai_response["data"])

            # Handle stage progression
            if ai_response.get("action") == "next_stage" or force_next_stage:
                session.current_stage = min(session.current_stage + 1, 7)  # Allow going to stage 7 to complete
                session.progress_percentage = int((session.current_stage - 1) / 6 * 100)

                # Force completion if we've been through enough stages
                conversation_length = len(conversation)
                if conversation_length > 30 or session.current_stage >= 7:  # After 30 messages or stage 7
                    session.current_stage = 7
                    session.status = 'completed'
                    session.progress_percentage = 100

            # Update session
            session.set_patient_data(patient_data)
            session.set_conversation_history(conversation)
            session.updated_at = datetime.utcnow()

            if session.current_stage > 6:
                session.status = 'completed'
                session.progress_percentage = 100

            db.session.commit()

            return {
                "message": ai_response.get("message", ""),
                "action": ai_response.get("action"),
                "stage": session.current_stage,
                "progress": session.progress_percentage,
                "completed": session.status == 'completed'
            }

        except Exception as e:
            return {"error": f"Lỗi xử lý: {str(e)}"}

    def update_patient_data(self, patient_data: Dict, new_data: Dict):
        """Update patient data with new information"""
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if key in base_dict:
                    if isinstance(base_dict[key], dict) and isinstance(value, dict):
                        deep_update(base_dict[key], value)
                    elif isinstance(base_dict[key], list) and isinstance(value, list):
                        base_dict[key].extend(value)
                    else:
                        base_dict[key] = value
                else:
                    base_dict[key] = value

        deep_update(patient_data, new_data)

    def get_session_summary(self, session_id: str) -> Dict:
        """Get session summary for progress tracking"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        stages_info = MedicalData.get_stage_questions()
        patient_data = session.get_patient_data()

        return {
            "session_id": session_id,
            "status": session.status,
            "current_stage": session.current_stage,
            "progress_percentage": session.progress_percentage,
            "stages": {
                i: {
                    "name": stage["name"],
                    "completed": i < session.current_stage,
                    "current": i == session.current_stage
                }
                for i, stage in stages_info.items()
            },
            "patient_data": patient_data,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }

    def validate_session_data(self, session_id: str) -> Dict:
        """Validate completeness of collected data"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        patient_data = session.get_patient_data()
        missing_fields = []
        warnings = []

        # Check required fields
        if not patient_data.get("demographics", {}).get("name"):
            missing_fields.append("Họ tên")

        if not patient_data.get("demographics", {}).get("age"):
            missing_fields.append("Tuổi")

        if not patient_data.get("chief_complaint", {}).get("main_complaint"):
            missing_fields.append("Lý do khám chính")

        # Check for potential issues
        if patient_data.get("medications") and not patient_data.get("medical_history", {}).get("allergies"):
            warnings.append("Chưa hỏi về dị ứng thuốc")

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "warnings": warnings,
            "completion_score": max(0, 100 - len(missing_fields) * 10 - len(warnings) * 5)
        }