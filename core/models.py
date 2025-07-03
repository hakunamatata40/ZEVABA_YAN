from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_mentor = models.BooleanField(default=False)
    clubs = models.ManyToManyField('Club', related_name='club_members', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return self.username

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    members = models.ManyToManyField(User, related_name='joined_clubs', blank=True)
    admins = models.ManyToManyField(User, related_name='admin_clubs', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='publications/', blank=True, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_publications')
    disliked_by = models.ManyToManyField(User, related_name='disliked_publications')
    created_at = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=50, choices=[('NEWS', 'News'), ('EVENT', 'Event')], null=True, blank=True)
    domain = models.CharField(max_length=50, null=True, blank=True)
    media = models.FileField(upload_to='medias/', null=True, blank=True)

    def __str__(self):
        return f"Publication by {self.user.username}"

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=[
        ('ADHERE', "J'adhère"),
        ('SUPPORT', 'Je soutiens'),
        ('ALTERNATIVE', 'Je propose une alternative'),
        ('CLARIFY', 'Je demande des précisions'),
    ])
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.type} on {self.publication}"

class Challenge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Notification for {self.user.username}"

class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Report by {self.reporter.username} against {self.reported_user.username}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

class ClubMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Club message by {self.sender.username} in {self.club.name}"
    
class Page(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    title = models.CharField(max_length=255)
    subscribers = models.ManyToManyField(User, related_name='subscribed_pages', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pages')
    followers = models.ManyToManyField(User, related_name='followed_pages')
    created_at = models.DateTimeField(auto_now_add=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_pages', blank=True)

    def __str__(self):
        return self.title
    
class Reply(models.Model):
    reaction = models.ForeignKey(Reaction, related_name='reply_set', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)