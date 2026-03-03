import re
file = "corpus/CDPH_falc_raw.txt"
file_clean = "corpus/CDPH_falc.txt"

with open(file, "r", encoding="utf-8") as f:
    contenu = f.read()

clean = contenu.replace("’", "'")
clean = re.sub(r"(?<![\.\?!:])\n", " ", clean)


with open(file_clean, "w", encoding="utf-8") as f:
    f.write(clean)

print("Le fichier FALC a été nettoyé avec succès")