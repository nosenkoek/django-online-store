from uuid import uuid4

from django.db import models
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
