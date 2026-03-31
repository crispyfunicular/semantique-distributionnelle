# TP3 — Analyse et correction des biais coloniaux (GloVe)

Ce TP entraîne un modèle GloVe sur le corpus de Rudyard Kipling pour mettre en évidence les biais coloniaux encodés dans les représentations distributionnelles, puis les atténuer via deux stratégies complémentaires.

## Installation

```bash
pip install -r requirements.txt
python -m nltk.downloader stopwords
```

## Prérequis

Le corpus doit être **préalablement lemmatisé** (une phrase par ligne, tokens séparés par des espaces). Le fichier attendu par défaut est `corpus/kipling_lemmes.txt`, produit par `lemmatisation.py`.

---

## Utilisation

### Mode standard — analyse des biais bruts

Entraîne un modèle GloVe et évalue les analogies vectorielles définies dans `analogies.txt`.

```bash
python tp3.py corpus/kipling_lemmes.txt
```

**Sortie** : `resultats/kipling_lemmes_resultats.md`

---

### Mode CDA — Counterfactual Data Augmentation

Entraîne **deux modèles** (standard + augmenté) et produit un tableau comparatif côte à côte.

Le corpus augmenté est le corpus original doublé par une version miroir où les termes coloniaux polarisés sont inversés (`english` ↔ `native`, `white` ↔ `brown`, `sahib` ↔ `servant`, `england` ↔ `india`, `city` ↔ `jungle`).

```bash
python tp3.py corpus/kipling_lemmes.txt --cda
```

**Sortie** : `resultats/kipling_lemmes_comparatif_cda.md`

---

### Mode Hard Debiasing — débiaisage post-hoc des vecteurs

Prend le modèle standard entraîné et retire la **direction du biais colonial** de tous les vecteurs par projection orthogonale (algorithme de Bolukbasi et al., 2016).

L'axe du biais est calculé par PCA sur les vecteurs de différence des paires définitionnelles (`english`−`native`, `white`−`brown`, `sahib`−`servant`, `england`−`india`).

```bash
python tp3.py corpus/kipling_lemmes.txt --debiais
```

**Sortie** : `resultats/kipling_lemmes_comparatif_debiais.md`

---

### Mode triple — comparaison des trois stratégies

Combine les deux flags pour comparer **Standard / CDA / Débiaisé** dans un unique tableau à six colonnes.

```bash
python tp3.py corpus/kipling_lemmes.txt --cda --debiais
```

**Sortie** : `resultats/kipling_lemmes_comparatif_triple.md`

---

## Structure du projet

```
tp3/
├── tp3.py              # Script principal (pipeline + débiaisage)
├── lemmatisation.py    # Lemmatisation spaCy du corpus brut
├── nettoyage.py        # Nettoyage du texte brut
├── analogies.txt       # Liste des analogies vectorielles à tester
├── requirements.txt    # Dépendances Python
├── tp3.md              # Rapport (contexte, hypothèses, résultats)
├── corpus/
│   ├── kipling_lemmes.txt   # Corpus lemmatisé (entrée principale)
│   └── kipling_clean.txt    # Corpus nettoyé (intermédiaire)
└── resultats/
    ├── kipling_lemmes_resultats.md          # Biais bruts
    ├── kipling_lemmes_comparatif_cda.md     # Standard vs CDA
    ├── kipling_lemmes_comparatif_debiais.md # Standard vs Débiaisé
    └── kipling_lemmes_comparatif_triple.md  # Les trois côte à côte
```
