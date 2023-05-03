import openai
from app.config import OPENAI_API_KEY

GENERATE_SEARCH_QUERY_PROMPT = """
あなたは検索クエリジェネレータです。
与えられた文章から、関連する求人データを検索するための検索クエリを生成してください。ただし以下の制約条件に従うこと。

## 制約条件
・出力結果例の形式に従ってJSON形式で回答します
・search_queryはスキーマに従うこと
・3件の検索クエリを生成すること
・titleには検索を一言で表す言葉を生成すること。最終的に`[title]の求人`として出力されます
・nullや空文字は記載してはいけません

schema = {
    "title": {"type": "string"},
    "search_query": {
        "keyword": {"type": "string"},
        "location": {"type": "string"},
        "min_salary": {"type": "number"}
    }
}

## 出力結果例
1件目
```json
{
    "title": "ソフトウェアエンジニア",
    "search_query": {
        "keyword": "ソフトウェアエンジニア",
        "location": "東京",
        "min_salary": 200000,
    }
}
```

2件目
```json
{
    "title": "データサイエンティスト",
    "search_query": {
        "keyword": "データサイエンティスト"
    }
}
```

3件目
```json
{
    "title": "販売スタッフ",
    "search_query": {
        "keyword": "販売スタッフ"
    }
}
```
"""

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
"""

IS_REQUIRED_SEARCH_AI_MESSAGE = """
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
                "content": f"{IS_REQUIRED_SEARCH_AI_MESSAGE.format(input=text)}",
            },
        ],
        max_tokens=30,
    )

    search_is_required = "true" in response["choices"][0]["message"]["content"].lower()
    print(f'response: {response["choices"][0]["message"]["content"]}')
    print(f"検索すべきか: {search_is_required}")
    return search_is_required


async def generate_search_query(text):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{GENERATE_SEARCH_QUERY_PROMPT}"},
            {"role": "user", "content": f"{text}"},
        ],
        max_tokens=2000,
    )

    sql_response = response["choices"][0]["message"]["content"]
    return sql_response
