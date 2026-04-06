"""
TP3 - Correction des biais

Ce script entraîne un modèle GloVe sur le corpus de Rudyard Kipling et utilise
des analogies vectorielles (ex. soldier - english + native = ?) pour mettre en
évidence les biais coloniaux encodés dans les représentations distributionnelles.

Deux stratégies de débiaisage sont proposées et comparables côte à côte :
  - CDA (--cda) : Counterfactual Data Augmentation — le corpus est doublé par
    inversion des termes coloniaux polarisés, puis un second modèle est entraîné.
  - Hard Debiasing (--debiais) : post-hoc — la direction du biais est identifiée
    par PCA sur les paires définitionnelles, puis retirée de tous les vecteurs.

Un filtre de fréquence minimale exclut les mots apparaissant moins de MIN_FREQ
fois dans le corpus, afin de réduire le bruit et la taille du vocabulaire.
"""

import sys
import os
import re

from mittens import GloVe
import numpy as np
from numpy.linalg import norm

import nltk
from nltk.corpus import stopwords

# Regex pour ne garder que les tokens composés de lettres (françaises ou anglaises) (+ tiret/apostrophes)
_TOKEN_VALIDE = re.compile(r"^[a-zàâäéèêëïîôùûüÿçœæ]+(['’\-][a-zàâäéèêëïîôùûüÿçœæ]+)*$")


# ==========================================
# UTILITAIRES DE CORPUS
# ==========================================

def filtrer_corpus(corpus: list, sw: bool = False, stopwords_set: set = None) -> list:
    """Filtre un corpus déjà lemmatisé (liste de listes de tokens).
    Si sw=True, retire les stopwords_set fournis."""
    corpus_filtre = []
    for phrase in corpus:
        phrase_filtree = []
        for mot in phrase:
            if len(mot) <= 1:
                continue
            if sw and stopwords_set and mot in stopwords_set:
                continue
            phrase_filtree.append(mot)
        if len(phrase_filtree) > 1:
            corpus_filtre.append(phrase_filtree)
    return corpus_filtre


def filtrer_hapax(corpus: list, min_freq: int = 5) -> list:
    """Exclut du corpus les mots dont la fréquence totale est inférieure à min_freq.

    La fréquence d'un mot est le nombre de fois qu'il apparaît dans l'ensemble
    des phrases (une occurrence par token, quel que soit le contexte).

    Args:
        corpus   : liste de listes de tokens (déjà filtrés des stopwords).
        min_freq : seuil minimal d'occurrences (inclus). Défaut : 5.

    Returns:
        Le corpus avec les mots rares remplacés par leur absence,
        et les phrases devenues trop courtes supprimées.
    """
    # Comptage des fréquences brutes
    frequences: dict = {}
    for phrase in corpus:
        for mot in phrase:
            frequences[mot] = frequences.get(mot, 0) + 1

    n_avant = len(frequences)
    mots_frequents = {mot for mot, freq in frequences.items() if freq >= min_freq}
    n_apres = len(mots_frequents)

    print(
        f"Filtre fréquence (min={min_freq}) : "
        f"{n_avant} → {n_apres} mots "
        f"({n_avant - n_apres} exclus)"
    )

    # Reconstruction du corpus sans les mots rares
    corpus_filtre = []
    for phrase in corpus:
        phrase_filtree = [mot for mot in phrase if mot in mots_frequents]
        if len(phrase_filtree) > 1:
            corpus_filtre.append(phrase_filtree)
    return corpus_filtre


def construire_matrice(corpus: list, taille_fenetre: int) -> dict:
    """Calcule une demi-matrice carrée de co-occurrences avec fenêtre glissante."""
    matrice = {}
    for phrase in corpus:
        longueur = len(phrase)
        for i in range(longueur):
            mot_cible = phrase[i]
            if mot_cible not in matrice:
                matrice[mot_cible] = {}
            limite = min(i + 1 + taille_fenetre, longueur)
            for j in range(i + 1, limite):
                mot_voisin = phrase[j]
                if mot_voisin not in matrice:
                    matrice[mot_voisin] = {}
                matrice[mot_cible][mot_voisin] = matrice[mot_cible].get(mot_voisin, 0) + 1
                matrice[mot_voisin][mot_cible] = matrice[mot_voisin].get(mot_cible, 0) + 1
    return matrice


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

    # Fixation de la graine aléatoire pour garantir la reproductibilité
    np.random.seed(42)

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
# Inversion du corpus (CDA)
# ==========================================


