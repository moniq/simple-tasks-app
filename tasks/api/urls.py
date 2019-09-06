from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import TaskList, TaskDetail


urlpatterns = [
    path('', TaskList.as_view()),
    path('task/<int:pk>/', TaskDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

