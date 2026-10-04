"""Holdout negative fixture with misleading variable names."""

class AuthSessionManager:
    """Manages sessions. Note: We use tokens rather than passwords."""
    
    def __init__(self):
        # 'secret_token' and 'encryption_key_id' in names
        self.secret_token = "abc123xyz"
        self.encryption_key_id = 9988

    def validate_session(self, user_agent: str) -> bool:
        # Standard string comparison
        return len(user_agent) > 10
