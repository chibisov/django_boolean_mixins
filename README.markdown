# Django boolean mixins

Django app with some usefull mixins for models.BooleanField. Every mixin is independent. 

## Installation
1) Install:

    git clone clone git://github.com/chibisov/django_boolean_mixins.git
    cd django_boolean_mixins/
    sudo python setup.py install

    # or with custom destination

    sudo python setup.py install --install-lib=/Library/Python/2.6/site-packages
    
    
2) Add application to your settings.py:
    
    INSTALLED_APPS = (
        ...
        'django_boolean_mixins',
        ...
    )

## ModelBooleanMixin
    
    from django.db import models
    from django.contrib.auth.models import User
    from django_boolean_mixins.models import ModelBooleanMixin
    
    class Article(ModelBooleanMixin, models.Model):
        # mixin should be first in model inheritance
        name = models.CharField(max_length=100)
        content = models.TextField()

        is_published = models.BooleanField(default=True)
        active = models.BooleanField()
        
        user_updated = models.ForeignKey(User, blank=True, null=True)

This mixin adds to your Manager's QuerySet new methods for any BooleanField:  
    
* filter\_by\_&lt;field\_name&gt;
* exclude\_&lt;field\_name&gt;

If &lt;field\_name&gt; starts with "is\_", then will be created same methods, without prefix "is\_". 
For our example will be created methods:

* filter\_by\_is_published()
* filter\_by\_published()
* filter\_by\_active()
* exclude\_is_published()
* exclude\_published()
* exclude\_active()

If model has both fields with names like "is\_&lt;field\_name&gt;" and "&lt;field\_name&gt;", 
then magic method without "**is\_**" prefix weel not be created:

    class ArticleWithCollideFields(ModelBooleanMixin, models.Model):
        is_published = models.BooleanField(default=True)
        published = models.BooleanField(default=True)

        # filter_by_published() and filter_by_is_published() are different methods
        
You can easily extend mixin's QuerySet or Manager:

    from django_boolean_mixins.models import (
                                       ModelBooleanMixin, 
                                       ModelBooleanMixinQuerySet,
                                       ModelBooleanMixinManager)

    class ArticleQuerySet(ModelBooleanMixinQuerySet):
        def exclude_bad_words(self):
            self = (self.filter_by_published()
                        .exclude(text__icontains="badword_1")
                        .exclude(text__icontains="badword_2"))

            return self

    class ArticleManager(ModelBooleanMixinManager):
        def get_query_set(self):
            return ArticleQuerySet(self.model)

        def __getattr__(self, name):
            return getattr(self.get_query_set(), name)

    class Article(ModelBooleanMixin, models.Model):    
        title = models.CharField(max_length=200, verbose_name="заголовок")
        text = models.TextField(verbose_name="текст")
        is_published = models.BooleanField(default=True)
        is_login_required = models.BooleanField(default=False)

        objects = ArticleManager()
        ...
        
And now you can use these methods for example in views:

    articles = Article.objects.filter_by_published().exclude_active().order_by("name")
    ...
    
Or in templates:

    {% for article in articles.filter_by_is_published %}
        {{ article.content }}
    {% endfor %}

    <!-- OR filter_by_published -->
    {% for article in articles.filter_by_published.filter_by_active %}
        {{ article.content }}
    {% endfor %}
    
One of usefull example is creating your custom mixin:

    class PublishedMixin(ModelBooleanMixin, models.Model):
        is_published = models.BooleanField(default=True)

        class Meta:
            abstract = True
    
    class Category(PublishedMixin, models.Model):
        name = models.CharField(max_length=255)
    
    class Article(PublishedMixin, models.Model):
        name = models.CharField(max_length=255)
        category = models.ForeignKey(Category)
        
You don't need to add by hand methods for every boolean field:
    
    # iterate by published categories
    for category in Category.objects.filter_by_published():
        # iterate by not published articles
        for article in category.article_set.exclude_published():
            print """This is not published article with name 
                     '{article.name}' of published category 
                     with name '{category.name}' """.format(category=category, 
                                                            article=article)


## AdminBooleanMixin
    
    from django.contrib import admin
    from yourapp.models import Article
    from django_boolean_mixins.admin import AdminBooleanMixin

    class ArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
        list_display = ("name", "is_published", "active")

    admin.site.register(Article, ArticleAdmin)
    
This mixin adds 2 actions for every BooleanField from list\_display option.  
First action - to set False, second - to set True.  


![actions example](https://github.com/chibisov/django_boolean_mixins/blob/master/django_boolean_mixins/static/img/actions.png?raw=true "Title")

By default adds actions with names like:

* "Set selected &lt;model\_verbose\_name\_plural&gt; &lt;field\_verbose\_name&gt; to True"
* "Set selected &lt;model\_verbose\_name\_plural&gt; &lt;field\_verbose\_name&gt; to False"

You can specify your own labels in admin.py:

    class ArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
        ...
        boolean_short_descriptions = {
            "is_published": ("Publish selected articles", "Unpublish selected articles"),
            "active": ("Activate selected articles", "Deactivate selected articles")
        }
        ...
        
For more flexibility you can use **model\_verbose\_name\_plural** and **field\_verbose\_name**, which will be [formatted](http://docs.python.org/library/stdtypes.html#str.format):
    
    class ArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
        ...
        boolean_short_descriptions = {
            "is_published": ("Publish selected {model_verbose_name_plural}", 
                             "Unpublish selected {model_verbose_name_plural}"),
            "active": ("Activate selected {model_verbose_name_plural}", 
                       "Deactivate {field_verbose_name} for selected {model_verbose_name_plural}")
        }
        ...
        
If you want, that one of actions used default text, you can specify it to None: 

    class ArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
        ...
        boolean_short_descriptions = {
            "is_published": (None, "Unpublish selected {model_verbose_name_plural}"),
            ...
        }
        ...

### Custom behavior
       
To trigger some custom behavior after action will end his job, you can specify **after\_any\_boolean_action** method 
in admin.py, which takes 2 arguments:

* A QuerySet containing the set of objects selected by the user  
* An HttpRequest representing the current request  

For example, update who changed the boolean state:

    class ArticleAdmin(AdminBooleanMixin, admin.ModelAdmin):
        ...
        def after_any_boolean_action(self, queryset, request):
            queryset.update(user_updated=request.user)
        ...