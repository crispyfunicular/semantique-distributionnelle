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

## Dossier `data/` : contenu et interprétation

Le dossier `data/` contient **tous les artefacts intermédiaires et finals** du pipeline. C’est ce dossier qu’il faut copier lorsque le pipeline a été exécuté sur une machine distante pour pouvoir ensuite analyser / visualiser localement les résultats.

### Fichiers produits

- **`occurrences.jsonl`** : *1 occurrence par ligne* (JSON). Chaque entrée contient notamment :
  - `occurrence_id` : identifiant unique de l’occurrence
  - `target` : le mot cible
  - `tokens` : la fenêtre de contexte (liste de tokens) utilisée ensuite pour l’encodage
  - (selon l’étape 2) positions/index du mot cible dans `tokens`
- **`targets.json`** : récap des paramètres d’extraction (corpus, liste de cibles, `k`, `n`, `seed`, etc.). Utile pour la traçabilité/reproductibilité.
- **`embeddings_<model>.npy`** : matrice NumPy de taille `(N_occurrences, dim)` contenant **un vecteur par occurrence** (moyenne des sous-tokens du mot cible).  
  Exemples : `embeddings_camembert.npy`, `embeddings_flaubert.npy`.
- **`embeddings_meta.jsonl`** : table de correspondance (JSONL) entre les occurrences et les lignes des matrices `.npy`.  
  Chaque ligne correspond à un couple *(occurrence, modèle)* et contient typiquement :
  - `occurrence_id` et `target`
  - `model` : nom du modèle (`camembert`, `flaubert`, …)
  - `row` : index de ligne dans `embeddings_<model>.npy` (0-indexé)
  → Pour retrouver le vecteur d’une occurrence, on filtre `embeddings_meta.jsonl` puis on prend `embeddings_<model>[row]`.
- **`polysemy_scores.json`** : scores de polysémie par **modèle** et par **mot cible**.  
  Le score correspond à une **dispersion** (écart-type) des similarités cosinus \(2\)-à-\(2\) entre les embeddings des occurrences d’un même mot : plus c’est dispersé, plus le mot est “polysémique” selon cette mesure.
- **`polysemy_ranking.json`** : classement des mots cibles **du plus au moins “polysémique”** (par modèle), basé sur `polysemy_scores.json`.

## Dépendances
Pour installer les dépendances du mini-projet :
`pip install -r mini_projet/requirements.txt`

Le script 5 (visualisation) utilise `matplotlib` (déjà dans `requirements.txt`).
Pour utiliser UMAP (`--method umap`), installez en plus :
`pip install umap-learn`

## Analyse des derniers résultats

Ces remarques portent sur les fichiers produits dans `data/` (en particulier `polysemy_scores.json` et `polysemy_ranking.json`) pour la configuration suivante : 4 cibles (`esprit`, `or`, `courir`, `porte`), \(n=30\) occurrences par cible, fenêtre \(k=10\) mots.

### Classement par modèle (score = écart-type des cosinus)

- **CamemBERT** : `courir` > `porte` > `or` > `esprit`
- **FlauBERT** : `courir` > `or` > `porte` > `esprit`

Ici, **`courir` est le mot le plus dispersé** (donc le plus “polysémique” selon cette mesure) et **`esprit` le moins dispersé** pour les deux modèles.

### Lecture des scores

- **Interprétation** : le score reporté (`cosine_std`) mesure la **dispersion des similarités cosinus** entre toutes les paires d’occurrences d’un même mot.  
  - score élevé → occurrences plus hétérogènes en embedding → hypothèse de plus grande polysémie / variation sémantique
  - score faible → occurrences plus homogènes → hypothèse de moindre polysémie / usages plus stables
- **Comparaison modèles** : dans ces résultats, **FlauBERT donne des dispersions plus fortes** (scores plus élevés) que CamemBERT pour les mêmes cibles. Cela peut refléter une séparation plus marquée des contextes (ou une variabilité plus forte) dans l’espace d’embedding du modèle.

### Points d’attention pour l’interprétation linguistique

- **`or`** : dans un corpus littéraire/général, `or` est souvent la conjonction/discours (“or, …”) plutôt que le nom (métal). Si l’objectif est d’étudier la polysémie d’un **nom**, il peut être utile de filtrer ou d’annoter les occurrences (POS) pour éviter de mélanger catégories/emplois.
- **Taille de l’échantillon** : avec \(n=30\) occurrences par cible, on obtient un signal exploitable mais encore bruité. Augmenter \(n\) et/ou diversifier les sources peut stabiliser le score et le classement.
- **Validation** : pour relier ce score à une notion linguistique de polysémie, il est recommandé de :
  - regarder quelques exemples de contextes aux extrêmes (occurrences très proches vs très éloignées),
  - compléter par une ressource/mesure externe (lexiques, inventaire de sens, statistiques, etc.),
  - utiliser la visualisation 2D (script 5) comme outil de confirmation qualitative.
