import openai
from app.config import OPENAI_API_KEY

IS_REQUIRED_SEARCH_SYSTEM_MESSAGE = """
## 前提
- あなたは与えられた文章から求人検索をする必要があるかをTrue/Falseで出力するAIです
- ユーザーから希望条件をヒアリングするAIの生成文章が与えられます
- 検索する場合は「少々お待ちください」といったユーザーに待ってもらうように伝えられます
- 出力例に従ってTrue/Falseのみを生成します

##出力例
直近の会話:こんにちは！どのようなことでお悩みですか？
OUTPUT:False

直近の会話:はい、エンジニアの求人は多くありますよ！お持ちのスキルや経験に合わせて、検索条件を絞ることができます。何か特定のエンジニア業界に興味がありますか？
OUTPUT:False

直近の会話:なるほど、Pythonを使ったバックエンド開発の求人をお探しですね。東京での勤務を希望されるとのことでしたので、条件に合う求人をお探しいたします。少々お待ちください。
OUTPUT:True

直近の会話:了解です。デジタルマーケティングの経験を活かせる、WebディレクターやPMの求人を探しますね。少々お待ちください。
OUTPUT:True

直近の会話:了解です。Web開発のフルスタックエンジニアとしての求人を検索します。少々お待ちください。
OUTPUT:True

直近の会話:了解です。販売スタッフの求人を探しますね。探してみます。少々お待ちください。
OUTPUT:True

"""

IS_REQUIRED_SEARCH_USER_MESSAGE = """
{input}
OUTPUT:
"""


async def is_required_search(message):
    openai.api_key = OPENAI_API_KEY
    print(f"{IS_REQUIRED_SEARCH_USER_MESSAGE.format(input=message)}")
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{IS_REQUIRED_SEARCH_SYSTEM_MESSAGE}"},
            {
                "role": "user",
                "content": f"{IS_REQUIRED_SEARCH_USER_MESSAGE.format(input=message)}",
            },
        ],
        max_tokens=30,
    )

    search_is_required = "true" in response["choices"][0]["message"]["content"].lower()
    print(f'response: {response["choices"][0]["message"]["content"]}')
    print(f"検索すべきか: {search_is_required}")
    return search_is_required


GENERATE_OPENSEARCH_QUERY_SYSTEM_MESSAGE = """
## Premise
- You are an AI that generates search queries for job listings in JSON format.
- The user's conversation is handled by a chat AI.
- You generate appropriate search queries based on the text that the chat AI has responded with.
- keyword words should be separated by spaces

## Constraints
- Generate JSON in the output format shown below. Start your response with ```json.
- Refer to the schema for the search_query (however, location and min_salary are optional fields).
- Generate 3 search queries.
- Answer all questions in Japanese. lang:ja

## Schema
{
"title": {"type": "string"},
"search_query": {
"keyword": {"type": "string"},
"location": {"type": "string"},
"min_salary": {"type": "number"}
}
}

## Output Format
```json
{
    "1": {
        "title": "ソフトウェア エンジニア",
        "search_query": {
            "keyword": "ソフトウェアエンジニア",
            "location": "東京",
            "min_salary": 200000,
        }
    },
    "2": {
        "title": "データサイエンティスト",
        "search_query": {
            "keyword": "データサイエンティスト"
        }
    },
    "3":  {
        "title": "販売スタッフ",
        "search_query": {
            "keyword": "販売スタッフ"
        }
    }
}
```
"""

GENERATE_OPENSEARCH_QUERY_USER_MESSAGE = """
{messages}

## Output
"""


async def generate_opensearch_query(messages):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": GENERATE_OPENSEARCH_QUERY_SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": GENERATE_OPENSEARCH_QUERY_USER_MESSAGE.format(
                    messages=messages
                ),
            },
        ],
        max_tokens=3000,
    )

    query = response["choices"][0]["message"]["content"]
    print(f"query: {query}")
    return query


GENERATE_PINECONE_QUERY_SYSTEM_MESSAGE = """
与えられた会話履歴のデータをもとに、ユーザーが働きたいと思えるような求人原稿について、以下の項目で1000字程度で記載してください。

## 制約条件
・内容は実際にありそうな具体的なものにしてください。実在しなくても可。
・仕事詳細は500文字以上で具体的に記載します
・月給はINT型です
・求人タイトル、仕事概要、仕事詳細は求人に応募したいと思う魅力的な文章にしてください
・出力形式は```jsonから始まり、```で終わるようにしてください


## 出力例
```json
{{
    "1": {
        "search_title": "Webアプリケーション開発エンジニア",
        "search_query": {
            "title": "Webアプリケーション開発エンジニア募集！",
            "job_type": "ソフトウェアエンジニア",
            "job_summary": "当社の開発チームで、Webアプリケーションの開発を担当していただくエンジニアを募集しています。",
            "job_details": "ReactやAngularを使ったフロントエンド開発、PHPやRuby on Railsを使ったバックエンド開発、データベース設計やデータベースの最適化、AWSのクラウド環境の構築、運用・保守、プロジェクトマネジメントなど、幅広い業務をお任せします。開発環境は個人の希望に合わせて調整可能です。",
            "monthly_salary": 350000,
            "location": "東京都千代田区"
        }
    }
}}
```
"""

GENERATE_PINECONE_QUERY_USER_MESSAGE = """
{messages}

## Output
"""


async def generate_pinecone_query(messages):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": GENERATE_PINECONE_QUERY_SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": GENERATE_PINECONE_QUERY_USER_MESSAGE.format(
                    messages=messages
                ),
            },
        ],
        max_tokens=3000,
    )

    query = response["choices"][0]["message"]["content"]
    return query
