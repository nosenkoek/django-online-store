DROP TABLE IF EXISTS "content".order_product;

DROP TABLE IF EXISTS "content".category_feature;
DROP TABLE IF EXISTS "content".product_feature;
DROP TABLE IF EXISTS "content".product;
DROP TABLE IF EXISTS "content".feature;
DROP TABLE IF EXISTS "content".category;
DROP TABLE IF EXISTS "content".feedback;
DROP TABLE IF EXISTS "content".manufacturer;

DROP TABLE IF EXISTS "content".order;
DROP TABLE IF EXISTS "content".delivery;
DROP TABLE IF EXISTS "content".payment;
DROP TABLE IF EXISTS "content".delivery_method;
DROP TABLE IF EXISTS "content".payment_method;



SELECT cat.name, COUNT(*) count_feature
FROM "content".category_feature AS cf
JOIN "content".category AS cat ON cat.id=cf.category_fk
JOIN "content".feature AS f ON f.id=cf.feature_fk
GROUP BY cat.name;

SELECT p.name product, c.name category, m.name manufacturer, p.added
FROM "content".product p
JOIN "content".category c ON c.id=p.category_fk
JOIN "content".manufacturer m ON m.id=p.manufacturer_fk
LIMIT 5;

SELECT p.name, c.name, f.name, pf.value
FROM "content".product_feature pf
JOIN "content".product p ON p.id=pf.product_fk
JOIN "content".feature f ON f.id=pf.feature_fk
JOIN "content".category c ON c.id=p.category_fk
AND p.id::text = '197106cb-49dd-4aba-9ff8-7f53ce198ad1';

SELECT *
FROM product p;

SELECT dm.name, d.price, d.address
FROM delivery d
JOIN delivery_method dm ON dm.id = d.delivery_method_fk;

SELECT p.name, COUNT(o.id)
FROM product p
JOIN order_product op ON op.product_fk = p.id
JOIN "order" o ON op.order_fk = o.id
GROUP BY p.id;

SELECT o.username, o.created, p.name, pm.name, dm.name, d.address
FROM "order" o
JOIN order_product op ON o.id = op.order_fk
JOIN product p ON p.id = op.product_fk
JOIN payment pay ON pay.id = o.payment_fk
JOIN payment_method pm ON pm.id = pay.payment_method_fk
JOIN delivery d ON d.id = o.delivery_fk
JOIN delivery_method dm ON dm.id = d.delivery_method_fk
ORDER BY o.username, p.name;