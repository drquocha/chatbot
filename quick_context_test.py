#!/usr/bin/env python3

"""
Quick test for context preservation in web search
"""

from chatbot import SimpleChatbot
from dotenv import load_dotenv

load_dotenv()

def test_context_preservation():
    """Test that conversation context is preserved during web searches"""
    print("🧪 QUICK CONTEXT TEST")
    print("=" * 50)

    chatbot = SimpleChatbot()

    # Step 1: Establish context
    print("👤 User: Xin chào, tôi tên là Anna")
    response1 = chatbot.get_response("Xin chào, tôi tên là Anna")
    print(f"🤖 Bot: {response1}")
    print()

    # Step 2: Trigger web search
    print("👤 User: Thủ tướng Việt Nam hiện tại là ai?")
    response2 = chatbot.get_response("Thủ tướng Việt Nam hiện tại là ai?")
    print(f"🤖 Bot: {response2}")
    print()

    # Step 3: Test context preservation
    print("👤 User: Tôi tên gì?")
    response3 = chatbot.get_response("Tôi tên gì?")
    print(f"🤖 Bot: {response3}")
    print()

    # Analysis
    context_preserved = "anna" in response3.lower() or "Anna" in response3
    print(f"✓ Bot remembers user name: {'✅' if context_preserved else '❌'}")

def test_cooking_questions():
    """Test that cooking questions don't trigger web search"""
    print("\n🧪 COOKING QUESTIONS TEST")
    print("=" * 50)

    chatbot = SimpleChatbot()

    cooking_questions = [
        "Cách nấu phở truyền thống như thế nào?",
        "Cách làm bánh mì Việt Nam",
        "Công thức làm bún bò Huế"
    ]

    for question in cooking_questions:
        needs_search = chatbot.needs_web_search(question)
        result = "❌" if needs_search else "✅"
        print(f"{result} {question} -> Search: {needs_search}")

if __name__ == "__main__":
    test_context_preservation()
    test_cooking_questions()