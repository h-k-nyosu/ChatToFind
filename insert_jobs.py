import os
import openai
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Depends
from contextlib import contextmanager

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

SQL_FORMAT_PROMPT = """
与えられた文章から、次のスキーマに当てはまる実行可能なSQLに変換してください。

## スキーマ
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    job_type VARCHAR(255) NOT NULL,
    job_summary TEXT NOT NULL,
    job_details TEXT NOT NULL,
    monthly_salary INT NOT NULL,
    location VARCHAR(255) NOT NULL
);

## 出力結果例
INSERT INTO jobs (title, job_type, job_summary, job_details, location) VALUES
('Job Title 1', 'Job Type 1', 'Job Summary 1', 'Job Details 1', 'Location 1'),
('Job Title 2', 'Job Type 2', 'Job Summary 2', 'Job Details 2', 'Location 2');
"""

GENERATE_JOB_TEXT = """
{job_type}の求人原稿について、以下の項目で1000字程度で記載してください。

## 項目
・求人タイトル
・仕事概要
・仕事詳細
・勤務地
・給与（月給）

## 制約条件
・内容は実際にありそうな具体的なものにしてください。実在しなくても大丈夫です
・仕事詳細は特に具体的な詳細まで記載してあるのが好ましいです
・ありきたりなものではなく、見てみたくなる求人タイトルを命名してください
"""

def convert_to_sql(text):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": f"{SQL_FORMAT_PROMPT}"},
                  {"role": "user", "content": f"{text}"}],
        max_tokens=2000,
    )

    sql_response = response['choices'][0]['message']['content']
    return sql_response


def generate_job_text(job_type):
    prompt = GENERATE_JOB_TEXT.format(job_type=job_type)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": f"{prompt}"}],
        max_tokens=2000,
    )
    job_text = f"職種名\n{job_type}"
    job_text += response['choices'][0]['message']['content']
    return job_text


DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_jobs(query:str):
    with get_db() as db:
        res = db.execute(text(query))
        db.commit()
        return res 

def main():
    job_list = ["ソフトウェアエンジニア", "グラフィックデザイナー", "データアナリスト", "プロジェクトマネージャー", "ウェブデザイナー", "マーケティングスペシャリスト", "広報・PR担当", "人事担当", "経理・財務担当", "営業担当", "イベントプランナー", "コンサルタント", "システム管理者", "コンテンツライター・エディター", "翻訳者・通訳者", "保育士・幼稚園教諭", "教育コーディネーター", "医師・看護師", "物流・倉庫管理", "料理人・シェフ", "バーテンダー", "美容師・美容部員", "フィットネスインストラクター", "不動産エージェント", "旅行アドバイザー", "インテリアデザイナー", "農業・園芸関連職", "環境・エネルギー関連職"]
    for job in job_list:
        for i in range(5):
            try:
                print(f"[INFO] {i}回目 職種名: {job}")
                job_text = generate_job_text(job)
                print(f"[INFO] job_text: {job_text}")
                job_query = convert_to_sql(job_text)
                print(f"[INFO] job_query: {job_query}")
                res = create_jobs(job_query)
                print(f"[INFO] res: {res}")
            except BaseException as e:
                print(f"[ERROR] {e}")
            

main()
