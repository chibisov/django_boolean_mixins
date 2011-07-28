# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import QuerySet
from django.test import TestCase

from django_boolean_mixins.models import ModelBooleanMixin

# Models
class Article(ModelBooleanMixin, models.Model):
    name = models.CharField(max_length=100)

    is_published = models.BooleanField(default=True)
    active = models.BooleanField(verbose_name="super active", default=True)
    leave_me_alone = models.BooleanField(default=True)
    
    user_updated = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return u"{self.name}".format(self=self)
        
class ArticleWithCollideFields(ModelBooleanMixin, models.Model):
    is_published = models.BooleanField(default=True)
    published = models.BooleanField(default=True)
    
class UnicodeArticle(ModelBooleanMixin, models.Model):
    name = models.CharField(verbose_name=u"название", max_length=100)
    is_published = models.BooleanField(verbose_name=u"Опубликовано")
    
    class Meta:
        verbose_name = u"Новость"
        verbose_name = u"Новости"

# model Testing
class MethodsCreationTest(TestCase):
    def setUp(self):
        class LocalArticle(ModelBooleanMixin, models.Model):
            name = models.CharField(max_length=100)
            never_mind = models.TextField()
            
            is_published = models.BooleanField(default=True)
            is_active = models.BooleanField()
            without_us = models.BooleanField()
            
        self.Article = LocalArticle
        
    def test_simple_filters_existing(self):
        self.assertTrue(hasattr(self.Article.objects.all(), "filter_by_is_published"))
        self.assertTrue(hasattr(self.Article.objects.all(), "filter_by_without_us"))

    def test_simple_exludes_existing(self):
        self.assertTrue(hasattr(self.Article.objects.all(), "exclude_is_published"))
        self.assertTrue(hasattr(self.Article.objects.all(), "exclude_without_us"))
    
    def test_magic_filters_existing(self):
        self.assertTrue(hasattr(self.Article.objects.all(), "filter_by_published"))
        
    def test_magic_excludes_existing(self):
        self.assertTrue(hasattr(self.Article.objects.all(), "exclude_published"))
        
    def test_magic_names(self):
        class Man(ModelBooleanMixin, models.Model):
            name = models.CharField(max_length=100)
            is_so_easy_is_so = models.BooleanField()
        
        self.assertFalse(hasattr(Man.objects.all(), 
                         "filter_by_so_easy_so"),
                         msg="Magic names should replace only is_ prefix, not other is_")
        self.assertTrue(hasattr(Man.objects.all(), "filter_by_so_easy_is_so"))
    
    def _test_custom_method_return_type(self):
        self.assertTrue(isinstance(self.Article.objects.all().filter_by_is_published(), QuerySet))
        
class MethodsWorksRightTest(TestCase):
    def setUp(self):
        # create 10 published and unactive articles
        for i in range(10):
            devnull = Article.objects.create(name="Nevermind", is_published=True, active=False)
        
         # create 4 unpublished and active articles
        for i in range(4):
            devnull = Article.objects.create(name="Nevermind", is_published=False, active=True)
            
            
    def test_filtering_and_excluding(self):
        # test filter published
        self.assertEquals(Article.objects.all().filter(is_published=True).count(),
                          Article.objects.all().filter_by_published().count())
                          
        # test exclude published
        self.assertEquals(Article.objects.all().filter(is_published=False).count(),
                          Article.objects.all().exclude_published().count())
        
        # test filter active
        self.assertEquals(Article.objects.all().filter(active=True).count(),
                          Article.objects.all().filter_by_active().count())
                          
        # test exclude active
        self.assertEquals(Article.objects.all().filter(active=False).count(),
                          Article.objects.all().exclude_active().count())
    
    def test_that_magic_method_returns_exact_set_as_not_magic(self):
        # filter
        self.assertEqual(set(Article.objects.all().filter_by_published().values_list("pk")),
                         set(Article.objects.all().filter_by_is_published().values_list("pk")))
                         
        # exclude
        self.assertEqual(set(Article.objects.all().exclude_published().values_list("pk")),
                         set(Article.objects.all().exclude_is_published().values_list("pk")))
        
    def test_for_names_collisions(self):
        for i in range(10):
            devnull = ArticleWithCollideFields.objects.create(is_published=True, published=False)

        for i in range(4):
            devnull = ArticleWithCollideFields.objects.create(is_published=False, published=True)
            
        self.assertNotEquals(ArticleWithCollideFields.objects.all().filter_by_published().count(),
                             ArticleWithCollideFields.objects.all().filter_by_is_published().count(),
                             msg="Models with collided names shouldn't create magic filtering")

