### Вопросы:
* Q и F фильтры, Func - запрос через функцию
* Проработка с TIMEZONE, чтобы адекватно работал  auto_now_add
* Как выбирать товары на главной странице? Хранение в редисе?
* Поправить карточки товаров в CSS, чтобы они по размеру "не плясали"
* Django-toolbar что логировать?
* Подумать над тем, чтобы автоматом закрывать категорию-родителя при закрытии всех потомков(is_active)
* Подумать, как вынести queryset для хедера, чтобы можно было его использовать на всех страницах сайта
* Сделать тесты для списка товаров и списка подкатегорий

# Сделано:

## База данных:

### Общее
* Каскадное отображение категорий в хедере
* Переработан скрипт для заполнения товарами
* Создана фикстура для категорий и их характеристик с картинками
* Добавлены слаги в товары и категории для отображения в URL
    
### Апп категории
* Полностью проработана админка для категорий.
* Создана вложенность категорий
* Добавлена фильтрация и поиск в категории и характеристиках
* Сделаны групповые действия для активации\деактивации категорий
* Добавлены тесты для характеристик моделей
* Добавлено поле slug для удобного отображения url

### Апп Товары
* Полностью проработана админка для товаров.
* Добавлена фильтрация и поиск в товарах по категории и производителю
* Сделаны сигналы на добавление/удаление характеристик у товаров
  - при создании товара, характеристики добавляются из категории
  - при изменении категории товара, характеристики добавляются из новой категории
  - при удалении/добавлении характеристики в категории 
  у ВСЕХ товаров данной категории эти характеристики удаляются/добавляются
* Добавлены тесты для характеристик моделей
* Добавлены тесты для сигналов моделей
* Изменен виджет для значения характеристик типа checkbox в товарах

## Представления
* Отдельно вынесен header и footer
* Сделана полностью главная страница. Разделена на блоки section, popular_product, limit_edition.
* Тесты для главной страницы
  + открытия страницы + используемый шаблон
  + проверка количества отображений категорий в навигации, рандом-категорий, 
  популярных товаров и лимитированных товаров
* Созданы страницы со списком подкатегорий
* Оптимизирован запрос в навигации по категориям
* Создана страница товаров с пагинатором