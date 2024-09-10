from rest_framework import serializers

from .models import Stories


class StoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stories
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'link': {'read_only': True},
        }