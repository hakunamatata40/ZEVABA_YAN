from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_POST
from core.models import User, Club, Publication, Reaction, Challenge, Project, Notification, Report, Message, ClubMessage
from core.forms import UserRegisterForm, PublicationForm, ReportForm, MessageForm, ClubMessageForm
from django.db.models import Q, Max, Count
import logging

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    clubs = Club.objects.all()[:5]
    challenges = Challenge.objects.all()[:5]
    return render(request, 'home.html', {'clubs': clubs, 'challenges': challenges})

def register(request):
    logger.info("Register view called")
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info(f"Creating user with username: {form.cleaned_data['username']}")
            user = form.save()
            login(request, user)
            logger.info(f"User {user.username} created and logged in")
            return redirect('feed')
        else:
            logger.warning(f"Form errors: {form.errors}")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            logger.info(f"User {username} logged in")
            return redirect('feed')
        messages.error(request, 'Invalid credentials')
        logger.warning(f"Failed login attempt for username: {username}")
    return render(request, 'login.html')

def user_logout(request):
    logger.info(f"User {request.user.username} logged out")
    logout(request)
    return render(request, 'logout.html')

@login_required
def feed(request):
    clubs = request.user.joined_clubs.all()
    publications = Publication.objects.filter(club__in=clubs).order_by('-created_at')
    reaction_choices = [
        ('ADHERE', "J'adhère"),
        ('SUPPORT', 'Je soutiens'),
        ('ALTERNATIVE', 'Je propose une alternative'),
        ('CLARIFY', 'Je demande des précisions'),
    ]
    return render(request, 'feed.html', {'publications': publications, 'reaction_choices': reaction_choices})

@login_required
def personalized_feed(request):
    clubs = request.user.joined_clubs.all()
    publications = Publication.objects.filter(club__in=clubs).order_by('-created_at')
    return render(request, 'personalized_feed.html', {'publications': publications})

@login_required
def publication_create(request):
    club_id = request.GET.get('club')
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.user = request.user
            if club_id:
                publication.club = get_object_or_404(Club, pk=club_id)
            publication.save()
            logger.info(f"Publication created by {request.user.username}")
            return redirect('feed')
    else:
        form = PublicationForm(user=request.user)
    return render(request, 'publication_create.html', {'form': form})

