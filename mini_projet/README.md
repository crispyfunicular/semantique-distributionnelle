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
- garde k mots à gauche et k mots à droite, -> *à définir*
- prend au plus N exemples par mot (toujours les mêmes si on garde la même seed),
- écrit les résultats dans un fichier `occurrences.jsonl` (une occurrence par ligne).
Utilisation depuis la racine : `python3 mini_projet/scripts/script_BERT.py --targets esprit or courir porte --k 10 --n 30`

### script 3 (TBD)
Ce script pourra lire ce fichier pour calculer des vecteurs avec CamemBERT et FlauBERT sur exactement les mêmes occurrences.

