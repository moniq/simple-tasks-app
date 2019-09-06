from rest_framework import serializers
from ..models import Task, Owner


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Owner
        fields = (
            'name',
            'surname',
        )


class TaskSerializer(serializers.ModelSerializer):

    owner = OwnerSerializer()
    priority = serializers.CharField(source='get_priority_display')

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


