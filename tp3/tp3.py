"""
TP3 - Correction des biais

Ce script entraîne un modèle GloVe sur des corpus littéraires français
(Colette et Proust) et utilise des analogies vectorielles (ex. roi - homme + femme)
pour mettre en évidence les biais de genre encodés dans les représentations
distributionnelles.
"""

import sys
import os
import re

#from glove import Corpus, Glove
from mittens import GloVe
import numpy as np
from numpy.linalg import norm

from tp2 import construire_matrice, filtrer_corpus


# Regex pour ne garder que les tokens composés de lettres françaises (+ tiret/apostrophe)
_TOKEN_VALIDE = re.compile(r"^[a-zàâäéèêëïîôùûüÿçœæ]+(['-][a-zàâäéèêëïîôùûüÿçœæ]+)*$")


def charger_corpus(fichier: str) -> list:
    """Charge un corpus déjà lemmatisé (une phrase par ligne, tokens séparés par des espaces).
    Filtre les artefacts Gutenberg (mots avec ':', caractères non-français, etc.)."""
    corpus = []
    with open(fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            tokens = [t for t in ligne.strip().split() if _TOKEN_VALIDE.match(t)]
            if len(tokens) > 1:
                corpus.append(tokens)
    print(f"Corpus chargé : {len(corpus)} phrases")
    return corpus


# ==========================================
# Conversion de la matrice dict → numpy
# ==========================================
def dict_vers_numpy(matrice_dict: dict):
    """
    Convertit la matrice de co-occurrences (dict de dicts, issue du TP2)
    en matrice numpy dense pour mittens.

    Retourne :
        - matrice : np.array de forme (V, V)
        - mot2index : dict {mot: index}
        - index2mot : dict {index: mot}
    """
    vocabulaire = sorted(matrice_dict.keys())
    mot2index = {mot: i for i, mot in enumerate(vocabulaire)}
    index2mot = {i: mot for mot, i in mot2index.items()}

    V = len(vocabulaire)
    matrice = np.zeros((V, V), dtype=np.float64)

    for mot, voisins in matrice_dict.items():
        i = mot2index[mot]
        for voisin, compte in voisins.items():
            j = mot2index[voisin]
            matrice[i][j] = compte

    print(f"Taille du vocabulaire : {V} mots")
    return matrice, mot2index, index2mot


# ==========================================
# Entraînement du modèle GloVe (mittens)
# ==========================================
def entrainer_glove(
    corpus_phrases: list, taille_fenetre: int = 10, dimensions: int = 100
):
    """
    Prend une liste de phrases lemmatisées et entraîne un modèle GloVe
    via la bibliothèque mittens.

    Retourne un objet contenant :
        - word_vectors : np.array (V, dimensions)
        - dictionary   : dict {mot: index}
        - index2mot    : dict {index: mot}
    """
    # Construction de la matrice de co-occurrences (réutilisation du TP2)
    matrice_dict = construire_matrice(corpus_phrases, taille_fenetre)

    # Conversion en matrice numpy dense pour mittens
    matrice_cooc, mot2index, index2mot = dict_vers_numpy(matrice_dict)

    # Entraînement de GloVe via mittens
    modele_glove = GloVe(n=dimensions, max_iter=100)
    vecteurs = modele_glove.fit(matrice_cooc)

    print(f"Entraînement terminé : {vecteurs.shape[0]} mots × {vecteurs.shape[1]} dimensions")

    # On encapsule les résultats dans un objet simple
    # pour garder la même interface que le reste du code
    class ModeleGloVe:
        pass

    modele = ModeleGloVe()
    modele.word_vectors = vecteurs
    modele.dictionary = mot2index
    modele.index2mot = index2mot

    return modele


# ==========================================
# Recherche de biais par analogie
# ==========================================
def resoudre_analogie(
    modele, mot_base: str, mot_moins: str, mot_plus: str, top_n: int = 5
):
    """
    Résout l'équation : X = mot_base - mot_moins + mot_plus
    Exemple : roi - homme + femme = ?

    Utilise un calcul vectorisé (NumPy) pour la similarité cosinus.
    """
    dico = modele.dictionary

    # Vérification que tous les mots existent dans le corpus
    for mot in [mot_base, mot_moins, mot_plus]:
        if mot not in dico:
            raise KeyError(
                f"Erreur : le mot '{mot}' est absent du vocabulaire du modèle."
            )

    # Calcul du vecteur théorique X = mot_base - mot_moins + mot_plus
    vec_resultat = (
        modele.word_vectors[dico[mot_base]]
        - modele.word_vectors[dico[mot_moins]]
        + modele.word_vectors[dico[mot_plus]]
    )

    # Similarités cosinus vectorisées (avec epsilon pour éviter la division par zéro)
    normes = norm(modele.word_vectors, axis=1) * norm(vec_resultat) + 1e-10
    sims = modele.word_vectors @ vec_resultat / normes

    # On exclut les mots de l'équation pour ne pas fausser le résultat
    for mot in [mot_base, mot_moins, mot_plus]:
        sims[dico[mot]] = -1

    # Sélection des top_n meilleurs indices en O(V) avec argpartition,
    # puis tri local des top_n résultats
    top_indices = np.argpartition(sims, -top_n)[-top_n:]
    indices = top_indices[np.argsort(sims[top_indices])[::-1]]

    return [(modele.index2mot[i], sims[i]) for i in indices]


# ==========================================
# Inversion du corpus (plus tard)
# ==========================================


def inverser_corpus(corpus_lemmatise: list, dico_cda: dict) -> list:
    """Génère un nouveau corpus en inversant les mots genrés."""
    corpus_inverse = []
    for phrase in corpus_lemmatise:
        phrase_inverse = [dico_cda.get(mot, mot) for mot in phrase]
        corpus_inverse.append(phrase_inverse)
    return corpus_inverse


def main():
    corpus = sys.argv[1] if len(sys.argv) > 1 else "corpus/sand.txt"

    # Nom du corpus pour le fichier de résultats (ex: "proust")
    nom_corpus = os.path.splitext(os.path.basename(corpus))[0]
    fichier_resultats = f"resultats/{nom_corpus}_resultats.md"
    os.makedirs("resultats", exist_ok=True)

    # Chargement du corpus (déjà lemmatisé) + filtrage stopwords
    corpus_brut = charger_corpus(corpus)
    corpus_propre = filtrer_corpus(corpus_brut, sw=True)

    # Entraînement
    modele = entrainer_glove(corpus_propre, taille_fenetre=10, dimensions=100)

    # Liste de toutes les analogies à tester
    analogies_a_tester = [
        # Contrôle
        ("roi", "homme", "femme"),
        ("roi", "femme", "homme"),
        # Rôles sociaux
        ("docteur", "homme", "femme"),
        ("docteur", "femme", "homme"),
        ("maître", "homme", "femme"),
        ("maître", "femme", "homme"),
        ("héros", "homme", "femme"),
        ("héros", "femme", "homme"),
        # Traits de caractère
        ("courage", "homme", "femme"),
        ("courage", "femme", "homme"),
        ("beauté", "homme", "femme"),
        ("beauté", "femme", "homme"),
        ("doux", "homme", "femme"),
        ("doux", "femme", "homme"),
        # Intellect vs émotion
        ("raison", "homme", "femme"),
        ("raison", "femme", "homme"),
        ("passion", "homme", "femme"),
        ("passion", "femme", "homme"),
        ("intelligence", "homme", "femme"),
        ("intelligence", "femme", "homme"),
        # Orientalisme et genre (Salammbô, Hérodias)
        ("esclave", "homme", "femme"),
        ("esclave", "femme", "homme"),
        ("prêtre", "homme", "femme"),
        ("prêtre", "femme", "homme"),
        ("voile", "homme", "femme"),
        ("voile", "femme", "homme"),
        ("servir", "homme", "femme"),
        ("servir", "femme", "homme"),
    ]

    # Écriture des résultats dans un fichier markdown
    with open(fichier_resultats, "w", encoding="utf-8") as f:
        f.write(f"# Résultats GloVe — {nom_corpus}\n\n")

        for base, moins, plus in analogies_a_tester:
            titre = f"{base} - {moins} + {plus} = ?"
            print(f"\nAnalogie : {titre}")
            f.write(f"## {titre}\n\n")

            try:
                resultats = resoudre_analogie(modele, base, moins, plus)
                f.write("| Mot | Score |\n|---|---|\n")
                for mot, score in resultats:
                    print(f" -> {mot} (Score: {score:.3f})")
                    f.write(f"| {mot} | {score:.3f} |\n")
                f.write("\n")
            except KeyError as e:
                print(e)
                f.write(f"*{e}*\n\n")

    print(f"\nRésultats sauvegardés dans {fichier_resultats}")


if __name__ == "__main__":
    main()
