from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True)
    category_id = models.UUIDField()
    name = models.CharField(max_length=30)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'category'


class DeliveryMethod(models.Model):
    id = models.UUIDField(primary_key=True)
    delivery_method_id = models.UUIDField()
    method = models.CharField(max_length=30)
    price = models.FloatField()
    free_from = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'delivery'


class Feature(models.Model):
    id = models.UUIDField(primary_key=True)
    feature_id = models.UUIDField()
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'feature'


class Manufacturer(models.Model):
    id = models.UUIDField(primary_key=True)
    manufacturer_id = models.UUIDField()
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'manufacturer'


class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True)
    payment_method_id = models.UUIDField()
    method = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'payment_method'


class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    profile_id = models.UUIDField()
    tel_number = models.CharField(max_length=10)
    patronymic = models.CharField(max_length=30)
    avatar = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profile'
