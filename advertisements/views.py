from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import Advertisement, FavoritesAdvertisment
from .serializers import AdvertisementSerializer, FavoritesAdvertismentSerializer
from .filters import AdvertisementFilter
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrAdmin
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled
class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    required_group = ['staff']
    def list(self, request, *args, **kwargs):
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                self.throttle_deny(request, throttle)
        data = Advertisement.objects.all()
        user = request.user
        valid_data = []
        for adv in data:
            if adv.status == "DRAFT" and user != adv.creator:
                continue
            else:
                valid_data.append(adv)
        serializer = AdvertisementSerializer(data=valid_data, many=True)
        serializer.is_valid()
        return Response(serializer.data)
    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrAdmin()] 
        if self.action in ["create"]:
            return [IsAuthenticated()]
        return []
    @action(methods=['post'], detail=True, url_path="add-favorite")
    def add_favorites(self, request, pk=None):
        pk = self.get_object()
        creator_adv = Advertisement.objects.filter(creator = request.user).first()
        if creator_adv != None:
            if request.user == creator_adv.creator:
                return Response({'detail':'You can\'t add your ad to favorites'},
                                status=status.HTTP_400_BAD_REQUEST)
        if FavoritesAdvertisment.objects.filter(user=request.user, advertisement=pk).exists():
            return Response({'detail':'Advertisement already in favorites'},
                           status=status.HTTP_400_BAD_REQUEST)
        favorites = FavoritesAdvertisment.objects.create(advertisement = pk, 
                                                        user = request.user)
        favorites.save()
        return Response({'detail':'Advertisement added to favorites.'}, 
                        status=status.HTTP_201_CREATED)
    @action(methods=['get'], detail=False, url_path="get-favorites")
    def get_favorites(self, request):
        data = FavoritesAdvertisment.objects.filter(user=request.user)
        serializer = FavoritesAdvertismentSerializer(
            data=data, many=True)
        serializer.is_valid()
        return Response(serializer.data)
    @action(methods=['delete'], detail=True, url_path='remove-from-favorites')
    def remove_from_favorites(self, request, pk=None):
        pk = self.get_object()
        data = FavoritesAdvertisment.objects.filter(advertisement_id=pk)
        if data.first() == None:
            return Response({'detail': 'this item is not in favorites'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            data.delete()
            return Response({'detail': 'the item was successfully removed from favorites'},
                         status=status.HTTP_200_OK)


