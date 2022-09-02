import re
from typing import Dict


class InitialDictFromURLMixin():
    def get_initial_dict(self) -> Dict[str, str]:
        """
        Преобразование диапазона цен.
        :param urlencode: параметры фильтра в url
        :return: словарь со значениями фильтрации
        """
        # todo: re.compile
        initial = re.findall(r"([^&]*=[^&]{1,})", self.request.GET.urlencode())
        initial_dict = {item.split('=')[0]: item.split('=')[1]
                        for item in initial}

        if 'price' in initial_dict.keys():
            price_str = initial_dict.get('price')

            initial_dict.update({'price_from': price_str.split('%3B')[0],
                                 'price_to': price_str.split('%3B')[1]})

        return initial_dict