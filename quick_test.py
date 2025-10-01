#!/usr/bin/env python3

import requests
import json

def test_chatbot():
    print("🤖 TESTING MEDICAL CHATBOT")
    print("=" * 50)

    session = requests.Session()

    # 1. Start session
    print("1. Starting session...")
    response = session.post('http://localhost:5001/start-session', json={})
    if response.status_code != 200:
        print("❌ Failed to start session")
        return

    data = response.json()
    print(f"✅ Session started: {data['session_id']}")
    print(f"🤖 Bot: {data['message']}")

    # 2. Simulate conversation
    messages = [
        "Tôi tên là Nguyễn Văn Quốc",
        "30 tuổi",
        "đau răng số 7 bên phải",
        "đau từ 2 ngày nay, rất đau, 8/10",
        "sưng nướu, sốt nhẹ",
        "không có tiền sử bệnh gì",
        "không dị ứng thuốc",
        "không"  # final question
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n{i+1}. 👤 User: {msg}")

        response = session.post('http://localhost:5001/chat',
                              json={'message': msg})

        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Bot: {data['message'][:100]}...")
            print(f"📊 Progress: {data.get('progress', 0)}%")

            if data.get('completed'):
                print("🎉 Session completed!")
                break
        else:
            print(f"❌ Error: {response.status_code}")
            break

    # 3. Get session summary
    session_id = session.cookies.get('session')
    if session_id:
        summary_response = session.get(f'http://localhost:5001/session-summary/{session_id}')
        if summary_response.status_code == 200:
            summary = summary_response.json()
            print("\n" + "="*50)
            print("📋 FINAL SUMMARY:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print("❌ Failed to get summary")

if __name__ == "__main__":
    test_chatbot()