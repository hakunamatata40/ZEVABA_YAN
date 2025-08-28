from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse

class User(AbstractUser):
    # Vos champs existants...
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_mentor = models.BooleanField(default=False)
    clubs = models.ManyToManyField('Club', related_name='club_members', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    
    # Nouveaux champs pour les informations détaillées
    relationship_status = models.CharField(
        max_length=20, 
        choices=[
            ('SINGLE', 'Célibataire'),
            ('RELATIONSHIP', 'En couple'),
            ('MARRIED', 'Marié(e)'),
            ('COMPLICATED', "C'est compliqué")
        ],
        default='SINGLE',
        blank=True
    )
    partner = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='partner_of'
    )
    schools = models.JSONField(default=list, blank=True)  # Pour stocker plusieurs écoles
    hobbies = models.JSONField(default=list, blank=True)  # Pour stocker plusieurs hobbies
    
    def __str__(self):
        return self.username

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    members = models.ManyToManyField(User, through='ClubMembership', related_name='joined_clubs', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('club_detail', kwargs={'pk': self.pk})

class ClubMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    join_date = models.DateTimeField(default=timezone.now)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'core_club_membership'  # Corrigé pour correspondre à la base de données

class ClubAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'core_club_admin'

class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_publications')
    disliked_by = models.ManyToManyField(User, related_name='disliked_publications')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=50, choices=[('NEWS', 'News'), ('EVENT', 'Event')], null=True, blank=True)
    domain = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Publication by {self.user.username}"

    def get_absolute_url(self):
        return reverse('publication_detail', kwargs={'pk': self.pk})

# Nouveau modèle pour les médias
class Media(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='medias')
    file = models.FileField(upload_to='medias/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Média pour publication {self.publication.id}"

    def is_pdf(self):
        return self.file.name.lower().endswith('.pdf') if self.file.name else False

    def is_image(self):
        if self.file.name:
            lower_name = self.file.name.lower()
            return any(lower_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
        return False

    def is_video(self):
        if self.file.name:
            lower_name = self.file.name.lower()
            return any(lower_name.endswith(ext) for ext in ['.mp4', '.mov', '.avi'])
        return False
    
    
class Challenge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.pk})

class Page(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    title = models.CharField(max_length=255)
    subscribers = models.ManyToManyField(User, related_name='subscribed_pages', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pages')
    followers = models.ManyToManyField(User, related_name='followed_pages')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'pk': self.pk})

# core/models.py
class Reaction(models.Model):
    REACTION_CHOICES = [
        ('THOUGHT', 'Ma pensée'),
        ('ADHERE', "J'adhère"),
        ('SUPPORT', 'Je soutiens'),
        ('ALTERNATIVE', 'Je propose une alternative'),
        ('CLARIFY', 'Je demande des précisions'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=REACTION_CHOICES, default='THOUGHT')
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def get_type_display(self):
        return dict(self.REACTION_CHOICES).get(self.type, self.type)
    

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    
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
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_read = models.ManyToManyField(User, related_name='read_club_messages', blank=True)

    def __str__(self):
        return f"Club message by {self.sender.username} in {self.club.name}"
    
    
class Reply(models.Model):
    reaction = models.ForeignKey(Reaction, related_name='reply_set', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.reaction}"


