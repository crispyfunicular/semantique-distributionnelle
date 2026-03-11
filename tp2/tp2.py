import spacy
import nltk
from nltk.corpus import stopwords
import math
import pandas as pd

# ==========================================
# PRÉPARATION DU CORPUS
# ==========================================

# Chargement du dictionnaire NLTK
nltk.download('stopwords')

# Chargement du modèle linguistique français (léger ou "small" / "sm")
#nlp = spacy.load("fr_core_news_sm")
nlp = spacy.load("fr_core_news_lg")

stopwords_nltk = set(stopwords.words('french'))

def preparer_corpus(file:str, stopwords:bool=False) -> list:
    """Lit un fichier, le segmente en phrases, le tokenise et le lemmatise (avec spaCy)
    Filtrage avec NLTK si stopwords=True"""
    
    # Ouverture et lecture du fichier
    with open(file, "r", encoding="utf-8") as f:
        texte = f.read()
    
    # analyse de l'ensemble du texte
    doc = nlp(texte)
    corpus = []
    
    # Segmentation en phrases (doc.sents)
    for phrase in doc.sents:
        phrase_filtree = []
        
        # Tokenisation
        for token in phrase:
            # Filtrage de la ponctuation (token.is_punct) et des espaces vides (token.is_space)
            if not token.is_punct and not token.is_space:

                # Filtrage des chiffres (ex : numéros de paragraphe)
                if token.is_digit:

                    continue
                # Lemmatisation (.lemma) et passage en minuscules (.lower())
                lemme = token.lemma_.lower()
                
                # Filtrage des lettres seules (ex : numéro d'alinéas)
                if len(lemme) <= 1:
                    continue

                # Filtrage fin avec NLTK
                # Si stopwords=True, on vérifie si le lemme est dans la liste NLTK (double condition)
                # Dans ce cas, on ignore ce mot et on passe au suivant
                if stopwords and lemme in stopwords_nltk:
                    continue

                phrase_filtree.append(lemme)
        
        # Filtrage des phrases de moins 2 mots
        # (pour ne pas mettre en échec la fenêtre glissante)
        if len(phrase_filtree) > 1:
            corpus.append(phrase_filtree)
            
    return corpus


# ==========================================
# MATRICE DE CO-OCCURRENCES
# ==========================================

def construire_matrice(corpus: list, taille_fenetre: int) -> dict:
    """Calcule une demi-matrice carrée de co-occurrences avec fenêtre glissante."""
    matrice = {}
    
    for phrase in corpus:
        # longueur de la phrase
        longueur = len(phrase)
        for i in range(longueur):
            mot_cible = phrase[i]
            
            # Création d'une entrée pour le mot cible si elle n'existe pas encore
            if mot_cible not in matrice:
                matrice[mot_cible] = {}
            
            # On conserve la valeur la plus petite (min) entre la taille de la fenêtre et la longueur de la phrase
            limite = min(i + 1 + taille_fenetre, longueur)
            
            for j in range(i + 1, limite):
                mot_voisin = phrase[j]
                
                # Création d'une entrée pour le mot voisin
                if mot_voisin not in matrice:
                    matrice[mot_voisin] = {}
                
                # Incrémentation (+ 1)
                # Si la combinaison n'existe pas --> création et mise à 0 avec .get(..., 0)
                matrice[mot_cible][mot_voisin] = matrice[mot_cible].get(mot_voisin, 0) + 1
                matrice[mot_voisin][mot_cible] = matrice[mot_voisin].get(mot_cible, 0) + 1
                
    return matrice


# ==========================================
# PPMI + LISSAGE DE LAPLACE
# ==========================================

