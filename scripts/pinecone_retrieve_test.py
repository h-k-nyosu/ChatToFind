import pinecone
import os
from dotenv import load_dotenv
import openai

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
index = pinecone.Index("chat-to-find")


GENERATE_JOB_TEXT = """
与えられた会話履歴のデータをもとに、ユーザーが働きたいと思えるような求人原稿について、以下の項目で1000字程度で記載してください。

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
"""


def generate_job_text(history):
    prompt = GENERATE_JOB_TEXT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "system", "content": f"過去の会話履歴: {history}"},
        ],
        max_tokens=2000,
        temperature=1.3,
    )
    job_text = response["choices"][0]["message"]["content"]
    return job_text


history = """
ユーザー: こんにちは、求人情報を探しています。

AI: こんにちは！どのような仕事をお探しですか？

ユーザー: IT関連の仕事がいいですね。

AI: IT業界にはさまざまな職種があります。具体的にどのようなスキルや経験をお持ちですか？

ユーザー: プログラミング経験があり、特にPythonを使った開発が得意です。

"""


def main():
    try:
        job_text = generate_job_text(history)
        print(f"[INFO] job_text: {job_text}")
        job_data = job_text.split("```json")[1].strip().strip("```").strip()
        # print(f"[INFO] job_data: {job_data}")

        # 求人データの埋め込みを計算
        res = openai.Embedding.create(input=job_data, engine=MODEL)
        embed = res["data"][0]["embedding"]

        result = index.query(vector=embed, top_k=3, include_metadata=True)
        matches = result["matches"]
        for match in matches:
            metadata = match["metadata"]
            content = metadata["content"]
            print(f"{content}\n")

    except BaseException as e:
        print(f"[ERROR] {e}")


main()
