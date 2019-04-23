from django.db import models
from django.conf import settings

# Create your models here.
class Track(models.Model):

    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.title:
            return '{}'.format(self.title)
        return self.description

class Like(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, related_name='likes', on_delete=models.CASCADE)
