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

index_name = "jobs"

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

from opensearchpy.helpers import bulk
from opensearchpy.helpers import scan


def delete_long_title_docs(index_name, os_client):
    # すべてのドキュメントを取得
    all_docs = scan(
        os_client,
        index=index_name,
        _source=["title"],
    )

    # タイトルの長さが35文字以上のドキュメントをフィルタリング
    docs_to_delete = [doc for doc in all_docs if len(doc["_source"]["title"]) > 40]

    # 削除用のアクションを準備
    actions = [
        {
            "_op_type": "delete",
            "_index": index_name,
            "_id": doc["_id"],
        }
        for doc in docs_to_delete
    ]

    # ドキュメントを一括削除
    success, _ = bulk(os_client, actions, stats_only=True, raise_on_error=False)
    return success


# OpenSearchクライアントを使って長いタイトルのドキュメントを削除
deleted_count = delete_long_title_docs(index_name, os_client)
print(f"削除されたドキュメント数: {deleted_count}")
