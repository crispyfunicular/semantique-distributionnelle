# Sémantique distributionnelle - mini-projet
> Catalina Alvarez Ortega & Morgane Bona-Pellissier (Master 1 pluriTAL)

## Consignes
> https://www.linguist.univ-paris-diderot.fr/~amsili/Ens/LZSET06/

**Etude de la polysémie avec des embeddings contextuels**  
A partir d'embeddings contextuels obtenus avec BERT pour un certain nombre d'occurrences de noms (ou de verbes) préalablement choisis, on définit un score de polysémie basé sur l'écart-type des similarités cosinus 2 à 2 des embeddings d'un même mot. L'objectif du projet est de déterminer à quel point ce score de polysémie correspond à la notion linguistique de polysémie. Pour cela, on pourra utiliser des visualisation 2D par réduction de dimensionalité pour confirmer les intuitions, mais on devra aussi corréler cette mesure avec une autre mesure de polysémie basée sur des ressources linguistiques ou à la rigueur sur des statistiques sur grand corpus.

## Pipeline
### `1.normalisation_corpus.py`
Normalise les fichiers du corpus pour éviter des incohérences d’écriture.

Ce script :
- remplace les apostrophes typographiques par une apostrophe simple ;
- remplace certaines graphies en `oe` par la ligature `œ` (liste contrôlée) ;
- réécrit les fichiers du dossier `mini_projet/corpus/` uniquement si un changement est nécessaire.

### `2.extraire_occurrences.py`
Extraction d'occurrences et de leur contexte (fenêtre de mots).

Ce script :
- cherche des mots cibles dans un corpus,
- garde k mots à gauche et k mots à droite,
- prend au plus N exemples par mot (toujours les mêmes si on garde la même seed),
- écrit les résultats dans un fichier `occurrences.jsonl` (une occurrence par ligne).

Utilisation depuis la racine :
`python3 mini_projet/scripts/2.extraire_occurrences.py --corpus mini_projet/corpus_complet.txt --targets esprit or courir porte --k 10 --n 30 --seed 42 --out_dir mini_projet/data`

Sorties (dans `mini_projet/data/`) :
- `occurrences.jsonl` : une occurrence par ligne
- `targets.json` : récap (corpus, k, n, seed, etc.)

### `3.encoder_embeddings.py`
Encodage des occurrences avec CamemBERT et/ou FlauBERT.

Ce script :
- lit `mini_projet/data/occurrences.jsonl`,
- calcule un vecteur par occurrence (moyenne des sous-tokens du mot cible),
- écrit les embeddings et un fichier de correspondance (métadonnées).

Utilisation depuis la racine :
`python3 mini_projet/scripts/3.encoder_embeddings.py --occurrences mini_projet/data/occurrences.jsonl --out_dir mini_projet/data --models camembert flaubert --batch_size 16 --device auto`

Sorties (dans `mini_projet/data/`) :
- `embeddings_camembert.npy` : matrice (N_occurrences, dim)
- `embeddings_flaubert.npy` : matrice (N_occurrences, dim)
- `embeddings_meta.jsonl` : lien entre `occurrence_id`, modèle et ligne dans la matrice

### `4.score_polysemie.py`
Calcul d'un score de polysémie à partir des embeddings.

Ce script :
- lit `embeddings_*.npy` et `embeddings_meta.jsonl`,
- calcule, pour chaque mot et pour chaque modèle, la dispersion des cosinus 2-à-2,
- écrit un fichier JSON de scores et un fichier JSON de classement (ranking).

Utilisation depuis la racine :
`python3 mini_projet/scripts/4.score_polysemie.py --data_dir mini_projet/data`

Sorties (dans `mini_projet/data/`) :
- `polysemy_scores.json` : scores par modèle et par mot
- `polysemy_ranking.json` : mots triés par score (par modèle)

### `5.visualiser_2d.py` (optionnel, pour l'oral)
Visualisation 2D des occurrences d'un mot cible (export PNG).

Par défaut : PCA 2D (rapide). Option : UMAP 2D (si installé).

Utilisation depuis la racine (exemple) :
`python3 mini_projet/scripts/5.visualiser_2d.py --data_dir mini_projet/data --model camembert --target esprit --method pca --out_dir mini_projet/data/viz --write_examples`

Sorties (dans `mini_projet/data/viz/`) :
- `<model>_<target>_<method>.png`
- (optionnel) `<model>_<target>_<method>_examples.txt` (quelques contextes)

## Dépendances
Pour installer les dépendances du mini-projet :
`pip install -r mini_projet/requirements.txt`

Le script 5 (visualisation) utilise `matplotlib` (déjà dans `requirements.txt`).
Pour utiliser UMAP (`--method umap`), installez en plus :
`pip install umap-learn`

