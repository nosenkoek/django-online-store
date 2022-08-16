class SortedItem():
    """
    Объект поля сортировки для списка товаров
    Args:
        field(str): поле в модели,
        verbose_name(str): название поля
    """
    def __init__(self, field: str, verbose_name: str):
        self._link = f'?sort={field}'
        self._title = verbose_name
        self._field = field

    @property
    def field(self) -> str:
        return self._field

    @property
    def link(self) -> str:
        return self._link

    @property
    def title(self) -> str:
        return self._title

    @property
    def get_reverse_field(self) -> str:
        """ Возвращает поле с обратной сортировкой"""
        return f'-{self._field}'

    @property
    def get_reverse_link(self) -> str:
        """ Возвращает ссылку с обратной сортировкой"""
        return f'?sort=-{self.field}'
