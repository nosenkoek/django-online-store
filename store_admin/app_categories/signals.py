from django.dispatch import receiver
from django.db.models.signals import post_save

from app_categories.models import CategoryFeature


@receiver(post_save, sender='app_categories.Category')
def add_features_subcategory(sender, instance, created, **kwargs):
    print(created)
    if instance.is_child_node():
        root_id = instance.get_root().category_id
        print(root_id, type(root_id))
        features = CategoryFeature.objects.filter(category_fk=str(root_id)).all()
        print(features)
        results = [CategoryFeature(category_fk=instance, feature_fk=feature) for feature in features]
        CategoryFeature.objects.bulk_create(results)
