from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Story
from .serializers import StorySerializer


class TodayStoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        story = Story.objects.filter(display_date=today, is_active=True).first()
        if not story:
            return Response({'detail': 'No story for today.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(StorySerializer(story).data)


class AllStoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Story.objects.filter(is_active=True).order_by('-display_date')
        trader = request.query_params.get('trader')
        if trader:
            queryset = queryset.filter(trader_name__icontains=trader)
        return Response(StorySerializer(queryset, many=True).data)