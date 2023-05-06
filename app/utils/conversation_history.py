import datetime


class ConversationHistory:
    def __init__(self, max_session_age_days=1):
        self.history = {}
        self.last_used = {}
        self.max_session_age_days = max_session_age_days

    def add_message(self, session_id, message_type, content):
        if session_id not in self.history:
            self.history[session_id] = []
        message = {"message_type": message_type, "content": content}
        self.history[session_id].append(message)
        self.last_used[session_id] = datetime.datetime.now()

    def get_history(self, session_id):
        return self.history.get(session_id, [])

    def format_history(self, session_id):
        history = self.get_history(session_id)
        return self._format_conversations(history)

    def get_recent_conversations(self, session_id, count=10):
        history = self.get_history(session_id)
        return history[-count:]

    def format_recent_conversations(self, session_id, count=10):
        recent_conversations = self.get_recent_conversations(session_id, count)
        return self._format_conversations(recent_conversations)

    def _format_conversations(self, conversations):
        formatted_conversations = ""

        for conversation in conversations:
            message_type = conversation["message_type"]
            content = conversation["content"]
            formatted_conversations += f"{message_type.capitalize()}: {content}\n"

        return formatted_conversations

    def remove_expired_sessions(self):
        now = datetime.datetime.now()
        expired_sessions = []

        for session_id, last_used in self.last_used.items():
            age = now - last_used
            if age.days >= self.max_session_age_days:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.history[session_id]
            del self.last_used[session_id]
