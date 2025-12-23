from django.db import models
from django.contrib.auth.models import User

class SystemConfig(models.Model):
    message = models.TextField(default="투표하세요")
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super(SystemConfig, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System Configuration"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_vote = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} voted for {self.candidate}"
