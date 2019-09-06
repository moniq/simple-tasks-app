from rest_framework import serializers
from ..models import Task, Owner, PRIORITY_CHOICES


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'start_date',
            'end_date',
            'owner',
            'priority',
        )


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Owner
        fields = (
            'name',
            'surname',
        )