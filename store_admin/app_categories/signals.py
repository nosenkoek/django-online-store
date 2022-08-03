from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from app_categories.models import CategoryFeature, Category, Feature


@receiver(post_save, sender=Category)
def add_features_subcategory(sender, instance, created, **kwargs) -> None:
    # В случае создании подкатегории, к ней добавляются характеристики из родителя
    # В случае изменения родителя у потомка, необходимо поменять характеристики
    if instance.is_child_node():
        root = instance.get_root()
        features = Feature.objects.filter(categories=root).all()

        if created:
            results = [CategoryFeature(category_fk=instance, feature_fk=feature) for feature in features]
        else:
            feature_category = CategoryFeature.objects.filter(category_fk=instance).all()
            feature_category.delete()

            results = [CategoryFeature(category_fk=instance, feature_fk=feature)
                       for feature in features]

        CategoryFeature.objects.bulk_create(results)

    # В случае изменения характеристик в родителе, изменяются характеристики у потомков
    if not created and instance.is_root_node():
        subcategories = instance.get_children()
        feature_category = CategoryFeature.objects.filter(category_fk__in=subcategories).all()
        feature_category.delete()

        features = Feature.objects.filter(categories=instance).all()

        results = [CategoryFeature(category_fk=subcategory, feature_fk=feature)
                   for feature in features
                   for subcategory in subcategories]
        CategoryFeature.objects.bulk_create(results)
