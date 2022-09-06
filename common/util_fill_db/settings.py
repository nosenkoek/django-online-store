DSN = {
    'dbname': 'store_db',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432,
    'options': '-c search_path=content',
    'connect_timeout': 5
}

MANUFACTURERS_COUNT = 5
PRODUCTS_IN_CATEGORY_COUNT = 125
PRODUCTS_LIMITED_COUNT = 10
PAGE_SIZE = 50

IMAGE_LINKS = [
    'product_images/mac.png',
    'product_images/videoca.png',
    'product_images/tablet.png',
    'product_images/wash.png',
    'product_images/smartphone.png',
    'product_images/watch.png',
    'product_images/audio.png',
    'product_images/notebook.png',
    'product_images/tv.png',
    'product_images/ddr4.png',
    'product_images/comp.png',
    'product_images/blender.png',
    'product_images/headset.png',
    'product_images/photo.png',
    'product_images/microwave.png',
]

FEATURES_VALUE = {
    'Оперативная память': ['2Гб', '4Гб', '8Гб', '16Гб'],
    'Память': ['64Гб', '128Гб', '256Гб', '512Гб'],
    'Цвет': ['белый', 'серебро', 'красный', 'черный', 'золото'],
    'Частота': ['2133МГц', '2666МГц', '3200МГц'],
    'Поколение': ['DDR4', 'DDR3'],
    'Экран': ['9"', '11"', '13"', '15"', '17"'],
    'Разъемы подключений': ['USB 2.0', 'USB 3.0', 'USB type-C',
                            'bluetooth', 'HDMI']
}

FEATURES_GROUP_TEXT = {
    'a721c742-44cf-444f-886a-93769378ca25': ['USB 2.0', 'USB 3.0',
                                             'USB type-C', 'bluetooth', 'HDMI']
}
