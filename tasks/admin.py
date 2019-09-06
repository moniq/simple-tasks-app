from django.contrib import admin
from .models import Task, Owner


admin.site.register(Task)
admin.site.register(Owner)

