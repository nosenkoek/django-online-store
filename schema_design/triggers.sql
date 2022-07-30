CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TRIGGER IF EXISTS feature_to_product_trigger ON category_feature;
DROP TRIGGER IF EXISTS product_trigger ON product;

CREATE OR REPLACE FUNCTION update_feature_product() RETURNS TRIGGER AS $$
    -- Функция для триггера при изменении характеристик в категории
    -- если удаляются характеристики из категории, то последовательно удаляются эти характеристики у товаров данной категории
    -- если добавляются характеристику в категорию, то данные характеристики добавляются к товарам этой категории
    -- если меняются характеристики, то в товарах также происходят эти изменения
    DECLARE
        product record;
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            DELETE FROM product_feature
                   WHERE (product_fk, feature_fk) IN (
                       SELECT product_fk, feature_fk
                       FROM product_feature pf
                       JOIN product p ON pf.product_fk = p.product_id
                       WHERE p.category_fk=OLD.category_fk AND feature_fk = OLD.feature_fk
                       );
            IF NOT FOUND THEN RETURN NULL; END IF;
        ELSIF (TG_OP = 'INSERT') THEN
            FOR product IN (SELECT product_id FROM product WHERE category_fk = NEW.category_fk)
            LOOP
                INSERT INTO product_feature(id, product_fk, feature_fk, value)
                VALUES(gen_random_uuid(), product.product_id, NEW.feature_fk, '-');
            END LOOP;
        ELSIF (TG_OP = 'UPDATE') THEN
            FOR product IN (SELECT product_id FROM product WHERE category_fk = NEW.category_fk)
            LOOP
                UPDATE product_feature SET feature_fk = NEW.feature_fk, value = '-'
                                       WHERE product.product_id=product_fk AND feature_fk = OLD.feature_fk;
            END LOOP;
        END IF;
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER feature_to_product_trigger
AFTER INSERT OR DELETE OR UPDATE ON category_feature
    FOR ROW EXECUTE FUNCTION update_feature_product();


CREATE OR REPLACE FUNCTION update_product_feature() RETURNS TRIGGER AS $$
    -- Функция для триггера при изменении товаров
    -- если добавляется товар, то проверяется в какой он категории и к нему добавляются эти характеристики
    -- если изменяется категория товара, изменяются его характеристики
    -- (здесь проблема:
    -- при изменении категории, сначала происходит апдейт товара, потом срабатывает триггер, а уже потом добавляются характеристики,
    -- получается, что при одновременном изменении категории и значения какой-либо характеристики, эта характеристика добавляется к товару,
    -- даже если в данной категории нет этой характеристики)

    DECLARE
        feature record;
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            FOR feature IN (SELECT feature_fk FROM category_feature WHERE category_fk = NEW.category_fk)
            LOOP
                INSERT INTO product_feature(id, product_fk, feature_fk, value)
                VALUES(gen_random_uuid(), NEW.product_id, feature.feature_fk, '-');
            END LOOP;
        ELSIF (TG_OP = 'UPDATE') AND (OLD.category_fk <> NEW.category_fk) THEN
            DELETE FROM product_feature WHERE product_fk = OLD.product_id;

            FOR feature IN (SELECT feature_fk FROM category_feature WHERE category_fk = NEW.category_fk)
            LOOP
                INSERT INTO product_feature(id, product_fk, feature_fk, value)
                VALUES(gen_random_uuid(), NEW.product_id, feature.feature_fk, '-');
            END LOOP;
        END IF;
        RETURN NULL;
    END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER product_trigger
AFTER INSERT OR UPDATE ON product
    FOR ROW EXECUTE FUNCTION update_product_feature();