def inverser_corpus(corpus_lemmatise: list, dico_cda: dict) -> list:
    """Génère un nouveau corpus en inversant les termes coloniaux polarisés."""
    corpus_inverse = []
    for phrase in corpus_lemmatise:
        phrase_inverse = [dico_cda.get(mot, mot) for mot in phrase]
        corpus_inverse.append(phrase_inverse)
    return corpus_inverse


# ==========================================
# Hard Debiasing post-hoc
# ==========================================

# Paires définitionnelles : (terme dominant, terme dominé)
# Elles servent à calculer l'axe colonial dans l'espace vectoriel.
#
# Axe Kipling (Inde) :
#   english/native, white/brown, sahib/servant, england/india
# Axe Conrad (Afrique / moral) — ajoutés d'après les résultats :
#   white/black   : biais racial conradien (light-white+black → darkness/shadow, stable ✅)
#   light/darkness: titre et thème central de Heart of Darkness (très stable ✅)
#   civilized/savage : soul-white+savage → patronize (fort, deux runs ✅)
PAIRES_BIAIS = [
    # --- Kipling : hiérarchie coloniale (Inde) ---
    ("english",   "native"),
    ("white",     "brown"),
    ("sahib",     "servant"),
    ("england",   "india"),
    # --- Conrad : biais racial et moral (Afrique) ---
    ("white",     "black"),
    ("light",     "darkness"),
    ("civilized", "savage"),
]


def generer_dico_cda(paires_biais: list = None) -> dict:
    """Génère le dictionnaire CDA par inversion symétrique des PAIRES_BIAIS.

    Pour chaque paire (dominant, dominé), les deux directions sont ajoutées :
        dominant  → dominé
        dominé   → dominant

    En cas de conflit (un mot présent dans plusieurs paires),
    la première occurrence l'emporte, ce qui évite les écrasements
    involontaires (ex. 'white' → 'brown' ne sera pas écrasé par 'white' → 'black').

    Args:
        paires_biais : liste de tuples (dominant, dominé).
                       Défaut : PAIRES_BIAIS.

    Returns:
        dict {mot: équivalent_inversé}
    """
    if paires_biais is None:
        paires_biais = PAIRES_BIAIS
    dico = {}
    for a, b in paires_biais:
        if a not in dico:
            dico[a] = b
        if b not in dico:
            dico[b] = a
    print(f"Dictionnaire CDA : {len(dico)} substitutions "
          f"issues de {len(paires_biais)} paires de biais.")
    return dico



def calculer_direction_biais(modele, paires_biais: list) -> np.ndarray:
    """Calcule le vecteur unitaire représentant l'axe du biais colonial.

    Pour chaque paire (mot_dominant, mot_dominé), on calcule le vecteur
    de différence. La première composante principale (PCA 1D par SVD)
    de ces différences est retenue comme direction du biais.

    Args:
        modele      : ModeleGloVe (word_vectors, dictionary)
        paires_biais: liste de tuples (mot_dominant, mot_dominé)

    Returns:
        Vecteur unitaire de forme (d,) représentant la direction coloniale.
    """
    dico = modele.dictionary
    differences = []
    for mot_a, mot_b in paires_biais:
        if mot_a in dico and mot_b in dico:
            diff = modele.word_vectors[dico[mot_a]] - modele.word_vectors[dico[mot_b]]
            differences.append(diff)
        else:
            print(f"[Débiaisage] Paire ignorée (mot absent) : ({mot_a}, {mot_b})")

    if not differences:
        raise ValueError("Aucune paire de biais valide trouvée dans le vocabulaire.")

    # PCA 1D via SVD : la première composante principale capture
    # la direction qui explique le plus de variance entre les différences.
    matrice = np.array(differences)  # forme (n_paires, d)
    _, _, Vt = np.linalg.svd(matrice, full_matrices=False)
    direction = Vt[0]  # première ligne = première composante principale
    return direction / np.linalg.norm(direction)  # normalisation unitaire


