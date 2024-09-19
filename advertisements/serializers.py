from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, FavoritesAdvertisment


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)
    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        user = self.context["request"].user
        open_advertaisment_count = Advertisement.objects.filter(creator=user).filter(status="OPEN").count()
        message = "У пользователя может быть не более 10 открытых объявлений"
        if self.context["request"].method == "POST":
            if(open_advertaisment_count >= 10):
                raise serializers.ValidationError(message) 
        elif self.context["request"].method == "PATCH" and  self.context["request"].data["status"] == "OPEN":
            if(open_advertaisment_count >= 10):
                raise serializers.ValidationError(message)
        return data
    
class FavoritesAdvertismentSerializer(serializers.ModelSerializer):
    advertisement = AdvertisementSerializer(read_only=True)
    class Meta:
        model = FavoritesAdvertisment
        fields = ('id', 'user', 'advertisement')    





