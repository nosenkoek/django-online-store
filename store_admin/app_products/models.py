from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from app_categories.models import Category, Feature


class Manufacturer(models.Model):
    """Производитель"""
    id = models.UUIDField(primary_key=True, default=uuid4,
                          editable=False)
    manufacturer_id = models.UUIDField(unique=True, default=uuid4,
                                       editable=False)
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
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('slug'))
    description = models.TextField(verbose_name=_('description'))
    price = models.DecimalField(max_digits=7, decimal_places=2,
                                verbose_name=_('price'),
                                validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='product_images/',
                              verbose_name=_('image'))
    added = models.DateTimeField(auto_now_add=True,
                                 verbose_name=_('added'))
    is_limited = models.BooleanField(verbose_name=_('is limited'))

    category_fk = models.ForeignKey(Category,
                                    on_delete=models.CASCADE,
                                    to_field='category_id',
                                    db_column='category_fk',
                                    verbose_name=_('category'))
    manufacturer_fk = models.ForeignKey('Manufacturer',
                                        on_delete=models.CASCADE,
                                        to_field='manufacturer_id',
                                        db_column='manufacturer_fk',
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
    product_fk = models.ForeignKey(Product,
                                   on_delete=models.CASCADE,
                                   to_field='product_id',
                                   db_column='product_fk',
                                   verbose_name=_('product'))
    feature_fk = models.ForeignKey(Feature,
                                   on_delete=models.CASCADE,
                                   to_field='feature_id',
                                   db_column='feature_fk',
                                   verbose_name=_('feature'))

    value = models.CharField(max_length=20, verbose_name=_('value'))

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
#     feedback_id = models.UUIDField(
#     unique=True,
#     default=uuid4,
#     editable=False)
#     text = models.TextField(verbose_name=_('text'))
#     product_fk = models.ForeignKey('Product', on_delete=models.CASCADE,
#                                    to_field='product_id',
#                                    db_column='product_fk',
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
