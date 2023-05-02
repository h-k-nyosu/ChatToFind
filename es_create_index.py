import os
import boto3
import openai
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

REGION = "ap-northeast-1"
OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST")
SERVICE = "es"

# AWS認証情報の取得
credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    SERVICE,
    session_token=credentials.token,
)

# OpenSearchクライアントの作成
os_client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": 443}],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=300,
)


def main():
    index_name = "jobs"

    mapping = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "kuromoji_analyzer": {
                        "type": "custom",
                        "tokenizer": "kuromoji_tokenizer",
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "title": {"type": "text", "analyzer": "kuromoji_analyzer"},
                "job_type": {"type": "text", "analyzer": "kuromoji_analyzer"},
                "job_summary": {"type": "text", "analyzer": "kuromoji_analyzer"},
                "job_details": {"type": "text", "analyzer": "kuromoji_analyzer"},
                "location": {"type": "text", "analyzer": "kuromoji_analyzer"},
                "monthly_salary": {"type": "long"},
            }
        },
    }

    # Delete the index if it exists
    if os_client.indices.exists(index_name):
        os_client.indices.delete(index_name)

    # Create the index with the new mapping
    os_client.indices.create(index=index_name, body=mapping)


if __name__ == "__main__":
    main()