def neutraliser_vecteurs(modele, paires_biais: list):
    """Retourne un nouveau ModeleGloVe dont les vecteurs sont débiaisés.

    Pour chaque mot w hors des paires définitionnelles :
        v_debias(w) = v(w) - (v(w) · bias_vec) * bias_vec

    Autrement dit, on retire la composante alignée sur l'axe colonial,
    rendant le mot insensible à cette direction.

    Les mots des paires définitionnelles sont conservés intacts
    (ils définissent l'axe et ne doivent pas être modifiés).

    Args:
        modele      : ModeleGloVe original (non modifié en place)
        paires_biais: liste de tuples (mot_dominant, mot_dominé)

    Returns:
        Nouveau ModeleGloVe avec word_vectors débiaisés.
    """
    direction = calculer_direction_biais(modele, paires_biais)
    print(f"Direction du biais calculée (PCA sur {len(paires_biais)} paires).")

    # Mots à ne pas neutraliser (ils définissent l'axe)
    mots_definitionnels = {mot for paire in paires_biais for mot in paire}

    # Copie profonde des vecteurs
    nouveaux_vecteurs = modele.word_vectors.copy()

    for mot, idx in modele.dictionary.items():
        if mot not in mots_definitionnels:
            v = nouveaux_vecteurs[idx]
            # Soustraction de la projection sur la direction du biais
            nouveaux_vecteurs[idx] = v - np.dot(v, direction) * direction

    n_neutralises = len(modele.dictionary) - len(mots_definitionnels)
    print(f"Vecteurs neutralisés : {n_neutralises} mots sur {len(modele.dictionary)}")

    # Fabrication d'un nouveau ModeleGloVe avec les vecteurs modifiés
    class ModeleGloVe:
        pass
    modele_debiais = ModeleGloVe()
    modele_debiais.word_vectors = nouveaux_vecteurs
    modele_debiais.dictionary   = modele.dictionary
    modele_debiais.index2mot    = modele.index2mot
    return modele_debiais



# ==========================================
# Génération de la matrice
# ==========================================

# Concepts à tester dans la matrice coloniale.
# Pour chaque mot_base, toutes les combinaisons
#   mot_moins ∈ {english, white} × mot_plus ∈ {native, brown, savage}
# sont générées automatiquement.
CONCEPTS_COLONIAUX = [
    # Humanité
    "man", "master", "human", "soul",
    # Raison / intelligence
    "mind", "wisdom", "think", "understand",
    # Ordre / civilisation
    "law", "order", "rule",
    # Espaces
    "home", "empire", "city",
    # Force / courage
    "brave", "soldier",
]

MOT_MOINS = ["english", "white"]
MOT_PLUS  = ["native", "brown"]

ANALOGIES_AUTRES = []


def generer_analogies_coloniales(
    concepts: list = None,
    mot_moins: list = None,
    mot_plus: list = None,
) -> list:
    """Génère la matrice complète des analogies coloniales.

    Pour chaque concept (mot_base), produit toutes les combinaisons :
        mot_moins ∈ {english, white} × mot_plus ∈ {native, brown, savage}

    Cela garantit que seul le mot_base distingue les groupes de tests,
    et non les termes coloniaux eux-mêmes.

    Args:
        concepts  : liste des mots_base (défaut : CONCEPTS_COLONIAUX)
        mot_moins : liste des termes dominants (défaut : MOT_MOINS)
        mot_plus  : liste des termes dominés   (défaut : MOT_PLUS)

    Returns:
        Liste de tuples (mot_base, mot_moins, mot_plus).
    """
    if concepts  is None: concepts  = CONCEPTS_COLONIAUX
    if mot_moins is None: mot_moins = MOT_MOINS
    if mot_plus  is None: mot_plus  = MOT_PLUS

    analogies = []
    for concept in concepts:
        for moins in mot_moins:
            for plus in mot_plus:
                analogies.append((concept, moins, plus))

    n = len(analogies)
    print(f"Matrice coloniale générée : {len(concepts)} concepts "
          f"× {len(mot_moins)} mot_moins × {len(mot_plus)} mot_plus = {n} analogies")
    return analogies


