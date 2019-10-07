from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import random
import string 

def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=10, unique=True, default=rand_slug())

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Client(models.Model):
    owner = models.ForeignKey(User, related_name='clients_created', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='clients', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=10, unique=True, default=rand_slug())
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='clients_joined', blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    client = models.ForeignKey(Client, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['client'])
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return '{}. {}'.format(self.order, self.title)

class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    
    class Meta:
        ordering = ['order']
        
class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
    
    def render(self):
        return render_to_string('clients/content/{}.html'.format(self._meta.model_name), {'item': self})

class File(ItemBase):
    file = models.FileField(upload_to='files')

