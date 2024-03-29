*Данные репозитория являются интеллектуальной собственностью автора 
и не подлежат копированию без согласования.*

# Веб-приложение интернет-магазин
На данном этапе реализован основной функционал показа товаров. Главная страница, 
страницы категорий и страницы каталогов товаров подкатегорий. Реализована возможность 
фильтрации и сортировки товаров для удобного выбора в каталоге. Наборы фильтров отличаются 
для каждой категории. Работает поисковая строка для полнотекстового поиска товара 
по названию, бренду и категории. Каждый товар имеет страницу, где отображается 
детальная информация о нем. Имеется страница популярных товаров, которые сортируются 
по количеству просмотров конкретных товаров.

Добавлен личный кабинет с возможностью регистрации. 
Товары добавляются в корзину со страниц со списками товаров и их детальных страниц. 
Имеется возможность изменить количество или удалить товары из корзины, а также очистить корзину.

Настроена панель администратора для удобного добавления/изменения товаров и категорий.

Интернет-магазин работает на английском и русском языках.

Для начала работы интернет-магазина созданы фикстуры с категориями и характеристиками,
добавлены медиа-файлы для отображения на сайте,
а также программа для заполнения БД случайными товарами (файл common/util_fill_db/fill_products.py).

# Процесс разворачивания проекта
Для разворачивания проекта используется docker-compose. Для этого необходимо:
- указать переменные окружения в store_admin/config/.env
```
DB_NAME =
DB_USER =
DB_PASSWORD =
SECRET_KEY=
```
- указать переменные окружения БД в schema_design/pg.env
```
POSTGRES_DB = 
POSTGRES_USER =
POSTGRES_PASSWORD =
PORT = 5432
```
- скачать данные репозитория и запустить docker:
```
docker-compose up -d --build
```
- при необходимости заполнить БД случайными товарами, для этого необходимо запустить скрипт 
```
common/util_fill_db/fill_products.py
```

# Архитектура приложения
## Основные компоненты
Интернет-магазин построен на базе фреймворка Django. Данное веб-приложение состоит 
из 5 основных компонентов (контейнеров):
- База данных (СУБД PostgreSQL),
- NoSql база данных (Redis),
- Elasticsearch,
- ETL,
- store_app.

## База данных
База данных разворачивается в контейнере db. Основные файлы хранятся в папке schema_design.

Инициализация базы производится с помощью запуска DDL-файла (init.sql), в котором 
описана структура БД, а также необходимые связи и индексы для работы.
Кроме этого, для дополнительной информации описаны основные типичные запросы к БД 
при работе интернет-магазина(schema_design/typical_query.sql), а также схема БД(schema_design/shema_db.jpg).

В дальнейшем взаимодействие с БД производится с помощью ORM-django. 
Запросы к БД оптимизированы с помощью методов select_related, prefetch_related.

## Приложение интернет-магазина
Разворачивается в контейнере store_app. Состоит из 5 приложений:
- категории (app_categories),
- товары (app_products),
- полнотекстовый поиск (app_search),
- пользователи (app_users),
- корзина (app_cart).

В данном проекте используется наследование в html-шаблонах. Имеется базовый шаблон, 
от которого наследуются остальные шаблоны. Имеются блоки header, footer и 
content(сами шаблоны, которые передаются во view).

### App_categories
Приложение, которое отвечает за хранение и обработку данных о категориях. 

Модели: 
- Category(для реализации вложенности категорий используется библиотека MPTT),
- Feature,
- CategoryFeature(промежуточная таблица для связи many-to-many). 

Представления:
- MainPageView,
- SubcategoriesListView.

Сервисы:
- **navi_categories_list.py** 

  NaviCategoriesList.get_context() - добавление данных о категориях для навигации в header.
- **section_factory.py**

  SectionsFactory.get_section_view(context_name) - фабрика (паттерн Фабричный метод), возвращает 
представление с контекстом блоков главной страницы.

Администрирование:
- групповые действия для активации/деактивации категорий
- поиск по названию категории/характеристики
- фильтрация по основным признакам

### App_products
Приложение отвечающие за товары. 

Модели: 
- Manufacturer,
- Product,
- Image,
- ProductFeature(промежуточная таблица для связи many-to-many),
- Feedback.

Сигналы:
- add_features_product, post_save - добавление характеристик к товарам из категории
- add_features_product_when_update_category, post_save - добавление характеристики в 
продукт при добавлении его в категорию
- delete_features_product_when_update_category, post_delete - удаление характеристики 
у продукта при удалении его из категории

Представления:
- ProductListView,
- ProductDetailView,
- PopularProductListView.

Сервисы:
- **decorator_count_views.py**

  cache_popular_product - декоратор, создает сортированный список популярных 
