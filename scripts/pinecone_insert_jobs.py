import pinecone
import os
from dotenv import load_dotenv
import openai
import uuid

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
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
pinecone.init(api_key=os.environ.get("PINCONE_API_KEY"), environment="us-east1-gcp")

# Pineconeのインデックス作成
pinecone_index_name = "chat-to-find"
if pinecone_index_name not in pinecone.list_indexes():
    pinecone.create_index(pinecone_index_name, dimension=1536)
index = pinecone.Index(pinecone_index_name)


GENERATE_JOB_TEXT = """
与えられた職業の求人原稿について、以下の項目で1000字程度で記載してください。

## 制約条件
・内容は実際にありそうな具体的なものにしてください。実在しなくても可。
・仕事詳細は500文字以上で具体的に記載します
・月給はINT型です
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
    "monthly_salary": 350000,
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
            {"role": "user", "content": f"職業： {job_type}"},
        ],
        max_tokens=2000,
        temperature=1.3,
    )
    job_text = response["choices"][0]["message"]["content"]
    return job_text


def main():
    job_list = [
        "エンジニア",
        "デザイナー",
        "データアナリスト",
        "プロジェクトマネージャー",
        "ウェブデザイナー",
        "マーケター",
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
    # 求人データの生成とインサートのプロセス
    for job in job_list:
        for i in range(10):
            try:
                print(f"[INFO] {i+1}回目 職種名: {job}")
                job_text = generate_job_text(job)
                job_data = job_text.split("```json")[1].strip().strip("```").strip()
                print(f"[INFO] job_data: {job_data}")

                # 求人データの埋め込みを計算
                res = openai.Embedding.create(input=job_data, engine=MODEL)
                embed = res["data"][0]["embedding"]
                print(f"[INFO] embed: {embed}")

                # Pineconeインデックスにアップサート
                job_id = f"{uuid.uuid4()}"
                index.upsert([(job_id, embed, {"content": job_data})])

            except BaseException as e:
                print(f"[ERROR] {e}")


main()
