import re
import glob
import os

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
