from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404

from .permissions_cotrols import CanManageObjectPermission
from hashtags.models import HashTag
from hashtags.serializers import HashTagSerializer


class HashTagListAPIView(APIView):
    """API view for listing the all hastags"""
    permission_classes = [CanManageObjectPermission]
    def get(self, request):
        hashtags = get_list_or_404(HashTag)
        seralizer = HashTagSerializer(hashtags, many=True)
        return Response(seralizer.data, status=status.HTTP_200_OK)
