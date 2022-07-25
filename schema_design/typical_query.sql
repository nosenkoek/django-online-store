-- ГЛАВНАЯ СТРАНИЦА
-- три избранных категории товаров
SELECT c.name, MIN(p.price)
FROM category c
JOIN product p on c.category_id = p.category_fk
AND c.is_active
GROUP BY c.name;

-- ORM Category.objects.filter(is_active=True).only('name').annotate(min_price=Min('product__price'))
EXPLAIN ANALYSE
SELECT "category"."id", "category"."name", MIN("product"."price") AS "min_price"
FROM "category"
LEFT OUTER JOIN "product" ON ("category"."category_id" = "product"."category_fk")
WHERE "category"."is_active"
GROUP BY "category"."id", "category"."name";


-- 8 топ товаров
SELECT p.name, p.price, p.image, c.name
FROM product p
JOIN category c on p.category_fk = c.category_id
ORDER BY p.price
LIMIT 8;

-- ограниченный тираж (создаем индекс product(id) WHERE is_limited)
EXPLAIN ANALYSE
SELECT p.name, p.price, p.image, c.name
FROM product p
JOIN category c on p.category_fk = c.category_id
AND p.is_limited;

-- ORM: Product.objects.select_related('category_fk').filter(is_limited=True, category_fk__is_active=True)
EXPLAIN ANALYSE
SELECT "product"."id", "product"."product_id", "product"."name", "product"."description",
       "product"."price", "product"."image", "product"."added", "product"."is_limited",
       "product"."category_fk", "product"."manufacturer_fk", "category"."id",
       "category"."category_id", "category"."name", "category"."is_active"
FROM "product"
INNER JOIN "category" ON ("product"."category_fk" = "category"."category_id")
WHERE ("category"."is_active" AND "product"."is_limited");


-- КАТАЛОГ
SELECT c.name, p.name, p.price, p.image
FROM product p
JOIN category c on p.category_fk = c.category_id
AND c.category_id = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc';

-- с фильтрами:
-- по названию (добавляем индекс GIN (по триграмм) по названию продукта)
EXPLAIN ANALYSE
SELECT p.name, p.price, p.image
FROM product p
WHERE p.name ILIKE '%owe%' AND p.category_fk = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc';


-- из ОРМ: Product.objects.filter(category_fk = '71ba1036-3bc0-4f5a-9246-c41292689f47', name__icontains='owe')
--                          .only('name', 'price').all()
EXPLAIN ANALYSE
SELECT "product"."id", "product"."name", "product"."price"
FROM "product"
WHERE ("product"."category_fk" = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc'::uuid
AND UPPER("product"."name"::text) LIKE UPPER('%owe%'));


-- по цене продукта (добавляем индекс по цене)
EXPLAIN ANALYSE
SELECT p.name, p.price, p.image
FROM product p
WHERE p.category_fk = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc'
AND (p.price <= 300 AND p.price >= 100);

-- из ОРМ: Product.objects
--                  .filter(category_fk = '71ba1036-3bc0-4f5a-9246-c41292689f47', price__lte=300, price__gte=100)
--                  .only('name', 'price').all()

EXPLAIN ANALYSE
SELECT "product"."id", "product"."name", "product"."price"
FROM "product"
WHERE ("product"."category_fk" = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc'
           AND "product"."price" >= 100.0 AND "product"."price" <= 300.0);


-- по характеристикам (добавляем индекс по pf.value - пока не понятно что именно нужно)
EXPLAIN ANALYSE
SELECT p.id, p.name, f.name, pf.value
FROM product p
JOIN product_feature pf ON p.product_id = pf.product_fk
JOIN feature f ON f.feature_id = pf.feature_fk
AND (f.name = 'Габариты' AND pf.value = 'own');

-- ORM: features = ProductFeature.objects.filter(product_fk=product).select_related('feature_fk')
-- 4 запроса =(

-- сортировка:
-- по количеству покупок товаров
SELECT p.name, p.price, p.image, COUNT(o.id) count_purchases
FROM "order" o
JOIN order_product op ON o.order_id = op.order_fk
JOIN product p ON p.product_id = op.product_fk
GROUP BY p.id
ORDER BY count_purchases DESC;

-- по цене товара
SELECT c.name, p.name, p.price, p.image
FROM product p
JOIN category c on p.category_fk = c.category_id
AND c.category_id = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc'
ORDER BY  p.price;

-- по количеству отзывов
SELECT p.name, p.price, p.image, COUNT(f.id) count_feedbacks
FROM product p
LEFT JOIN feedback f ON f.product_fk = p.product_id
GROUP BY p.id
ORDER BY count_feedbacks DESC;

-- ORM: Product.objects
--              .only('name', 'price')
--              .annotate(count_feedbacks=Count('feedback__id'))
--              .order_by('-count_feedbacks')
EXPLAIN ANALYSE
SELECT "product"."product_id", "product"."name", "product"."price", COUNT("feedback"."id") AS "count_feedbacks"
FROM "product"
LEFT OUTER JOIN "feedback" ON ("product"."product_id" = "feedback"."product_fk")
GROUP BY "product"."product_id", "product"."name", "product"."price"
ORDER BY "count_feedbacks" DESC;

-- по новизне
SELECT c.name, p.name, p.price, p.image
FROM product p
JOIN category c on p.category_fk = c.category_id
AND c.category_id = 'd87dd098-6830-4553-bdc0-3bd6e8b5d1cc'
ORDER BY  p.added;

-- ЛИЧНЫЙ КАБИНЕТ
-- история заказов
SELECT o.created, o.total_price, dm.name, pm.name, pay.status_payment, pay.error
FROM "order" o
JOIN delivery d ON o.delivery_fk = d.delivery_id
JOIN delivery_method dm ON d.delivery_method_fk = dm.method_id
JOIN payment pay ON o.payment_fk = pay.payment_id
JOIN payment_method pm ON pay.payment_method_fk = pm.method_id
WHERE user_fk = 1;
