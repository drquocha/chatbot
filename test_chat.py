#!/usr/bin/env python3

import requests
import json

# Test session creation
print("1. Creating session...")
session = requests.Session()
response = session.post('http://localhost:5001/start-session',
                       json={},
                       headers={'Content-Type': 'application/json'})

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"Session ID: {data.get('session_id')}")

    # Test chat
    print("\n2. Testing chat...")
    chat_response = session.post('http://localhost:5001/chat',
                                json={'message': 'tôi tên là Hà Văn Quốc'},
                                headers={'Content-Type': 'application/json'})

    print(f"Chat Status: {chat_response.status_code}")
    print(f"Chat Response: {chat_response.text}")
else:
    print("Failed to create session")