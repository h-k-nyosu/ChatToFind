class ConversationHistory:
    def __init__(self):
        self.history = {}

    def add_message(self, session_id, message_type, content):
        if session_id not in self.history:
            self.history[session_id] = []

        message = {"message_type": message_type, "content": content}
        self.history[session_id].append(message)

    def get_history(self, session_id):
        return self.history.get(session_id, [])

    def format_history(self, session_id):
        history = self.get_history(session_id)
        return self._format_conversations(history)

    def get_recent_conversations(self, session_id, count=5):
        history = self.get_history(session_id)
        return history[-count:]

    def format_recent_conversations(self, session_id, count=5):
        recent_conversations = self.get_recent_conversations(session_id, count)
        return self._format_conversations(recent_conversations)

    def _format_conversations(self, conversations):
        formatted_conversations = ""

        for conversation in conversations:
            message_type = conversation["message_type"]
            content = conversation["content"]
            formatted_conversations += f"{message_type.capitalize()}: {content}\n"

        return formatted_conversations
