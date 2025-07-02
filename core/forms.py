from django import forms
from django.contrib.auth.models import User
from .models import Club, Publication, Report, Message, ClubMessage

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

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