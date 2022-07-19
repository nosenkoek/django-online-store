CREATE SCHEMA IF NOT EXISTS "content";

-- PRODUCTS

DROP TABLE IF EXISTS "content".order_product;

DROP TABLE IF EXISTS "content".category_feature;
DROP TABLE IF EXISTS "content".product_feature;
DROP TABLE IF EXISTS "content".product;
DROP TABLE IF EXISTS "content".feature;
DROP TABLE IF EXISTS "content".category;
DROP TABLE IF EXISTS "content".feedback;
DROP TABLE IF EXISTS "content".manufacturer;

CREATE TABLE "content".category (
    id uuid PRIMARY KEY,
    category_id uuid NOT NULL,
    name varchar(30) NOT NULL,
    is_active bool NOT NULL
);

CREATE TABLE "content".feature(
    id uuid PRIMARY KEY,
    feature_id uuid NOT NULL,
    name varchar(30) NOT NULL
);

CREATE TABLE "content".category_feature(
--     id uuid PRIMARY KEY,
    category_fk uuid REFERENCES "content".category(id) ON DELETE CASCADE,
    feature_fk uuid REFERENCES "content".feature(id) ON DELETE CASCADE,
    CONSTRAINT category_feature_pk PRIMARY KEY (category_fk, feature_fk)
);

CREATE TABLE "content".feedback(
    id uuid PRIMARY KEY,
    feedback_id uuid NOT NULL,
    text text NOT NULL,
    username varchar(30) NOT NULL  -- todo:потом переделать в FK
);

CREATE TABLE "content".manufacturer (
    id uuid PRIMARY KEY,
    manufacturer_id uuid NOT NULL,
    name varchar(30) NOT NULL
);

CREATE TABLE "content".product(
    id uuid PRIMARY KEY,
    product_id uuid NOT NULL,
    name varchar(50) NOT NULL,
    description text NOT NULL,
    price real NOT NULL,
    image varchar(30) NOT NULL,
    added timestamp NOT NULL,
    is_limited bool NOT NULL,
    category_fk uuid REFERENCES "content".category(id) ON DELETE CASCADE,
    manufacturer_fk uuid REFERENCES "content".manufacturer(id) ON DELETE CASCADE,
    feedback_fk uuid REFERENCES "content".feedback(id) ON DELETE CASCADE
);

-- TODO: подумать как сделать ограничение, чтобы к товару не была добавлена характеристика НЕ из той категории
CREATE TABLE "content".product_feature(
    product_fk uuid REFERENCES "content".product(id) ON DELETE CASCADE,
    feature_fk uuid REFERENCES "content".feature(id) ON DELETE CASCADE,
    value varchar(20) NOT NULL,
    CONSTRAINT product_feature_pk PRIMARY KEY (product_fk, feature_fk)
);

-- ORDERS

DROP TABLE IF EXISTS "content".order;
DROP TABLE IF EXISTS "content".delivery;
DROP TABLE IF EXISTS "content".payment;
DROP TABLE IF EXISTS "content".delivery_method;
DROP TABLE IF EXISTS "content".payment_method;



CREATE TABLE "content".payment_method (
	id uuid PRIMARY KEY,
	method_id uuid NOT NULL,
	name varchar(30) NOT NULL
);

CREATE TABLE "content".delivery_method (
	id uuid PRIMARY KEY,
	method_id uuid NOT NULL,
	name varchar(30) NOT NULL,
	price real NOT NULL,
	free_from real
);

CREATE TABLE "content".delivery(
    id uuid PRIMARY KEY,
    delivery_id uuid NOT NULL,
    price real NOT NULL,  -- todo: продумать автозаполнение или проверку
    address text NOT NULL, -- возможно использовать json
    delivery_method_fk uuid REFERENCES "content".delivery_method ON DELETE CASCADE
);

CREATE TABLE "content".payment(
    id uuid PRIMARY KEY,
    payment_id uuid NOT NULL,
    status_payment bool NOT NULL,
    error text,
    payment_method_fk uuid REFERENCES "content".payment_method ON DELETE CASCADE
);


CREATE TABLE "content".order(
    id uuid PRIMARY KEY,
    order_id uuid NOT NULL,
    created timestamp NOT NULL,
    total_price real NOT NULL,
    username varchar(30) NOT NULL,  -- todo:потом переделать в FK
    delivery_fk uuid UNIQUE REFERENCES "content".delivery ON DELETE CASCADE,
    payment_fk uuid UNIQUE REFERENCES "content".payment ON DELETE CASCADE
);

CREATE TABLE "content".order_product(
    order_fk uuid REFERENCES "content".order(id) ON DELETE CASCADE,
    product_fk uuid REFERENCES "content".product(id) ON DELETE CASCADE,
    CONSTRAINT order_product_pk PRIMARY KEY (order_fk, product_fk)
)

-- TODO: нет 2х таблиц User Profile
-- DROP TABLE IF EXISTS "content".profile;
--
-- CREATE TABLE "content".profile (
--     id uuid PRIMARY KEY,
-- 	profile_id uuid NOT NULL,
--     tel_number varchar(10) NOT NULL,
-- 	patronymic varchar(30) NOT NULL,
-- 	avatar text
-- );