@require_POST
@login_required
def react(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    reaction_type = request.POST.get('type')
    comment = request.POST.get('comment', '').strip()

    valid_reaction_types = ['ADHERE', 'SUPPORT', 'ALTERNATIVE', 'CLARIFY']
    
    if reaction_type not in valid_reaction_types:
        return JsonResponse({'success': False, 'error': 'Type de réaction invalide'})
    
    if not comment:
        return JsonResponse({'success': False, 'error': 'Le commentaire ne peut pas être vide'})
    
    reaction = Reaction(
        user=request.user,
        publication=publication,
        type=reaction_type,
        comment=comment,
        created_at=timezone.now()
    )
    reaction.save()
    logger.info(f"Reaction {reaction_type} added by {request.user.username} on publication {pk}")
    
    return JsonResponse({
        'success': True,
        'username': request.user.username,
        'user_id': request.user.id,
        'reaction_type_label': reaction.get_type_display(),
        'comment': reaction.comment,
        'created_at': reaction.created_at.strftime('%d/%m/%Y %H:%M')
    })

@require_POST
@login_required
def like_dislike(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    action = request.POST.get('action')
    user = request.user

    if action not in ['like', 'dislike']:
        return JsonResponse({'success': False, 'error': 'Action invalide'})

    if action == 'like':
        if user in publication.liked_by.all():
            publication.liked_by.remove(user)
            publication.likes -= 1
        else:
            publication.liked_by.add(user)
            publication.likes += 1
            if user in publication.disliked_by.all():
                publication.disliked_by.remove(user)
                publication.dislikes -= 1
    elif action == 'dislike':
        if user in publication.disliked_by.all():
            publication.disliked_by.remove(user)
            publication.dislikes -= 1
        else:
            publication.disliked_by.add(user)
            publication.dislikes += 1
            if user in publication.liked_by.all():
                publication.liked_by.remove(user)
                publication.likes -= 1

    publication.save()
    logger.info(f"{action} by {user.username} on publication {pk}")
    return JsonResponse({
        'success': True,
        'likes': publication.likes,
        'dislikes': publication.dislikes,
        'user_liked': user in publication.liked_by.all(),
        'user_disliked': user in publication.disliked_by.all()
    })

@login_required
def clubs(request):
    clubs = Club.objects.all()
    return render(request, 'clubs.html', {'clubs': clubs})

@login_required
def club_detail(request, pk):
    club = get_object_or_404(Club, pk=pk)
    publications = Publication.objects.filter(club=club).order_by('-created_at')
    reaction_choices = [
        ('ADHERE', "J'adhère"),
        ('SUPPORT', 'Je soutiens'),
        ('ALTERNATIVE', 'Je propose une alternative'),
        ('CLARIFY', 'Je demande des précisions'),
    ]
    return render(request, 'club_detail.html', {'club': club, 'publications': publications, 'reaction_choices': reaction_choices})

@require_POST
@login_required
def club_subscribe(request, pk):
    club = get_object_or_404(Club, pk=pk)
    logger.info(f"Attempting to subscribe user {request.user.username} to club {club.name}")
    if request.user not in club.members.all():
        club.members.add(request.user)
        Notification.objects.create(
            user=club.creator,
            message=f"{request.user.username} s'est abonné à votre club {club.name}"
        )
        logger.info(f"{request.user.username} subscribed to club {club.name}")
    else:
        logger.info(f"{request.user.username} is already a member of club {club.name}")
    return redirect('club_detail', pk=pk)

@require_POST
@login_required
def club_unsubscribe(request, pk):
    club = get_object_or_404(Club, pk=pk)
    logger.info(f"Attempting to unsubscribe user {request.user.username} from club {club.name}")
    if request.user in club.members.all():
        club.members.remove(request.user)
        logger.info(f"{request.user.username} unsubscribed from club {club.name}")
    else:
        logger.info(f"{request.user.username} is not a member of club {club.name}")
    return redirect('club_detail', pk=pk)

@require_POST
@login_required
def club_manage_admins(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if request.user != club.creator and request.user not in club.admins.all():
        logger.error(f"Unauthorized access by {request.user.username} to manage admins of club {club.name}")
        return HttpResponseBadRequest("Accès non autorisé")
    user_id = request.POST.get('user_id')
    action = request.POST.get('action')
    user = get_object_or_404(User, pk=user_id)
    if action == 'add_admin':
        club.admins.add(user)
        Notification.objects.create(
            user=user,
            message=f"Vous avez été nommé admin du club {club.name}"
        )
        logger.info(f"{user.username} added as admin to club {club.name}")
    elif action == 'remove_admin':
        club.admins.remove(user)
        Notification.objects.create(
            user=user,
            message=f"Vous n'êtes plus admin du club {club.name}"
        )
        logger.info(f"{user.username} removed as admin from club {club.name}")
    return redirect('club_manage_admins', pk=pk)

@require_POST
@login_required
def report_user(request, pk):
    reported_user = get_object_or_404(User, pk=pk)
    if request.user == reported_user:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas vous signaler vous-même'})
    reason = request.POST.get('reason', '').strip()
    if not reason:
        return JsonResponse({'success': False, 'error': 'La raison du signalement est requise'})
    Report.objects.create(
        reporter=request.user,
        reported_user=reported_user,
        reason=reason
    )
    logger.info(f"User {request.user.username} reported {reported_user.username}")
    return JsonResponse({'success': True})

@login_required
def search(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query) if query else User.objects.none()
    clubs = Club.objects.filter(name__icontains=query) if query else Club.objects.none()
    return render(request, 'search.html', {'users': users, 'clubs': clubs, 'query': query})

@login_required
def search_suggestions(request):
    query = request.GET.get('query', '')
    logger.info(f"Search suggestions query: {query}")
    users = User.objects.filter(username__icontains=query)[:5]
    clubs = Club.objects.filter(name__icontains=query)[:5]
    data = {
        'users': [{'id': user.id, 'username': user.username} for user in users],
        'clubs': [{'id': club.id, 'name': club.name, 'is_member': request.user in club.members.all()} for club in clubs]
    }
    logger.info(f"Search suggestions response: {data}")
    return JsonResponse(data)

@login_required
def send_message(request, pk):
    recipient = get_object_or_404(User, pk=pk)
    if request.user == recipient:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas vous envoyer un message à vous-même'})
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            Notification.objects.create(
                user=recipient,
                message=f"Nouveau message de {request.user.username}"
            )
            logger.info(f"Message sent from {request.user.username} to {recipient.username}: {message.content}")
            return JsonResponse({
                'success': True,
                'sender': request.user.username,
                'content': message.content,
                'created_at': message.created_at.strftime('%d/%m/%Y %H:%M')
            })
    else:
        form = MessageForm()
    return render(request, 'send_message.html', {'form': form, 'recipient': recipient})

@login_required
def messages(request):
    conv_type = request.GET.get('type')
    conv_id = request.GET.get('id')
    logger.info(f"Messages view called with type: {conv_type}, id: {conv_id}")

    # Get recent conversations (user and club)
    user_convs = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values('sender', 'recipient').annotate(
        last_message_time=Max('created_at'),
        unread_count=Count('id', filter=Q(is_read=False, recipient=request.user))
    ).order_by('-last_message_time')[:10]
    
    club_convs = ClubMessage.objects.filter(
        club__members=request.user
    ).values('club').annotate(
        last_message_time=Max('created_at'),
        unread_count=Count('id', filter=Q(club__members=request.user))
    ).order_by('-last_message_time')[:10]
    
    conversations = []
    for conv in user_convs:
        other_user_id = conv['recipient'] if conv['sender'] == request.user.id else conv['sender']
        try:
            other_user = User.objects.get(id=other_user_id)
            last_message = Message.objects.filter(
                Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user)
            ).order_by('-created_at').first()
            conversations.append({
                'type': 'user',
                'id': other_user.id,
                'name': other_user.username,
                'last_message': last_message.content if last_message else '',
                'last_message_time': conv['last_message_time'],
                'unread_count': conv['unread_count']
            })
        except User.DoesNotExist:
            logger.warning(f"User ID {other_user_id} not found")
    
    for conv in club_convs:
        try:
            club = Club.objects.get(id=conv['club'])
            last_message = ClubMessage.objects.filter(club=club).order_by('-created_at').first()
            conversations.append({
                'type': 'club',
                'id': club.id,
                'name': club.name,
                'last_message': last_message.content if last_message else '',
                'last_message_time': conv['last_message_time'],
                'unread_count': conv['unread_count']
            })
        except Club.DoesNotExist:
            logger.warning(f"Club ID {conv['club']} not found")
    
    conversations.sort(key=lambda x: x['last_message_time'] or timezone.now(), reverse=True)
    
    # Get selected conversation messages
    messages = []
    selected_conversation = None
    if conv_type and conv_id:
        logger.info(f"Loading conversation: type={conv_type}, id={conv_id}")
        if conv_type == 'user':
            try:
                other_user = get_object_or_404(User, pk=conv_id)
                selected_conversation = {
                    'type': 'user',
                    'id': other_user.id,
                    'name': other_user.username
                }
                messages = Message.objects.filter(
                    Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user)
                ).order_by('created_at')
                # Mark messages as read
                updated_count = messages.filter(recipient=request.user, is_read=False).update(is_read=True)
                logger.info(f"Marked {updated_count} messages as read for user {request.user.username}")
            except User.DoesNotExist:
                logger.error(f"User ID {conv_id} not found")
                return HttpResponseBadRequest("Utilisateur non trouvé")
        elif conv_type == 'club':
            try:
                club = get_object_or_404(Club, pk=conv_id)
                if request.user not in club.members.all():
                    logger.error(f"User {request.user.username} is not a member of club {club.name}")
                    return HttpResponseBadRequest("Vous devez être membre du club")
                selected_conversation = {
                    'type': 'club',
                    'id': club.id,
                    'name': club.name
                }
                messages = ClubMessage.objects.filter(club=club).order_by('created_at')
            except Club.DoesNotExist:
                logger.error(f"Club ID {conv_id} not found")
                return HttpResponseBadRequest("Club non trouvé")
    
    # Mark selected conversation
    for conv in conversations:
        conv['selected'] = conv['type'] == conv_type and str(conv['id']) == conv_id
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {
            'conversations': [{
                'type': conv['type'],
                'id': conv['id'],
                'name': conv['name'],
                'last_message': conv['last_message'],
                'last_message_time': conv['last_message_time'].strftime('%d/%m/%Y %H:%M') if conv['last_message_time'] else '',
                'unread_count': conv['unread_count'],
                'selected': conv['selected']
            } for conv in conversations],
            'messages': [{
                'sender': msg.sender.username,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_sender': msg.sender == request.user
            } for msg in messages],
            'selected_conversation': selected_conversation
        }
        logger.info(f"AJAX response: {response_data}")
        return JsonResponse(response_data)
    
    return render(request, 'messages.html', {
        'recent_conversations': conversations,
        'selected_conversation': selected_conversation,
        'messages': messages
    })

@login_required
def search_messages(request):
    query = request.GET.get('query', '')
    logger.info(f"Search messages query: {query}")
    user_convs = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user),
        Q(content__icontains=query)
    ).values('sender', 'recipient').annotate(
        last_message_time=Max('created_at'),
        unread_count=Count('id', filter=Q(is_read=False, recipient=request.user))
    ).order_by('-last_message_time')[:10]
    
    club_convs = ClubMessage.objects.filter(
        club__members=request.user,
        content__icontains=query
    ).values('club').annotate(
        last_message_time=Max('created_at'),
        unread_count=Count('id', filter=Q(club__members=request.user))
    ).order_by('-last_message_time')[:10]
    
    conversations = []
    for conv in user_convs:
        other_user_id = conv['recipient'] if conv['sender'] == request.user.id else conv['sender']
        try:
            other_user = User.objects.get(id=other_user_id)
            last_message = Message.objects.filter(
                Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user)
            ).order_by('-created_at').first()
            conversations.append({
                'type': 'user',
                'id': other_user.id,
                'name': other_user.username,
                'last_message': last_message.content if last_message else '',
                'last_message_time': conv['last_message_time'].strftime('%d/%m/%Y %H:%M') if conv['last_message_time'] else '',
                'unread_count': conv['unread_count']
            })
        except User.DoesNotExist:
            logger.warning(f"User ID {other_user_id} not found")
    
    for conv in club_convs:
        try:
            club = Club.objects.get(id=conv['club'])
            last_message = ClubMessage.objects.filter(club=club).order_by('-created_at').first()
            conversations.append({
                'type': 'club',
                'id': club.id,
                'name': club.name,
                'last_message': last_message.content if last_message else '',
                'last_message_time': conv['last_message_time'].strftime('%d/%m/%Y %H:%M') if conv['last_message_time'] else '',
                'unread_count': conv['unread_count']
            })
        except Club.DoesNotExist:
            logger.warning(f"Club ID {conv['club']} not found")
    
    conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
    
    response_data = {'conversations': conversations}
    logger.info(f"Search messages response: {response_data}")
    return JsonResponse(response_data)

