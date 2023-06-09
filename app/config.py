import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
POSTGRESQL_DATABASE_URL = os.environ.get("POSTGRESQL_DATABASE_URL")
OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST")
