CREATE SCHEMA IF NOT EXISTS "content";

DROP TABLE IF EXISTS "content".order_product;
DROP TABLE IF EXISTS "content".category_feature;
DROP TABLE IF EXISTS "content".product_feature;
DROP TABLE IF EXISTS "content".feedback;
DROP TABLE IF EXISTS "content".image;
DROP TABLE IF EXISTS "content".product;
DROP TABLE IF EXISTS "content".feature;
DROP TABLE IF EXISTS "content".category;
DROP TABLE IF EXISTS "content".manufacturer;
DROP TABLE IF EXISTS "content".order;
DROP TABLE IF EXISTS "content".delivery;
DROP TABLE IF EXISTS "content".payment;
DROP TABLE IF EXISTS "content".delivery_method;
DROP TABLE IF EXISTS "content".payment_method;
DROP TABLE IF EXISTS "content".profile;

DROP TYPE IF EXISTS type_feature_enum;
DROP INDEX IF EXISTS product_name_trgm_idx;
DROP INDEX IF EXISTS product_price_idx;
DROP INDEX IF EXISTS feature_value_idx;
DROP INDEX IF EXISTS product_limited_idx;


-- CATEGORIES
CREATE TYPE type_feature_enum AS ENUM ('select', 'checkbox', 'text');

CREATE TABLE "content".category (
    id uuid PRIMARY KEY,
    category_id uuid UNIQUE NOT NULL,
    slug varchar(50) UNIQUE NOT NULL,
    name varchar(30) NOT NULL,
    icon varchar(100),
    image varchar(100),
    is_active bool NOT NULL,
    parent_id uuid,
    rght int,
    lft int,
    tree_id int,
    level int
);

CREATE TABLE "content".feature(
    id uuid PRIMARY KEY,
    feature_id uuid UNIQUE NOT NULL,
    name varchar(30) NOT NULL,
    slug varchar(30) UNIQUE NOT NULL,
    type_feature type_feature_enum NOT NULL
);

CREATE TABLE "content".category_feature(
    id uuid PRIMARY KEY,
    category_fk uuid NOT NULL,
    feature_fk uuid NOT NULL
);

-- PRODUCTS

CREATE TABLE "content".manufacturer (
    id uuid PRIMARY KEY,
    manufacturer_id uuid UNIQUE NOT NULL,
    name varchar(30) NOT NULL
);


CREATE TABLE "content".product(
    id uuid PRIMARY KEY,
    product_id uuid UNIQUE NOT NULL,
    name varchar(50) NOT NULL,
    slug varchar(50) UNIQUE NOT NULL,
    description text NOT NULL,
    price decimal NOT NULL,
    main_image varchar(100) NOT NULL,
    added timestamp NOT NULL,
    count int NOT NULL,
    is_limited bool NOT NULL,
    category_fk uuid NOT NULL,
    manufacturer_fk uuid NOT NULL
);

CREATE TABLE "content".image (
    id uuid PRIMARY KEY,
    image_id uuid UNIQUE NOT NULL,
    image varchar(100) NOT NULL,
    product_fk uuid NOT NULL
);

CREATE TABLE "content".feedback(
    id uuid PRIMARY KEY,
    feedback_id uuid UNIQUE NOT NULL,
    text text NOT NULL,
    product_fk uuid NOT NULL,
    user_fk int NOT NULL
);

CREATE TABLE "content".product_feature(
    id uuid PRIMARY KEY ,
    product_fk uuid NOT NULL,
    feature_fk uuid NOT NULL,
    value varchar(40) NOT NULL
);


-- ORDERS
CREATE TABLE "content".payment_method (
	id uuid PRIMARY KEY,
	method_id uuid UNIQUE NOT NULL,
	name varchar(30) NOT NULL
);

CREATE TABLE "content".delivery_method (
	id uuid PRIMARY KEY,
	method_id uuid UNIQUE NOT NULL,
	name varchar(30) NOT NULL,
	price decimal NOT NULL,
	free_from real
);

CREATE TABLE "content".delivery(
    id uuid PRIMARY KEY,
    delivery_id uuid UNIQUE NOT NULL,
    price decimal NOT NULL,  -- todo: продумать автозаполнение или проверку
    address text NOT NULL, -- возможно использовать json
    delivery_method_fk uuid NOT NULL
);

CREATE TABLE "content".payment(
    id uuid PRIMARY KEY,
    payment_id uuid UNIQUE NOT NULL,
    status_payment bool NOT NULL,
    error text,
    payment_method_fk uuid NOT NULL
);

CREATE TABLE "content".order(
    id uuid PRIMARY KEY,
    order_id uuid UNIQUE NOT NULL,
    created timestamp NOT NULL,
    total_price decimal NOT NULL,
    delivery_fk uuid UNIQUE NOT NULL ,
    payment_fk uuid UNIQUE NOT NULL,
    user_fk int NOT NULL
);

