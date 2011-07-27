# encoding: utf8
from django.contrib import admin
from django.contrib.messages.api import MessageFailure
from django.db import models
from django.utils.translation import ugettext_lazy, ugettext as _

class AdminBooleanMixin(admin.ModelAdmin):
    boolean_short_descriptions = {}
    
    def __init__(self, *args, **kwargs):
        super(AdminBooleanMixin, self).__init__(*args, **kwargs)
        
        self.actions_to_append = {}
        
        # iterate over all Model fields
        for field in self.model._meta.fields:
            if (isinstance(field, models.BooleanField) 
                and field.name in self.list_display):
                # only BooleanField and wich in 'list_display'
                
                for bool_value in (True, False): # create methods for set True and False
                    new_action_name = self._generate_boolean_field_action_name(field_name=field.name, 
                                                                               bool_value=bool_value)
                
                    if not hasattr(self, new_action_name):
                        created_action = self.create_action(field=field, 
                                                            action_name=new_action_name, 
                                                            bool_value=bool_value)
                        func = created_action[0]
                        setattr(self, new_action_name, func)
            
                        # this dict will be added to get_actions() method
                        self.actions_to_append[new_action_name] = created_action
    
    def _generate_boolean_field_action_name(self, field_name, bool_value):
        """
        Generates action name - will be used in for 'def NAME'
        """
        return "{field_name}_to_{bool_value}_action".format(
                            field_name=field_name,
                            bool_value=str(bool_value).lower())
    
    def create_action(self, action_name, field, bool_value):
        """
        Returns tuple (function, name, short_description)
        """
        def func(modeladmin, request, queryset):
            rows_updated = queryset.update(**{field.name: bool_value})
            
            msg = u"{rows_updated} {verbose_name_plural} affected".format(
                                                rows_updated=rows_updated, 
                                                verbose_name_plural=self.model._meta.verbose_name_plural)
            
            if hasattr(self, "after_any_boolean_action"):
                self.after_any_boolean_action(request=request, queryset=queryset)
                
            try:
                modeladmin.message_user(request, msg)
            except MessageFailure, e:
                pass
        
        name = action_name
        
        custom_short_description = self.boolean_short_descriptions.get(field.name)
        short_description_for_this_method = None
        if custom_short_description:
            if bool_value:
                short_description_for_this_method = custom_short_description[0]
            else:
                short_description_for_this_method = custom_short_description[1]                
        
        model_verbose_name_plural = field.model._meta.verbose_name_plural.lower()
        field_verbose_name = field.verbose_name
        
        if short_description_for_this_method:
            short_description = short_description_for_this_method.format(model_verbose_name_plural=model_verbose_name_plural,
                                                                         field_verbose_name=field_verbose_name)
        else:
            short_description = (u"Set selected {model_verbose_name_plural} {field_verbose_name} to {bool_value}"
                                                .format(field_verbose_name=field_verbose_name, 
                                                        model_verbose_name_plural=model_verbose_name_plural,
                                                        bool_value=bool_value))
        return (func, name, short_description)
        
    def get_actions(self, *args, **kwargs):
        actions = super(AdminBooleanMixin, self).get_actions(*args, **kwargs)

        actions.update(self.actions_to_append)

        return actions