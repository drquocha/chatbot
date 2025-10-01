#!/usr/bin/env python3

"""
Test script to verify web search context preservation and LLM-based decision making fixes
"""

from chatbot import SimpleChatbot
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_context_preservation():
    """Test that conversation context is preserved during web searches"""
    print("🧪 TEST 1: Context Preservation During Web Search")
    print("=" * 60)

    chatbot = SimpleChatbot()

    # Step 1: Establish context
    print("👤 User: Xin chào, tôi tên là Minh")
    response1 = chatbot.get_response("Xin chào, tôi tên là Minh")
    print(f"🤖 Bot: {response1}")
    print()

    # Step 2: Ask a non-search question to build more context
    print("👤 User: Tôi đang học về lịch sử Việt Nam")
    response2 = chatbot.get_response("Tôi đang học về lịch sử Việt Nam")
    print(f"🤖 Bot: {response2}")
    print()

    # Step 3: Ask a question that should trigger web search but reference previous context
    print("👤 User: Thủ tướng Việt Nam hiện tại là ai?")
    response3 = chatbot.get_response("Thủ tướng Việt Nam hiện tại là ai?")
    print(f"🤖 Bot: {response3}")
    print()

    # Step 4: CRITICAL TEST - Ask follow-up question that requires context from step 3
    print("👤 User: Ông ấy bao nhiêu tuổi?")
    response4 = chatbot.get_response("Ông ấy bao nhiêu tuổi?")
    print(f"🤖 Bot: {response4}")
    print()

    # Step 5: Test if bot still remembers the user's name from step 1
    print("👤 User: Tôi tên gì?")
    response5 = chatbot.get_response("Tôi tên gì?")
    print(f"🤖 Bot: {response5}")
    print()

    # Analysis
    print("📊 ANALYSIS:")
    context_preserved = "minh" in response5.lower() or "Minh" in response5
    search_context_preserved = "phạm minh chính" in response4.lower() or "thủ tướng" in response4.lower()

    print(f"✓ Bot remembers user name: {'✅' if context_preserved else '❌'}")
    print(f"✓ Bot understands 'ông ấy' refers to PM: {'✅' if search_context_preserved else '❌'}")
    print()

def test_llm_decision_making():
    """Test the LLM-based web search decision making"""
    print("🧪 TEST 2: LLM-Based Web Search Decision Making")
    print("=" * 60)

    chatbot = SimpleChatbot()

    test_cases = [
        # Should NOT trigger web search
        ("Hãy giải thích về khái niệm 'tin tức' trong ngành báo chí", False),
        ("Cách nấu phở truyền thống như thế nào?", False),
        ("Python là gì?", False),
        ("Bạn có thể giúp tôi học tiếng Anh không?", False),

        # Should trigger web search
        ("Thủ tướng Việt Nam hiện tại là ai?", True),
        ("Giá vàng SJC hôm nay bao nhiêu?", True),
        ("Tình hình COVID-19 mới nhất ở Việt Nam", True),
        ("Ai đang là Tổng Bí thư Đảng Cộng sản Việt Nam?", True),
    ]

    for question, expected_search in test_cases:
        print(f"📝 Question: {question}")
        actual_search = chatbot.needs_web_search(question)
        result = "✅" if actual_search == expected_search else "❌"
        print(f"   Expected search: {expected_search} | Actual: {actual_search} {result}")
        print()
        time.sleep(0.5)  # Small delay to avoid rate limiting

def test_conversation_flow():
    """Test complete conversation flow with mixed search and non-search questions"""
    print("🧪 TEST 3: Mixed Conversation Flow")
    print("=" * 60)

    chatbot = SimpleChatbot()

    questions = [
        "Xin chào, tôi tên là Nam, tôi đang quan tâm đến tình hình chính trị",
        "Tổng Bí thư Đảng hiện tại là ai?",  # Should search
        "Ông ấy từ tỉnh nào?",  # Should search but maintain context
        "Cảm ơn bạn. Bây giờ tôi muốn hỏi về nấu ăn",  # Should NOT search
        "Cách làm bánh mì Việt Nam",  # Should NOT search
        "Còn giá bánh mì hiện tại ở Sài Gòn bao nhiêu?",  # Should search
    ]

    for i, question in enumerate(questions, 1):
        print(f"👤 Turn {i}: {question}")
        response = chatbot.get_response(question)
        print(f"🤖 Bot: {response[:100]}{'...' if len(response) > 100 else ''}")
        print()
        time.sleep(1)  # Delay between questions

def main():
    print("🔧 TESTING WEB SEARCH FIXES")
    print("🎯 Goals:")
    print("1. Verify conversation context is preserved during web searches")
    print("2. Test LLM-based web search decision making")
    print("3. Ensure natural conversation flow")
    print()

    try:
        test_llm_decision_making()
        print("\n" + "="*80 + "\n")

        test_context_preservation()
        print("\n" + "="*80 + "\n")

        test_conversation_flow()

        print("🎉 All tests completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("Please check your OpenAI API key and internet connection.")

if __name__ == "__main__":
    main()