import openai
from app.config import OPENAI_API_KEY

IS_REQUIRED_SEARCH_SYSTEM_MESSAGE = """
## 前提
- あなたは与えられた文章から求人検索をする必要があるかをTrue/Falseで出力するAIです
- ユーザーから希望条件をヒアリングするAIの生成文章が与えられます
- 出力例に従ってTrue/Falseのみを生成します

##出力例
INPUT:こんにちは！どのようなことでお悩みですか？
OUTPUT:False

INPUT:はい、エンジニアの求人は多くありますよ！お持ちのスキルや経験に合わせて、検索条件を絞ることができます。何か特定のエンジニア業界に興味がありますか？
OUTPUT:False

INPUT:なるほど、Pythonを使ったバックエンド開発の求人をお探しですね。東京での勤務を希望されるとのことでしたので、条件に合う求人をお探しいたします。少々お待ちください。
OUTPUT:True

INPUT:了解です。リモートワーク可能なマーケティングの求人も探してみますね。ただし、都内での勤務も考えていただけると幅が広がります。
OUTPUT:True

INPUT:了解です。Web開発のフルスタックエンジニアとしての求人を探してみますね。
OUTPUT:True
"""

IS_REQUIRED_SEARCH_USER_MESSAGE = """
INPUT:{input}
OUTPUT:
"""


async def is_required_search(text):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{IS_REQUIRED_SEARCH_SYSTEM_MESSAGE}"},
            {
                "role": "user",
                "content": f"{IS_REQUIRED_SEARCH_USER_MESSAGE.format(input=text)}",
            },
        ],
        max_tokens=30,
    )

    search_is_required = "true" in response["choices"][0]["message"]["content"].lower()
    print(f'response: {response["choices"][0]["message"]["content"]}')
    print(f"検索すべきか: {search_is_required}")
    return search_is_required


GENERATE_SEARCH_QUERY_SYSTEM_MESSAGE = """
## 前提
- あなたは求人を探すための検索クエリをJSONで生成するAIです
- ユーザーとの会話はチャットAIが行なっています
- あなたはチャットAIがレスポンスをした文章をもとに適切な検索クエリを生成します

## 制約条件
- 出力形式のようなJSONを生成します。```jsonで回答を始めてください
- search_queryはスキーマを参考にしてください（ただしlocation, min_salaryは任意項目です）
- 3件の検索クエリを生成すること


## スキーマ
{
    "title": {"type": "string"},
    "search_query": {
        "keyword": {"type": "string"},
        "location": {"type": "string"},
        "min_salary": {"type": "number"}
    }
}

## 出力形式
```json
{
    "1": {
        "title": "ソフトウェアエンジニア",
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

GENERATE_SEARCH_QUERY_USER_MESSAGE = """
## AIチャットによる回答
{message}

## それを踏まえたJSON形式の出力
"""


async def generate_search_query(message):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": GENERATE_SEARCH_QUERY_SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": GENERATE_SEARCH_QUERY_USER_MESSAGE.format(message=message),
            },
        ],
        max_tokens=3000,
    )

    query = response["choices"][0]["message"]["content"]
    print(f"query: {query}")
    return query
