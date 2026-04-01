"""Lemmatisation des textes nettoyés avec spaCy.

Usage :
    python tp3/lemmatisation.py                        # français, modèle sm
    python tp3/lemmatisation.py --lang en --model lg   # anglais, modèle lg
"""

import os
import glob
import argparse
import spacy

# ==========================================
# CONFIGURATION
# ==========================================

MODELES = {
    "fr": {"sm": "fr_core_news_sm", "md": "fr_core_news_md", "lg": "fr_core_news_lg"},
    "en": {"sm": "en_core_web_sm", "md": "en_core_web_md", "lg": "en_core_web_lg"},
}

DIR_ENTREE_DEFAUT = "tp3/corpus/corpus_clean"
DIR_SORTIE_DEFAUT = "tp3/corpus/corpus_lemmes"


# ==========================================
# LEMMATISATION
# ==========================================

CHUNK_SIZE = 500_000  # caractères par chunk (≈ 100k tokens)


def _lemmatiser_chunk(texte: str, nlp) -> list:
    """Lemmatise un chunk de texte et retourne une liste de phrases."""
    doc = nlp(texte)
    phrases = []
    for phrase in doc.sents:
        tokens = []
        for token in phrase:
            if token.is_punct or token.is_space or token.is_digit:
                continue
            lemme = token.lemma_.lower()
            if len(lemme) <= 1:
                continue
            tokens.append(lemme)
        if len(tokens) > 1:
            phrases.append(" ".join(tokens))
    return phrases


def lemmatiser(texte: str, nlp) -> str:
    """Lemmatise un texte avec spaCy, en découpant par chunks si nécessaire.

    - Supprime la ponctuation, les espaces et les chiffres
    - Lemmatise et passe en minuscules
    - Supprime les tokens d'un seul caractère
    - Conserve la segmentation en phrases (une phrase par ligne)
    """
    if len(texte) <= CHUNK_SIZE:
        return "\n".join(_lemmatiser_chunk(texte, nlp))

    # Découpage sur les sauts de ligne pour ne pas couper en plein mot
    lignes = texte.split("\n")
    chunks = []
    chunk_courant = []
    taille_courante = 0

    for ligne in lignes:
        taille_ligne = len(ligne) + 1  # +1 pour le \n
        if taille_courante + taille_ligne > CHUNK_SIZE and chunk_courant:
            chunks.append("\n".join(chunk_courant))
            chunk_courant = []
            taille_courante = 0
        chunk_courant.append(ligne)
        taille_courante += taille_ligne

    if chunk_courant:
        chunks.append("\n".join(chunk_courant))

    print(f"    (texte long : {len(texte):,} caractères → {len(chunks)} chunks)")
    phrases = []
    for i, chunk in enumerate(chunks, 1):
        print(f"    chunk {i}/{len(chunks)}...")
        phrases.extend(_lemmatiser_chunk(chunk, nlp))

    return "\n".join(phrases)


# ==========================================
# TRAITEMENT DU CORPUS
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Lemmatisation du corpus nettoyé")
    parser.add_argument("--lang", choices=MODELES.keys(), default="fr",
                        help="Langue du corpus (fr, en)")
    parser.add_argument("--model", choices=["sm", "md", "lg"], default="sm",
                        help="Taille du modèle spaCy (sm, md, lg)")
    parser.add_argument("--input", default=DIR_ENTREE_DEFAUT,
                        help=f"Dossier d'entrée (défaut : {DIR_ENTREE_DEFAUT})")
    parser.add_argument("--output", default=DIR_SORTIE_DEFAUT,
                        help=f"Dossier de sortie (défaut : {DIR_SORTIE_DEFAUT})")
    args = parser.parse_args()

    DIR_ENTREE = args.input
    DIR_SORTIE = args.output

    nom_modele = MODELES[args.lang][args.model]
    print(f"Chargement du modèle {nom_modele}...")
    nlp = spacy.load(nom_modele)

    # Augmenter la limite pour les longs textes (les chunks resteront en dessous)
    nlp.max_length = 6_000_000

    fichiers = sorted(glob.glob(os.path.join(DIR_ENTREE, "**", "*.txt"), recursive=True))
    print(f"{len(fichiers)} fichier(s) à lemmatiser.\n")

    for fichier in fichiers:
        # Lecture
        with open(fichier, "r", encoding="utf-8") as f:
            texte = f.read()

        # Lemmatisation
        resultat = lemmatiser(texte, nlp)

        # Écriture dans le dossier de sortie (même arborescence)
        chemin_rel = os.path.relpath(fichier, DIR_ENTREE)
        fichier_sortie = os.path.join(DIR_SORTIE, chemin_rel)
        os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)

        with open(fichier_sortie, "w", encoding="utf-8") as f:
            f.write(resultat + "\n")

        print(f"  {fichier} -> {fichier_sortie}")

    print("\nLemmatisation terminée.")


if __name__ == "__main__":
    main()
