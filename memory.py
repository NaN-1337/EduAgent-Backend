"""
Memory module for managing conversation history.
"""
from typing import List, Tuple
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


class ConversationMemory:
    """Simple conversation memory manager."""
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of messages to keep in history.
        """
        self.max_messages = max_messages
        self.messages: List[BaseMessage] = []
    
    def add_user_message(self, message: str):
        """
        Add a user message to history.
        
        Args:
            message: User message text.
        """
        self.messages.append(HumanMessage(content=message))
        self._trim_history()
    
    def add_ai_message(self, message: str):
        """
        Add an AI message to history.
        
        Args:
            message: AI message text.
        """
        self.messages.append(AIMessage(content=message))
        self._trim_history()
    
    def _trim_history(self):
        """Keep only the most recent messages."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_history(self) -> List[BaseMessage]:
        """
        Get all messages in history.
        
        Returns:
            List of messages.
        """
        return self.messages
    
    def get_history_string(self) -> str:
        """
        Get conversation history as a formatted string.
        
        Returns:
            Formatted conversation history.
        """
        if not self.messages:
            return "No previous conversation."
        
        history_lines = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                history_lines.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_lines.append(f"Assistant: {msg.content}")
        
        return "\n".join(history_lines)
    
    def get_recent_exchanges(self, n: int = 3) -> List[Tuple[str, str]]:
        """
        Get the n most recent question-answer pairs.
        
        Args:
            n: Number of exchanges to retrieve.
            
        Returns:
            List of (question, answer) tuples.
        """
        exchanges = []
        i = 0
        
        while i < len(self.messages) - 1 and len(exchanges) < n:
            if isinstance(self.messages[i], HumanMessage) and \
               isinstance(self.messages[i + 1], AIMessage):
                exchanges.append((
                    self.messages[i].content,
                    self.messages[i + 1].content
                ))
            i += 2
        
        return list(reversed(exchanges))[-n:]
    
    def clear(self):
        """Clear all conversation history."""
        self.messages = []
        print("Conversation history cleared.")
    
    def __len__(self) -> int:
        """Return number of messages in history."""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """String representation of memory."""
        return f"ConversationMemory(messages={len(self.messages)}, max={self.max_messages})"


if __name__ == "__main__":
    # Test the memory
    memory = ConversationMemory(max_messages=4)
    
    print("Testing Conversation Memory...\n")
    
    # Add some messages
    memory.add_user_message("Hello, how are you?")
    memory.add_ai_message("I'm doing well, thank you!")
    memory.add_user_message("What's the weather like?")
    memory.add_ai_message("I don't have access to real-time weather data.")
    
    print(f"Memory state: {memory}")
    print(f"\nConversation history:\n{memory.get_history_string()}")
    
    # Test trimming
    print("\nAdding more messages to test trimming...")
    memory.add_user_message("Tell me a joke.")
    memory.add_ai_message("Why did the chicken cross the road?")
    
    print(f"\nAfter trimming: {memory}")
    print(f"\nConversation history:\n{memory.get_history_string()}")