товаров по количеству просмотров и сохраняет его в Redis. Применен паттерн 
Стратегия для рабочей версии проекта и для выполнения модульных тестов.

- **handler_url_params.py**

  InitialDictFromURLMixin.get_initial_dict - создает словарь с данными фильтрации 
  товаров в каталоге из URL-адреса

- **sorted_item.py**

  SortedItem - Dataclass для создания объектов сортировки (например: Цена, Популярность)
AddSortedItemToContextMixin.add_sorted_item_to_context() - добавляет объекты сортировки в контекст

Фильтры для админки(filters/admin_filters.py):
- ProductCategoryFilterAdmin,
- ProductManufacturerFilterAdmin,
- FeedbackProductFilterAdmin,
- FeedbackUsernameFilterAdmin.

Фильтры для отображений(filters/product_filters.py):
используется библиотека django-filter
- ProductFilterCommon 

  Объект фильтров для товаров всех категорий(цена, название, наличие и производитель).

- ProductFilter

  Объект фильтров, в котором динамически добавляются поля характеристик по выбранной категории.

Шаблонные теги (templatetags/tags.py):
- solve_url

  Тег для "сборки" URL-адреса при выборе различных параметров сортировки/фильтрации/пагинации

Администрирование товаров:
- поиск товаров по названию товара/производителя
- дополнительная фильтрация товаров по категории и производителю(текст)
- изменен виджет для ввода характеристик с типом checkbox на да/нет.

Администрирование отзывов:
- поиск отзывов по тексту,
- фильтрация отзывов по логину(username) пользователя и товару.

### App_search
Реализует полнотекстовый поиск по товарам с помощью elasticsearch.

Представления:
- SearchResultListView

Сервисы:
- SearchResultMixin.search_match(query: str)

  Возвращает список product_id товаров релевантных по query из ES.

Шаблонные теги (templatetags/tags.py):
- **solve_url**

  Тег для "сборки" URL-адреса при выборе различных параметров сортировки/фильтрации/пагинации

- **url_clear_filter**

  Тег для расчета URL при очистке фильтра, сохраняет текст запроса поиска.

### App_users
Приложение, реализующее работу с пользователями. Вход и выход из личного кабинета, 
регистрация новых пользователей и странницы аккаунта и изменения профиля.

Модели: 
- User(AbstractUser) 
  пользовательская модель для добавления новых полей (аватар, телефон, отчество).

Представления:
- RegisterView (регистрация новых пользователей, 2 формы - основная и профиль)
- UserLoginView 
- UserLogoutView
- AccountView (представление для отображения страницы личного кабинета)
- ProfileView (представление для страницы редактирования профиля)

Формы:
- RegisterForm (форма для регистрации нового пользователя)
  Поля: username, first_name, last_name, patronymic, tel_number,  email, password1, password2

- UserProfileForm (форма для редактирования профиля ModelForm User)
  Поля: full_name, tel_number, avatar, email, password1, password2


Сервисы (services.py):
- LoginUserMixin.authenticate_and_login(self, username: str, raw_password: str) - вход в систему пользователя
- InitialDictMixin.get_initial_form(user: User) - возвращает словарь с данными для заполнения формы
- SetPasswordMixin.set_password(self, form: UserProfileForm) - устанавливает новый пароль и входит в систему

Администрирование:
- поиск по username, имени и фамилии,
- расширенный показ данных в сводной таблице.

### App_cart
Приложение, реализующее работу с корзиной пользователя. 
Данные о наполненности корзины хранятся на стороне "клиента" в сессии. 
Данные сессий сохраняются в NoSql-бд Redis.

Представления:
- CartView (отображение корзины)
- AddProductCartView (добавление товара в корзину со страниц со списками товаров) 
При переходе к этой view происходит добавление товара в корзину и переадресация на страницу, 
на которой был пользователь.
- UpdateProductCartVIew (добавление товаров через форму, используется на детальной страницу товаров)
- RemoveProductCartView (удаление 1шт. товара из корзины)
- DeleteAllProductCartView (удаление товаров одного типа из корзины)
- ClearCartView (очищение корзины)

Формы:
- CartAddProductForm (форма для добавления определенного количества товаров)
  Поля: quantity, update.

Сервисы (services/mixins_for_cart.py):
- GetContextTotalPriceCartMixin.get_context_price_cart(self) - возвращает словарь с данными о корзине для хэдера
- CartRequestMixin - добавляет объект корзины в атрибуты основного класса
- NextURLRequestMixin - добавляет в атрибуты класса страницы перехода

Объект корзины Cart (сart.py):
Создается на основании сессии пользователя, определяются основные параметры. 
Данные в сессии хранятся в виде словаря:
```
{product_id: {'quantity': count}}
```
где product_id: UUID товара, count: int, количество данного товара в корзине

