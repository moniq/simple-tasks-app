from django.views import generic
from .models import Task
from django.shortcuts import get_list_or_404


class TaskListView(generic.ListView):
    model = Task

    def get_queryset(self):
        return Task.objects.filter(parent=None)