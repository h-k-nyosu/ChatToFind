from typing import List
from .models import Item


def get_items() -> List[Item]:
    items = [
        Item(name="アイテム1", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム2", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム3", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム4", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム5", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム6", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム7", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム8", image="https://placehold.jp/300x100.png"),
        Item(name="アイテム9", image="https://placehold.jp/300x100.png"),
    ]
    return items
