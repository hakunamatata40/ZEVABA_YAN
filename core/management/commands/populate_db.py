from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Club, Publication, Reaction, Challenge, Project, Notification
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the ZEVABA database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # Create Users
        users = []
        for i in range(20):
            username = f'user_{i+1}'
            email = f'user{i+1}@example.com'
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                interests=[random.choice(['Technologie', 'Écologie', 'Santé', 'Business', 'Culture'])],
                score=random.randint(0, 100),
                is_mentor=(i < 2)  # First two users are mentors
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Created 20 users'))

        # Create Superuser
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.stdout.write(self.style.SUCCESS('Created superuser'))

        # Create Clubs
        club_data = [
            ('Club des Solutions Agricoles', 'Réflexions sur l’agriculture durable en Afrique.'),
            ('Club Startups et Innovations', 'Espace pour les entrepreneurs et innovateurs.'),
            ('Club Santé et Bien-être', 'Discussions sur la santé et le bien-être.'),
            ('Club Afro Business', 'Stratégies pour le développement économique africain.'),
            ('Club Culture et Patrimoine', 'Valorisation de la culture africaine.'),
        ]
        clubs = []
        for name, desc in club_data:
            club = Club.objects.create(
                name=name,
                description=desc,
                creator=random.choice(users),
                created_at=timezone.now()
            )
            # Add random members to each club
            club.members.set(random.sample(users, random.randint(5, 15)))
            clubs.append(club)
        self.stdout.write(self.style.SUCCESS('Created 5 clubs'))

        # Create Publications
        publication_data = [
            ('Comment utiliser l’IA pour optimiser les cultures ?', 'IDEA', 'TECH'),
            ('Solution pour réduire les déchets plastiques', 'SOLUTION', 'ECO'),
            ('Concept d’une application de télémédecine', 'CONCEPT', 'HEALTH'),
            ('Stratégie pour développer une startup en Afrique', 'IDEA', 'BUSINESS'),
            ('Comment préserver le patrimoine culturel ?', 'QUESTION', 'CULTURE'),
            ('Défi : Digitaliser l’artisanat rural', 'CHALLENGE', 'BUSINESS'),
            ('Idée pour une énergie renouvelable accessible', 'IDEA', 'ECO'),
            ('Solution pour l’accès à l’eau potable', 'SOLUTION', 'HEALTH'),
            ('Concept de marketplace pour artisans', 'CONCEPT', 'BUSINESS'),
            ('Question sur l’éducation numérique', 'QUESTION', 'TECH'),
            ('Défi : Réduire l’empreinte carbone', 'CHALLENGE', 'ECO'),
            ('Idéeshe pour un système de santé connecté', 'IDEA', 'HEALTH'),
            ('Solution pour l’agriculture urbaine', 'SOLUTION', 'ECO'),
            ('Concept de mentorat en ligne', 'CONCEPT', 'BUSINESS'),
            ('Question sur l’innovation sociale', 'QUESTION', 'CULTURE'),
            ('Défi : Améliorer l’accès à l’éducation', 'CHALLENGE', 'CULTURE'),
            ('Idée pour une plateforme collaborative', 'IDEA', 'TECH'),
            ('Solution pour le recyclage local', 'SOLUTION', 'ECO'),
            ('Concept de microfinance durable', 'CONCEPT', 'BUSINESS'),
            ('Question sur la digitalisation des PME', 'QUESTION', 'TECH'),
        ]
        publications = []
        for content, type_, domain in publication_data:
            pub = Publication.objects.create(
                user=random.choice(users),
                club=random.choice(clubs) if random.choice([True, False]) else None,
                content=content,
                type=type_,
                domain=domain,
                created_at=timezone.now(),
                likes=random.randint(0, 50),
                dislikes=random.randint(0, 10)
            )
            publications.append(pub)
        self.stdout.write(self.style.SUCCESS('Created 20 publications'))

        # Create Reactions
        reaction_types = ['ADHERE', 'SUPPORT', 'ALTERNATIVE', 'CLARIFY']
        reaction_comments = [
            'Excellente idée, je soutiens pleinement !',
            'Intéressant, mais pourrais-tu préciser les coûts ?',
            'Je propose une alternative avec une approche communautaire.',
            'Je suis d’accord, mais il faut plus de données.'
        ]
        for _ in range(30):
            Reaction.objects.create(
                user=random.choice(users),
                publication=random.choice(publications),
                type=random.choice(reaction_types),
                comment=random.choice(reaction_comments),
                created_at=timezone.now()
            )
        self.stdout.write(self.style.SUCCESS('Created 30 reactions'))

        # Create Challenges
        challenge_data = [
            ('Digitaliser l’artisanat rural', 'Comment digitaliser le secteur artisanal en Afrique ?', random.choice(clubs)),
            ('Réduire l’empreinte carbone', 'Solutions pour une Afrique plus verte', None),
            ('Accès à l’éducation', 'Améliorer l’accès à l’éducation numérique', random.choice(clubs)),
            ('Santé communautaire', 'Proposer des solutions de santé accessibles', random.choice(clubs)),
            ('Innovation agricole', 'Optimiser les rendements agricoles durablement', random.choice(clubs)),
        ]
        for title, desc, club in challenge_data:
            Challenge.objects.create(
                title=title,
                description=desc,
                club=club,
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=30),
                created_at=timezone.now()
            )
        self.stdout.write(self.style.SUCCESS('Created 5 challenges'))

        # Create Projects
        project_data = [
            ('Plateforme de santé connectée', 'Développement d’une app de télémédecine.', random.choice(clubs)),
            ('Recyclage communautaire', 'Système local de gestion des déchets.', random.choice(clubs)),
            ('Marketplace artisanale', 'Plateforme pour artisans africains.', random.choice(clubs)),
        ]
        for title, desc, club in project_data:
            project = Project.objects.create(
                title=title,
                description=desc,
                club=club,
                created_at=timezone.now()
            )
            project.members.set(random.sample(users, random.randint(3, 10)))
        self.stdout.write(self.style.SUCCESS('Created 3 projects'))

        # Create Notifications
        notification_messages = [
            'Nouvelle publication dans le club {club}.',
            'Votre publication a reçu une réaction !',
            'Nouveau défi communautaire disponible : {challenge}.',
            'Vous avez été invité à rejoindre un club.',
            'Une de vos publications a été likée.'
        ]
        for _ in range(20):
            club = random.choice(clubs)
            challenge = random.choice(Challenge.objects.all())
            message = random.choice(notification_messages).format(
                club=club.name if '{club}' in notification_messages else '',
                challenge=challenge.title if '{challenge}' in notification_messages else ''
            )
            Notification.objects.create(
                user=random.choice(users),
                message=message,
                read=random.choice([True, False]),
                created_at=timezone.now()
            )
        self.stdout.write(self.style.SUCCESS('Created 20 notifications'))

        self.stdout.write(self.style.SUCCESS('Database population completed successfully!'))