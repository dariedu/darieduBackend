from rest_framework import serializers

from .models import Stories


class StoriesSerializer(serializers.ModelSerializer):
    link = serializers.URLField(max_length=500, read_only=True, source='get_link')

    class Meta:
        model = Stories
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'link': {'read_only': True},
        }