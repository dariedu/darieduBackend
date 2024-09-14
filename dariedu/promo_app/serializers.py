from rest_framework import serializers
from .models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    # TODO we need here only GET and UPDATE to take the promotion
    class Meta:
        model = Promotion
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            # TODO and all the others?
        }