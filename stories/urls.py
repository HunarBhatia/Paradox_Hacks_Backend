from django.urls import path
from .views import TodayStoryView, AllStoriesView

urlpatterns = [
    path('today/', TodayStoryView.as_view(), name='today-story'),
    path('', AllStoriesView.as_view(), name='all-stories'),
]