Методы объекта Cart:
- save() - сохранение корзины в сессии,
- add(product_id: UUID, quantity=1, updated=False) - добавление товаров в корзину,
если установлен флаг updated=False - увеличение количества на 1, 
если updated=True - значение количества товара берется из формы
- remove(product_id: UUID) - уменьшение количества товара в корзине на 1,
- delete_all(product_id: UUID) - удаление товара в корзине,
- clear() - очистка корзины,
- get_total_price() - возвращает общую стоимость всех товаров в корзине,
- get_quantity(product_id: UUID) - возвращает количество товаров 1 типа.


## NoSql база данных. Redis
Разворачивается в контейнере redis. На данном этапе служит для хранения 
информации о количестве просмотров товаров, списка 16 популярных товаров, 
а также для хранения даты и времени последней миграции данных из БД в elasticsearch.

Redis используется в качестве базы для хранения кэша, для этого подключается 
бэкэнд из библиотеки redis-django.

Ключи:
- count_views - хэш-таблица с парами product_id - количество просмотров
- popular_product_ids - список с product_id популярных товаров
- pg_updated_at - дата и время последней миграции из БД в es
- count_views_test - аналогично count_views, создается при выполнении модульных тестов, 
удаляется вместе с тестовой БД
- popular_product_ids_test - аналогично popular_product_ids, создается при выполнении 
модульных тестов, удаляется вместе с тестовой БД

## Elasticsearch
Разворачивается в контейнере es. Elasticsearch версии 7.17.6. Создает 1 ноду.

## ETL
Разворачивается в контейнере etl. Сервис для создания индекса в es и заполнения 
его актуальными данными из БД.

Индекс products с полями:
- product_id(уникальный идентификатор товара для поиска его в БД)
- category(название категории товара)
- name(название товара)
- description(описание товара)
- manufacturer(производитель)

Данные в индексе могут быть на английском и русском языках, введены стандартные стоп-слова, 
слова приводятся к начальной форме и убран притяжательный падеж в английском языке.
Создание индекса производится с помощью скрипта:
```
etl/init.py
```
Описание настроек индекса отражены в файле:
```
etl/es_index.json
```
Основная миграция производится запуском файла:
```
etl/main.py
```

Для запуска процесса миграции данных PG -> ES по расписанию в контейнере 
запускается bash-скрипт. 
```
etl/etl.sh
```
В ходе его работы проверяется состояние ES-сервера и с частотой в 5 минут 
запускает main.py. 

ETL состоит из 3х основных блоков:
- подключение к разным источникам данных (PostgreSQL, Redis и Elasticsearch)
  ```
  etl/utils/connectors.py
   ```
  Используется паттерн Фабричный метод. 

  FactoryConnection.get_connection(key: str) возвращает контекст-менеджер для подключения.

- обработчики взаимодействия с источниками данных (загрузка и выгрузка).
  ```
  etl/utils/handlers.py
   ```
  Используется паттерн Фабричный метод.

  ETLHandler - внешний интерфейс:
  + get_pg_updated_at() - получение даты/времени последней миграции из redis
  + load_pg_updated_at() - запись даты/времени в redis произведенной миграции
  + get_pg_data(pg_updated_at) - получение пакета данных из PG(генератор)
  + load_es_data(es_data) - запись данных в es
  
- адаптер для трансформации данных, полученных из БД, в вид принимаемый ES. 
- Паттерн Адаптер.
  ```
  etl/utils/pg_es_adapter.py
   ```
  Для валидации данных и преобразования в словарь используется библиотека Pydantic.

# Модульные тесты приложения

Для проверки сохранения работоспособности веб-приложения после изменений были написаны 
модульные тесты на основные элементы проекта. Перед тем, как развернуть приложение 
с изменениями рекомендуется запускать тесты, для этого необходимо:
- развернуть в докере 3 основных компонента: PostgreSQL, Elasticsearch и Redis
- проверить настройки серверов в store_admin/config/components/database.py
  ```
  REDIS_HOST = 'localhost'
  REDIS_PORT = 6379
  
  ES_HOST = 'localhost'
  ES_PORT = 9200
   ```
- локально запустить команду :
  ```
  python manage.py test
   ```

# Дальнейшее развитие проекта
На данном этапе реализована только часть предполагаемого общего функционала. 
В дальнейшем планируется добавить:
- приложение app_orders:
  + возможность оформления заказов
  + просмотр истории заказов
  + просмотр детальной информации о заказе
- приложение app_payment:
  + оплата заказа (с помощью карты или со случайного счета)
- приложение app_compare:
  + возможность добавления товара к сравнению
  + страница отображения сравнения товаров
  