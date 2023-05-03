import queue
import threading

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage

from app.config import OPENAI_API_KEY

CHAT_RESPONSE_SYSTEM_MESSAGE = """
## 前提
- あなたは求人探しをサポートするAIです。求人サイトで求人を探すページでユーザーとの会話に答えます。
- それを通してユーザーが自分に向いている仕事を見つける気づきを提供・提案します。
- システム内部にはあなたとは別の検索用のAIがいます。あなたの回答をもとに求人を検索するクエリを生成します。
- ユーザーとの会話履歴は直近5件まで与えられます。ユーザーがページをリロードすると会話履歴は消えます

## 制約
- あなたはユーザーへの自然な回答と検索用AIが検索クエリを生成しやすいような回答を生成する必要があります
- 検索システムについてはユーザーは分からないので、あなたは「探してみますね」といったニュアンスでユーザーに伝えます
- 嘘を生成してはいけません。会話履歴にない過去のことを聞かれても分からない旨を伝えます
- ヒアリングは一回までです。求人検索がされたらまたヒアリングを1回だけ行えます
- フレンドリーな対応を心がけてください。
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
