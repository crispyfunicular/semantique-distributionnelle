import spacy
from nltk.corpus import stopwords
import math

# ==========================================
# PRÉPARATION DU CORPUS
# ==========================================

# Chargement du modèle linguistique français
nlp = spacy.load("fr_core_news_sm")

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
                # Lemmatisation (.lemma) et passage en minuscules (.lower())
                lemme = token.lemma_.lower()

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
# SIMILARITÉ COSINUS
# ==========================================

def similarite_cosinus(vecteur_a, vecteur_b) -> float:
    """Calcule le cosinus de l'angle entre deux vecteurs."""
    # Produit scalaire
    produit_scalaire = sum(vecteur_a[mot] * vecteur_b.get(mot, 0) for mot in vecteur_a)
    
    # Normes (longueurs des vecteurs)
    norme_a = math.sqrt(sum(valeur**2 for valeur in vecteur_a.values()))
    norme_b = math.sqrt(sum(valeur**2 for valeur in vecteur_b.values()))
    
    # Sécurité contre la division par zéro
    if norme_a == 0 or norme_b == 0:
        return 0.0
        
    return produit_scalaire / (norme_a * norme_b)


def main():
    # CORPUS CDPH_OFFICIEL
    ## Avec stopwords
    corpus_officiel = preparer_corpus("corpus/CDPH_officiel.txt")
    ## Sans stopwords
    corpus_officiel_stopwords = preparer_corpus("corpus/CDPH_officiel.txt", True)

    # MATRICES CDPH_OFFICIEL
    ## Avec stopwords - fenêtre 2
    mat_off_w2 = construire_matrice(corpus_officiel, taille_fenetre=2)

    ## Avec stopwords - fenêtre 15
    mat_off_w15 = construire_matrice(corpus_officiel, taille_fenetre=15)

    ## Avec stopwords - fenêtre 50
    mat_off_w15 = construire_matrice(corpus_officiel, taille_fenetre=50)

    ## Sans stopwords - fenêtre 2
    mat_off_w2 = construire_matrice(corpus_officiel_stopwords, taille_fenetre=2)

    ## Sans stopwords - fenêtre 15
    mat_off_w15 = construire_matrice(corpus_officiel_stopwords, taille_fenetre=15)

    ## sans stopwords - fenêtre 50
    mat_off_w15 = construire_matrice(corpus_officiel_stopwords, taille_fenetre=50)


    # CORPUS CDPH_FALC
    ## Avec stopwords
    corpus_falc = preparer_corpus("corpus/CDPH_falc.txt")
    ## Sans stopwords
    corpus_falc_stopwords = preparer_corpus("corpus/CDPH_falc.txt", True)

    # MATRICES CDPH_FALC
    ## Avec stopwords - fenêtre 2
    mat_falc_w2 = construire_matrice(corpus_falc, taille_fenetre=2)

    ## Avec stopwords - fenêtre 15
    mat_falc_w15 = construire_matrice(corpus_falc, taille_fenetre=15)

    ## Avec stopwords - fenêtre 50
    mat_falc_w15 = construire_matrice(corpus_falc, taille_fenetre=50)

    ## Avec stopwords - fenêtre 50
    mat_falc_w15 = construire_matrice(corpus_falc, taille_fenetre=50)

    ## Sans stopwords - fenêtre 2
    mat_falc_w2 = construire_matrice(corpus_falc_stopwords, taille_fenetre=2)

    ## Sans stopwords - fenêtre 15
    mat_falc_w15 = construire_matrice(corpus_falc_stopwords, taille_fenetre=15)

    ## Sans stopwords - fenêtre 50
    mat_falc_w15 = construire_matrice(corpus_falc_stopwords, taille_fenetre=50)


    mots_cible = ["droit", "personne", "handicapé", "enfant", "femme", "discrimination", "liberté", "dignité", "accessibilité", "autonomie"]


if __name__ == "__main__":
    main()