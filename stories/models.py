from django.db import models


class Story(models.Model):
    title = models.CharField(max_length=255)
    trader_name = models.CharField(max_length=100)
    content = models.TextField()
    famous_quote = models.CharField(max_length=500)
    key_lesson = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trader_name} — {self.title}"

    class Meta:
        verbose_name_plural = "Stories"