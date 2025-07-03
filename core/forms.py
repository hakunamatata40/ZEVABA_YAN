from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Club,Page, Publication, Report, Message, ClubMessage
from django.contrib.auth.forms import UserCreationForm

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'Nom du club'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'rows': 4, 'placeholder': 'Décris ton club...'}),
        }

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'Nom de la page'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'rows': 4, 'placeholder': 'À propos de cette page...'}),
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    is_mentor = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'bio', 'profile_picture', 'is_mentor']
class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['content', 'type', 'domain', 'club', 'media']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['club'].queryset = Club.objects.filter(members=user)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Raison du signalement...'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Écrire un message...'}),
        }

class ClubMessageForm(forms.ModelForm):
    class Meta:
        model = ClubMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Écrire un message au club...'}),
        }