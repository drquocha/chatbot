#!/usr/bin/env python3

import requests
import json

def quick_test():
    print("🩺 FINAL TEST - PATIENT DATA SAVING")
    print("=" * 50)

    session = requests.Session()

    # 1. Start
    response = session.post('http://localhost:5001/start-session', json={})
    data = response.json()
    session_id = data['session_id']
    print(f"✅ Session: {session_id}")

    # 2. Quick conversation
    messages = [
        "Tôi tên Nguyễn Văn Nam",
        "35 tuổi",
        "đau bụng từ sáng nay"
    ]

    for msg in messages:
        print(f"👤 {msg}")
        response = session.post('http://localhost:5001/chat', json={'message': msg})
        data = response.json()
        print(f"🤖 {data['message'][:50]}...")
        print(f"📊 Progress: {data.get('progress', 0)}%")
        print()

    # 3. Check summary immediately
    summary_response = session.get(f'http://localhost:5001/session-summary/{session_id}')
    if summary_response.status_code == 200:
        summary = summary_response.json()
        patient_data = summary.get('patient_data', {})

        print("🎯 PATIENT DATA SUMMARY:")
        print(f"Name: {patient_data.get('demographics', {}).get('name', 'EMPTY')}")
        print(f"Age: {patient_data.get('demographics', {}).get('age', 'EMPTY')}")
        print(f"Chief complaint: {patient_data.get('chief_complaint', {}).get('main_complaint', 'EMPTY')}")

        if patient_data.get('demographics', {}).get('name'):
            print("✅ PATIENT DATA SAVING: SUCCESS!")
        else:
            print("❌ PATIENT DATA SAVING: FAILED!")
    else:
        print("❌ Cannot get summary")

if __name__ == "__main__":
    quick_test()