def appliquer_ppmi(matrice: dict, lissage: float = 0.0) -> dict:
    """Transforme une matrice de co-occurrences en matrice PPMI avec lissage de Laplace.
    
    lissage : valeur k pour le lissage de Laplace (0.0 = pas de lissage, 1.0 = lissage standard)
    
    Formule PMI(w1, w2) = log2( C(w1,w2) * N / (f(w1) * f(w2)) )
    Formule PPMI = max(0, PMI)  →  on ne garde que les valeurs positives
    
    Avec lissage de Laplace (k) :
    - C_lisse(w1, w2)  = C(w1, w2) + k
    - f_lisse(w1)      = f(w1) + k * (V - 1)   (V-1 voisins possibles)
    - N_lisse          = N + k * V * (V - 1)    (toutes les paires dirigées)
    """
    V = len(matrice)
    k = lissage

    # Comptes marginaux : f(w) = somme de toutes ses co-occurrences
    marginaux = {mot: sum(contextes.values()) for mot, contextes in matrice.items()}

    # Total (chaque paire dirigée est comptée : w1→w2 et w2→w1)
    N = sum(marginaux.values())

    # Corrections pour le lissage
    N_lisse = N + k * V * (V - 1)

    ppmi = {}
    for w1 in matrice:
        ppmi[w1] = {}
        f_w1 = marginaux[w1] + k * (V - 1)
        for w2, count in matrice[w1].items():
            f_w2 = marginaux[w2] + k * (V - 1)
            c_lisse = count + k
            if f_w1 > 0 and f_w2 > 0 and N_lisse > 0:
                pmi = math.log2((c_lisse * N_lisse) / (f_w1 * f_w2))
                if pmi > 0:  # PPMI : on ignore les valeurs négatives
                    ppmi[w1][w2] = pmi

    return ppmi


# ==========================================
# SIMILARITÉ COSINUS
# ==========================================

def similarite_cosinus(vecteur_a: dict, vecteur_b: dict) -> float:
    """Calcule le cosinus de l'angle entre deux vecteurs pour calculer leur similarité cosinus.
    Exemple de vecteur : {"homme": 5, "loi": 3}
    """
    # Produit scalaire :
    ## for mot in vecteur_a : on parcourt tous les mots voisins du mot A
    ## vecteur_a[mot] * vecteur_b.get(mot, 0) : on multiplie la fréquence du mot dans le vecteur A par sa fréquence dans le vecteur B
    ## vecteur_b.get(mot, 0) : si le mot voisin existe pour A mais pas pour B, on multiplie par 0 et le résultat sera donc 0.
    produit_scalaire = sum(vecteur_a[mot] * vecteur_b.get(mot, 0) for mot in vecteur_a)
    
    # Normes (longueurs des vecteurs)
    ## Application du théorème de Pythagore :
    ### 1. on élève toutes les fréquences au carré (**2)
    ### 2. on additionne tous les carrés (sum())
    ### 3. on calcule la racine carrée de cette somme (math.sqrt())
    norme_a = math.sqrt(sum(valeur**2 for valeur in vecteur_a.values()))
    norme_b = math.sqrt(sum(valeur**2 for valeur in vecteur_b.values()))
    
    # Si un mot n'a aucun voisin --> empêcher la division par zéro
    if norme_a == 0 or norme_b == 0:
        return 0.0
        
    return produit_scalaire / (norme_a * norme_b)


def top_10_voisins(mot_cible: str, matrice: dict) -> list:
    """Trouve les 10 mots avec la plus forte similarité cosinus."""
    if mot_cible not in matrice:
        return []
    
    # Ex : {"loi": 0.85, "humain": 0.92}
    scores = {}

    # Extraction du dictionnaire de fréquences (le vecteur) correspondant au mot cible
    vecteur_cible = matrice[mot_cible]
    
    # mot_vocabulaire -> clé (le mot testé par la boucle)
    # vecteur_voisin -> valeur (les fréquences)
    for mot_vocabulaire, vecteur_voisin in matrice.items():
        # Ne pas comparer un mot à lui-même
        if mot_vocabulaire != mot_cible:
            # Mesure de la similarité cosinus entre le mot cible (vecteur-cible) et le mot testé par la boucle (vecteur_voisin)
            score = similarite_cosinus(vecteur_cible, vecteur_voisin)
            
            # Le score est > 0 si les deux mots ont au moins un contexte en commun
            if score > 0:
                scores[mot_vocabulaire] = score
                
    # On effectue un tri décroissant des scores
    # On ne conserve que les 10 premier résultats
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]


