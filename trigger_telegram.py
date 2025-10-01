#!/usr/bin/env python3

import requests
import json
import time

def trigger_telegram_notification():
    print("🚨 FORCING TELEGRAM NOTIFICATION")
    print("=" * 60)

    session = requests.Session()

    # Start session
    print("🤖 Khởi tạo session...")
    response = session.post('http://localhost:5001/start-session', json={})
    data = response.json()
    session_id = data['session_id']

    print(f"✅ Session ID: {session_id}")
    print()

    # Extended conversation to force stage progression
    messages = [
        "Tôi tên Nguyễn Thị Hoa",
        "32 tuổi",
        "đau bụng từ sáng nay",
        "đau vùng bụng dưới bên phải, mức 8/10",
        "có nôn và sốt 38.5",
        "đau khi di chuyển",
        "không có tiền sử phẫu thuật",
        "không dị ứng thuốc",
        "chưa uống thuốc gì",
        "gia đình không có bệnh gì",
        "không hút thuốc, không uống rượu",
        "có thêm triệu chứng khó tiêu",
        "đau từ lúc 6h sáng đến giờ",
        "không có tiêu chảy",
        "thông tin này đã đầy đủ",
        "tôi xác nhận thông tin chính xác",
        "hoàn thành thu thập bệnh sử"
    ]

    for i, msg in enumerate(messages, 1):
        print(f"🗣️  Turn {i}: {msg}")

        # Send message
        chat_response = session.post('http://localhost:5001/chat',
                                   json={'message': msg})

        if chat_response.status_code == 200:
            data = chat_response.json()

            stage = data.get('stage', 1)
            progress = data.get('progress', 0)
            status = data.get('status', 'active')
            completed = data.get('completed', False)

            print(f"📊 Stage: {stage} | Progress: {progress}% | Status: {status}")
            print(f"🤖 AI: {data['message'][:60]}...")

            if completed or data.get('action') == 'end_session':
                print("\n🎉 SESSION COMPLETED!")
                print("📨 TELEGRAM NOTIFICATION SENT!")
                break
            elif stage > 6:
                print(f"\n✅ Stage {stage} reached - Should trigger completion!")
                # Try one more confirmation
                final_response = session.post('http://localhost:5001/chat',
                                            json={'message': 'Xác nhận hoàn thành'})
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    if final_data.get('completed'):
                        print("🎉 FINAL COMPLETION TRIGGERED!")
                        print("📨 TELEGRAM NOTIFICATION SENT!")
                        break
        else:
            print(f"❌ Error: {chat_response.status_code}")
            break

        print("-" * 40)
        time.sleep(0.5)  # Small delay between messages

    # Check final summary
    try:
        summary_response = session.get(f'http://localhost:5001/session-summary/{session_id}')
        if summary_response.status_code == 200:
            summary = summary_response.json()
            final_status = summary.get('status', 'unknown')
            print(f"\n📋 FINAL STATUS: {final_status}")

            if final_status == 'completed':
                print("✅ SESSION MARKED AS COMPLETED")
                print("📨 Telegram notification should have been sent!")
            else:
                print(f"⚠️  Session status: {final_status}")
        else:
            print(f"❌ Could not get summary: {summary_response.status_code}")
    except Exception as e:
        print(f"❌ Error getting summary: {e}")

if __name__ == "__main__":
    trigger_telegram_notification()