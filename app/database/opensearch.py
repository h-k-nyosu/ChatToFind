import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from app.config import OPENSEARCH_HOST
from dotenv import load_dotenv

REGION = "ap-northeast-1"
OPENSEARCH_HOST = OPENSEARCH_HOST
SERVICE = "es"

# AWS認証情報の取得
load_dotenv()
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

# 接続が正常に行われているか確認
try:
    if os_client.ping():
        print("Connected to OpenSearch")
    else:
        print("Unable to connect to OpenSearch")
except Exception as e:
    print("Error:", e)
    import traceback

    traceback.print_exc()
