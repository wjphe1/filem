from django import forms
from django.forms.models import inlineformset_factory
from .models import Client, Module


ModuleFormSet = inlineformset_factory(Client, Module, fields=['title', 'description'], can_delete=True)
