"""
Session Manager - In-memory session storage for chatbot conversations.
Sessions are temporary and not persisted to any database.
"""
import uuid
import time
from typing import Dict, List, Optional
from threading import Lock


class SessionManager:
    """
    Manages in-memory chat sessions with automatic cleanup of old sessions.
    Sessions are identified by unique session_id and store conversation history.
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize the session manager.
        
        Args:
            session_timeout: Time in seconds before a session expires (default: 1 hour)
        """
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = session_timeout
        self.lock = Lock()
    
    def create_session(
        self,
        lesson_content: str,
        subject: str,
        user_role: str,
        grade: Optional[int] = None
    ) -> str:
        """
        Create a new chat session.
        
        Args:
            lesson_content: The lesson content for this session
            subject: Subject name (e.g., "Biologie", "Matematică")
            user_role: Either "student" or "individual"
            grade: Grade level (required if user_role is "student")
            
        Returns:
            session_id: Unique identifier for this session
        """
        session_id = str(uuid.uuid4())
        
        with self.lock:
            self.sessions[session_id] = {
                "session_id": session_id,
                "lesson_content": lesson_content,
                "subject": subject,
                "user_role": user_role,
                "grade": grade,
                "conversation_history": [],
                "created_at": time.time(),
                "last_accessed": time.time()
            }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Session data dictionary or None if not found/expired
        """
        with self.lock:
            session = self.sessions.get(session_id)
            
            if session is None:
                return None
            
            # Check if session has expired
            if time.time() - session["last_accessed"] > self.session_timeout:
                # Session expired, remove it
                del self.sessions[session_id]
                return None
            
            # Update last accessed time
            session["last_accessed"] = time.time()
            
            return session
    
    def update_session(
        self,
        session_id: str,
        conversation_history: List[Dict]
    ) -> bool:
        """
        Update the conversation history for a session.
        
        Args:
            session_id: The session identifier
            conversation_history: Updated conversation history
            
        Returns:
            True if successful, False if session not found
        """
        with self.lock:
            session = self.sessions.get(session_id)
            
            if session is None:
                return False
            
            session["conversation_history"] = conversation_history
            session["last_accessed"] = time.time()
            
            return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        current_time = time.time()
        
        with self.lock:
            expired_sessions = [
                sid for sid, session in self.sessions.items()
                if current_time - session["last_accessed"] > self.session_timeout
            ]
            
            for sid in expired_sessions:
                del self.sessions[sid]
            
            return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """Get the number of active sessions."""
        with self.lock:
            return len(self.sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get basic info about a session without full conversation history.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dictionary with session metadata or None if not found
        """
        session = self.get_session(session_id)
        
        if session is None:
            return None
        
        return {
            "session_id": session["session_id"],
            "user_role": session["user_role"],
            "grade": session["grade"],
            "message_count": len(session["conversation_history"]),
            "created_at": session["created_at"],
            "last_accessed": session["last_accessed"]
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager instance."""
    global _session_manager
    
    if _session_manager is None:
        _session_manager = SessionManager(session_timeout=3600)  # 1 hour timeout
    
    return _session_manager
