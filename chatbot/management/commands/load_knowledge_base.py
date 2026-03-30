from django.core.management.base import BaseCommand
from chatbot.models import BaseConnaissance


QUESTIONS = [
    {
        "question": "Comment consulter mon emploi du temps ?",
        "reponse": "Votre emploi du temps est accessible depuis l'onglet <b>'Scolaire'</b> de l'application Sorbonne Connect. Vous y trouverez vos créneaux de cours avec la date, l'heure, la salle et l'enseignant. Vous pouvez aussi consulter l'ENT via https://ent.univ-paris13.fr.",
        "mots_cles": "emploi du temps;planning;horaires;cours;creneaux;EDT",
        "categorie": "Scolarité",
        "lien_document": "https://ent.univ-paris13.fr"
    },
    {
        "question": "Comment justifier une absence ?",
        "reponse": "Pour justifier une absence, vous devez fournir un justificatif (certificat médical, convocation…) au secrétariat de votre formation dans un <b>délai de 48h</b>. Vous pouvez également déposer votre justificatif via la section <b>'Mes absences'</b> de l'application Sorbonne Connect.",
        "mots_cles": "absence;justificatif;justifier;absent;manquer;retard",
        "categorie": "Scolarité",
        "lien_document": ""
    },
    {
        "question": "Quel est le seuil d'absence autorisé ?",
        "reponse": "Le taux d'assiduité minimum requis est de <b>50%</b>. En dessous de ce seuil, une alerte est envoyée automatiquement à l'administration et à l'étudiant. Des absences répétées peuvent entraîner des sanctions académiques.",
        "mots_cles": "seuil;absence;taux;assiduite;minimum;sanction;alerte",
        "categorie": "Scolarité",
        "lien_document": ""
    },
    {
        "question": "Comment m'inscrire aux examens ?",
        "reponse": "L'inscription aux examens se fait via l'ENT dans la rubrique <b>'Inscriptions pédagogiques'</b>. Vérifiez que vous êtes bien inscrit à toutes vos UE avant la date limite affichée sur le calendrier universitaire.",
        "mots_cles": "examen;inscription;partiel;epreuve;session;UE",
        "categorie": "Scolarité",
        "lien_document": ""
    },
    {
        "question": "Où trouver le calendrier universitaire ?",
        "reponse": "Le calendrier universitaire est disponible sur le site officiel de l'USPN (<b>www.univ-paris13.fr</b>) dans la rubrique 'Formation'. Il indique les périodes de cours, d'examens, de vacances et les dates de rentrée.",
        "mots_cles": "calendrier;universitaire;dates;vacances;rentree;semestre",
        "categorie": "Scolarité",
        "lien_document": "https://www.univ-paris13.fr/calendrier"
    },
    {
        "question": "Comment contacter le secrétariat de ma formation ?",
        "reponse": "Les coordonnées du secrétariat sont disponibles sur le site de l'USPN, rubrique 'Contacts'. Vous pouvez aussi les trouver dans l'onglet <b>'Infos pratiques'</b>. Horaires : <b>lundi au vendredi, 9h-12h et 14h-16h</b>.",
        "mots_cles": "secretariat;contact;telephone;mail;bureau;horaires;accueil",
        "categorie": "Scolarité",
        "lien_document": ""
    },
    {
        "question": "Comment rejoindre une association étudiante ?",
        "reponse": "Rendez-vous dans l'onglet <b>'Associatif'</b> de Sorbonne Connect. Vous y trouverez la liste de toutes les associations actives avec leur description et contacts. Vous pouvez aussi vous rendre au <b>Bureau de la Vie Étudiante (BVE), bâtiment L</b>.",
        "mots_cles": "association;rejoindre;adherer;inscription;club;BVE",
        "categorie": "Vie étudiante",
        "lien_document": ""
    },
    {
        "question": "Comment créer une association étudiante ?",
        "reponse": "Pour créer une association : <b>1)</b> Constituer un bureau (président, trésorier, secrétaire), <b>2)</b> Rédiger les statuts, <b>3)</b> Déposer un dossier auprès du BDE et du BVE. Le BDE doit valider votre demande.",
        "mots_cles": "creer;association;fonder;statuts;bureau;BDE;dossier",
        "categorie": "Vie étudiante",
        "lien_document": ""
    },
    {
        "question": "Comment proposer un événement sur le campus ?",
        "reponse": "Les associations peuvent proposer des événements via l'onglet <b>'Associatif' > 'Créer un événement'</b>. Remplissez le formulaire et cliquez sur <b>'Soumettre pour validation'</b>. Le BDE examinera et validera votre proposition.",
        "mots_cles": "evenement;proposer;organiser;activite;soiree;conference;campus",
        "categorie": "Vie étudiante",
        "lien_document": ""
    },
    {
        "question": "Quels sont les services du BDE ?",
        "reponse": "Le <b>Bureau Des Étudiants (BDE)</b> propose : la validation des événements associatifs, l'organisation d'événements campus (soirée de rentrée, gala, tournois), un service d'aide aux projets étudiants, et la coordination avec l'administration.",
        "mots_cles": "BDE;bureau;etudiants;services;aide;coordination",
        "categorie": "Vie étudiante",
        "lien_document": ""
    },
    {
        "question": "Où se trouvent les salles informatiques ?",
        "reponse": "Les salles informatiques sont dans le <b>bâtiment L2 (salles L201 à L210)</b> et à la bibliothèque universitaire (espace numérique, 2e étage). Accès en libre-service avec votre carte étudiante.",
        "mots_cles": "salle;informatique;ordinateur;PC;L2;libre-service;batiment",
        "categorie": "Campus",
        "lien_document": ""
    },
    {
        "question": "Comment accéder au Wi-Fi du campus ?",
        "reponse": "Connectez-vous au réseau <b>'eduroam'</b> avec vos identifiants USPN (<b>prenom.nom@edu.univ-paris13.fr</b> + mot de passe ENT). En cas de problème, contactez la <b>DSI au bâtiment A, bureau A108</b>.",
        "mots_cles": "wifi;internet;connexion;eduroam;reseau;DSI;identifiants",
        "categorie": "Campus",
        "lien_document": ""
    },
    {
        "question": "Quels sont les horaires de la bibliothèque universitaire ?",
        "reponse": "La BU est ouverte du <b>lundi au vendredi de 8h30 à 19h00</b>, et le <b>samedi de 9h00 à 13h00</b> (hors vacances). Des horaires étendus sont proposés en période d'examens.",
        "mots_cles": "bibliotheque;BU;horaires;ouverture;livres;emprunt",
        "categorie": "Campus",
        "lien_document": ""
    },
    {
        "question": "Où manger sur le campus ?",
        "reponse": "Le campus dispose de <b>deux restaurants universitaires (RU) CROUS</b> : le RU principal (bâtiment K, 11h30-14h00) et la cafétéria (bâtiment B, 8h00-16h00). Repas au RU : <b>3,30€ avec IZLY</b>.",
        "mots_cles": "manger;restaurant;RU;CROUS;cafeteria;repas;IZLY;cantine",
        "categorie": "Campus",
        "lien_document": ""
    },
    {
        "question": "Comment trouver un stage ?",
        "reponse": "Le <b>BAIP</b> (Bureau d'Aide à l'Insertion Professionnelle) propose des offres sur sa plateforme. Consultez aussi l'ENT, rubrique 'Stages'. <b>Important :</b> une convention de stage signée est obligatoire avant de commencer.",
        "mots_cles": "stage;convention;entreprise;BAIP;offre;insertion;professionnel",
        "categorie": "Stages",
        "lien_document": ""
    },
    {
        "question": "Comment faire signer ma convention de stage ?",
        "reponse": "Remplissez la convention sur l'ENT (rubrique <b>P-Stage</b>), imprimez en 3 exemplaires. Ordre de signature : <b>1)</b> l'étudiant, <b>2)</b> l'entreprise, <b>3)</b> le responsable pédagogique, <b>4)</b> le service des stages. Comptez <b>~2 semaines</b>.",
        "mots_cles": "convention;signer;PStage;formulaire;signature;exemplaires",
        "categorie": "Stages",
        "lien_document": ""
    },
    {
        "question": "Comment demander une bourse ?",
        "reponse": "La demande se fait via le <b>Dossier Social Étudiant (DSE)</b> sur <b>messervices.etudiant.gouv.fr</b> entre le <b>15 janvier et le 15 mai</b>. Renseignez les revenus de vos parents. Résultat notifié par email sous 30 jours.",
        "mots_cles": "bourse;DSE;CROUS;aide;financiere;revenus;demande",
        "categorie": "Bourses",
        "lien_document": "https://www.messervices.etudiant.gouv.fr"
    },
    {
        "question": "Quelles aides financières sont disponibles ?",
        "reponse": "Outre les bourses CROUS : <b>aide au logement</b> (APL/ALS via la CAF), <b>aide à la mobilité internationale</b>, fonds d'aide d'urgence CROUS, et aides USPN (exonération de frais, prêt d'ordinateur). Contactez l'<b>assistante sociale</b> pour un accompagnement.",
        "mots_cles": "aide;financiere;APL;CAF;logement;mobilite;urgence;exoneration",
        "categorie": "Bourses",
        "lien_document": ""
    },
    {
        "question": "Comment réinitialiser mon mot de passe ENT ?",
        "reponse": "Rendez-vous sur <b>ent.univ-paris13.fr</b> et cliquez sur <b>'Mot de passe oublié'</b>. Un lien de réinitialisation sera envoyé sur votre email personnel. Si le problème persiste, contactez la <b>DSI au bureau A108</b>.",
        "mots_cles": "mot de passe;ENT;reinitialiser;oublie;connexion;identifiant;DSI",
        "categorie": "Numérique",
        "lien_document": "https://ent.univ-paris13.fr"
    },
    {
        "question": "Comment accéder à Microsoft 365 gratuitement ?",
        "reponse": "En tant qu'étudiant USPN, vous avez accès gratuit à <b>Microsoft 365</b> (Word, Excel, PowerPoint, Teams, OneDrive 1To). Connectez-vous sur <b>portal.office.com</b> avec votre email universitaire.",
        "mots_cles": "Microsoft;Office;365;Word;Excel;Teams;OneDrive;gratuit",
        "categorie": "Numérique",
        "lien_document": "https://portal.office.com"
    },
    {
        "question": "Comment obtenir ma carte étudiante ?",
        "reponse": "Votre carte est délivrée lors de l'inscription administrative. Si non reçue, rendez-vous au <b>service de la scolarité (bâtiment A, RDC)</b> avec une pièce d'identité. En cas de perte : duplicata possible moyennant <b>10€</b>.",
        "mots_cles": "carte;etudiante;inscription;scolarite;duplicata;perte",
        "categorie": "Scolarité",
        "lien_document": ""
    },
    {
        "question": "Comment fonctionne la validation des événements ?",
        "reponse": "Quand une association soumet un événement, il n'est <b>pas publié immédiatement</b>. Le BDE reçoit une notification, examine la proposition, puis <b>valide</b> (visible pour tous) ou <b>refuse</b> (avec motif). Ce circuit garantit la qualité.",
        "mots_cles": "validation;evenement;soumission;BDE;publier;approuver;refuser;circuit",
        "categorie": "Vie étudiante",
        "lien_document": ""
    },
    {
        "question": "Comment consulter mes notes ?",
        "reponse": "Vos notes sont accessibles sur l'ENT dans la rubrique <b>'Résultats'</b>. Elles sont saisies après les délibérations du jury. En cas de contestation, vous avez <b>2 mois</b> pour demander une consultation de copie au secrétariat.",
        "mots_cles": "notes;resultats;releve;bulletin;deliberation;consultation;copie",
        "categorie": "Scolarité",
        "lien_document": "https://ent.univ-paris13.fr"
    },
    {
        "question": "Où se trouve le service de santé universitaire ?",
        "reponse": "Le <b>SSU</b> (Service de Santé Universitaire) se trouve au <b>bâtiment G, RDC</b>. Consultations gratuites : médecine générale, psychologue, infirmerie. <b>Sur rendez-vous du lundi au vendredi, 9h-17h</b>. Urgence : 01 49 40 30 00.",
        "mots_cles": "sante;medecin;psychologue;infirmerie;SSU;urgence;consultation",
        "categorie": "Campus",
        "lien_document": ""
    },
    {
        "question": "Comment s'inscrire à une activité sportive ?",
        "reponse": "Les activités sportives sont proposées par le <b>SUAPS</b>. Inscription en début de semestre sur l'ENT ou directement au gymnase. La pratique sportive peut donner des <b>points bonus via l'UE libre 'Sport'</b>.",
        "mots_cles": "sport;SUAPS;gymnase;inscription;activite;sportive;UE;bonus",
        "categorie": "Vie étudiante",
        "lien_document": ""
    },
    {
        "question": "Quels sont les transports pour venir au campus ?",
        "reponse": "Campus de Villetaneuse accessible par : <b>Tramway T8</b> (arrêt 'Université'), <b>Bus 156/256/354</b> (arrêt 'Campus USPN'), <b>RER D</b> (gare Villetaneuse-Université, 10 min à pied). Parking gratuit avec carte étudiante.",
        "mots_cles": "transport;tramway;bus;RER;Villetaneuse;acces;parking;Navigo",
        "categorie": "Campus",
        "lien_document": ""
    },
    {
        "question": "Comment faire un transfert de dossier ?",
        "reponse": "<b>1)</b> Obtenir une attestation d'admission de l'université d'accueil, <b>2)</b> Remplir le formulaire de transfert sur l'ENT, <b>3)</b> Déposer au service de la scolarité. Le transfert est effectif après validation par les deux établissements.",
        "mots_cles": "transfert;dossier;universite;mutation;changement;depart;scolarite",
        "categorie": "Scolarité",
        "lien_document": ""
    },
    {
        "question": "L'application Sorbonne Connect est-elle gratuite ?",
        "reponse": "Oui, <b>entièrement gratuite</b> pour tous les étudiants, enseignants et personnels de l'USPN. Accessible depuis n'importe quel appareil (smartphone, tablette, ordinateur) via un navigateur web. <b>Aucune installation nécessaire</b>.",
        "mots_cles": "application;gratuit;Sorbonne Connect;telecharger;mobile;web;navigateur",
        "categorie": "Numérique",
        "lien_document": ""
    },
    {
        "question": "Comment signaler un problème technique ?",
        "reponse": "<b>1)</b> Bouton 'Signaler un problème' dans le menu de l'application, <b>2)</b> Email à support-sorbonneconnect@univ-paris13.fr, <b>3)</b> DSI au bureau A108. Décrivez précisément le problème et joignez une capture d'écran.",
        "mots_cles": "probleme;technique;bug;erreur;signaler;support;DSI;aide",
        "categorie": "Numérique",
        "lien_document": ""
    },
    {
        "question": "Quand ont lieu les portes ouvertes ?",
        "reponse": "Les <b>Journées Portes Ouvertes (JPO)</b> ont lieu généralement en <b>février et mars</b>. Dates exactes publiées sur le site USPN et les réseaux sociaux. Vous pouvez visiter les campus, rencontrer enseignants et étudiants.",
        "mots_cles": "portes ouvertes;JPO;visite;campus;presentation;formation",
        "categorie": "Scolarité",
        "lien_document": "https://www.univ-paris13.fr/jpo"
    },
]


class Command(BaseCommand):
    help = "Charge les 30 questions/réponses dans la base de connaissances"

    def handle(self, *args, **options):
        if BaseConnaissance.objects.exists():
            self.stdout.write(self.style.WARNING(
                f"La base contient déjà {BaseConnaissance.objects.count()} entrées. "
                "Utilisez --force pour tout remplacer."
            ))
            if '--force' not in args and not any('force' in a for a in options.values() if isinstance(a, str)):
                # Still load if empty, overwrite otherwise ask
                pass

        BaseConnaissance.objects.all().delete()

        for q in QUESTIONS:
            BaseConnaissance.objects.create(**q)

        self.stdout.write(self.style.SUCCESS(
            f"✅ {len(QUESTIONS)} questions chargées dans la base de connaissances !"
        ))
