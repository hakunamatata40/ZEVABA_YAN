from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    interests = models.JSONField(default=list)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    score = models.IntegerField(default=0)
    is_mentor = models.BooleanField(default=False)

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    admins = models.ManyToManyField(User, related_name='admin_clubs', blank=True)
    members = models.ManyToManyField(User, related_name='clubs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    type = models.CharField(max_length=50)
    domain = models.CharField(max_length=50)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_publications', blank=True)
    disliked_by = models.ManyToManyField(User, related_name='disliked_publications', blank=True)
    media = models.FileField(upload_to='publications/%Y/%m/%d/', null=True, blank=True)

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('ADHERE', "J'adhère"),
        ('SUPPORT', 'Je soutiens'),
        ('ALTERNATIVE', 'Je propose une alternative'),
        ('CLARIFY', 'Je demande des précisions'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class ClubMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
class Challenge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(default=timezone.now)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)