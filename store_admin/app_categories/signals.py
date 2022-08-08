from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from app_categories.models import CategoryFeature, Category, Feature


@receiver(post_save, sender=Category)
def add_features_subcategory(sender, instance, created, **kwargs) -> None:
    """Сигнал для добавления/удаления/изменения характеристик в подкатегории в зависимости от родительской категории"""
    update_fields = kwargs.get('update_fields', [])
    all_fields = frozenset({'is_active', 'icon', 'parent', 'category_id', 'name'})

    # Из-за переопределения save в библиотеке mptt.
    # Там, в случае update_fields=None, он переопределяет на все изменяемые поля.
    if update_fields == all_fields:
        update_fields = None

    # В случае создании подкатегории, к ней добавляются характеристики из родителя
    if instance.is_child_node() and created:
        root = instance.get_root()
        features = Feature.objects.filter(categories=root).all()
        results = [CategoryFeature(category_fk=instance, feature_fk=feature) for feature in features]
        CategoryFeature.objects.bulk_create(results)

    # В случае изменения родителя у потомка, необходимо поменять характеристики
    if instance.is_child_node() and not created and update_fields and 'parent' in update_fields:
        root = instance.get_root()
        features = Feature.objects.filter(categories=root).all()

        feature_category = CategoryFeature.objects.filter(category_fk=instance).all()
        feature_category.delete()
        print('delete_feature_child')
        results = [CategoryFeature(category_fk=instance, feature_fk=feature)
                   for feature in features]

        CategoryFeature.objects.bulk_create(results)


@receiver(post_save, sender=CategoryFeature)
def add_features_category(sender, instance, created, **kwargs) -> None:
    if instance.category_fk.is_root_node():
        subcategory = instance.category_fk.get_children()[0]
        if subcategory:
            feature = instance.feature_fk
            CategoryFeature.objects.create(category_fk=subcategory, feature_fk=feature)


@receiver(post_delete, sender=CategoryFeature)
def add_features_category(sender, instance,  **kwargs) -> None:
    if instance.category_fk.is_root_node():
        subcategory = instance.category_fk.get_children()[0]
        if subcategory:
            feature = instance.feature_fk
            CategoryFeature.objects.filter(category_fk=subcategory, feature_fk=feature).all().delete()

