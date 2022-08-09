from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from app_products.models import Product, ProductFeature
from app_categories.models import Feature, CategoryFeature


@receiver(post_save, sender=Product)
def add_features_product(sender, instance, created, **kwargs) -> None:
    """Добавление характеристик из категорий"""
    update_fields = kwargs.get('update_fields', [])
    category = instance.category_fk
    features = [ProductFeature(product_fk=instance, feature_fk=feature, value='-')
                for feature in Feature.objects.filter(categories=category)]

    if created:
        ProductFeature.objects.bulk_create(features)

    if update_fields and 'category_fk' in update_fields:
        feature_product = ProductFeature.objects.filter(product_fk=instance).all()
        feature_product.delete()

        ProductFeature.objects.bulk_create(features)


@receiver(post_save, sender=CategoryFeature)
def add_features_product_when_update_category(sender, instance, created, **kwargs) -> None:
    """Добавление характеристики в продукт при добавлении его в категорию"""
    feature = instance.feature_fk
    category = instance.category_fk
    products = Product.objects.filter(category_fk=category).all()

    product_feature = [ProductFeature(product_fk=product, feature_fk=feature, value='-')
                       for product in products]

    ProductFeature.objects.bulk_create(product_feature)


@receiver(post_delete, sender=CategoryFeature)
def delete_features_product_when_update_category(sender, instance, **kwargs) -> None:
    """Удаление характеристики у продукта при удалении его из категории"""
    feature = instance.feature_fk
    category = instance.category_fk
    products = Product.objects.filter(category_fk=category).all()

    product_feature = ProductFeature.objects.filter(product_fk__in=products, feature_fk=feature).all()
    product_feature.delete()
