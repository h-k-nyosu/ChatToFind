from typing import List
from .models import Item

def get_items() -> List[Item]:
    items = [
        Item(name="アイテム1", image="https://placehold.jp/300x200.png"),
        Item(name="アイテム2", image="https://placehold.jp/300x200.png"),
        Item(name="アイテム3", image="https://placehold.jp/300x200.png"),
        # 他のアイテムを追加
    ]
    return items
