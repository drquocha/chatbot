#!/usr/bin/env python3

import requests
import json

def complete_patient_test():
    print("🏥 COMPLETE PATIENT TEST - TRIGGER TELEGRAM")
    print("=" * 60)

    session = requests.Session()

    # Start session
    print("🤖 Khởi tạo session...")
    response = session.post('http://localhost:5001/start-session', json={})
    data = response.json()
    session_id = data['session_id']

    print(f"✅ Session ID: {session_id}")
    print(f"🤖 Bot: {data['message']}")
    print()

    # Complete patient interaction to trigger completion
    patient_responses = [
        "Chào bác sĩ, em tên Trần Văn Minh",
        "Em 32 tuổi ạ",
        "Em bị đau bụng từ sáng nay",
        "Đau ở vùng bụng dưới bên phải, đau nhói, mức 8/10",
        "Em có nôn 1 lần và sốt 38.2 độ",
        "Đau khi đi lại, ho cũng đau hơn",
        "Em không có tiền sử phẫu thuật",
        "Không dị ứng thuốc nào",
        "Em chưa uống thuốc gì",
        "Gia đình không có tiền sử bệnh gì",
        "Em không hút thuốc không uống rượu",
        "Thông tin này chính xác rồi ạ, em xác nhận"
    ]

    for i, response in enumerate(patient_responses):
        print(f"👤 Bệnh nhân: {response}")

        # Send message
        chat_response = session.post('http://localhost:5001/chat',
                                   json={'message': response})

        if chat_response.status_code == 200:
            data = chat_response.json()
            print(f"🤖 Bác sĩ AI: {data['message'][:80]}...")
            print(f"📊 Tiến độ: {data.get('progress', 0)}% | Giai đoạn: {data.get('stage', 1)}")

            if data.get('completed'):
                print("\n🎉 HOÀN THÀNH THU THẬP BỆNH SỬ!")
                print("📨 Telegram notification should be sent now!")
                break
            elif data.get('action') == 'emergency':
                print("\n🚨 CẢNH BÁO KHẨN CẤP!")
                break

        else:
            print(f"❌ Lỗi: {chat_response.status_code} - {chat_response.text}")
            break

        print("-" * 50)

    # Get final summary
    print("\n📋 Lấy tóm tắt cuối...")
    try:
        summary_response = session.get(f'http://localhost:5001/session-summary/{session_id}')
        if summary_response.status_code == 200:
            summary = summary_response.json()
            print("✅ TÓM TẮT BỆNH SỬ HOÀN CHỈNH:")
            print(f"Tên: {summary.get('patient_data', {}).get('demographics', {}).get('name', 'N/A')}")
            print(f"Tuổi: {summary.get('patient_data', {}).get('demographics', {}).get('age', 'N/A')}")
            print(f"Triệu chứng chính: {summary.get('patient_data', {}).get('chief_complaint', {}).get('main_complaint', 'N/A')}")
            print(f"Trạng thái: {summary.get('status', 'N/A')}")

            if summary.get('status') == 'completed':
                print("🎯 SESSION COMPLETED SUCCESSFULLY!")
                print("📨 TELEGRAM NOTIFICATION SHOULD BE SENT!")
        else:
            print(f"❌ Không lấy được tóm tắt: {summary_response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi lấy tóm tắt: {e}")

if __name__ == "__main__":
    complete_patient_test()