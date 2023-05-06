import openai
from app.config import OPENAI_API_KEY

IS_REQUIRED_SEARCH_SYSTEM_MESSAGE = """
## 前提
- あなたは与えられた文章から求人検索をする必要があるかをTrue/Falseで出力するAIです
- ユーザーから希望条件をヒアリングするAIの生成文章が与えられます
- 出力例に従ってTrue/Falseのみを生成します

##出力例
直近の会話:こんにちは！どのようなことでお悩みですか？
OUTPUT:False

直近の会話:はい、エンジニアの求人は多くありますよ！お持ちのスキルや経験に合わせて、検索条件を絞ることができます。何か特定のエンジニア業界に興味がありますか？
OUTPUT:False

直近の会話:なるほど、Pythonを使ったバックエンド開発の求人をお探しですね。東京での勤務を希望されるとのことでしたので、条件に合う求人をお探しいたします。少々お待ちください。
OUTPUT:True

直近の会話:了解です。リモートワーク可能なマーケティングの求人も探してみますね。ただし、都内での勤務も考えていただけると幅が広がります。
OUTPUT:True

直近の会話:了解です。Web開発のフルスタックエンジニアとしての求人を探してみますね。
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

GENERATE_OPENSEARCH_QUERY_USER_MESSAGE = """
## response by Chat AI
{ai_message}

## Output
"""


async def generate_opensearch_query(ai_message):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": GENERATE_OPENSEARCH_QUERY_SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": GENERATE_OPENSEARCH_QUERY_USER_MESSAGE.format(
                    message=ai_message
                ),
            },
        ],
        max_tokens=3000,
    )

    query = response["choices"][0]["message"]["content"]
    print(f"query: {query}")
    return query


async def generate_opensearch_query(message):
    openai.api_key = OPENAI_API_KEY

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": GENERATE_OPENSEARCH_QUERY_SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": GENERATE_OPENSEARCH_QUERY_USER_MESSAGE.format(
                    message=message
                ),
            },
        ],
        max_tokens=3000,
    )

    query = response["choices"][0]["message"]["content"]
    print(f"query: {query}")
    return query
