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

## スキーマ
class JobQueryParams:
    keyword: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[int] = None

## 出力結果例
1件目
```json
{{
    "title": "ソフトウェアエンジニア",
    "search_query": {
        "keyword": "ソフトウェアエンジニア",
        "location": "東京",
        "min_salary": 200000,
    }
}}
```

2件目
```json
{{
    "title": "データサイエンティスト",
    "search_query": {
        "keyword": "データサイエンティスト"
    }
}}
```

3件目
```json
{{
    "title": "販売スタッフ",
    "search_query": {
        "keyword": "販売スタッフ"
    }
}}
```

"""


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