CREATE TABLE "content".order_product(
    id uuid PRIMARY KEY,
    count int NOT NULL,
    order_fk uuid NOT NULL,
    product_fk uuid NOT NULL
);

CREATE TABLE "content".profile (
    id uuid PRIMARY KEY,
	profile_id uuid UNIQUE NOT NULL,
    tel_number varchar(10) NOT NULL,
	patronymic varchar(30) NOT NULL,
	avatar varchar(100),
	user_fk int UNIQUE NOT NULL
);


ALTER TABLE category
    ADD CONSTRAINT parent_fk FOREIGN KEY (parent_id)
        REFERENCES category(category_id);

ALTER TABLE category_feature
    ADD CONSTRAINT category_fk FOREIGN KEY (category_fk)
        REFERENCES category(category_id) ON DELETE CASCADE;
ALTER TABLE category_feature
    ADD CONSTRAINT feature_fk FOREIGN KEY (feature_fk)
        REFERENCES feature(feature_id) ON DELETE CASCADE;
ALTER TABLE category_feature
    ADD CONSTRAINT category_feature_uk UNIQUE (category_fk, feature_fk);

ALTER TABLE product
    ADD CONSTRAINT category_fk FOREIGN KEY (category_fk)
        REFERENCES category(category_id) ON DELETE CASCADE;
ALTER TABLE product
    ADD CONSTRAINT manufacturer_fk FOREIGN KEY (manufacturer_fk)
        REFERENCES manufacturer(manufacturer_id) ON DELETE CASCADE;

ALTER TABLE image
    ADD CONSTRAINT product_fk FOREIGN KEY (product_fk)
        REFERENCES product(product_id) ON DELETE CASCADE;

ALTER TABLE product_feature
    ADD CONSTRAINT product_fk FOREIGN KEY (product_fk)
        REFERENCES product(product_id) ON DELETE CASCADE;
ALTER TABLE product_feature
    ADD CONSTRAINT feature_fk FOREIGN KEY (feature_fk)
        REFERENCES feature(feature_id) ON DELETE CASCADE;
ALTER TABLE product_feature
    ADD CONSTRAINT product_feature_uk UNIQUE (product_fk, feature_fk);

ALTER TABLE feedback
    ADD CONSTRAINT product_fk FOREIGN KEY (product_fk)
        REFERENCES product(product_id) ON DELETE CASCADE;
ALTER TABLE feedback
    ADD CONSTRAINT user_fk FOREIGN KEY (user_fk)
        REFERENCES auth_user(id) ON DELETE CASCADE;

ALTER TABLE delivery
    ADD CONSTRAINT delivery_method_fk FOREIGN KEY (delivery_method_fk)
        REFERENCES delivery_method(method_id) ON DELETE CASCADE;

ALTER TABLE payment
    ADD CONSTRAINT payment_method_fk FOREIGN KEY (payment_method_fk)
        REFERENCES payment_method(method_id) ON DELETE CASCADE;

ALTER TABLE "order"
    ADD CONSTRAINT delivery_fk FOREIGN KEY (delivery_fk)
        REFERENCES delivery(delivery_id) ON DELETE CASCADE;
ALTER TABLE "order"
    ADD CONSTRAINT payment_fk FOREIGN KEY (payment_fk)
        REFERENCES payment(payment_id) ON DELETE CASCADE;
ALTER TABLE "order"
    ADD CONSTRAINT user_fk FOREIGN KEY (user_fk)
        REFERENCES auth_user(id) ON DELETE CASCADE;

ALTER TABLE order_product
    ADD CONSTRAINT order_fk FOREIGN KEY (order_fk)
        REFERENCES "order"(order_id) ON DELETE CASCADE;
ALTER TABLE order_product
    ADD CONSTRAINT product_fk FOREIGN KEY (product_fk)
        REFERENCES product(product_id) ON DELETE CASCADE;
ALTER TABLE order_product
    ADD CONSTRAINT order_product_uk UNIQUE (order_fk, product_fk);

ALTER TABLE profile
    ADD CONSTRAINT user_fk FOREIGN KEY (user_fk)
        REFERENCES auth_user(id) ON DELETE CASCADE;


CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX product_name_trgm_idx ON product USING GIN (UPPER(name) gin_trgm_ops);
CREATE INDEX product_price_idx ON product(price);
CREATE INDEX feature_value_idx ON product_feature(value); -- todo: возможно придется исправить
CREATE INDEX product_limited_idx ON product(id) WHERE is_limited;
-- todo: можно добавить еще "content".category(id) WHERE is_active;
