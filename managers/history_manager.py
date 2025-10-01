"""
HistoryManager - Handles conversation history with sliding window capability
"""

from typing import List, Dict

class HistoryManager:
    def __init__(self, max_messages: int = 20):
        self.conversation_history: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        self._apply_sliding_window()

    def get_history(self) -> List[Dict[str, str]]:
        """Get full conversation history"""
        return self.conversation_history.copy()

    def get_history_except_last(self) -> List[Dict[str, str]]:
        """Get conversation history excluding the last message"""
        return self.conversation_history[:-1].copy()

    def update_last_message(self, role: str, content: str):
        """Update the last message in history"""
        if self.conversation_history:
            self.conversation_history[-1] = {"role": role, "content": content}

    def clear(self):
        """Clear all conversation history"""
        self.conversation_history = []

    def _apply_sliding_window(self):
        """Apply sliding window to keep only recent messages"""
        if len(self.conversation_history) > self.max_messages:
            # Keep system messages at the beginning if any
            system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
            recent_messages = self.conversation_history[-(self.max_messages - len(system_messages)):]

            self.conversation_history = system_messages + recent_messages

    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.conversation_history)

    def get_last_message(self) -> Dict[str, str]:
        """Get the last message"""
        return self.conversation_history[-1] if self.conversation_history else None