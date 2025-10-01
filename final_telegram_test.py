#!/usr/bin/env python3

import requests
import json
import time

def final_telegram_test():
    print("🎯 FINAL TELEGRAM TEST - FORCE COMPLETION")
    print("=" * 60)

    session = requests.Session()

    # Start session
    print("🤖 Starting session...")
    response = session.post('http://localhost:5001/start-session', json={})
    data = response.json()
    session_id = data['session_id']

    print(f"✅ Session ID: {session_id}")
    print()

    # Extended conversation to reach stage 7 and force completion
    messages = [
        "Tôi tên Bùi Văn Tâm",          # 1
        "35 tuổi",                       # 2
        "đau bụng từ chiều hôm qua",    # 3
        "đau vùng bụng dưới bên phải, mức 9/10", # 4
        "có nôn và sốt 39 độ",          # 5
        "đau khi di chuyển và ho",      # 6
        "không có tiền sử phẫu thuật",  # 7
        "không dị ứng thuốc nào",       # 8
        "chưa uống thuốc gì cả",        # 9
        "gia đình không có bệnh gì",    # 10
        "không hút thuốc không uống rượu", # 11
        "có triệu chứng khó tiêu",      # 12
        "đau từ lúc 3h chiều hôm qua",  # 13
        "không có tiêu chảy",           # 14
        "thông tin này đã đầy đủ rồi",  # 15
        "tôi xác nhận hoàn thành",      # 16
        "không cần thêm gì nữa"        # 17
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
            completed = data.get('completed', False)
            action = data.get('action', '')

            print(f"📊 Stage: {stage} | Progress: {progress}% | Completed: {completed} | Action: {action}")
            print(f"🤖 AI: {data['message'][:60]}...")

            if completed or action == 'end_session':
                print("\n🎉 COMPLETION DETECTED!")
                print("📨 TELEGRAM NOTIFICATION SHOULD BE SENT!")
                break
            elif i >= 16:  # Force break after enough messages
                print(f"\n✅ Reached {i} turns - Should have triggered completion")
                break
        else:
            print(f"❌ Error: {chat_response.status_code}")
            break

        print("-" * 40)
        time.sleep(0.5)

    # Final summary check
    try:
        summary_response = session.get(f'http://localhost:5001/session-summary/{session_id}')
        if summary_response.status_code == 200:
            summary = summary_response.json()
            final_status = summary.get('status', 'unknown')
            final_stage = summary.get('current_stage', 1)
            print(f"\n📋 FINAL RESULTS:")
            print(f"Status: {final_status}")
            print(f"Stage: {final_stage}")

            if final_status == 'completed':
                print("✅ SESSION MARKED AS COMPLETED")
                print("📨 Telegram notification should have been sent!")
            else:
                print(f"⚠️  Session still in status: {final_status}")
        else:
            print(f"❌ Could not get summary: {summary_response.status_code}")
    except Exception as e:
        print(f"❌ Error getting summary: {e}")

if __name__ == "__main__":
    final_telegram_test()