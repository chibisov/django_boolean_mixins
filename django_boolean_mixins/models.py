# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError

# models
class ModelBooleanMixinQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(ModelBooleanMixinQuerySet, self).__init__(*args, **kwargs)
        
        model_field_names_list = [field.name for field in self.model._meta.fields]
        
        for field in self.model._meta.fields:
            if isinstance(field, models.BooleanField):
                field_names = [field.name]
                if field.name.startswith("is_"):
                    # prepare new name for magic filter
                    cut_name = field.name.replace("is_", "", 1)
                    if cut_name not in model_field_names_list:
                        field_names.append(cut_name)
                
                filter_lambda = self._filter_boolean(field.name)
                exclude_lambda = self._exclude_boolean(field.name)
                
                for field_name in field_names:
                    filter_method_name = "filter_by_{field_name}".format(field_name=field_name)
                    exclude_method_name = "exclude_{field_name}".format(field_name=field_name)
                    
                    if not hasattr(self, filter_method_name):
                        setattr(self, filter_method_name, filter_lambda) # add filter method
                    if not hasattr(self, exclude_method_name):
                        setattr(self, exclude_method_name, exclude_lambda) # add exclude method

    def _filter_boolean(self, field_name):
        """
        Method for filtering boolean field.
        Returns lambda
        """
        q_condition = self._get_q_condition_for_boolean_field(field_name)
        return lambda: self.filter(q_condition)
        
    def _exclude_boolean(self, field_name):
        """
        Method for excluding boolean field.
        Returns lambda
        """
        q_condition = self._get_q_condition_for_boolean_field(field_name)
        return lambda: self.exclude(q_condition)
        
    def _get_q_condition_for_boolean_field(self, field_name):
        """
        Method generates Q object condition for boolean
        """
        q_condition = Q(**{field_name: True})
        return q_condition
        

class ModelBooleanMixinManager(models.Manager):
    def get_query_set(self):
        return ModelBooleanMixinQuerySet(self.model)
        
    def __getattr__(self, name):
        black_list_of_prefix = ("_", "__")
        is_delegate = bool([i for i in black_list_of_prefix if not name.startswith(i)])
        if is_delegate:
            return getattr(self.get_query_set(), name)
        else:
            raise AttributeError

# Create your models here.
class ModelBooleanMixin(models.Model):
    
    objects = ModelBooleanMixinManager()
    
    class Meta:
        abstract = True