def main():

    import argparse
    parser = argparse.ArgumentParser(
        description="Entraînement GloVe et analyse des biais coloniaux (corpus Kipling + Conrad)."
    )
    parser.add_argument(
        "corpus", type=str, nargs="?", default="corpus/corpus_lemmes.txt",
        help="Chemin vers le corpus lemmatisé (ex: corpus/corpus_lemmes.txt)"
    )
    parser.add_argument(
        "--cda", action="store_true",
        help="Activer le Counterfactual Data Augmentation : entraîne un second "
             "modèle sur le corpus doublé par inversion des termes coloniaux."
    )
    parser.add_argument(
        "--debiais", action="store_true",
        help="Activer le Hard Debiasing post-hoc : retire la direction du biais "
             "colonial des vecteurs du modèle standard par projection orthogonale."
    )
    args = parser.parse_args()

    corpus = args.corpus

    # Nom du corpus pour le fichier de résultats (ex: "proust")
    nom_corpus = os.path.splitext(os.path.basename(corpus))[0]
    if args.cda and args.debiais:
        fichier_resultats = f"resultats/{nom_corpus}_comparatif_triple.md"
    elif args.cda:
        fichier_resultats = f"resultats/{nom_corpus}_comparatif_cda.md"
    elif args.debiais:
        fichier_resultats = f"resultats/{nom_corpus}_comparatif_debiais.md"
    else:
        fichier_resultats = f"resultats/{nom_corpus}_resultats.md"
    os.makedirs("resultats", exist_ok=True)

    # Détection de la langue selon le corpus pour les stopwords.
    # Par défaut English (Kipling + Conrad) ; French seulement si explicitement indiqué.
    if "french" in nom_corpus.lower() or nom_corpus.lower().startswith("fr_"):
        langue = "french"
    else:
        langue = "english"

    stopwords_set = set(stopwords.words(langue))
    print(f"Langue détectée : {langue} (stopwords NLTK)")

    # Chargement du corpus (déjà lemmatisé) + filtrage stopwords
    corpus_brut = charger_corpus(corpus)
    corpus_propre = filtrer_corpus(corpus_brut, sw=True, stopwords_set=stopwords_set)

    # Exclusion des mots rares (hapax et quasi-hapax)
    MIN_FREQ = 5
    corpus_propre = filtrer_hapax(corpus_propre, min_freq=MIN_FREQ)

    # Entraînement Standard
    print("\n--- Entraînement du modèle STANDARD ---")
    modele_standard = entrainer_glove(corpus_propre, taille_fenetre=10, dimensions=100)
    
    # Entraînement CDA si activé
    modele_cda = None
    if args.cda:
        print("\n--- Entraînement du modèle AUGMENTÉ (CDA) ---")
        dico_cda = generer_dico_cda()
        corpus_inverse = inverser_corpus(corpus_propre, dico_cda)
        corpus_augmente = corpus_propre + corpus_inverse
        print(f"Taille du corpus augmenté : {len(corpus_augmente)} phrases (original: {len(corpus_propre)})")
        modele_cda = entrainer_glove(corpus_augmente, taille_fenetre=10, dimensions=100)

    # Hard Debiasing post-hoc si activé
    modele_debiais = None
    if args.debiais:
        print("\n--- Hard Debiasing post-hoc ---")
        modele_debiais = neutraliser_vecteurs(modele_standard, PAIRES_BIAIS)

    analogies_a_tester = generer_analogies_coloniales() + ANALOGIES_AUTRES
    print(f"\n{len(analogies_a_tester)} analogies au total "
          f"(matrice coloniale + {len(ANALOGIES_AUTRES)} analogies complémentaires)")

    # On détermine quels modèles sont actifs
    modeles_actifs = [("Standard", modele_standard)]
    if args.cda:
        modeles_actifs.append(("CDA", modele_cda))
    if args.debiais:
        modeles_actifs.append(("Débiaisé", modele_debiais))

    # -------------------------------------------------------
    # Phase 1 : calcul de toutes les analogies
    # resultats[base][moins][plus][nom_modele] = [(mot, score), ...]
    # -------------------------------------------------------
    resultats = {}
    for base, moins, plus in analogies_a_tester:
        resultats.setdefault(base, {}).setdefault(moins, {}).setdefault(plus, {})
        for nom_modele, modele in modeles_actifs:
            print(f"  {base} − {moins} + {plus}  [{nom_modele}] ...", end="  ")
            try:
                res = resoudre_analogie(modele, base, moins, plus)
                print(res[0][0])
            except KeyError as e:
                res = [(f"*{e}*", None)]
                print("absent du vocabulaire")
            resultats[base][moins][plus][nom_modele] = res

    # -------------------------------------------------------
    # Phase 2 : écriture en markdown
    # -------------------------------------------------------

    def _cellule(res, top_n: int = 3) -> str:
        """Formate les top_n résultats d'une analogie en une chaîne compacte."""
        items = []
        for mot, score in res[:top_n]:
            items.append(f"{mot} ({score:.3f})" if score is not None else mot)
        return ", ".join(items) if items else "—"

    with open(fichier_resultats, "w", encoding="utf-8") as f:
        f.write(f"# Résultats GloVe — {nom_corpus}\n\n")
        f.write("> Équation : `concept − mot_moins + mot_plus = ?`  \n")
        f.write("> Lignes = `mot_plus` (terme colonisé) · "
                "Colonnes = `mot_moins` (terme dominant)  \n")
        f.write("> Chaque cellule : 3 réponses les plus proches (score cosinus)\n\n")

        # ---- Matrice coloniale : un tableau 2D par concept ----
        for base in CONCEPTS_COLONIAUX:
            if base not in resultats:
                continue
            f.write(f"## {base}\n\n")

            for nom_modele, _ in modeles_actifs:
                if len(modeles_actifs) > 1:
                    f.write(f"**{nom_modele}**\n\n")

                # En-tête
                f.write("| |")
                for moins in MOT_MOINS:
                    f.write(f" **{moins}** |")
                f.write("\n|---|")
                for _ in MOT_MOINS:
                    f.write("---|")
                f.write("\n")

                # Lignes (une par mot_plus)
                for plus in MOT_PLUS:
                    f.write(f"| **{plus}** |")
                    for moins in MOT_MOINS:
                        try:
                            res = resultats[base][moins][plus][nom_modele]
                            f.write(f" {_cellule(res)} |")
                        except KeyError:
                            f.write(" — |")
                    f.write("\n")
                f.write("\n")

        # ---- Analogies complémentaires (hors-matrice) ----
        extras = [(b, m, p) for b, m, p in ANALOGIES_AUTRES if b in resultats]
        if extras:
            f.write("## Analogies complémentaires\n\n")
            for base, moins, plus in extras:
                titre = f"{base} − {moins} + {plus} = ?"
                f.write(f"### {titre}\n\n")
                for nom_modele, _ in modeles_actifs:
                    if len(modeles_actifs) > 1:
                        f.write(f"**{nom_modele}**\n\n")
                    try:
                        res = resultats[base][moins][plus][nom_modele]
                        f.write("| Rang | Mot | Score |\n|---|---|---|\n")
                        for i, (mot, score) in enumerate(res, 1):
                            str_score = f"{score:.3f}" if score is not None else "—"
                            f.write(f"| {i} | {mot} | {str_score} |\n")
                    except KeyError:
                        f.write("*Données non disponibles.*\n")
                    f.write("\n")

    print(f"\nRésultats sauvegardés dans {fichier_resultats}")



if __name__ == "__main__":
    main()
