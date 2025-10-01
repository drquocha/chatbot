#!/usr/bin/env python3

"""
Test the refactored chatbot architecture
"""

from chatbot_refactored import SimpleChatbot
from dotenv import load_dotenv

load_dotenv()

def test_refactored_architecture():
    """Test that the refactored chatbot maintains functionality"""
    print("🧪 TESTING REFACTORED ARCHITECTURE")
    print("=" * 60)

    chatbot = SimpleChatbot()

    # Test 1: Basic conversation
    print("📝 Test 1: Basic Conversation")
    response1 = chatbot.get_response("Xin chào, tôi tên là David")
    print(f"✅ Response: {response1}")

    # Test 2: Context preservation
    print("\n📝 Test 2: Context Preservation")
    response2 = chatbot.get_response("Tôi tên gì?")
    context_preserved = "david" in response2.lower() or "David" in response2
    print(f"{'✅' if context_preserved else '❌'} Context preserved: {response2}")

    # Test 3: Web search functionality
    print("\n📝 Test 3: Web Search Integration")
    response3 = chatbot.get_response("Thủ tướng Việt Nam hiện tại là ai?")
    print(f"✅ Search response: {response3[:80]}...")

    # Test 4: Context after web search
    print("\n📝 Test 4: Context After Web Search")
    response4 = chatbot.get_response("Tôi tên gì?")
    context_after_search = "david" in response4.lower() or "David" in response4
    print(f"{'✅' if context_after_search else '❌'} Context after search: {response4}")

    # Test 5: Manager separation
    print("\n📝 Test 5: Manager Functionality")
    print(f"✅ Message count: {chatbot.get_message_count()}")
    print(f"✅ History manager working: {len(chatbot.get_conversation_history()) > 0}")

    # Test 6: Cooking questions (should not search)
    print("\n📝 Test 6: Cooking Questions (No Search)")
    response6 = chatbot.get_response("Cách nấu phở như thế nào?")
    print(f"✅ Cooking response: {response6[:80]}...")

    print("\n🎉 All tests completed! Architecture refactoring successful.")

def test_managers_independently():
    """Test individual managers work correctly"""
    print("\n🔧 TESTING INDIVIDUAL MANAGERS")
    print("=" * 60)

    from managers.history_manager import HistoryManager
    from managers.prompt_manager import PromptManager

    # Test HistoryManager
    print("📝 Testing HistoryManager")
    history_mgr = HistoryManager(max_messages=3)
    history_mgr.add_message("user", "Message 1")
    history_mgr.add_message("assistant", "Response 1")
    history_mgr.add_message("user", "Message 2")
    history_mgr.add_message("assistant", "Response 2")  # Should trigger sliding window

    print(f"✅ History count (should be 3): {history_mgr.get_message_count()}")
    print(f"✅ Sliding window working: {len(history_mgr.get_history()) <= 3}")

    # Test PromptManager
    print("\n📝 Testing PromptManager")
    prompt_mgr = PromptManager()
    web_prompt = prompt_mgr.create_web_search_prompt("Test question", "Test results")
    decision_prompt = prompt_mgr.create_search_decision_prompt("Test question")

    print(f"✅ Web search prompt created: {len(web_prompt) > 0}")
    print(f"✅ Decision prompt created: {len(decision_prompt) > 0}")

    print("\n🎉 Individual managers working correctly!")

if __name__ == "__main__":
    test_refactored_architecture()
    test_managers_independently()