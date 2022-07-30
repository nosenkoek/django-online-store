from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def svg_validator(file):
    if not file.name.endswith('.svg'):
        raise ValidationError(_('File not SVG'))


class Category(models.Model):
    """ Набор категорий """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30, verbose_name=_('name'))
    icon = models.FileField(upload_to='icons_categories/', validators=[svg_validator],
                            null=True, blank=True, verbose_name=_('icon'))
    is_active = models.BooleanField(verbose_name=_('is_active'))

    features = models.ManyToManyField('Feature',
                                      through='CategoryFeature')

    class Meta:
        managed = False
        db_table = 'category'
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Feature(models.Model):
    """ Набор характеристик """

    class TypeFeature(models.TextChoices):
        SELECT = 'select', _('select')
        CHECKBOX = 'checkbox', _('yes/no')
        TEXT = 'text', _('text')

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    feature_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30, verbose_name=_('name'))
    type_feature = models.CharField(max_length=30, choices=TypeFeature.choices,
                                    default=TypeFeature.TEXT, verbose_name=_('type feature'))

    categories = models.ManyToManyField('Category',
                                        through='CategoryFeature')

    class Meta:
        managed = False
        db_table = 'feature'
        verbose_name = _('feature')
        verbose_name_plural = _('features')

    def __str__(self):
        return self.name


class CategoryFeature(models.Model):
    """Связь между категориями и характеристиками"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category_fk = models.ForeignKey(Category, on_delete=models.CASCADE,
                                    to_field='category_id', db_column='category_fk',
                                    verbose_name=_('category'))
    feature_fk = models.ForeignKey(Feature, on_delete=models.CASCADE,
                                   to_field='feature_id', db_column='feature_fk',
                                   verbose_name=_('feature'))

    class Meta:
        managed = False
        db_table = 'category_feature'
        unique_together = (('category_fk', 'feature_fk'),)
        verbose_name = _('category with features')
        verbose_name_plural = _('categories with features')

    def __str__(self):
        return f'{self.category_fk} {self.feature_fk}'


class Manufacturer(models.Model):
    """Производитель"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    manufacturer_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=30, verbose_name=_('name'))

    class Meta:
        managed = False
        db_table = 'manufacturer'
        verbose_name = _('manufacturer')
        verbose_name_plural = _('manufacturers')

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товары"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product_id = models.UUIDField(unique=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))
    price = models.FloatField(verbose_name=_('price'), validators=[MinValueValidator(0)])
    image = models.CharField(max_length=100, verbose_name=_('image'))    # todo: не забыть исправить
    # image = models.ImageField(upload_to='product_images/', verbose_name=_('image'))
    added = models.DateTimeField(verbose_name=_('added'))
    is_limited = models.BooleanField(verbose_name=_('is_limited'))

    category_fk = models.ForeignKey(Category, on_delete=models.CASCADE,
                                    to_field='category_id', db_column='category_fk',
                                    verbose_name=_('category'))
    manufacturer_fk = models.ForeignKey('Manufacturer', on_delete=models.CASCADE,
                                        to_field='manufacturer_id', db_column='manufacturer_fk',
                                        verbose_name=_('manufacturer'))

    features = models.ManyToManyField(Feature, through='ProductFeature')

    class Meta:
        managed = False
        db_table = 'product'
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.name


class ProductFeature(models.Model):
    """Связь между товарами и характеристиками"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product_fk = models.ForeignKey(Product, on_delete=models.CASCADE,
                                   to_field='product_id', db_column='product_fk',
                                   verbose_name=_('product'))
    feature_fk = models.ForeignKey(Feature, on_delete=models.CASCADE,
                                   to_field='feature_id', db_column='feature_fk',
                                   verbose_name=_('feature'))

    value = models.CharField(max_length=20, verbose_name=_('value'))

    def clean(self):
        # todo: додумать как сделать верное заполнение и отображение поля
        if (self.feature_fk.type_feature == 'checkbox'
                and self.value not in (_('no'), _('yes'))):
            raise ValidationError(_('Value must be yes/no'))

    class Meta:
        managed = False
        db_table = 'product_feature'
        unique_together = (('product_fk', 'feature_fk'),)
        verbose_name = _('product with features')
        verbose_name_plural = _('products with features')

    def __str__(self):
        return f'{self.product_fk} {self.feature_fk}'

# todo: перенести в users
# class Feedback(models.Model):
#     """Отзывы"""
#     id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
#     feedback_id = models.UUIDField(unique=True, default=uuid4, editable=False)
#     text = models.TextField(verbose_name=_('text'))
#     product_fk = models.ForeignKey('Product', on_delete=models.CASCADE,
#                                    to_field='product_id', db_column='product_fk',
#                                    verbose_name=_('product'))
#     user_fk = models.ForeignKey(User, on_delete=models.CASCADE,
#                                 db_column='user_fk', verbose_name=_('user'))
#
#     class Meta:
#         managed = False
#         db_table = 'feedback'
#         verbose_name = _('feedback')
#         verbose_name_plural = _('feedbacks')
#
#     def __str__(self):
#         return self.text
