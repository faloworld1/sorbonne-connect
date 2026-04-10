import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialisation de Faker en français
fake = Faker('fr_FR')

def generate_fake_data():
    # Connexion à la base de données locale
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    print("Connexion à db.sqlite3 réussie. Création des tables...")

    # 1. Création de la table pour le Pilier Académique (Présences)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scolarite_presence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_nom TEXT,
            filiere TEXT,
            date_cours DATE,
            matiere TEXT,
            statut_appel TEXT,
            justificatif_soumis BOOLEAN
        )
    ''')

    # 2. Création de la table pour le Pilier Engagement (Vie du Campus)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campus_evenement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre_publication TEXT,
            organisateur TEXT,
            categorie TEXT,
            date_publication DATE,
            vues_uniques INTEGER,
            clics_interactivite INTEGER
        )
    ''')

    # Nettoyage de sécurité : vide les tables avant de les remplir pour éviter les doublons si on relance le script
    cursor.execute('DELETE FROM scolarite_presence')
    cursor.execute('DELETE FROM campus_evenement')

    print("Génération des données en cours...")

    # --- GÉNÉRATION DES PRÉSENCES ---
    filieres = ['BUT Informatique', 'Licence Gestion', 'BUT RT', 'Master MEEF', 'Licence Droit']
    matieres = ['Algorithmique', 'Base de données', 'Droit du travail', 'Comptabilité', 'Réseaux', 'Anglais', 'Management']
    statuts = ['Présent', 'Absent', 'Retard']
    
    # Création d'une cohorte de 50 étudiants
    etudiants = []
    for _ in range(50):
        etudiants.append({
            'nom': fake.name(),
            'filiere': random.choice(filieres),
            # On crée volontairement 15% d'étudiants "décrocheurs" qui auront beaucoup d'absences pour vos graphiques
            'est_decrocheur': random.random() < 0.15 
        })

    date_debut = datetime.now() - timedelta(days=120) # On simule un historique de 4 mois
    
    for _ in range(1500): # 1500 lignes de présence générées
        etudiant = random.choice(etudiants)
        date_cours = date_debut + timedelta(days=random.randint(0, 120))
        
        # Les décrocheurs ont 60% de chance d'être absents, les autres seulement 10%
        if etudiant['est_decrocheur']:
            statut = random.choices(statuts, weights=[30, 60, 10])[0] 
        else:
            statut = random.choices(statuts, weights=[85, 10, 5])[0] 
            
        justificatif = True if statut == 'Absent' and random.random() < 0.2 else False
        
        cursor.execute('''
            INSERT INTO scolarite_presence (etudiant_nom, filiere, date_cours, matiere, statut_appel, justificatif_soumis)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (etudiant['nom'], etudiant['filiere'], date_cours.strftime('%Y-%m-%d'), random.choice(matieres), statut, justificatif))

    # --- GÉNÉRATION DES ÉVÉNEMENTS ---
    organisateurs = ['BDE Sorbonne', 'Asso Gaming', 'Mairie Épinay', 'Service Culturel', 'Asso Solidaire', 'SUAPS']
    categories = ['Fête', 'Sport', 'Culture', 'Orientation']    
    for _ in range(200): # 200 événements générés
        date_pub = date_debut + timedelta(days=random.randint(0, 120))
        vues = random.randint(80, 900)
        clics = int(vues * random.uniform(0.1, 0.5)) # Le taux de clic varie entre 10% et 50% des vues
        
        cursor.execute('''
            INSERT INTO campus_evenement (titre_publication, organisateur, categorie, date_publication, vues_uniques, clics_interactivite)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fake.catch_phrase(), random.choice(organisateurs), random.choice(categories), date_pub.strftime('%Y-%m-%d'), vues, clics))

    # Sauvegarde finale en base de données
    conn.commit()
    conn.close()
    print("Succès ! 1500 présences et 200 événements ont été injectés dans db.sqlite3.")

if __name__ == '__main__':
    generate_fake_data() 

    