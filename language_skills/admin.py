# yourapp/admin.py

from django.contrib import admin
from .models import ListeningModule, ModuleQA, UserAnswer

admin.site.register(ListeningModule)
admin.site.register(ModuleQA)
admin.site.register(UserAnswer)

