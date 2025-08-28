from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Club,Page, Publication, Report, Message, ClubMessage, Media
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from .models import Media


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    

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
        fields = ['content', 'type', 'domain', 'club']  # Enlève 'media' ici

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['club'].queryset = Club.objects.filter(members=user)

# Nouveau formulaire pour un seul média
class MediaForm(forms.ModelForm):
    file = MultipleFileField(required=False)  # Utilisez le champ personnalisé
    
    class Meta:
        model = Media
        fields = ['file']


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


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'})
        }


class ProfileDetailsForm(forms.ModelForm):
    # Champs pour les écoles (saisie multiple)
    school_name = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Nom de l\'école'})
    )
    school_start_year = forms.IntegerField(
        min_value=1900, 
        max_value=2100, 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Année de début'})
    )
    school_end_year = forms.IntegerField(
        min_value=1900, 
        max_value=2100, 
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Année de fin'})
    )
    
    # Champ pour les hobbies (saisie multiple)
    hobby = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ajouter un loisir/hobby'})
    )
    
    class Meta:
        model = User
        fields = ['relationship_status', 'partner', 'schools', 'hobbies']
        widgets = {
            'partner': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'relationship_status': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les utilisateurs disponibles comme partenaires (exclure soi-même)
        self.fields['partner'].queryset = User.objects.exclude(id=self.instance.id)