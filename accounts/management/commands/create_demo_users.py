from django.core.management.base import BaseCommand

from accounts.models import Utilisateur


class Command(BaseCommand):
    help = 'Crée les comptes de démonstration pour chaque rôle'

    def handle(self, *args, **options):
        demo_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'Campus',
                'email': 'admin@uspn.fr',
                'role': 'admin_univ',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'etudiant1',
                'password': 'etudiant123',
                'first_name': 'Marie',
                'last_name': 'Dupont',
                'email': 'marie.dupont@uspn.fr',
                'role': 'etudiant',
                'numero_etudiant': '20240001',
                'formation': 'BIDABI1',
            },
            {
                'username': 'etudiant2',
                'password': 'etudiant123',
                'first_name': 'Thomas',
                'last_name': 'Martin',
                'email': 'thomas.martin@uspn.fr',
                'role': 'etudiant',
                'numero_etudiant': '20240002',
                'formation': 'BIDABI1',
            },
            {
                'username': 'enseignant1',
                'password': 'enseignant123',
                'first_name': 'Jean',
                'last_name': 'Professeur',
                'email': 'jean.professeur@uspn.fr',
                'role': 'enseignant',
            },
            {
                'username': 'bde1',
                'password': 'bde12345',
                'first_name': 'Sophie',
                'last_name': 'BDE',
                'email': 'bde@uspn.fr',
                'role': 'bde',
            },
            {
                'username': 'asso1',
                'password': 'asso1234',
                'first_name': 'Lucas',
                'last_name': 'Association',
                'email': 'asso@uspn.fr',
                'role': 'association',
            },
        ]

        for data in demo_users:
            password = data.pop('password')
            username = data['username']

            user, created = Utilisateur.objects.get_or_create(
                username=username,
                defaults=data,
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ {username} ({data["role"]}) créé'
                ))
            else:
                self.stdout.write(f'  → {username} existe déjà')

        self.stdout.write(self.style.SUCCESS('\nComptes de démo prêts !'))
