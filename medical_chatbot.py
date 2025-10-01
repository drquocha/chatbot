import openai
import os
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from models import MedicalData, MedicalPrompts, PatientSession, db
from telegram_notifier import send_telegram_message
from language_manager import LanguageManager
from web_search import WebSearcher
import threading

class MedicalChatbot:
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.prompts = MedicalPrompts()
        self.language_manager = LanguageManager()
        self.web_searcher = WebSearcher()

    def create_session(self, language='vi') -> str:
        """Create new patient session"""
        session = PatientSession()
        session.language = language if language in ['vi', 'en'] else 'vi'
        session.set_patient_data(MedicalData.get_initial_structure())
        session.set_conversation_history([])

        db.session.add(session)
        db.session.commit()

        return session.id

    def get_session(self, session_id: str) -> Optional[PatientSession]:
        """Get patient session by ID"""
        return PatientSession.query.get(session_id)

    def check_red_flags(self, message: str, language='vi') -> bool:
        """Check for emergency symptoms"""
        message_lower = message.lower()
        red_flags = self.language_manager.get_red_flags(language)
        for flag in red_flags:
            if flag in message_lower:
                return True
        return False

    def get_clinical_prompt(self, patient_data: Dict, conversation: List) -> str:
        """Get adaptive clinical reasoning prompt"""

        # Ensure inputs are correct types
        if not isinstance(patient_data, dict):
            patient_data = {}
        if not isinstance(conversation, list):
            conversation = []

        # Analyze current clinical picture
        chief_complaint_data = patient_data.get('chief_complaint', {})
        if not isinstance(chief_complaint_data, dict):
            chief_complaint_data = {}
        chief_complaint = chief_complaint_data.get('main_complaint', '')

        symptoms = patient_data.get('symptoms', [])
        if not isinstance(symptoms, list):
            symptoms = []

        demographics = patient_data.get('demographics', {})
        if not isinstance(demographics, dict):
            demographics = {}

        # Recent conversation context
        recent_messages = [msg for msg in conversation[-6:] if isinstance(msg, dict) and msg.get('role') in ['user', 'assistant']]

        # Check for PubMed summary
        pubmed_summary = patient_data.get('pubmed_summary')
        pubmed_section = ""
        if pubmed_summary and pubmed_summary not in ["pending", "failed"]:
            pubmed_section = f"""


TÓM TẮT TỪ Y VĂN (PUBMED):
Dựa trên triệu chứng chính, đây là các hướng tiếp cận và chẩn đoán phân biệt tiềm năng:
{pubmed_summary}
Sử dụng thông tin này để hỏi các câu hỏi mục tiêu nhằm xác nhận hoặc loại trừ các khả năng trên.
"""

        # Safe formatting
        symptoms_text = []
        for s in symptoms:
            if isinstance(s, dict):
                symptoms_text.append(s.get('name', ''))
            else:
                symptoms_text.append(str(s))

        # Build prompt safely without f-strings
        patient_info = demographics.get('name', '') + ', ' + demographics.get('age', '') + ', ' + demographics.get('gender', '')
        symptoms_info = ', '.join(symptoms_text)
        patient_data_str = json.dumps(patient_data, ensure_ascii=False, indent=2)
        conversation_str = json.dumps(recent_messages[-4:], ensure_ascii=False, indent=2)

        prompt = """
TÌNH HÌNH LÂM SÀNG HIỆN TẠI:
Bệnh nhân: """ + patient_info + """
Vấn đề chính: """ + chief_complaint + """
Triệu chứng: """ + symptoms_info + pubmed_section + """

DỮ LIỆU ĐÃ THU THẬP:
""" + patient_data_str + """

CUỘC TRÒ CHUYỆN GẦN ĐÂY:
""" + conversation_str + """

CLINICAL REASONING:
Dựa vào thông tin hiện có, hãy quyết định câu hỏi tiếp theo theo nguyên tắc:
1. An toàn trước tiên - kiểm tra red flags nếu cần
2. Giá trị thông tin cao - hỏi để phân biệt chẩn đoán (sử dụng gợi ý từ PubMed nếu có)
3. Hiệu quả - tránh hỏi lại hoặc không liên quan

DISCRIMINATING QUESTIONS dựa vào chief complaint:
- Nếu đau bụng: vị trí, lan tỏa, sốt, nôn, đại tiện
- Nếu đau đầu: đột ngột/dần, vị trí, kèm buồn nôn/nhìn mờ
- Nếu ho: khô/có đờm, máu, sốt, khó thở
- Nếu đau ngực: tính chất, lan tỏa, khó thở, đổ mồ hôi

CHỈ hỏi tiền sử/thuốc/gia đình khi LIÊN QUAN trực tiếp đến vấn đề hiện tại.

🚨 NHIỆM VỤ BẮT BUỘC - TRÍCH XUẤT DỮ LIỆU:
Đây là quy tắc BẮNG BUỘC, KHÔNG THỂ BỎ QUA:

1. Sau MỖI câu trả lời của bệnh nhân, bạn PHẢI phân tích và trích xuất TOÀN BỘ thông tin y tế
2. Thông tin bao gồm: tên, tuổi, triệu chứng, thời gian, vị trí, mức độ, tiền sử, thuốc...
3. Đặt tất cả vào trường "data" với cấu trúc chuẩn:

CHUẨN TRÍCH XUẤT:
- Nếu bệnh nhân nói "tôi tên Quốc, 30 tuổi" → "demographics": {"name": "Quốc", "age": "30"}
- Nếu bệnh nhân nói "đau bụng từ hôm qua" → "chief_complaint": {"main_complaint": "đau bụng", "duration": "từ hôm qua"}
- Nếu bệnh nhân nói "sốt nhẹ, nôn" → "symptoms": [{"name": "sốt", "severity": "nhẹ"}, {"name": "nôn", "present": true}]

⚠️ LƯU Ý: Nếu trường "data" trống hoặc không có, hệ thống sẽ mất hết thông tin!

ĐỊNH DẠNG RESPONSE BẮT BUỘC:
Trả về JSON với cấu trúc:
- message: câu hỏi tiếp theo cho bệnh nhân
- action: continue/final_question/show_summary/complete
- clinical_reasoning: lý do lâm sàng của câu hỏi
- data: object chứa thông tin trích xuất được

VÍ DỤ CỤ THỂ:
data phải có: demographics (name, age, gender), chief_complaint (main_complaint, duration), symptoms (name, severity, location), medical_history, medications

QUAN TRỌNG: Trường "data" KHÔNG BAO GIỜ ĐƯỢC TRỐNG! Luôn phải có ít nhất thông tin vừa trích xuất được.
"""
        return prompt

    def process_message(self, session_id: str, user_message: str) -> Dict:
        """Process user message and return response using clinical reasoning"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        # Get session language
        session_language = session.language or 'vi'

        # Check for emergency symptoms
        if self.check_red_flags(user_message, session_language):
            return {
                "message": self.language_manager.get_emergency_response(session_language),
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

        # Build AI prompt
        # The stage_prompt is removed to allow for a more natural, AI-driven conversation flow
        # stage_prompt = self.get_stage_prompt(session.current_stage, patient_data, conversation)

        # Include the entire conversation for better context
        context_messages = []
        for msg in conversation:
            if isinstance(msg, dict) and msg.get('role') in ['user', 'assistant']:
                context_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })

        messages = [
            {"role": "system", "content": self.get_clinical_prompt(patient_data, conversation)}
        ]

        # Add context messages
        messages.extend(context_messages)

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
                raw_response = response.choices[0].message.content
                print(f"DEBUG: Raw AI response: {raw_response}")

                ai_response = json.loads(raw_response)
                print(f"DEBUG: Parsed AI response keys: {ai_response.keys()}")

                # Ensure ai_response is a dictionary
                if not isinstance(ai_response, dict):
                    ai_response = {
                        "message": str(ai_response),
                        "action": "continue"
                    }
            except Exception as e:
                # Fallback if JSON parsing fails
                ai_response = {
                    "message": response.choices[0].message.content,
                    "action": "continue"
                }

            # Adaptive clinical decision making
            message_lower = user_message.lower()
            conversation_length = len(conversation)

            # Ensure ai_response is a dictionary before proceeding
            if not isinstance(ai_response, dict):
                ai_response = {
                    "message": str(ai_response) if ai_response else "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
                    "action": "continue"
                }

            # Check current session status and handle accordingly
            current_status = session.status

            # Handle completion requests at any stage
            completion_keywords = ["hỏi lại", "mấy lần", "rồi đó", "được chưa", "!!!", "mắc mệt", "qua lẹ", "qua đi", "mất thời gian", "ăn chửi", "đủ rồi", "xong chưa", "kết thúc", "dừng lại", "thôi", "hết rồi", "xong rồi"]

            # Handle responses based on current status
            if current_status == 'final_question':
                # User is responding to "Còn câu gì muốn chia sẻ thêm không?"
                negative_responses = ["không", "không có", "hết rồi", "thôi", "xong", "ok", "được rồi"]
                positive_responses = ["có", "còn", "thêm"]

                if any(keyword in message_lower for keyword in negative_responses) or any(keyword in message_lower for keyword in completion_keywords):
                    ai_response["action"] = "show_summary"
                elif any(keyword in message_lower for keyword in positive_responses):
                    ai_response["action"] = "continue"
                    ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'additional_info')
                else:
                    # Extract any additional information provided
                    ai_response["action"] = "show_summary"

            elif current_status == 'awaiting_confirmation':
                # User is responding to summary confirmation
                confirmation_positive = ["có", "đúng", "chính xác", "ok", "được", "vâng"]
                confirmation_negative = ["không", "sai", "chưa đúng", "cần sửa", "bổ sung"]

                if any(keyword in message_lower for keyword in confirmation_positive) or any(keyword in message_lower for keyword in completion_keywords):
                    ai_response["action"] = "complete"
                    ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'completion_confirmed')
                elif any(keyword in message_lower for keyword in confirmation_negative):
                    ai_response["action"] = "need_more_info"
                    ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'need_correction')
                else:
                    # Treat any response as completion request
                    ai_response["action"] = "complete"
                    ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'general_completion')

            # General completion check for any stage
            elif any(keyword in message_lower for keyword in completion_keywords):
                if current_status in ['active', 'need_more_info']:
                    ai_response["action"] = "final_question"
                    ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'final_question')
                else:
                    ai_response["action"] = "complete"
                    ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'simple_completion')

            # Auto-complete if conversation too long, but follow proper workflow
            elif conversation_length > 15:
                ai_response["action"] = "final_question"
                ai_response["message"] = self.language_manager.get_workflow_message(session_language, 'lengthy_conversation')

            # Add AI response to conversation
            conversation.append({
                "role": "assistant",
                "content": ai_response.get("message", ""),
                "timestamp": datetime.now().isoformat(),
                "action": ai_response.get("action"),
                "data": ai_response.get("data")
            })

            # Update patient data if provided by AI, or extract from conversation
            if ai_response.get("data"):
                self.update_patient_data(patient_data, ai_response["data"])
                session.set_patient_data(patient_data)  # CRITICAL: Save to session
                print(f"DEBUG: Updated and saved patient data from AI")
            else:
                # If AI didn't provide structured data, try to extract it ourselves
                print(f"DEBUG: AI didn't provide data, extracting from message: '{user_message}'")
                extracted_data = self.extract_data_from_message(user_message, patient_data)
                print(f"DEBUG: Extracted data: {extracted_data}")
                if extracted_data:
                    self.update_patient_data(patient_data, extracted_data)
                    session.set_patient_data(patient_data)  # CRITICAL: Save to session
                    print(f"DEBUG: Updated and saved patient data from extraction")

            # === Start PubMed Search Thread ===
            patient_data = session.get_patient_data() # Re-get the latest data
            chief_complaint = patient_data.get('chief_complaint', {}).get('main_complaint')
            
            # Start search if a complaint exists and a search hasn't been started
            if chief_complaint and 'pubmed_summary' not in patient_data:
                # Add a placeholder to prevent starting multiple searches
                patient_data['pubmed_summary'] = "pending"
                session.set_patient_data(patient_data)
                db.session.commit()

                # Start the background search
                thread = threading.Thread(
                    target=self._search_and_store_pubmed_summary,
                    args=(session.id, chief_complaint)
                )
                thread.start()
            # =================================

            # Handle workflow actions
            completed = False
            progress = min(conversation_length * 10, 100)

            # Handle different action types
            action = ai_response.get("action")

            if action == "final_question":
                progress = 85
                session.status = 'final_question'
            elif action == "show_summary":
                # Generate preliminary summary for review
                summary_data = self._generate_preliminary_summary(patient_data)
                ai_response["message"] = f"Dựa trên thông tin bạn đã cung cấp, tôi tóm tắt lại như sau:\n\n{summary_data}\n\nThông tin trên có chính xác không? Có cần bổ sung gì thêm không?"
                progress = 95
                session.status = 'awaiting_confirmation'
            elif action == "need_more_info":
                progress = 80
                session.status = 'need_more_info'
            elif action in ["complete", "emergency"]:
                completed = True
                progress = 100
                session.status = 'completed'
            elif action == "continue" and current_status not in ['active']:
                # Reset to active if continuing from other states
                session.status = 'active'

            # Update session
            session.set_patient_data(patient_data)
            session.set_conversation_history(conversation)
            session.updated_at = datetime.utcnow()
            session.progress_percentage = progress

            # Stage progression based on conversation length
            conversation_length = len(conversation)
            if conversation_length > 15:  # Force completion after sufficient conversation
                session.current_stage = 7
                session.status = 'completed'
                session.progress_percentage = 100
            elif conversation_length > 12:
                session.current_stage = 6
            elif conversation_length > 9:
                session.current_stage = 5
            elif conversation_length > 6:
                session.current_stage = 4
            elif conversation_length > 4:
                session.current_stage = 3
            elif conversation_length > 2:
                session.current_stage = 2

            if session.current_stage > 6:
                session.status = 'completed'
                session.progress_percentage = 100

            # If conversation is complete, generate and return the final summary
            if session.status == 'completed' or ai_response.get("action") == "summarize":
                final_summary = self._generate_text_summary(patient_data)

                # Generate clinical insights for doctor
                clinical_insights = self._generate_clinical_insights(patient_data, conversation)
                doctor_message = f"{final_summary}\n\n{clinical_insights}"

                # Send the enhanced summary to Telegram
                send_telegram_message(doctor_message)

                return {
                    "message": final_summary,
                    "action": "end_session",
                    "stage": 7,
                    "progress": 100,
                    "completed": True
                }

            # For non-summary turns, save log and commit session
            self._save_conversation_log(session)
            db.session.commit()

            return {
                "message": ai_response.get("message", ""),
                "action": ai_response.get("action"),
                "stage": session.current_stage,
                "progress": session.progress_percentage,
                "completed": completed
            }

        except Exception as e:
            return {"error": f"Lỗi xử lý: {str(e)}"}

    def _search_and_store_pubmed_summary(self, session_id: str, query: str):
        """
        (Worker Thread) Searches PubMed and stores the summary in the session's patient_data.
        """
        try:
            summary = self.web_searcher.search_pubmed(query)
            if summary:
                # This runs in a separate thread, so we need to be careful with DB session.
                # For this implementation, we re-fetch the session and commit the single update.
                session = self.get_session(session_id)
                if session:
                    patient_data = session.get_patient_data()
                    patient_data['pubmed_summary'] = summary
                    session.set_patient_data(patient_data)
                    db.session.commit()
        except Exception as e:
            print(f"[THREAD ERROR] Failed to search PubMed for session {session_id}: {e}")
            # Optionally, update status to 'failed'
            session = self.get_session(session_id)
            if session:
                patient_data = session.get_patient_data()
                patient_data['pubmed_summary'] = "failed"
                session.set_patient_data(patient_data)
                db.session.commit()

    def update_patient_data(self, patient_data: Dict, new_data: Dict):
        """Update patient data with new information"""
        # Ensure both inputs are dictionaries
        if not isinstance(patient_data, dict):
            patient_data = {}
        if not isinstance(new_data, dict):
            return

        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if key in base_dict:
                    if isinstance(base_dict[key], dict) and isinstance(value, dict):
                        deep_update(base_dict[key], value)
                    elif isinstance(base_dict[key], list) and isinstance(value, list):
                        # Prevent duplicates for lists like symptoms and medications
                        if key in ['symptoms', 'medications']:
                            self._merge_unique_items(base_dict[key], value)
                        else:
                            base_dict[key].extend(value)
                    else:
                        base_dict[key] = value
                else:
                    base_dict[key] = value

        deep_update(patient_data, new_data)

    def _merge_unique_items(self, existing_list: list, new_items: list):
        """Merge items into list while avoiding duplicates"""
        for new_item in new_items:
            # Check if item already exists
            is_duplicate = False
            for existing_item in existing_list:
                if isinstance(new_item, dict) and isinstance(existing_item, dict):
                    # For symptoms and medications, check name similarity
                    if new_item.get('name', '').lower() == existing_item.get('name', '').lower():
                        # Update existing item with new details
                        existing_item.update(new_item)
                        is_duplicate = True
                        break
                elif str(new_item).lower() == str(existing_item).lower():
                    is_duplicate = True
                    break

            if not is_duplicate:
                existing_list.append(new_item)

    def extract_data_from_message(self, user_message: str, current_data: Dict) -> Dict:
        """Extract structured data from user message using pattern matching"""
        message_lower = user_message.lower()
        extracted = {}

        # Extract name (if demographics not already set)
        current_name = current_data.get('demographics', {}).get('name', '')
        if not current_name:
            # Look for common name patterns
            if any(phrase in message_lower for phrase in ['tôi tên', 'tên tôi', 'tôi là']):
                words = user_message.split()
                for i, word in enumerate(words):
                    if word.lower() in ['tên', 'là'] and i + 1 < len(words):
                        name = words[i + 1].strip(',.')
                        if name and len(name) > 1:
                            extracted['demographics'] = {'name': name}
                            break
            # Heuristic for single-word name reply
            elif len(user_message.split()) == 1 and len(user_message) > 1:
                 extracted['demographics'] = {'name': user_message.strip()}


        # Extract chief complaint (if not already set)
        current_complaint = current_data.get('chief_complaint', {}).get('main_complaint', '')
        if not current_complaint:
            pain_keywords = ['đau', 'nhức', 'khó chịu', 'ho', 'sốt', 'chóng mặt', 'buồn nôn', 'tiêu chảy']
            for keyword in pain_keywords:
                if keyword in message_lower:
                    extracted['chief_complaint'] = {'main_complaint': user_message.strip()}
                    break

        # Extract symptoms from current message
        symptoms = []

        # Helper function to check for negation
        def is_negated(symptom: str, message: str) -> bool:
            negation_patterns = [f'không {symptom}', f'chưa {symptom}', f'không có {symptom}']
            for pattern in negation_patterns:
                if pattern in message:
                    return True
            return False

        # Fever patterns
        import re
        if not is_negated('sốt', message_lower):
            fever_pattern = r'sốt.*?(\d+)\s*độ'
            fever_match = re.search(fever_pattern, message_lower)
            if fever_match:
                symptoms.append({
                    'name': 'sốt',
                    'severity': f"{fever_match.group(1)} độ"
                })
            elif 'sốt' in message_lower:
                symptoms.append({'name': 'sốt'})

        # Pain patterns with more detailed location extraction
        pain_locations = {
            'đau bụng': 'bụng',
            'đau đầu': 'đầu',
            'đau ngực': 'ngực',
            'thượng vị': 'thượng vị',
            'hạ sườn': 'hạ sườn',
            'đau lưng': 'lưng'
        }

        # Extract detailed pain description
        pain_info = {}
        if 'đau' in message_lower:
            # Look for severity ratings (x/10)
            severity_pattern = r'(\d+)/10'
            severity_match = re.search(severity_pattern, message_lower)
            if severity_match:
                pain_info['severity'] = f"{severity_match.group(1)}/10"

            # Extract location details
            location_details = []
            if 'thượng vị' in message_lower:
                location_details.append('thượng vị')
            if 'phía dưới' in message_lower and 'bên phải' in message_lower:
                location_details.append('phía dưới bên phải')
            elif 'bên phải' in message_lower:
                location_details.append('bên phải')
            elif 'bên trái' in message_lower:
                location_details.append('bên trái')

            if location_details:
                pain_info['location'] = ', '.join(location_details)

            # Find the main pain type
            for pain_type, location in pain_locations.items():
                if pain_type in message_lower:
                    pain_info['name'] = pain_type
                    if 'location' not in pain_info:
                        pain_info['location'] = location
                    break

            if pain_info.get('name'):
                symptoms.append(pain_info)

        # Other symptoms with severity modifiers
        other_symptoms = {
            'buồn nôn': 'buồn nôn',
            'nôn': 'nôn',
            'tiêu chảy': 'tiêu chảy',
            'chướng bụng': 'chướng bụng',
            'mệt mỏi': 'mệt mỏi',
            'khó thở': 'khó thở',
            'mệt': 'mệt mỏi'
        }

        for symptom_key, symptom_name in other_symptoms.items():
            if is_negated(symptom_key, message_lower):
                continue

            if symptom_key in message_lower:
                symptom_info = {'name': symptom_name}

                # Look for severity modifiers
                severity_modifiers = ['hơi', 'nhiều', 'rất', 'ít', 'nhẹ', 'nặng']
                for modifier in severity_modifiers:
                    # Check if modifier is near the symptom keyword to avoid mis-association
                    try:
                        if modifier in message_lower.split(symptom_key)[0].split()[-2:]:
                             symptom_info['severity'] = modifier
                             break
                    except IndexError:
                        continue

                symptoms.append(symptom_info)

        if symptoms:
            extracted['symptoms'] = symptoms

        # Extract time information
        time_patterns = ['từ sáng nay', 'từ hôm qua', 'từ tuần trước', 'từ tháng trước', 'bắt đầu từ']
        for pattern in time_patterns:
            if pattern in message_lower:
                if 'chief_complaint' not in extracted:
                    extracted['chief_complaint'] = {}
                extracted['chief_complaint']['duration'] = pattern
                break

        # Extract medical history
        medical_history = {}

        # Surgery history
        surgery_keywords = ['phẫu thuật', 'mổ', 'nội soi']
        procedure_keywords = ['thủng dạ dày', 'cắt ruột thừa', 'túi thừa đại tràng', 'nội soi']

        for keyword in surgery_keywords + procedure_keywords:
            if keyword in message_lower:
                if 'surgeries' not in medical_history:
                    medical_history['surgeries'] = []
                medical_history['surgeries'].append(user_message.strip())
                break

        # Chronic conditions
        chronic_keywords = ['bệnh tiểu đường', 'cao huyết áp', 'tim mạch', 'hen suyễn', 'viêm gan']
        for keyword in chronic_keywords:
            if keyword in message_lower:
                if 'chronic_conditions' not in medical_history:
                    medical_history['chronic_conditions'] = []
                medical_history['chronic_conditions'].append(keyword)

        # Allergies
        allergy_keywords = ['dị ứng', 'không dung nạp']
        for keyword in allergy_keywords:
            if keyword in message_lower:
                if 'allergies' not in medical_history:
                    medical_history['allergies'] = []
                # Extract just the allergen, not the whole message
                if 'dị ứng với' in message_lower:
                    allergen = message_lower.split('dị ứng với')[1].strip()
                    medical_history['allergies'].append(allergen)
                else:
                    medical_history['allergies'].append(user_message.strip())
                break

        if medical_history:
            extracted['medical_history'] = medical_history

        # Extract medications
        medications = []
        med_keywords = ['thuốc', 'aspirin', 'paracetamol', 'ibuprofen']
        for keyword in med_keywords:
            if keyword in message_lower:
                # Extract dosage pattern (number + mg/g + /day/ngày)
                import re
                dosage_pattern = r'(\d+)\s*(mg|g).*?/(ngày|day)'
                dosage_match = re.search(dosage_pattern, message_lower)

                if dosage_match:
                    med_name = keyword if keyword != 'thuốc' else user_message.strip()
                    medications.append({
                        'name': med_name,
                        'dosage': f"{dosage_match.group(1)}{dosage_match.group(2)}/{dosage_match.group(3)}"
                    })
                elif keyword != 'thuốc':
                    medications.append({'name': keyword})

        if medications:
            extracted['medications'] = medications

        # Extract social history including sensitive information
        social_history = {}
        if 'không hút thuốc' in message_lower:
            social_history['smoking'] = 'không'
        elif 'hút thuốc' in message_lower:
            social_history['smoking'] = 'có'

        if 'không uống rượu' in message_lower:
            social_history['alcohol'] = 'không'
        elif 'uống rượu' in message_lower or 'có uống rượu' in message_lower:
            social_history['alcohol'] = 'có'

        # Sexual history (important for anal conditions)
        if 'quan hệ đường hậu môn' in message_lower or 'quan hệ hậu môn' in message_lower:
            social_history['sexual_activity'] = 'quan hệ đường hậu môn'

        # Extract frequency if mentioned
        if 'ngày' in message_lower and any(char.isdigit() for char in message_lower):
            import re
            freq_match = re.search(r'(\d+).*?lần.*?ngày', message_lower)
            if freq_match:
                social_history['sexual_frequency'] = f"{freq_match.group(1)} lần/ngày"

        # Risk factors
        if 'biện pháp bảo vệ' in message_lower:
            if 'khi có khi không' in message_lower:
                social_history['protection'] = 'không thường xuyên'
            elif 'không' in message_lower:
                social_history['protection'] = 'không'
            else:
                social_history['protection'] = 'có'

        if social_history:
            extracted['social_history'] = social_history

        return extracted

    def _generate_preliminary_summary(self, patient_data: dict) -> str:
        """Generate a preliminary summary for patient review"""
        if not isinstance(patient_data, dict):
            patient_data = {}

        demographics = patient_data.get("demographics", {})
        chief_complaint = patient_data.get("chief_complaint", {})
        symptoms = patient_data.get("symptoms", [])
        history = patient_data.get("medical_history", {})
        medications = patient_data.get("medications", [])
        social_history = patient_data.get("social_history", {})

        summary = "**THÔNG TIN CÁ NHÂN:**\n"
        summary += f"- Họ tên: {demographics.get('name', 'Chưa có')}\n"

        summary += f"\n**VẤN ĐỀ CHÍNH:**\n"
        summary += f"- Triệu chứng: {chief_complaint.get('main_complaint', 'Chưa có')}\n"

        if symptoms:
            summary += f"\n**CÁC TRIỆU CHỨNG:**\n"
            for symptom in symptoms[:5]:  # Show first 5 symptoms
                if isinstance(symptom, dict):
                    name = symptom.get('name', '')
                    severity = f" ({symptom.get('severity')})" if symptom.get('severity') else ""
                    summary += f"- {name}{severity}\n"

        if history.get('surgeries'):
            summary += f"\n**TIỀN SỬ PHẪU THUẬT:**\n"
            for surgery in history['surgeries'][:3]:  # Show first 3
                summary += f"- {surgery}\n"

        if medications:
            summary += f"\n**THUỐC ĐANG DÙNG:**\n"
            for med in medications[:3]:  # Show first 3
                if isinstance(med, dict):
                    summary += f"- {med.get('name', '')} {med.get('dosage', '')}\n"

        return summary

    def _generate_clinical_insights(self, patient_data: dict, conversation: list) -> str:
        """Generate clinical insights for the doctor"""
        if not isinstance(patient_data, dict):
            patient_data = {}

        demographics = patient_data.get("demographics", {})
        chief_complaint = patient_data.get("chief_complaint", {})
        symptoms = patient_data.get("symptoms", [])
        history = patient_data.get("medical_history", {})
        medications = patient_data.get("medications", [])

        insights = "\n=== CLINICAL INSIGHTS CHO BÁC SĨ ===\n\n"

        # Differential Diagnosis
        insights += "**CHẨN ĐOÁN PHÂN BIỆT:**\n"
        main_complaint = chief_complaint.get('main_complaint', '').lower()

        if 'đau bụng' in main_complaint:
            insights += "- Viêm ruột thừa (nếu đau hạ sườn phải)\n"
            insights += "- Viêm túi mật (nếu đau thượng vị phải + sốt)\n"
            insights += "- Viêm dạ dày/loét dạ dày (nếu có tiền sử)\n"
            insights += "- Viêm tụy (nếu đau lan ra lưng)\n"
            insights += "- Tắc ruột (nếu có nôn + chướng bụng)\n"

        elif 'đau đầu' in main_complaint:
            insights += "- Migraine\n"
            insights += "- Căng thẳng thần kinh\n"
            insights += "- Tăng huyết áp\n"
            insights += "- Viêm xoang\n"

        elif 'ho' in main_complaint:
            insights += "- Viêm phế quản\n"
            insights += "- Viêm phổi\n"
            insights += "- Hen suyễn\n"
            insights += "- COPD\n"

        elif 'đau hậu môn' in main_complaint or 'hậu môn' in main_complaint:
            insights += "- Bệnh trĩ (nội trĩ, ngoại trĩ)\n"
            insights += "- Rạn kẽ hậu môn (anal fissure)\n"
            insights += "- Viêm áp xe hậu môn\n"
            insights += "- Polyp trực tràng\n"
            insights += "- Ung thư trực tràng (nếu tuổi >50)\n"
            insights += "- Chấn thương hậu môn\n"

        # Suggested Tests
        insights += "\n**ĐỀ NGHỊ XÉT NGHIỆM:**\n"
        if 'đau bụng' in main_complaint and any('sốt' in str(s).lower() for s in symptoms):
            insights += "- Công thức máu (WBC, CRP)\n"
            insights += "- Siêu âm bụng\n"
            insights += "- Amylase, Lipase (nếu nghi ngờ viêm tụy)\n"
            insights += "- Chức năng gan (AST, ALT, Bilirubin)\n"

        if 'đau hậu môn' in main_complaint or 'hậu môn' in main_complaint:
            insights += "- Công thức máu (loại trừ thiếu máu do mất máu mãn tính)\n"
            insights += "- Xét nghiệm phân tìm máu ẩn\n"
            insights += "- Nội soi trực tràng sigma (nếu cần)\n"
            insights += "- HIV test (nếu có yếu tố nguy cơ)\n"
            insights += "- Xét nghiệm STDs (Syphilis, Gonorrhea, Chlamydia)\n"

        if any('sốt' in str(s).lower() for s in symptoms):
            insights += "- Cấy máu (nếu sốt cao)\n"
            insights += "- Nước tiểu (tổng quát + cấy)\n"

        # Physical Examination Focus
        insights += "\n**KHÁM LÂM SÀNG CẦN CHÚ Ý:**\n"
        if 'đau bụng' in main_complaint:
            insights += "- Khám bụng: độ mềm, áp tâm, phản ứng thành bụng\n"
            insights += "- Dấu hiệu Murphy (viêm túi mật)\n"
            insights += "- Điểm McBurney (viêm ruột thừa)\n"
            insights += "- Kiểm tra ruột thừa: dấu Rovsing, Psoas\n"

        if 'đau hậu môn' in main_complaint or 'hậu môn' in main_complaint:
            insights += "- Khám vùng hậu môn: quan sát vết rạn, khối trĩ, sưng tấy\n"
            insights += "- Thăm trực tràng bằng tay (nếu bệnh nhân cho phép)\n"
            insights += "- Kiểm tra phản xạ hậu môn\n"
            insights += "- Quan sát tính chất máu: tươi, sậm, có cục máu đông\n"
            insights += "- Khám bẹn: sờ hạch lympho\n"

        # Red Flags to Watch
        insights += "\n**DẤU HIỆU CẢNH BÁO:**\n"
        red_flags = []
        if any('sốt' in str(s).lower() for s in symptoms):
            red_flags.append("Sốt cao >39°C - nghi ngờ nhiễm trùng nghiêm trọng")
        if 'nôn' in main_complaint.lower() or any('nôn' in str(s).lower() for s in symptoms):
            red_flags.append("Nôn liên tục - nghi ngờ tắc ruột")
        if history.get('surgeries'):
            red_flags.append("Tiền sử phẫu thuật - nghi ngờ biến chứng sau mổ")

        # Anal-specific red flags
        if 'đau hậu môn' in main_complaint or 'hậu môn' in main_complaint:
            bleeding_symptoms = [s for s in symptoms if 'máu' in str(s).lower() or 'chảy máu' in str(s).lower()]
            if bleeding_symptoms:
                red_flags.append("Chảy máu hậu môn - cần loại trừ ung thư trực tràng")

            # Check for high-risk sexual behavior
            conversation_text = ' '.join([msg.get('content', '') for msg in conversation if isinstance(msg, dict)])
            if 'quan hệ' in conversation_text.lower() or 'hiv' in conversation_text.lower():
                red_flags.append("Yếu tố nguy cơ cao STDs/HIV - cần xét nghiệm screening")

        for flag in red_flags:
            insights += f"⚠️ {flag}\n"

        # Risk Factors
        insights += "\n**YẾU TỐ NGUY CƠ:**\n"
        if medications:
            for med in medications:
                if isinstance(med, dict) and 'aspirin' in med.get('name', '').lower():
                    insights += "- Dùng Aspirin: nguy cơ loét dạ dày, xuất huyết tiêu hóa\n"

        if history.get('surgeries'):
            insights += f"- Tiền sử phẫu thuật: {', '.join(history['surgeries'])}\n"

        # Sexual health risk factors for anal conditions
        social_history = patient_data.get('social_history', {})
        if social_history.get('sexual_activity'):
            insights += f"- Hoạt động tình dục: {social_history['sexual_activity']}\n"
            if social_history.get('protection') == 'không thường xuyên':
                insights += "- Không sử dụng biện pháp bảo vệ thường xuyên - nguy cơ STDs\n"
            if social_history.get('sexual_frequency'):
                insights += f"- Tần suất cao ({social_history['sexual_frequency']}) - nguy cơ chấn thương\n"

        return insights

    def _generate_text_summary(self, patient_data: dict) -> str:
        """Generate a final text summary from patient data."""
        # Ensure patient_data is a dictionary
        if not isinstance(patient_data, dict):
            patient_data = {}

        demographics = patient_data.get("demographics", {})
        chief_complaint = patient_data.get("chief_complaint", {})
        symptoms = patient_data.get("symptoms", [])
        history = patient_data.get("medical_history", {})
        medications = patient_data.get("medications", [])
        family_history = patient_data.get("family_history", [])
        social_history = patient_data.get("social_history", {})

        # Ensure all retrieved values are of expected type
        if not isinstance(demographics, dict):
            demographics = {}
        if not isinstance(chief_complaint, dict):
            chief_complaint = {}
        if not isinstance(symptoms, list):
            symptoms = []
        if not isinstance(history, dict):
            history = {}
        if not isinstance(medications, list):
            medications = []
        if not isinstance(family_history, list):
            family_history = []
        if not isinstance(social_history, dict):
            social_history = {}

        summary = "### TÓM TẮT BỆNH SỬ ###\n\n"
        summary += f"**THÔNG TIN BỆNH NHÂN**\n"
        summary += f"- **Họ và tên:** {demographics.get('name', 'Chưa rõ')}\n"
        summary += f"- **Tuổi:** {demographics.get('age', 'Chưa rõ')}\n"
        summary += f"- **Giới tính:** {demographics.get('gender', 'Chưa rõ')}\n\n"

        summary += f"**LÝ DO ĐẾN KHÁM**\n"
        summary += f"- **Triệu chứng chính:** {chief_complaint.get('main_complaint', 'Chưa rõ')}\n\n"

        summary += "**BỆNH SỬ HIỆN TẠI**\n"
        summary += f"- **Mô tả:** {chief_complaint.get('description', 'Chưa có mô tả chi tiết')}\n"
        if symptoms:
            # Remove duplicates and format symptoms nicely
            unique_symptoms = []
            seen_symptoms = set()

            for s in symptoms:
                if isinstance(s, dict):
                    symptom_name = s.get('name', 'không rõ')
                    if symptom_name not in seen_symptoms:
                        symptom_detail = symptom_name
                        if s.get('severity'):
                            symptom_detail += f" ({s.get('severity')})"
                        if s.get('location') and s.get('location') != symptom_name:
                            symptom_detail += f" - {s.get('location')}"
                        unique_symptoms.append(symptom_detail)
                        seen_symptoms.add(symptom_name)
                else:
                    symptom_str = str(s)
                    if symptom_str not in seen_symptoms:
                        unique_symptoms.append(symptom_str)
                        seen_symptoms.add(symptom_str)

            summary += f"- **Các triệu chứng kèm theo:** {', '.join(unique_symptoms)}\n"
        summary += "\n"

        summary += "**TIỀN SỬ BỆNH**\n"
        if history.get('chronic_conditions'):
            summary += f"- **Bệnh mãn tính:** {', '.join(history['chronic_conditions'])}\n"
        if history.get('surgeries'):
            summary += f"- **Phẫu thuật:** {', '.join(history['surgeries'])}\n"
        if history.get('allergies'):
            summary += f"- **Dị ứng:** {', '.join(history['allergies'])}\n"
        if not any([history.get('chronic_conditions'), history.get('surgeries'), history.get('allergies')]):
            summary += "- Không có tiền sử bệnh đặc biệt\n"
        summary += "\n"

        if medications:
            summary += "**THUỐC ĐANG DÙNG**\n"
            # Remove duplicate medications
            unique_meds = []
            seen_meds = set()

            for med in medications:
                if isinstance(med, dict):
                    med_name = med.get('name', 'Chưa rõ').lower()
                    if med_name not in seen_meds:
                        summary += f"- {med.get('name', 'Chưa rõ')} ({med.get('dosage', 'liều lượng không rõ')})\n"
                        seen_meds.add(med_name)
                else:
                    med_str = str(med).lower()
                    if med_str not in seen_meds:
                        summary += f"- {str(med)}\n"
                        seen_meds.add(med_str)
            summary += "\n"

        if family_history:
            summary += f"**TIỀN SỬ GIA ĐÌNH**\n"
            summary += f"- {', '.join(family_history)}\n\n"

        if any(v for v in social_history.values() if v):
            summary += f"**LỐI SỐNG VÀ YẾU TỐ NGUY CƠ**\n"
            if social_history.get('smoking'):
                summary += f"- Hút thuốc: {social_history['smoking']}\n"
            if social_history.get('alcohol'):
                summary += f"- Rượu bia: {social_history['alcohol']}\n"
            if social_history.get('sexual_activity'):
                summary += f"- Hoạt động tình dục: {social_history['sexual_activity']}\n"
                if social_history.get('sexual_frequency'):
                    summary += f"- Tần suất: {social_history['sexual_frequency']}\n"
                if social_history.get('protection'):
                    summary += f"- Biện pháp bảo vệ: {social_history['protection']}\n"
            summary += "\n"
        
        summary += "---\n"
        summary += "Báo cáo này được tạo tự động. Thông tin chỉ mang tính tham khảo, không thay thế cho chẩn đoán của bác sĩ."
        
        return summary

    def _save_conversation_log(self, session: PatientSession):
        """Saves the entire session data to a log file."""
        try:
            log_dir = 'instance/logs'
            os.makedirs(log_dir, exist_ok=True)
            
            file_path = os.path.join(log_dir, f"{session.id}.json")
            
            log_data = {
                "sessionId": session.id,
                "createdAt": session.created_at.isoformat(),
                "updatedAt": session.updated_at.isoformat(),
                "status": session.status,
                "currentStage": session.current_stage,
                "progressPercentage": session.progress_percentage,
                "patientData": session.get_patient_data(),
                "conversationHistory": session.get_conversation_history()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[LOGGING ERROR] Failed to save log for session {session.id}: {e}")

    def get_session_summary(self, session_id: str) -> Dict:
        """Get session summary and progress"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        patient_data = session.get_patient_data()
        conversation = session.get_conversation_history()

        return {
            "session_id": session.id,
            "status": session.status,
            "current_stage": session.current_stage,
            "progress_percentage": session.progress_percentage,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "patient_data": patient_data,
            "conversation_history": conversation
        }

    def validate_session_data(self, session_id: str) -> Dict:
        """Validate session data completeness"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        patient_data = session.get_patient_data()
        if not isinstance(patient_data, dict):
            patient_data = {}

        validation_result = {
            "is_complete": True,
            "missing_fields": [],
            "warnings": []
        }

        # Check required demographics
        demographics = patient_data.get('demographics', {})
        if not isinstance(demographics, dict):
            demographics = {}

        if not demographics.get('name'):
            validation_result["missing_fields"].append("name")
            validation_result["is_complete"] = False

        # Check chief complaint
        chief_complaint = patient_data.get('chief_complaint', {})
        if not isinstance(chief_complaint, dict):
            chief_complaint = {}

        if not chief_complaint.get('main_complaint'):
            validation_result["missing_fields"].append("main_complaint")
            validation_result["is_complete"] = False

        return validation_result