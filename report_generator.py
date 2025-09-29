from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import json
import os

class MedicalReportGenerator:
    def __init__(self):
        # Try to register Vietnamese font
        try:
            font_path = "/System/Library/Fonts/Arial.ttf"  # macOS path
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
        except:
            pass  # Use default font if Vietnamese font not available

        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles for medical report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            fontName='Helvetica-Bold',
            fontSize=16,
            spaceAfter=12,
            alignment=1  # Center
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=12,
            spaceAfter=6,
            textColor=colors.blue
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBody',
            fontName='Helvetica',
            fontSize=10,
            spaceAfter=6
        ))

        self.styles.add(ParagraphStyle(
            name='Important',
            fontName='Helvetica-Bold',
            fontSize=10,
            spaceAfter=6,
            textColor=colors.red
        ))

    def generate_report(self, session_data: dict, output_path: str) -> str:
        """Generate PDF medical report"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []
        patient_data = session_data.get('patient_data', {})

        # Header
        story.append(Paragraph("BÁO CÁO BỆNH SỬ", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))

        # Patient Information
        story.append(Paragraph("THÔNG TIN BỆNH NHÂN", self.styles['SectionHeader']))
        demographics = patient_data.get('demographics', {})

        patient_info = [
            ['Họ tên:', demographics.get('name', 'Không có')],
            ['Tuổi:', demographics.get('age', 'Không có')],
            ['Giới tính:', demographics.get('gender', 'Không có')],
            ['Nghề nghiệp:', demographics.get('occupation', 'Không có')],
            ['Địa chỉ:', demographics.get('address', 'Không có')],
            ['Số điện thoại:', demographics.get('phone', 'Không có')],
            ['Ngày thu thập:', datetime.now().strftime('%d/%m/%Y %H:%M')]
        ]

        patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(patient_table)
        story.append(Spacer(1, 12))

        # Chief Complaint
        story.append(Paragraph("LÝ DO KHÁM BỆNH", self.styles['SectionHeader']))
        chief_complaint = patient_data.get('chief_complaint', {})

        complaint_text = f"""
        Lý do chính: {chief_complaint.get('main_complaint', 'Không có')}<br/>
        Thời gian xuất hiện: {chief_complaint.get('duration', 'Không rõ')}<br/>
        Khởi phát: {chief_complaint.get('onset', 'Không rõ')}<br/>
        Mô tả chi tiết: {chief_complaint.get('description', 'Không có')}
        """
        story.append(Paragraph(complaint_text, self.styles['CustomBody']))
        story.append(Spacer(1, 12))

        # Symptoms
        symptoms = patient_data.get('symptoms', [])
        if symptoms:
            story.append(Paragraph("TRIỆU CHỨNG", self.styles['SectionHeader']))
            for i, symptom in enumerate(symptoms, 1):
                symptom_text = f"{i}. {symptom.get('name', '')}"
                if symptom.get('duration'):
                    symptom_text += f" (Thời gian: {symptom['duration']})"
                if symptom.get('severity'):
                    symptom_text += f" (Mức độ: {symptom['severity']}/10)"
                story.append(Paragraph(symptom_text, self.styles['CustomBody']))
            story.append(Spacer(1, 12))

        # Medical History
        story.append(Paragraph("TIỀN SỬ BỆNH", self.styles['SectionHeader']))
        med_history = patient_data.get('medical_history', {})

        # Chronic conditions
        chronic = med_history.get('chronic_conditions', [])
        if chronic:
            story.append(Paragraph("Bệnh mãn tính:", self.styles['CustomBody']))
            for condition in chronic:
                story.append(Paragraph(f"• {condition}", self.styles['CustomBody']))

        # Surgeries
        surgeries = med_history.get('surgeries', [])
        if surgeries:
            story.append(Paragraph("Phẫu thuật:", self.styles['CustomBody']))
            for surgery in surgeries:
                story.append(Paragraph(f"• {surgery}", self.styles['CustomBody']))

        # Allergies
        allergies = med_history.get('allergies', [])
        if allergies:
            story.append(Paragraph("Dị ứng:", self.styles['Important']))
            for allergy in allergies:
                story.append(Paragraph(f"• {allergy}", self.styles['Important']))

        story.append(Spacer(1, 12))

        # Medications
        medications = patient_data.get('medications', [])
        if medications:
            story.append(Paragraph("THUỐC ĐANG SỬ DỤNG", self.styles['SectionHeader']))

            med_data = []
            med_data.append(['Tên thuốc', 'Liều lượng', 'Tần suất', 'Thời gian dùng'])

            for med in medications:
                med_data.append([
                    med.get('name', ''),
                    med.get('dosage', ''),
                    med.get('frequency', ''),
                    med.get('duration', '')
                ])

            if len(med_data) > 1:  # Has data beyond header
                med_table = Table(med_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                med_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
                ]))
                story.append(med_table)

        story.append(Spacer(1, 12))

        # Family History
        family_history = patient_data.get('family_history', [])
        if family_history:
            story.append(Paragraph("TIỀN SỬ GIA ĐÌNH", self.styles['SectionHeader']))
            for history in family_history:
                story.append(Paragraph(f"• {history}", self.styles['CustomBody']))
            story.append(Spacer(1, 12))

        # Social History
        social_history = patient_data.get('social_history', {})
        if any(social_history.values()):
            story.append(Paragraph("YẾU TỐ XÃ HỘI", self.styles['SectionHeader']))

            social_info = []
            if social_history.get('smoking'):
                social_info.append(f"Hút thuốc: {social_history['smoking']}")
            if social_history.get('alcohol'):
                social_info.append(f"Uống rượu: {social_history['alcohol']}")
            if social_history.get('exercise'):
                social_info.append(f"Tập thể dục: {social_history['exercise']}")
            if social_history.get('diet'):
                social_info.append(f"Chế độ ăn: {social_history['diet']}")

            for info in social_info:
                story.append(Paragraph(f"• {info}", self.styles['CustomBody']))

            story.append(Spacer(1, 12))

        # Recent Labs
        recent_labs = patient_data.get('recent_labs', [])
        if recent_labs:
            story.append(Paragraph("XÉT NGHIỆM GẦN ĐÂY", self.styles['SectionHeader']))
            for lab in recent_labs:
                lab_text = f"• {lab.get('name', '')} ({lab.get('date', '')}): {lab.get('result', '')}"
                story.append(Paragraph(lab_text, self.styles['CustomBody']))
            story.append(Spacer(1, 12))

        # AI Notes
        ai_notes = patient_data.get('ai_notes', {})
        if ai_notes:
            story.append(Paragraph("GHI CHÚ TỪ HỆ THỐNG", self.styles['SectionHeader']))

            # Red flags
            red_flags = ai_notes.get('red_flags', [])
            if red_flags:
                story.append(Paragraph("⚠️ Điểm cần lưu ý:", self.styles['Important']))
                for flag in red_flags:
                    story.append(Paragraph(f"• {flag}", self.styles['Important']))

            # Summary
            summary = ai_notes.get('summary', '')
            if summary:
                story.append(Paragraph("Tóm tắt:", self.styles['CustomBody']))
                story.append(Paragraph(summary, self.styles['CustomBody']))

            # Recommendations
            recommendations = ai_notes.get('recommendations', [])
            if recommendations:
                story.append(Paragraph("Khuyến nghị:", self.styles['CustomBody']))
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", self.styles['CustomBody']))

        # Footer
        story.append(Spacer(1, 24))
        story.append(Paragraph("---", self.styles['CustomBody']))
        story.append(Paragraph(
            "Báo cáo này được tạo tự động từ hệ thống thu thập bệnh sử. "
            "Vui lòng mang theo khi đến khám để bác sĩ tham khảo.",
            self.styles['CustomBody']
        ))

        # Build PDF
        doc.build(story)
        return output_path

    def generate_summary_json(self, session_data: dict, output_path: str) -> str:
        """Generate JSON summary for API integration"""
        summary = {
            "generated_at": datetime.now().isoformat(),
            "session_id": session_data.get('session_id'),
            "patient_data": session_data.get('patient_data', {}),
            "completion_status": session_data.get('status'),
            "data_quality": {
                "completeness_score": session_data.get('completion_score', 0),
                "missing_fields": session_data.get('missing_fields', []),
                "warnings": session_data.get('warnings', [])
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        return output_path