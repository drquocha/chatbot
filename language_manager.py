"""
Language Manager for Medical Chatbot
Supports Vietnamese and English languages
"""

class LanguageManager:
    def __init__(self):
        self.languages = {
            'vi': {
                'system_prompt': """Bạn là một AI trợ lý y tế chuyên nghiệp hỗ trợ thu thập bệnh sử. Nhiệm vụ của bạn là:

1. Thu thập thông tin bệnh sử một cách có hệ thống và an toàn
2. Đặt câu hỏi theo thứ tự logic, từ tổng quát đến chi tiết
3. Trả lời dưới dạng JSON với format: {"message": "nội dung", "action": "continue"}
4. Sử dụng ngôn ngữ thân thiện, dễ hiểu
5. Ưu tiên an toàn - luôn khuyến khích gặp bác sĩ nếu có dấu hiệu nghiêm trọng

QUAN TRỌNG: Luôn trả về JSON hợp lệ. Không bao giờ chẩn đoán hoặc đưa ra lời khuyên y tế.""",

                'red_flags': [
                    'đau ngực dữ dội', 'khó thở nặng', 'mất ý thức', 'co giật',
                    'đau đầu dữ dội đột ngột', 'nôn máu', 'đau bụng dữ dội',
                    'sốt cao trên 39 độ', 'khó thở khi nghỉ ngơi'
                ],

                'emergency_response': "⚠️ CẢNH BÁO: Các triệu chứng bạn mô tả có thể nghiêm trọng. Vui lòng GỌI 115 hoặc ĐẾN BỆNH VIỆN NGAY LẬP TỨC. Đây không phải lúc để thu thập thông tin mà cần cấp cứu y tế ngay.",

                'ui_text': {
                    'title': 'Hệ thống Thu thập Bệnh sử Y tế',
                    'subtitle': 'Thu thập thông tin an toàn, chính xác và có cấu trúc',
                    'welcome_title': 'Chào mừng bạn đến với hệ thống thu thập bệnh sử',
                    'welcome_description': 'Hệ thống sẽ giúp bạn chuẩn bị thông tin y tế một cách có cấu trúc trước khi gặp bác sĩ. Quá trình này hoàn toàn bảo mật và mất khoảng 10-15 phút.',
                    'welcome_note': 'Đây chỉ là công cụ thu thập thông tin, không thay thế việc khám bác sĩ trực tiếp.',
                    'start_button': 'Bắt đầu thu thập thông tin',
                    'input_placeholder': 'Nhập câu trả lời của bạn...',
                    'send_button': 'Gửi',
                    'typing_indicator': 'Đang soạn tin...',
                    'progress_text': 'hoàn thành',
                    'completed_title': 'Hoàn thành thu thập thông tin!',
                    'completed_description': 'Cảm ơn bạn đã cung cấp thông tin. Bạn có thể tải báo cáo bệnh sử để mang theo khi đi khám.',
                    'download_pdf': 'Tải báo cáo PDF',
                    'export_json': 'Xuất dữ liệu JSON',
                    'quick_buttons': {
                        'yes': 'Có',
                        'no': 'Không',
                        'not_remember': 'Không nhớ rõ',
                        'not_have': 'Chưa có'
                    },
                    'language_switch': 'English'
                },

                'error_messages': {
                    'empty_message': 'Tin nhắn không được để trống',
                    'processing_error': 'Lỗi xử lý tin nhắn',
                    'connection_error': 'Lỗi kết nối',
                    'session_not_found': 'Không tìm thấy phiên làm việc'
                },

                'workflow_messages': {
                    'additional_info': 'Vâng, bạn hãy chia sẻ thêm thông tin đó với tôi.',
                    'completion_confirmed': 'Cảm ơn bạn đã xác nhận thông tin. Chúng ta đã hoàn thành việc thu thập bệnh sử. Báo cáo đã được tạo và gửi cho bác sĩ.',
                    'need_correction': 'Tôi hiểu. Bạn có thể cho tôi biết thêm thông tin cần bổ sung hoặc sửa đổi không?',
                    'general_completion': 'Cảm ơn bạn. Chúng ta đã hoàn thành việc thu thập bệnh sử. Báo cáo đã được tạo và gửi cho bác sĩ.',
                    'final_question': 'Tôi hiểu bạn muốn kết thúc. Trước khi hoàn tất, còn câu gì bạn muốn chia sẻ thêm với mình không?',
                    'simple_completion': 'Cảm ơn bạn đã cung cấp thông tin. Chúng ta đã hoàn thành việc thu thập bệnh sử.',
                    'lengthy_conversation': 'Cảm ơn bạn đã cung cấp nhiều thông tin hữu ích. Còn câu gì bạn muốn chia sẻ thêm với mình không?',
                    'initial_greeting': 'Xin chào! Tôi là trợ lý y tế sẽ giúp bạn thu thập thông tin bệnh sử trước khi gặp bác sĩ. Quá trình này sẽ mất khoảng 10-15 phút và hoàn toàn bảo mật. Chúng ta bắt đầu nhé!\\n\\nTrước tiên, xin cho biết họ tên đầy đủ của bạn?'
                }
            },

            'en': {
                'system_prompt': """You are a professional medical AI assistant specializing in medical history collection. Your tasks are:

1. Systematically and safely collect medical history information
2. Ask questions in logical order, from general to specific
3. Respond in JSON format: {"message": "content", "action": "continue"}
4. Use friendly, easy-to-understand language
5. Prioritize safety - always encourage seeing a doctor for serious symptoms

IMPORTANT: Always return valid JSON. Never diagnose or provide medical advice.""",

                'red_flags': [
                    'severe chest pain', 'severe shortness of breath', 'loss of consciousness', 'seizures',
                    'sudden severe headache', 'vomiting blood', 'severe abdominal pain',
                    'high fever over 102°F', 'difficulty breathing at rest'
                ],

                'emergency_response': "⚠️ WARNING: The symptoms you describe may be serious. Please CALL 911 or GO TO THE EMERGENCY ROOM IMMEDIATELY. This is not the time to collect information but to seek immediate medical attention.",

                'ui_text': {
                    'title': 'Medical History Collection System',
                    'subtitle': 'Safe, accurate, and structured information gathering',
                    'welcome_title': 'Welcome to the Medical History Collection System',
                    'welcome_description': 'This system will help you prepare medical information in a structured way before seeing a doctor. This process is completely confidential and takes about 10-15 minutes.',
                    'welcome_note': 'This is only an information gathering tool, not a replacement for direct medical consultation.',
                    'start_button': 'Start Information Collection',
                    'input_placeholder': 'Enter your response...',
                    'send_button': 'Send',
                    'typing_indicator': 'Typing...',
                    'progress_text': 'complete',
                    'completed_title': 'Information Collection Complete!',
                    'completed_description': 'Thank you for providing the information. You can download the medical history report to bring with you to your appointment.',
                    'download_pdf': 'Download PDF Report',
                    'export_json': 'Export JSON Data',
                    'quick_buttons': {
                        'yes': 'Yes',
                        'no': 'No',
                        'not_remember': 'Don\'t remember',
                        'not_have': 'Don\'t have'
                    },
                    'language_switch': 'Tiếng Việt'
                },

                'error_messages': {
                    'empty_message': 'Message cannot be empty',
                    'processing_error': 'Message processing error',
                    'connection_error': 'Connection error',
                    'session_not_found': 'Session not found'
                },

                'workflow_messages': {
                    'additional_info': 'Yes, please share that additional information with me.',
                    'completion_confirmed': 'Thank you for confirming the information. We have completed the medical history collection. The report has been created and sent to the doctor.',
                    'need_correction': 'I understand. Could you please provide the additional information that needs to be added or corrected?',
                    'general_completion': 'Thank you. We have completed the medical history collection. The report has been created and sent to the doctor.',
                    'final_question': 'I understand you want to finish. Before we complete, is there anything else you would like to share with me?',
                    'simple_completion': 'Thank you for providing the information. We have completed the medical history collection.',
                    'lengthy_conversation': 'Thank you for providing so much useful information. Is there anything else you would like to share with me?',
                    'initial_greeting': 'Hello! I am a medical assistant who will help you collect medical history information before seeing a doctor. This process will take about 10-15 minutes and is completely confidential. Let\'s get started!\\n\\nFirst, could you please provide your full name?'
                }
            }
        }

    def get_text(self, language, key, subkey=None):
        """Get translated text for given language and key"""
        if language not in self.languages:
            language = 'vi'  # Default to Vietnamese

        lang_data = self.languages[language]

        if subkey:
            return lang_data.get(key, {}).get(subkey, '')

        return lang_data.get(key, '')

    def get_system_prompt(self, language='vi'):
        """Get system prompt for chatbot"""
        return self.get_text(language, 'system_prompt')

    def get_red_flags(self, language='vi'):
        """Get red flag symptoms list"""
        return self.get_text(language, 'red_flags')

    def get_emergency_response(self, language='vi'):
        """Get emergency response message"""
        return self.get_text(language, 'emergency_response')

    def get_ui_text(self, language='vi', key=None):
        """Get UI text translations"""
        if key:
            return self.get_text(language, 'ui_text', key)
        return self.get_text(language, 'ui_text')

    def get_error_message(self, language='vi', error_type='processing_error'):
        """Get error message translation"""
        return self.get_text(language, 'error_messages', error_type)

    def get_workflow_message(self, language='vi', message_type='additional_info'):
        """Get workflow message translation"""
        return self.get_text(language, 'workflow_messages', message_type)

    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.languages.keys())