@login_required
def club_messages(request, pk):
    club = get_object_or_404(Club, pk=pk)
    logger.info(f"Accessing club messages for club {club.name} by user {request.user.username}")
    if request.user not in club.members.all():
        logger.error(f"User {request.user.username} is not a member of club {club.name}")
        return HttpResponseBadRequest("Vous devez être membre du club pour accéder à la messagerie")
    if request.method == 'POST':
        form = ClubMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.club = club
            message.save()
            for member in club.members.exclude(id=request.user.id):
                Notification.objects.create(
                    user=member,
                    message=f"Nouveau message dans le club {club.name} de {request.user.username}"
                )
            logger.info(f"Club message sent by {request.user.username} in club {club.name}: {message.content}")
            return JsonResponse({
                'success': True,
                'sender': request.user.username,
                'content': message.content,
                'created_at': message.created_at.strftime('%d/%m/%Y %H:%M')
            })
    else:
        form = ClubMessageForm()
    messages = ClubMessage.objects.filter(club=club).order_by('created_at')
    return render(request, 'club_messages.html', {'club': club, 'messages': messages, 'form': form})

@login_required
def challenges(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenges.html', {'challenges': challenges})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    publications = Publication.objects.filter(user=user)
    return render(request, 'profile.html', {'profile_user': user, 'publications': publications})

@login_required
def subscriptions(request):
    user = request.user
    clubs = user.joined_clubs.all()
    return render(request, 'subscriptions.html', {'clubs': clubs})

@login_required
def mentorship(request):
    mentors = User.objects.filter(is_mentor=True)
    return render(request, 'mentorship.html', {'mentors': mentors})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

@login_required
def history(request):
    publications = Publication.objects.filter(user=request.user)
    return render(request, 'history.html', {'publications': publications})

@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'notifications': notifications})

def help(request):
    return render(request, 'help.html')
