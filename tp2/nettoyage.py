import re
import glob
import os

raw_files = glob.glob("tp2/corpus/*_raw.txt")

for file in raw_files:
    with open(file, "r", encoding="utf-8") as f:
        contenu = f.read()

    clean = contenu.replace("’", "'")
    # Suppression des numéros de page (ex : "Page 5 sur 53")
    clean = re.sub(r"Page\s+\d+\s+sur\s+\d+\r?\n?", "", clean)
    # Étape 1 : les doubles (ou plus) sauts de ligne marquent une frontière de phrase -> on garde un seul \n
    clean = re.sub(r"(\r?\n){2,}", "\n", clean)
    # Étape 2 : les \n simples en milieu de paragraphe sont fusionnés (sauf après .?!:•)
    clean = re.sub(r"(?<![\.?!:•])\r?\n", " ", clean)

    file_clean = file.replace("_raw", "")
    with open(file_clean, "w", encoding="utf-8") as f:
        f.write(clean)

print("Nettoyage terminé.")