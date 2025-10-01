#!/usr/bin/env python3

import requests
import json

def chat_as_patient():
    print("🏥 LIVE TEST - Tôi sẽ đóng vai BỆNH NHÂN")
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

    # Simulate realistic patient interaction
    patient_responses = [
        "Chào bác sĩ, em tên Lê Thị Mai",
        "Em 28 tuổi ạ",
        "Em bị đau bụng từ hôm qua ạ",
        "Đau ở vùng bụng dưới bên phải, đau âm ỉ rồi chuyển thành đau nhói",
        "Từ tối qua đến giờ, khoảng 18 tiếng rồi ạ. Đau mức 7/10",
        "Em có nôn 2 lần, sốt nhẹ khoảng 37.8 độ",
        "Đau khi đi bộ, khi ho hay hắt hơi cũng đau hơn",
        "Em không có tiền sử phẫu thuật gì ạ",
        "Không dị ứng thuốc gì ạ",
        "Em chưa uống thuốc gì hết",
        "Gia đình em không ai bị bệnh gì đặc biệt",
        "Em không hút thuốc, không uống rượu",
        "Không có gì thêm ạ"
    ]

    for i, response in enumerate(patient_responses):
        print(f"👤 Bệnh nhân: {response}")

        # Send message
        chat_response = session.post('http://localhost:5001/chat',
                                   json={'message': response})

        if chat_response.status_code == 200:
            data = chat_response.json()
            print(f"🤖 Bác sĩ AI: {data['message']}")
            print(f"📊 Tiến độ: {data.get('progress', 0)}% | Giai đoạn: {data.get('stage', 1)}")

            if data.get('completed'):
                print("\n🎉 HOÀN THÀNH THU THẬP BỆNH SỬ!")
                break
            elif data.get('action') == 'emergency':
                print("\n🚨 CẢNH BÁO KHẨN CẤP!")
                break

        else:
            print(f"❌ Lỗi: {chat_response.status_code} - {chat_response.text}")
            break

        print("-" * 50)

    # Try to get final summary
    print("\n📋 Lấy tóm tắt cuối...")
    try:
        summary_response = session.get(f'http://localhost:5001/session-summary/{session_id}')
        if summary_response.status_code == 200:
            summary = summary_response.json()
            print("✅ TÓM TẮT BỆNH SỬ:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Không lấy được tóm tắt: {summary_response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi lấy tóm tắt: {e}")

if __name__ == "__main__":
    chat_as_patient()