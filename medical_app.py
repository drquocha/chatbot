from flask import Flask, render_template, request, jsonify, send_file, session as flask_session
import os
from dotenv import load_dotenv
from models import db, PatientSession, MedicalData
from medical_chatbot import MedicalChatbot
from report_generator import MedicalReportGenerator
import uuid
import tempfile
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'medical-chatbot-secret-key')

# Database configuration - Force SQLite for now
print("DEBUG: Forcing SQLite database")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_chatbot.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize chatbot and report generator
chatbot = MedicalChatbot()
report_generator = MedicalReportGenerator()

@app.before_request
def create_tables():
    if not hasattr(create_tables, "created"):
        db.create_all()
        create_tables.created = True

@app.route('/')
def index():
    return render_template('medical_index.html')

@app.route('/start-session', methods=['POST'])
def start_session():
    """Start new medical data collection session"""
    try:
        session_id = chatbot.create_session()
        flask_session['session_id'] = session_id

        return jsonify({
            'session_id': session_id,
            'message': 'Xin chào! Tôi là trợ lý y tế sẽ giúp bạn thu thập thông tin bệnh sử trước khi gặp bác sĩ. Quá trình này sẽ mất khoảng 10-15 phút và hoàn toàn bảo mật. Chúng ta bắt đầu nhé!\\n\\nTrước tiên, xin cho biết họ tên đầy đủ của bạn?',
            'stage': 1,
            'progress': 0
        })

    except Exception as e:
        return jsonify({'error': f'Không thể tạo phiên làm việc: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        session_id = flask_session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Phiên làm việc không tồn tại'}), 400

        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Tin nhắn không được để trống'}), 400

        # Process message through medical chatbot
        response = chatbot.process_message(session_id, user_message)

        if response.get('error'):
            return jsonify(response), 500

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Lỗi xử lý tin nhắn: {str(e)}'}), 500

@app.route('/session-summary/<session_id>')
def get_session_summary(session_id):
    """Get session summary and progress"""
    try:
        summary = chatbot.get_session_summary(session_id)
        if summary.get('error'):
            return jsonify(summary), 404

        return jsonify(summary)

    except Exception as e:
        return jsonify({'error': f'Lỗi lấy thông tin phiên: {str(e)}'}), 500

@app.route('/validate-session/<session_id>')
def validate_session(session_id):
    """Validate session data completeness"""
    try:
        validation = chatbot.validate_session_data(session_id)
        return jsonify(validation)

    except Exception as e:
        return jsonify({'error': f'Lỗi kiểm tra dữ liệu: {str(e)}'}), 500

@app.route('/generate-report/<session_id>')
def generate_report(session_id):
    """Generate and download PDF report"""
    try:
        # Get session summary
        summary = chatbot.get_session_summary(session_id)
        if summary.get('error'):
            return jsonify(summary), 404

        # Validate data
        validation = chatbot.validate_session_data(session_id)
        summary.update(validation)

        # Generate PDF report
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = report_generator.generate_report(summary, temp_file.name)

        # Generate filename
        patient_name = summary.get('patient_data', {}).get('demographics', {}).get('name', 'Benh_nhan')
        safe_name = ''.join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Benh_su_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'error': f'Lỗi tạo báo cáo: {str(e)}'}), 500

@app.route('/export-json/<session_id>')
def export_json(session_id):
    """Export session data as JSON"""
    try:
        # Get session summary
        summary = chatbot.get_session_summary(session_id)
        if summary.get('error'):
            return jsonify(summary), 404

        # Validate data
        validation = chatbot.validate_session_data(session_id)
        summary.update(validation)

        # Generate JSON file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        json_path = report_generator.generate_summary_json(summary, temp_file.name)

        # Generate filename
        patient_name = summary.get('patient_data', {}).get('demographics', {}).get('name', 'Benh_nhan')
        safe_name = ''.join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Benh_su_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

        return send_file(
            json_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({'error': f'Lỗi xuất dữ liệu: {str(e)}'}), 500

@app.route('/admin/sessions')
def admin_sessions():
    """Admin view of all sessions"""
    try:
        sessions = PatientSession.query.order_by(PatientSession.created_at.desc()).limit(50).all()

        sessions_data = []
        for session in sessions:
            patient_data = session.get_patient_data()
            patient_name = patient_data.get('demographics', {}).get('name', 'Chưa có tên')

            sessions_data.append({
                'id': session.id,
                'patient_name': patient_name,
                'status': session.status,
                'current_stage': session.current_stage,
                'progress_percentage': session.progress_percentage,
                'created_at': session.created_at.strftime('%d/%m/%Y %H:%M'),
                'updated_at': session.updated_at.strftime('%d/%m/%Y %H:%M')
            })

        return jsonify(sessions_data)

    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách phiên: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Medical Chatbot',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)