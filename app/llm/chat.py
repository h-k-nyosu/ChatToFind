import queue
import threading

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage

from app.config import OPENAI_API_KEY


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
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(f"data: {token}\n\n")


def chat_response_thread(g, prompt):
    try:
        chat = ChatOpenAI(
            verbose=True,
            streaming=True,
            callback_manager=CallbackManager([ChainStreamHandler(g)]),
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY,
        )
        chat(
            [
                SystemMessage(
                    content="あなたは転職エージェントAIとしてユーザーの転職相談に乗ります。必要に応じてヒアリングをするなど、ユーザーニーズに合った提案をしてください。"
                ),
                HumanMessage(content=prompt),
            ]
        )

    finally:
        g.send(f"data: END\n\n")
        g.close()


def generate_chat_response(prompt):
    g = ThreadedGenerator()
    threading.Thread(target=chat_response_thread, args=(g, prompt)).start()
    return g
