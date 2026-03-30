"""
Nettoyage des fichiers Gutenberg : supprime les en-têtes et licences
pour ne garder que le texte littéraire.

Usage : python nettoyage_gutenberg.py corpus/corpus_raw/sand/ corpus/corpus_raw/flaubert/
"""

import sys
import os
import glob


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python nettoyage_gutenberg.py <dossier1> [dossier2] ...")
        sys.exit(1)

    for dossier in sys.argv[1:]:
        print(f"\n=== {dossier} ===")
        nettoyer_dossier(dossier)
