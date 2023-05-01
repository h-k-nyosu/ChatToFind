import os
import boto3
import openai
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv
from jsonfinder import jsonfinder
import json
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# REGION = "ap-northeast-1"
# OPENSEARCH_HOST = os.environ.get("OPENSEARCH_HOST")
# SERVICE = "es"

# # AWS認証情報の取得
# credentials = boto3.Session().get_credentials()
# aws_auth = AWS4Auth(
#     credentials.access_key,
#     credentials.secret_key,
#     REGION,
#     SERVICE,
#     session_token=credentials.token,
# )

# # OpenSearchクライアントの作成
# os_client = OpenSearch(
#     hosts=[{"host": OPENSEARCH_HOST, "port": 443}],
#     http_auth=aws_auth,
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection,
#     timeout=300,
# )


GENERATE_JOB_TEXT = """
与えられた職種の求人原稿について、以下の項目で1000字程度で記載してください。

## 制約条件
・内容は実際にありそうな具体的なものにしてください。実在しなくても可。
・仕事詳細は500文字以上で具体的に記載します
・求人タイトル、仕事概要、仕事詳細は求人に応募したいと思う魅力的な文章にしてください
・出力は```jsonから始まります

## 出力形式
```json
{{
    "title": [求人タイトル],
    "job_type": [職種],
    "job_summary": [仕事概要],
    "job_details": [仕事詳細],
    "monthly_salary": [月給],
    "location": [勤務地]
}}
```

## 出力例
```json
{{
    "title": "Webアプリケーション開発エンジニア募集！",
    "job_type": "ソフトウェアエンジニア",
    "job_summary": "当社の開発チームで、Webアプリケーションの開発を担当していただくエンジニアを募集しています。",
    "job_details": "ReactやAngularを使ったフロントエンド開発、PHPやRuby on Railsを使ったバックエンド開発、データベース設計やデータベースの最適化、AWSのクラウド環境の構築、運用・保守、プロジェクトマネジメントなど、幅広い業務をお任せします。開発環境は個人の希望に合わせて調整可能です。",
    "monthly_salary": "350000",
    "location": "東京都千代田区"
}}
```
"""


def generate_job_text(job_type):
    prompt = GENERATE_JOB_TEXT.format(job_type=job_type)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"職種： {job_type}"},
        ],
        max_tokens=2000,
    )
    job_text = f"職種名\n{job_type}"
    job_text += response["choices"][0]["message"]["content"]
    return job_text


def main():
    job_list = [
        "ソフトウェアエンジニア",
        "グラフィックデザイナー",
        "データアナリスト",
        "プロジェクトマネージャー",
        "ウェブデザイナー",
        "マーケティングスペシャリスト",
        "広報・PR担当",
        "人事担当",
        "経理・財務担当",
        "営業担当",
        "イベントプランナー",
        "コンサルタント",
        "システム管理者",
        "コンテンツライター・エディター",
        "翻訳者・通訳者",
        "保育士・幼稚園教諭",
        "教育コーディネーター",
        "医師・看護師",
        "物流・倉庫管理",
        "料理人・シェフ",
        "バーテンダー",
        "美容師・美容部員",
        "フィットネスインストラクター",
        "不動産エージェント",
        "旅行アドバイザー",
        "インテリアデザイナー",
        "農業・園芸関連職",
        "環境・エネルギー関連職",
    ]
    for job in job_list:
        for i in range(1):
            try:
                # print(f"[INFO] {i}回目 職種名: {job}")
                job_text = generate_job_text(job)
                print(f"[INFO] job_text: {job_text}")
                job_query = job_text.split("```json")[1].strip().strip("```").strip()
                print(f"[INFO] job_query: {job_query}")
                # res = create_jobs(index="jobs", body=job_query)
                # print(f"[INFO] res: {res}")
            except BaseException as e:
                print(f"[ERROR] {e}")


main()
