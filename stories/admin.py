from django.contrib import admin
from .models import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('trader_name', 'title', 'display_date', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('trader_name', 'title')
    ordering = ('-created_at',)