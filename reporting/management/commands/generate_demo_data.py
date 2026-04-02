import random
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Utilisateur
from campus.models import Association, Evenement, Publication, Cours, Emargement, Annonce
from chatbot.models import BaseConnaissance, LogChatbot


class Command(BaseCommand):
    help = 'Génère des données de démonstration réalistes pour la visualisation Power BI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime les données existantes avant de générer',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Suppression des données existantes...')
            LogChatbot.objects.all().delete()
            Emargement.objects.all().delete()
            Evenement.objects.all().delete()
            Publication.objects.all().delete()
            Annonce.objects.all().delete()
            Cours.objects.all().delete()
            Association.objects.all().delete()
            Utilisateur.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.MIGRATE_HEADING('\n═══ Génération des données de démonstration ═══\n'))

        etudiants = self._create_etudiants()
        enseignants = self._create_enseignants()
        bde_users = self._create_bde_users()
        asso_users = self._create_asso_users()
        admin = self._get_or_create_admin()

        associations = self._create_associations(asso_users, etudiants)
        cours_list = self._create_cours(enseignants)
        evenements = self._create_evenements(etudiants + bde_users + asso_users, associations)
        publications = self._create_publications(bde_users + [admin])
        annonces = self._create_annonces(admin)
        self._create_emargements(cours_list, etudiants)
        self._create_chatbot_logs(etudiants + enseignants)

        self.stdout.write(self.style.SUCCESS('\n✅ Génération terminée !'))
        self._print_summary()

    # ──────────────────── Utilisateurs ────────────────────

    def _get_or_create_admin(self):
        admin, created = Utilisateur.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Campus',
                'email': 'admin@uspn.fr',
                'role': 'admin_univ',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        return admin

    def _create_etudiants(self):
        self.stdout.write('  Création des étudiants...')
        formations = ['BIDABI1', 'BIDABI2', 'INFO-L1', 'INFO-L2', 'INFO-L3', 'MATH-L1']
        prenoms_noms = [
            ('Marie', 'Dupont'), ('Thomas', 'Martin'), ('Léa', 'Bernard'),
            ('Hugo', 'Petit'), ('Chloé', 'Moreau'), ('Lucas', 'Garcia'),
            ('Emma', 'Roux'), ('Nathan', 'Faure'), ('Camille', 'Durand'),
            ('Louis', 'Fournier'), ('Sarah', 'Girard'), ('Raphaël', 'Bonnet'),
            ('Inès', 'Lambert'), ('Jules', 'Mercier'), ('Manon', 'Robin'),
            ('Adam', 'Leroy'), ('Jade', 'Simon'), ('Théo', 'Laurent'),
            ('Lina', 'Michel'), ('Ethan', 'Lefebvre'), ('Alice', 'Morel'),
            ('Noah', 'Fontaine'), ('Clara', 'Chevalier'), ('Gabriel', 'Blanchard'),
            ('Zoé', 'Masson'), ('Arthur', 'Rivière'), ('Eva', 'Lemoine'),
            ('Paul', 'Gauthier'), ('Ambre', 'Perrot'), ('Maxime', 'Nguyen'),
        ]

        etudiants = []
        for i, (prenom, nom) in enumerate(prenoms_noms, start=1):
            username = f'etudiant{i}'
            formation = formations[i % len(formations)]
            user, created = Utilisateur.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': f'{prenom.lower()}.{nom.lower()}@edu.uspn.fr',
                    'role': 'etudiant',
                    'numero_etudiant': f'2024{i:04d}',
                    'formation': formation,
                },
            )
            if created:
                user.set_password('etudiant123')
                user.save()
            etudiants.append(user)

        self.stdout.write(self.style.SUCCESS(f'    → {len(etudiants)} étudiants'))
        return etudiants

    def _create_enseignants(self):
        self.stdout.write('  Création des enseignants...')
        data = [
            ('enseignant1', 'Jean', 'Professeur', 'jean.professeur@uspn.fr'),
            ('enseignant2', 'Claire', 'Dubois', 'claire.dubois@uspn.fr'),
            ('enseignant3', 'Pierre', 'Lemaire', 'pierre.lemaire@uspn.fr'),
            ('enseignant4', 'Nathalie', 'Bertrand', 'nathalie.bertrand@uspn.fr'),
            ('enseignant5', 'François', 'Morin', 'francois.morin@uspn.fr'),
        ]
        enseignants = []
        for username, prenom, nom, email in data:
            user, created = Utilisateur.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': email,
                    'role': 'enseignant',
                },
            )
            if created:
                user.set_password('enseignant123')
                user.save()
            enseignants.append(user)

        self.stdout.write(self.style.SUCCESS(f'    → {len(enseignants)} enseignants'))
        return enseignants

    def _create_bde_users(self):
        self.stdout.write('  Création des membres BDE...')
        data = [
            ('bde1', 'Sophie', 'BDE', 'bde@uspn.fr'),
            ('bde2', 'Antoine', 'Responsable', 'antoine.bde@uspn.fr'),
        ]
        users = []
        for username, prenom, nom, email in data:
            user, created = Utilisateur.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': email,
                    'role': 'bde',
                },
            )
            if created:
                user.set_password('bde12345')
                user.save()
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'    → {len(users)} BDE'))
        return users

    def _create_asso_users(self):
        self.stdout.write('  Création des responsables asso...')
        data = [
            ('asso1', 'Lucas', 'Association', 'asso@uspn.fr'),
            ('asso2', 'Mélanie', 'Culturel', 'melanie.asso@uspn.fr'),
            ('asso3', 'Karim', 'Sport', 'karim.sport@uspn.fr'),
        ]
        users = []
        for username, prenom, nom, email in data:
            user, created = Utilisateur.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': email,
                    'role': 'association',
                },
            )
            if created:
                user.set_password('asso1234')
                user.save()
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'    → {len(users)} responsables asso'))
        return users

    # ──────────────────── Associations ────────────────────

    def _create_associations(self, asso_users, etudiants):
        self.stdout.write('  Création des associations...')
        assos_data = [
            ('BDE USPN', 'Bureau des Étudiants — organisation des événements campus, soirées et accompagnement des projets étudiants.'),
            ('Club Informatique', 'Ateliers de programmation, hackathons et conférences tech pour les passionnés du numérique.'),
            ('Association Sportive USPN', 'Football, basketball, volley, running... Tournois inter-formations et championnat universitaire.'),
            ('Ciné-Club Villetaneuse', 'Projections hebdomadaires, débats cinématographiques et festivals.'),
            ('USPN Solidarité', 'Actions humanitaires, collectes alimentaires et soutien aux étudiants en difficulté.'),
            ('Club Data Science', 'Ateliers Machine Learning, Kaggle, projets data et visualisation.'),
        ]

        associations = []
        for i, (nom, desc) in enumerate(assos_data):
            responsable = asso_users[i % len(asso_users)]
            asso, created = Association.objects.get_or_create(
                nom=nom,
                defaults={
                    'description': desc,
                    'responsable': responsable,
                    'active': True,
                },
            )
            if created:
                # Ajouter des membres aléatoires
                nb_membres = random.randint(5, 15)
                membres = random.sample(etudiants, min(nb_membres, len(etudiants)))
                asso.membres.set(membres)
            associations.append(asso)

        self.stdout.write(self.style.SUCCESS(f'    → {len(associations)} associations'))
        return associations

    # ──────────────────── Cours ────────────────────

    def _create_cours(self, enseignants):
        self.stdout.write('  Création des cours...')
        cours_data = [
            # (nom, formation, jour, h_debut, h_fin, salle)
            ('Bases de données', 'BIDABI1', 'lundi', '08:30', '10:30', 'L201'),
            ('Statistiques', 'BIDABI1', 'lundi', '10:45', '12:45', 'L202'),
            ('Python pour la Data', 'BIDABI1', 'mardi', '08:30', '10:30', 'L203'),
            ('Business Intelligence', 'BIDABI1', 'mercredi', '08:30', '10:30', 'L204'),
            ('Visualisation de données', 'BIDABI1', 'jeudi', '08:30', '10:30', 'L201'),
            ('Programmation R', 'BIDABI2', 'lundi', '08:30', '10:30', 'L205'),
            ('Machine Learning', 'BIDABI2', 'mardi', '10:45', '12:45', 'L201'),
            ('Big Data', 'BIDABI2', 'mercredi', '14:00', '16:00', 'L203'),
            ('Algorithmique', 'INFO-L1', 'lundi', '14:00', '16:00', 'L302'),
            ('Architecture des ordinateurs', 'INFO-L1', 'mardi', '08:30', '10:30', 'L303'),
            ('Programmation C', 'INFO-L2', 'mercredi', '08:30', '10:30', 'L302'),
            ('Systèmes d\'exploitation', 'INFO-L2', 'jeudi', '10:45', '12:45', 'L303'),
            ('Réseaux informatiques', 'INFO-L3', 'vendredi', '08:30', '10:30', 'L304'),
            ('Analyse mathématique', 'MATH-L1', 'mardi', '14:00', '16:00', 'B102'),
            ('Algèbre linéaire', 'MATH-L1', 'jeudi', '14:00', '16:00', 'B103'),
        ]

        cours_list = []
        for i, (nom, formation, jour, h_deb, h_fin, salle) in enumerate(cours_data):
            enseignant = enseignants[i % len(enseignants)]
            h_d = time(*map(int, h_deb.split(':')))
            h_f = time(*map(int, h_fin.split(':')))
            cours, _ = Cours.objects.get_or_create(
                nom=nom,
                formation=formation,
                defaults={
                    'enseignant': enseignant,
                    'jour': jour,
                    'heure_debut': h_d,
                    'heure_fin': h_f,
                    'salle': salle,
                },
            )
            cours_list.append(cours)

        self.stdout.write(self.style.SUCCESS(f'    → {len(cours_list)} cours'))
        return cours_list

    # ──────────────────── Événements ────────────────────

    def _create_evenements(self, organisateurs, associations):
        self.stdout.write('  Création des événements...')
        now = timezone.now()
        evenements_data = [
            ('Soirée de rentrée 2025', 'Grande soirée de bienvenue pour les nouveaux étudiants.', -90),
            ('Hackathon IA USPN', 'Compétition de 24h autour de l\'intelligence artificielle.', -60),
            ('Conférence : Les métiers de la data', 'Intervenants professionnels du secteur data/BI.', -45),
            ('Tournoi de football inter-filières', 'Matchs entre formations, ambiance garantie !', -30),
            ('Atelier CV et lettre de motivation', 'Avec le BAIP, préparez vos candidatures.', -20),
            ('Ciné-débat : The Social Dilemma', 'Projection suivie d\'un débat sur les réseaux sociaux.', -15),
            ('Journée portes ouvertes', 'Présentation des formations et du campus.', -10),
            ('Collecte alimentaire solidaire', 'Apportez vos dons au hall du bâtiment A.', -7),
            ('Workshop Power BI', 'Introduction à la visualisation de données avec Power BI.', -5),
            ('Gala USPN 2026', 'Soirée de gala annuelle — dress code : élégant.', -3),
            ('Conférence cybersécurité', 'Les enjeux de la sécurité informatique en 2026.', 2),
            ('Rencontre alumni data science', 'Échanges avec les anciens diplômés du parcours data.', 5),
            ('Marathon du code', 'Défi de programmation en équipe sur 12h.', 7),
            ('Salon des stages et alternances', 'Entreprises partenaires pour vos recherches.', 10),
            ('Journée du développement durable', 'Conférences et ateliers éco-responsables.', 12),
            ('Tournoi e-sport League of Legends', 'Inscriptions en équipe de 5, places limitées.', 15),
            ('Workshop Machine Learning', 'Atelier pratique scikit-learn et TensorFlow.', 18),
            ('Soirée culturelle internationale', 'Musique, danse et gastronomie du monde.', 20),
            ('Conférence blockchain', 'Comprendre la blockchain et ses applications.', 25),
            ('Cérémonie de remise des diplômes', 'Promotion 2025 — rendez-vous à l\'amphithéâtre A.', 30),
            ('Atelier initiation Python', 'Pour les débutants : premiers pas en Python.', 35),
            ('Forum des associations', 'Découvrez les associations du campus et rejoignez-les.', 40),
            ('Sortie escalade en groupe', 'Activité détente et cohésion entre étudiants.', 45),
            ('Masterclass Excel avancé', 'TCD, Power Query, macros VBA — niveau avancé.', 50),
            ('Table ronde : Femmes dans le numérique', 'Témoignages et parcours inspirants.', 55),
        ]

        statuts = ['approuve'] * 15 + ['en_attente'] * 6 + ['refuse'] * 4
        lieux = [
            'Amphithéâtre A', 'Salle L201', 'Gymnase', 'Hall bâtiment A',
            'Salle de conférence B', 'Bibliothèque', 'Cafétéria', 'Salle L302',
        ]

        evenements = []
        for i, (titre, desc, offset_days) in enumerate(evenements_data):
            dt_debut = now + timedelta(days=offset_days, hours=random.randint(9, 17))
            dt_fin = dt_debut + timedelta(hours=random.randint(2, 5))
            statut = statuts[i % len(statuts)]
            organisateur = random.choice(organisateurs)
            asso = random.choice(associations) if random.random() > 0.4 else None

            evt, created = Evenement.objects.get_or_create(
                titre=titre,
                defaults={
                    'description': desc,
                    'date_debut': dt_debut,
                    'date_fin': dt_fin,
                    'lieu': random.choice(lieux),
                    'organisateur': organisateur,
                    'association': asso,
                    'statut': statut,
                },
            )
            evenements.append(evt)

        self.stdout.write(self.style.SUCCESS(f'    → {len(evenements)} événements'))
        return evenements

    # ──────────────────── Publications ────────────────────

    def _create_publications(self, auteurs):
        self.stdout.write('  Création des publications...')
        publications_data = [
            ('Bienvenue aux nouveaux étudiants !', 'Le BDE vous souhaite une excellente rentrée. Retrouvez toutes les infos pratiques ici.', 'publie', -80),
            ('Résultats du hackathon IA', 'L\'équipe DataMinds remporte le premier prix avec un projet de détection de fraudes.', 'publie', -55),
            ('Guide de survie à l\'USPN', '10 conseils pour bien commencer votre année universitaire.', 'publie', -70),
            ('Témoignage : Mon stage chez Capgemini', 'Marie D. partage son expérience de stage en data engineering.', 'publie', -40),
            ('Les meilleurs outils gratuits pour étudiants', 'GitHub Student Pack, Office 365, JetBrains... notre sélection.', 'publie', -35),
            ('Compte-rendu AG du BDE', 'Retour sur l\'assemblée générale du 15 février. Nouveaux projets votés.', 'publie', -25),
            ('Offres de stages — Mars 2026', 'Compilation des offres de stages reçues par le BAIP ce mois-ci.', 'publie', -18),
            ('Retour sur la journée portes ouvertes', 'Plus de 500 visiteurs ! Photos et vidéos disponibles.', 'publie', -9),
            ('Programme de mentorat 2026', 'Les étudiants de M2 accompagnent les L1 : inscrivez-vous.', 'publie', -5),
            ('Classement USPN : top 20 national', 'L\'USPN gagne 3 places dans le classement des universités françaises.', 'publie', -2),
            ('Nouveau partenariat avec Microsoft', 'Azure for Education : crédit cloud gratuit pour les étudiants.', 'brouillon', -1),
            ('Recrutement bénévoles gala', 'On cherche 30 bénévoles pour le gala du 15 mai. Qui est chaud ?', 'brouillon', 0),
            ('Résultats tournoi football', 'La formation BIDABI1 remporte le tournoi inter-filières !', 'publie', -28),
            ('Élections BDE 2026-2027', 'Les candidatures sont ouvertes jusqu\'au 30 avril.', 'publie', -3),
            ('Guide Parcoursup pour les lycéens', 'Article archivé — mis à jour pour la session 2026.', 'archive', -100),
            ('Workshop Power BI — Slides', 'Retrouvez les slides de l\'atelier Power BI du 28 mars.', 'publie', -4),
            ('Interview du directeur de la formation BIDABI', 'Perspectives et évolution du Master BI & Data Analytics.', 'publie', -12),
            ('Tutoriel : Configurer Git et GitHub', 'Pas-à-pas pour les débutants de la formation INFO.', 'publie', -50),
        ]

        publications = []
        for titre, contenu, statut, offset_days in publications_data:
            auteur = random.choice(auteurs)
            pub, created = Publication.objects.get_or_create(
                titre=titre,
                defaults={
                    'contenu': contenu,
                    'auteur': auteur,
                    'statut': statut,
                },
            )
            publications.append(pub)

        self.stdout.write(self.style.SUCCESS(f'    → {len(publications)} publications'))
        return publications

    # ──────────────────── Annonces ────────────────────

    def _create_annonces(self, admin):
        self.stdout.write('  Création des annonces...')
        annonces_data = [
            ('Fermeture exceptionnelle — 1er avril', 'Le campus sera fermé le 1er avril pour travaux de maintenance.', 'urgent', ''),
            ('Inscriptions pédagogiques S2', 'Les inscriptions pédagogiques pour le semestre 2 sont ouvertes jusqu\'au 15 avril.', 'important', 'etudiant'),
            ('Évaluation des enseignements', 'Merci de compléter l\'évaluation en ligne avant le 20 avril.', 'info', 'etudiant'),
            ('Saisie des notes — rappel', 'Les enseignants sont priés de saisir les notes du S1 avant le 10 avril.', 'important', 'enseignant'),
            ('Nouveau règlement intérieur', 'Le nouveau règlement du campus entre en vigueur le 1er mai 2026.', 'info', ''),
            ('Planning des examens S2', 'Le planning des examens du semestre 2 est disponible sur l\'ENT.', 'important', 'etudiant'),
            ('Maintenance serveur ENT', 'L\'ENT sera indisponible samedi 5 avril de 2h à 6h.', 'info', ''),
            ('Appel à projets BDE', 'Proposez vos idées d\'événements pour le mois de mai.', 'info', 'bde'),
            ('Bourse de mobilité internationale', 'Deadline : 30 avril. Dossiers à déposer au service des relations internationales.', 'important', 'etudiant'),
            ('Journée de formation enseignants', 'Atelier pédagogie numérique le 12 avril, salle B201.', 'info', 'enseignant'),
            ('Fermeture bibliothèque vacances', 'La BU sera fermée du 20 au 28 avril (vacances de printemps).', 'info', ''),
            ('Résultats élections BDE', 'La liste « Campus Ensemble » est élue avec 62% des voix.', 'info', ''),
        ]

        annonces = []
        for titre, contenu, priorite, dest_role in annonces_data:
            ann, created = Annonce.objects.get_or_create(
                titre=titre,
                defaults={
                    'contenu': contenu,
                    'auteur': admin,
                    'priorite': priorite,
                    'destinataires_role': dest_role,
                    'active': True,
                },
            )
            annonces.append(ann)

        self.stdout.write(self.style.SUCCESS(f'    → {len(annonces)} annonces'))
        return annonces

    # ──────────────────── Émargements ────────────────────

    def _create_emargements(self, cours_list, etudiants):
        self.stdout.write('  Création des émargements (présences)...')
        today = date.today()
        total_created = 0

        # Générer des émargements sur les 10 dernières semaines
        jours_map = {
            'lundi': 0, 'mardi': 1, 'mercredi': 2,
            'jeudi': 3, 'vendredi': 4, 'samedi': 5,
        }

        for cours in cours_list:
            # Étudiants inscrits dans cette formation
            etudiants_cours = [e for e in etudiants if e.formation == cours.formation]
            if not etudiants_cours:
                continue

            jour_num = jours_map.get(cours.jour, 0)

            # Trouver les 10 dernières occurrences de ce jour
            dates_cours = []
            d = today
            for _ in range(80):  # chercher dans les 80 derniers jours
                d -= timedelta(days=1)
                if d.weekday() == jour_num:
                    dates_cours.append(d)
                if len(dates_cours) >= 10:
                    break

            for date_cours in dates_cours:
                emargements_batch = []
                for etu in etudiants_cours:
                    # Taux de présence réaliste : ~75-90% selon l'étudiant
                    taux_presence = random.uniform(0.55, 0.95)
                    present = random.random() < taux_presence

                    emargements_batch.append(Emargement(
                        cours=cours,
                        etudiant=etu,
                        date=date_cours,
                        present=present,
                    ))

                # Bulk create en ignorant les doublons
                created = Emargement.objects.bulk_create(
                    emargements_batch,
                    ignore_conflicts=True,
                )
                total_created += len(created)

        self.stdout.write(self.style.SUCCESS(f'    → {total_created} émargements'))

    # ──────────────────── Logs chatbot ────────────────────

    def _create_chatbot_logs(self, utilisateurs):
        self.stdout.write('  Création des logs chatbot...')
        now = timezone.now()
        base_connaissances = list(BaseConnaissance.objects.all())

        if not base_connaissances:
            self.stdout.write(self.style.WARNING(
                '    ⚠ Base de connaissances vide. Lancez d\'abord : manage.py load_knowledge_base'
            ))
            return

        # Questions qui matchent (formulées par des étudiants)
        questions_match = [
            'Comment consulter mon emploi du temps ?',
            'je cherche mon emploi du temps',
            'où voir mes cours ?',
            'comment justifier une absence',
            'je veux justifier mon absence',
            'quel est le seuil d\'absence ?',
            'combien d\'absences autorisées',
            'inscription aux examens',
            'comment m\'inscrire aux partiels ?',
            'calendrier universitaire dates',
            'quand sont les vacances ?',
            'contact secrétariat formation',
            'numéro du secrétariat',
            'rejoindre une association',
            'comment adhérer à une asso',
            'créer une association étudiante',
            'proposer un événement campus',
            'organiser une soirée',
            'services du BDE ?',
            'le BDE fait quoi ?',
            'salles informatiques où',
            'Wi-Fi campus comment se connecter',
            'mot de passe eduroam',
            'horaires bibliothèque',
            'la BU ferme à quelle heure',
            'où manger sur le campus',
            'restaurant universitaire prix',
            'comment trouver un stage ?',
            'offres de stage BAIP',
            'convention de stage signature',
            'comment faire signer ma convention',
            'demander une bourse CROUS',
            'bourse comment ça marche',
            'aides financières disponibles',
            'APL logement étudiant',
            'réinitialiser mot de passe ENT',
            'j\'ai oublié mon mot de passe',
            'accès Microsoft 365 gratuit',
            'activer Office 365 étudiant',
            'obtenir ma carte étudiante',
            'carte étudiante perdue',
            'consulter mes notes',
            'où sont mes résultats ?',
            'santé universitaire médecin',
            'rendez-vous psychologue campus',
            'sport universitaire inscription',
            'activités sportives SUAPS',
            'transport campus Villetaneuse',
            'bus pour aller à l\'USPN',
            'transfert dossier autre université',
            'Sorbonne Connect c\'est gratuit ?',
        ]

        # Questions qui ne matchent pas (hors sujet ou trop vagues)
        questions_no_match = [
            'quel temps fait-il demain',
            'qui est le président de la France',
            'raconte-moi une blague',
            'comment cuisiner des pâtes',
            'bonjour',
            'salut ça va ?',
            'merci',
            'rien',
            'test',
            'asdf',
            'quelle est la capitale du Japon',
            'comment pirater un compte',
            'tu connais ChatGPT ?',
            'aide moi à tricher à l\'examen',
            'donne-moi les réponses du partiel',
        ]

        logs_batch = []
        # Générer entre 250 et 350 logs sur les 90 derniers jours
        nb_logs = random.randint(250, 350)

        for _ in range(nb_logs):
            # 72% de chance d'avoir un match
            is_match = random.random() < 0.72

            if is_match and base_connaissances:
                question = random.choice(questions_match)
                entry = random.choice(base_connaissances)

                # Satisfaction : 60% évalué, dont 80% utile
                if random.random() < 0.60:
                    satisfaction = 'Utile' if random.random() < 0.80 else 'Pas utile'
                else:
                    satisfaction = ''

                logs_batch.append(LogChatbot(
                    session_id=f'session_{random.randint(1000, 9999)}',
                    question_posee=question,
                    reponse_fournie=entry.reponse[:300],
                    match_trouve=True,
                    question_matchee=entry,
                    satisfaction=satisfaction,
                ))
            else:
                question = random.choice(questions_no_match)
                fallback = (
                    "Je suis désolé, je ne peux répondre qu'aux questions concernant "
                    "la vie à l'USPN."
                )

                if random.random() < 0.40:
                    satisfaction = 'Pas utile' if random.random() < 0.70 else 'Utile'
                else:
                    satisfaction = ''

                logs_batch.append(LogChatbot(
                    session_id=f'session_{random.randint(1000, 9999)}',
                    question_posee=question,
                    reponse_fournie=fallback,
                    match_trouve=False,
                    question_matchee=None,
                    satisfaction=satisfaction,
                ))

        # Répartir les dates sur 90 jours
        created_logs = LogChatbot.objects.bulk_create(logs_batch)

        # Mettre à jour les dates pour les répartir
        for log in LogChatbot.objects.filter(pk__in=[l.pk for l in created_logs]):
            random_offset = timedelta(
                days=random.randint(0, 90),
                hours=random.randint(8, 22),
                minutes=random.randint(0, 59),
            )
            LogChatbot.objects.filter(pk=log.pk).update(
                date_heure=now - random_offset,
            )

        self.stdout.write(self.style.SUCCESS(f'    → {len(created_logs)} logs chatbot'))

    # ──────────────────── Résumé ────────────────────

    def _print_summary(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Résumé des données ──'))
        self.stdout.write(f'  Utilisateurs :  {Utilisateur.objects.count()}')
        self.stdout.write(f'    - Étudiants :   {Utilisateur.objects.filter(role="etudiant").count()}')
        self.stdout.write(f'    - Enseignants : {Utilisateur.objects.filter(role="enseignant").count()}')
        self.stdout.write(f'    - BDE :         {Utilisateur.objects.filter(role="bde").count()}')
        self.stdout.write(f'    - Associations :{Utilisateur.objects.filter(role="association").count()}')
        self.stdout.write(f'    - Admin :       {Utilisateur.objects.filter(role="admin_univ").count()}')
        self.stdout.write(f'  Associations :  {Association.objects.count()}')
        self.stdout.write(f'  Cours :         {Cours.objects.count()}')
        self.stdout.write(f'  Événements :    {Evenement.objects.count()}')
        self.stdout.write(f'  Publications :  {Publication.objects.count()}')
        self.stdout.write(f'  Annonces :      {Annonce.objects.count()}')
        self.stdout.write(f'  Émargements :   {Emargement.objects.count()}')
        self.stdout.write(f'  Logs chatbot :  {LogChatbot.objects.count()}')

        presents = Emargement.objects.filter(present=True).count()
        total_e = Emargement.objects.count()
        taux = round(presents / total_e * 100, 1) if total_e else 0
        matchs = LogChatbot.objects.filter(match_trouve=True).count()
        total_l = LogChatbot.objects.count()
        taux_m = round(matchs / total_l * 100, 1) if total_l else 0

        self.stdout.write(f'\n  📊 Taux d\'assiduité :  {taux}%')
        self.stdout.write(f'  📊 Taux de match :     {taux_m}%')
        self.stdout.write('')
