from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import random
from .models import Story


@shared_task
def rotate_daily_story():
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # Get active stories not shown in last 30 days
    candidates = Story.objects.filter(
        is_active=True
    ).exclude(
        display_date__gte=thirty_days_ago
    )

    if not candidates.exists():
        # All stories shown recently — reset and pick any active story
        candidates = Story.objects.filter(is_active=True)

    if not candidates.exists():
        return "No active stories found."

    story = random.choice(list(candidates))
    story.display_date = today
    story.save()

    return f"Today's story set to: {story.trader_name}"