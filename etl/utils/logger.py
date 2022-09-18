import logging
from os import path


class SingletonMeta(type):
    """ Паттерн Одиночка. Создание мета класса"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, *kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ETLLogger(metaclass=SingletonMeta):
    def __init__(self):
        self._my_path = path.dirname(path.abspath(__file__))
        self._logger = logging.getLogger('logger')
        self._config_log()
        self._config_err()

    def _config_log(self):
        path_log = path.join(self._my_path, '../log/logging.log')
        logging.basicConfig(filename=path_log,
                            filemode='a',
                            encoding='utf-8',
                            level=logging.INFO,
                            format='%(levelname)s | %(asctime)s | %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S'
                            )

    def _config_err(self):
        path_err = path.join(self._my_path, '../log/errors.log')
        err_handler = logging.FileHandler(path_err, mode='a', encoding='utf-8')
        error_format = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s')
        err_handler.setFormatter(error_format)
        err_handler.setLevel(logging.ERROR)

        self._logger.addHandler(err_handler)

    def get_logger(self):
        return self._logger
