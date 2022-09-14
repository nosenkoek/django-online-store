from dataclasses import dataclass


@dataclass
class SortedItem():
    field: str
    title: str
    reverse_field: str = None
    link: str = None
    reverse_link: str = None

    def __post_init__(self):
        self.reverse_field = f'-{self.field}'


class AddSortedItemToContextMixin():
    """Миксин для добавления полей сортировки товаров"""
    SORTED_LIST = [
        SortedItem('price', 'Цене'),
        SortedItem('added', 'Новизне')
    ]

    def add_sorted_item_to_context(self) -> None:
        """ Добавление списка полей для сортировки"""
        self.extra_context.update({'sorted_list': self.SORTED_LIST})
