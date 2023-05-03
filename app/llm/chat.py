import queue
import threading

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage

from app.config import OPENAI_API_KEY

CHAT_RESPONSE_SYSTEM_MESSAGE = """
あなたは転職エージェントAIとしてユーザーの転職相談に乗ります。必要に応じてヒアリングをするなど、ユーザーニーズに合った提案をしてください。
"""

CONVERSATION_HISTORY_MESSAGE = """
## 過去5件の会話履歴
{history}
"""


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen, session_id, conversation_history):
        super().__init__()
        self.gen = gen
        self.session_id = session_id
        self.conversation_history = conversation_history
        self.temp_ai_message = ""

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(f"data: {token}\n\n")
        self.temp_ai_message += token

    def finish(self):
        self.conversation_history.add_message(
            self.session_id, "ai", self.temp_ai_message
        )
        self.temp_ai_message = ""


def chat_response_thread(g, user_message, session_id, conversation_history):
    try:
        chain_stream_handler = ChainStreamHandler(g, session_id, conversation_history)
        chat = ChatOpenAI(
            verbose=True,
            streaming=True,
            callback_manager=CallbackManager([chain_stream_handler]),
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY,
        )
        # 会話履歴を追加
        history = CONVERSATION_HISTORY_MESSAGE.format(
            history=conversation_history.format_recent_conversations(session_id)
        )
        # ユーザーメッセージの記録
        conversation_history.add_message(session_id, "user", user_message)

        chat(
            [
                SystemMessage(content=CHAT_RESPONSE_SYSTEM_MESSAGE),
                SystemMessage(content=history),
                HumanMessage(content=user_message),
            ]
        )

    finally:
        chain_stream_handler.finish()
        g.send(f"data: END\n\n")
        g.close()


def generate_chat_response(user_message, session_id, conversation_history):
    g = ThreadedGenerator()
    threading.Thread(
        target=chat_response_thread,
        args=(g, user_message, session_id, conversation_history),
    ).start()
    return g
