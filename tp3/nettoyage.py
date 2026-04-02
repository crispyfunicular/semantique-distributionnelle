"""
Nettoyage des fichiers texte :

1. nettoyer_gutenberg(fichier) — extrait le texte entre les marqueurs
   START/END de Project Gutenberg (lecture ligne à ligne).

2. nettoyer_dossier(dossier) — nettoie tous les .txt d'un dossier
   et écrit le résultat concaténé dans un fichier {nom}_raw.txt.

3. Pipeline complète : parcourt corpus_raw/**/*.txt, applique le nettoyage
   Gutenberg (regex), normalise les apostrophes, supprime les numéros de
   page, fusionne les sauts de ligne et écrit dans corpus_clean/.

Usage autonome :
    python nettoyage.py                          # pipeline complète
    python nettoyage.py <dossier1> [dossier2] …  # nettoyage Gutenberg par dossier
"""

import re
import sys
import os
import glob


# ──────────────────────────────────────────────
#  Fonctions utilitaires (ex nettoyage_gutenberg)
# ──────────────────────────────────────────────

def nettoyer_gutenberg(fichier: str) -> str:
    """Extrait le texte entre les marqueurs START/END de Project Gutenberg."""
    with open(fichier, "r", encoding="utf-8") as f:
        lignes = f.readlines()

    debut = 0
    fin = len(lignes)

    for i, ligne in enumerate(lignes):
        if "*** START OF" in ligne and "PROJECT GUTENBERG" in ligne:
            debut = i + 1
        if "*** END OF" in ligne and "PROJECT GUTENBERG" in ligne:
            fin = i
            break

    texte = "".join(lignes[debut:fin]).strip()
    return texte


def nettoyer_dossier(dossier: str):
    """Nettoie tous les .txt d'un dossier et écrit le résultat concaténé."""
    nom = os.path.basename(dossier.rstrip("/"))
    fichier_sortie = os.path.join(os.path.dirname(dossier.rstrip("/")), f"{nom}_raw.txt")

    textes = []
    for fichier in sorted(glob.glob(os.path.join(dossier, "*.txt"))):
        print(f"  Nettoyage de {os.path.basename(fichier)}...")
        texte = nettoyer_gutenberg(fichier)
        textes.append(texte)
        print(f"    → {len(texte)} caractères conservés")

    texte_complet = "\n\n".join(textes)
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write(texte_complet)

    print(f"  → Écrit dans {fichier_sortie} ({len(texte_complet)} caractères)")


# ──────────────────────────────────────────────
#  Pipeline complète (ex nettoyage.py original)
# ──────────────────────────────────────────────

def pipeline_complete():
    """Parcourt corpus_raw, nettoie et écrit dans corpus_clean."""
    raw_files = glob.glob("tp3/corpus_raw/**/*.txt", recursive=True)

    for file in raw_files:
        with open(file, "r", encoding="utf-8") as f:
            contenu = f.read()

        # Suppression de l'en-tête Project Gutenberg (avant *** START OF ... ***)
        contenu = re.sub(r"^.*?\*\*\* START OF .+? \*\*\*\r?\n", "", contenu, flags=re.DOTALL)
        # Suppression du pied de page Project Gutenberg (après *** END OF ... ***)
        contenu = re.sub(r"\*\*\* END OF .+? \*\*\*.*$", "", contenu, flags=re.DOTALL)

        # Suppression du bloc "Produced by ..." (multi-lignes, souvent après le START)
        contenu = re.sub(r"Produced by .+?(\r?\n){2,}", "\n", contenu, flags=re.DOTALL)

        # Normalisation des apostrophes typographiques
        clean = contenu.replace("\u2019", "'")
        # Suppression des numéros de page (ex : "Page 5 sur 53")
        clean = re.sub(r"Page\s+\d+\s+sur\s+\d+\r?\n?", "", clean)
        # Étape 1 : les doubles (ou plus) sauts de ligne marquent une frontière de phrase -> on garde un seul \n
        clean = re.sub(r"(\r?\n){2,}", "\n", clean)
        # Étape 2 : les \n simples en milieu de paragraphe sont fusionnés (sauf après .?!:•)
        clean = re.sub(r"(?<![\\.?!:•])\r?\n", " ", clean)

        # Écriture dans tp3/corpus_clean/ en conservant la structure de sous-dossiers
        rel_path = os.path.relpath(file, "tp3/corpus_raw")
        file_clean = os.path.join("tp3/corpus_clean", rel_path)
        os.makedirs(os.path.dirname(file_clean), exist_ok=True)
        clean = clean.strip() + "\n"
        with open(file_clean, "w", encoding="utf-8") as f:
            f.write(clean)

        print(f"  {file} -> {file_clean}")

    print("Nettoyage terminé.")


# ──────────────────────────────────────────────
#  Point d'entrée
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) >= 2:
        # Mode dossier(s) : nettoyage Gutenberg par auteur
        for dossier in sys.argv[1:]:
            print(f"\n=== {dossier} ===")
            nettoyer_dossier(dossier)
    else:
        # Sans arguments : pipeline complète corpus_raw -> corpus_clean
        pipeline_complete()


if __name__ == "__main__":
    main()
