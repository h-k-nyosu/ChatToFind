import pinecone
import os
from dotenv import load_dotenv
import openai
from app.config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENV
import uuid

load_dotenv()

openai.api_key = OPENAI_API_KEY
# get API key from top-right dropdown on OpenAI website

openai.Engine.list()  # check we have authenticated

MODEL = "text-embedding-ada-002"

res = openai.Embedding.create(
    input=[
        "Sample document text goes here",
        "there will be several phrases in each batch",
    ],
    engine=MODEL,
)

# Pineconeのセットアップ
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

pinecone_index_name = "chat-to-find"
index = pinecone.Index(pinecone_index_name)
