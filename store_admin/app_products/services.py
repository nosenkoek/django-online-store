from dataclasses import dataclass


# todo: подумать тут над pydantic
@dataclass
class SortedItem():
    field: str
    title: str
    reverse_field: str = None
    link: str = None
    reverse_link: str = None

    def __post_init__(self):
        self.reverse_field = f'-{self.field}'