def main():
    fichier_sortie = "resultats_analyse.md"

    # OFFICIEL
    # Corpus sans stopwords
    corpus_off = preparer_corpus("corpus/officiel.txt", True)

    # Matrices
    ## Fenêtre 3 (f3)
    mat_off_f3 = construire_matrice(corpus_off, taille_fenetre=3)

    ## Fenêtre 10 (f10)
    mat_off_f10 = construire_matrice(corpus_off, taille_fenetre=10)

    ## Fenêtre 25 (f25)
    mat_off_f25 = construire_matrice(corpus_off, taille_fenetre=25)


    # FALC
    # Corpus sans stopwords
    corpus_falc = preparer_corpus("corpus/FALC.txt", True)

    # Matrices
    ## Fenêtre 3 (f3)
    mat_falc_f3 = construire_matrice(corpus_falc, taille_fenetre=3)

    ## Fenêtre 10 (f10)
    mat_falc_f10 = construire_matrice(corpus_falc, taille_fenetre=10)

    ## Fenêtre 25 (f25)
    mat_falc_f25 = construire_matrice(corpus_falc, taille_fenetre=25)


    # PPMI avec lissage de Laplace (k=1)
    ## Officiel
    ppmi_off_f3  = appliquer_ppmi(mat_off_f3,  lissage=1.0)
    ppmi_off_f10 = appliquer_ppmi(mat_off_f10, lissage=1.0)
    ppmi_off_f25 = appliquer_ppmi(mat_off_f25, lissage=1.0)

    ## FALC
    ppmi_falc_f3  = appliquer_ppmi(mat_falc_f3,  lissage=1.0)
    ppmi_falc_f10 = appliquer_ppmi(mat_falc_f10, lissage=1.0)
    ppmi_falc_f25 = appliquer_ppmi(mat_falc_f25, lissage=1.0)


    mots_cible = ["droit", "personne", "handicapé", "enfant", "femme", "discrimination", "accessibilité", "liberté", "dignité", "autonomie", "argent", "chose"]


    # Affichage des résultats
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        
        # Titre du document
        f.write("Résultat de l'analyse sémantique\n\n")

        for mot in mots_cible:
            f.write(f"Mot cible : « **{mot.upper()}** »\n\n")

            # Préparation du tableau vide
            col_fenetre = ["f3", "f10", "f25"]
            col_officiel = ["Absent", "Absent", "Absent"]
            col_falc = ["Absent", "Absent", "Absent"]

            # Corpus officiel
            if mot in mat_off_f25:
                col_officiel[0] = ", ".join([v[0] for v in top_10_voisins(mot, ppmi_off_f3)[:5]])
                col_officiel[1] = ", ".join([v[0] for v in top_10_voisins(mot, ppmi_off_f10)[:5]])
                col_officiel[2] = ", ".join([v[0] for v in top_10_voisins(mot, ppmi_off_f25)[:5]])

            # Corpus FALC
            if mot in mat_falc_f25:
                col_falc[0] = ", ".join([v[0] for v in top_10_voisins(mot, ppmi_falc_f3)[:5]])
                col_falc[1] = ", ".join([v[0] for v in top_10_voisins(mot, ppmi_falc_f10)[:5]])
                col_falc[2] = ", ".join([v[0] for v in top_10_voisins(mot, ppmi_falc_f25)[:5]])

            # Création du tableau Pandas
            tableau = pd.DataFrame({
                "Fenêtre": col_fenetre,
                "Corpus officiel": col_officiel,
                "Corpus FALC": col_falc
            })
            
            # Ecriture dans le fichier
            f.write(tableau.to_markdown(index=False))
            
            # Ajout de sauts de ligne pour aérer le document
            f.write("\n\n\n\n")


if __name__ == "__main__":
    main()