# admin Testing
from django.contrib import admin
from django_boolean_mixins.admin import AdminBooleanMixin

# ModelAdmins
class ArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
    list_display = ("name", "is_published", "active")
    
    boolean_short_descriptions = {
        "is_published": (None, "Unpublish"),
        "active": (None, "Deactivate {field_verbose_name} for selected {model_verbose_name_plural}")
    }

class UnicodeArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
    list_display = ("name", "is_published")
    
    boolean_short_descriptions = {
        "is_published": (None, u"Разопубликова {model_verbose_name_plural}"),
    }
    
admin.site.register(Article, ArticleAdmin)

# unit tests
class AdminActionMethodsTest(TestCase):
    def setUp(self):                  
        self.article_admin = ArticleAdmin(model=Article, admin_site=None)
        
        for i in range(10):
            devnull = Article.objects.create(name="Nevermind", is_published=True)
    
    def test_action_name_generator(self):
        action_name = self.article_admin._generate_boolean_field_action_name(
                                                    field_name="chicharita", 
                                                    bool_value=False)
        self.assertEquals(action_name, "chicharita_to_false_action")
    
    def test_methods_exists(self):
        self.assertTrue(hasattr(self.article_admin, "is_published_to_true_action"))
        self.assertTrue(hasattr(self.article_admin, "is_published_to_false_action"))
        
        self.assertTrue(hasattr(self.article_admin, "active_to_true_action"))
        self.assertTrue(hasattr(self.article_admin, "active_to_false_action"))
        
    def test_update(self):
        qset_to_update = Article.objects.all()
        self.article_admin.is_published_to_false_action(self.article_admin, request=None, queryset=qset_to_update)

        self.assertEquals(set(qset_to_update.values_list("pk", flat=True)),
                          set(Article.objects.all().exclude_published().values_list("pk", flat=True)))
    
    def test_boolean_short_descriptions(self):
        is_published = Article._meta.get_field_by_name("is_published")[0]
        active = Article._meta.get_field_by_name("active")[0]
        
        self.assertEquals(self.article_admin.create_action(field=is_published, 
                                                           action_name="nevermind",
                                                           bool_value=True)[2], 
                          "Set selected articles is published to True")
                          
        self.assertEquals(self.article_admin.create_action(field=is_published, 
                                                           action_name="nevermind",
                                                           bool_value=False)[2], 
                          "Unpublish")
        self.assertEquals(self.article_admin.create_action(field=active, 
                                                           action_name="nevermind",
                                                           bool_value=True)[2], 
                          "Set selected articles super active to True")
        self.assertEquals(self.article_admin.create_action(field=active, 
                                                           action_name="nevermind",
                                                           bool_value=False)[2], 
                          "Deactivate super active for selected articles")
    
    # Admin site testing
    def test_show_actions_for_fields_only_from_list_display(self):
        # leave_me_alone not in list
        self.assertFalse(hasattr(self.article_admin, "leave_me_alone_to_true_action"))
        self.assertFalse(hasattr(self.article_admin, "leave_me_alone_to_false_action"))
        
    def test_unicode(self):
        admin.site.register(UnicodeArticle, UnicodeArticleAdmin)
    
class CustomBehaviorsTest(TestCase):
    def setUp(self):        
        for i in range(10):
            devnull = Article.objects.create(name="Nevermind", is_published=True)
        
        self.user = User.objects.create(username="chibisov",
                                        email="noemail@ya.ru",
                                        password="123456")
        
        user = self.user
        class CustomArticleAdmin(ArticleAdmin):
            def after_any_boolean_action(self, request, queryset):
                queryset.update(user_updated=user)
                
        self.article_admin = CustomArticleAdmin(model=Article, admin_site=None)
    
    def test_after_any_boolean_action(self):
        qset_to_update = Article.objects.all()
        
        self.article_admin.is_published_to_false_action(self.article_admin, 
                                                        request=None, 
                                                        queryset=qset_to_update)
        
        # check old behavior
        self.assertEquals(set(qset_to_update.values_list("pk", flat=True)),
                          set(qset_to_update.exclude_published().values_list("pk", flat=True)))
        
        # check new behavior
        self.assertEquals(qset_to_update[0].user_updated, self.user)