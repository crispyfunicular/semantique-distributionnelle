# TP2 - Influence de la taille du contexte
**Morgane Bona-Pellissier**, Master 1 pluriTAL  
morgane@bona-pellissier.net  

L'ensemble de ce projet est disponible sur le dépôt suivant : `https://github.com/crispyfunicular/semantique-distributionnelle/tp2`

## Consignes
https://www.linguist.univ-paris-diderot.fr/~amsili/Ens/LZSET06/

1. choix d'un corpus pas trop gros, segmentation et tokenisation ;
2. calcul d'une matrice terme-terme (demi-matrice carrée) pour une taille de fenêtre donnée ;
3. choix de 10 mots variés apparaissant dans le corpus ;
4. pour chacun des mots choisis, identification des 10 mots les plus voisins par similarité cosinus.


## Choix du corpus
### Choix des textes
Pour ce travail, nous avons choisi d'étudier, outre l'influence de la taille du contexte sur la similarité cosinus, l'éventuelle incidence de la rédaction de textes en « facile à lire et à comprendre » (FALC) sur les résultats obtenus.  
Notre choix de corpus s'est donc porté sur la *Convention relative aux droits des personnes handicapées* (CDPH), à la fois dans sa version française officielle que dans sa version « officiellement reconnue » en français FALC.

### Hypothèse
Nous partons de l'hypothèse que, si les deux textes partagent un référentiel sémantique strictement identique, ils mobilisent pourtant des stratégies syntaxiques et lexicales opposées. En effet, le texte officiel devrait se caractériser par une forte densité conceptuelle et des phrases complexes, tandis que la version FALC devrait s'appuyer sur une syntaxe courte et un vocabulaire concret et désambiguïsé. Il nous a donc semblé pertinent de comparer les résultats obtenus pour chacun de ces textes.

> La complexité ou spécificité de certaines informations nécessiterait que des experts du domaine (p. ex. : juristes,  médecins, etc.) soient associés au travail de rédaction / transcription en FALC pour permettre une clarification de l’information sans pour autant en perdre ou en diminuer le sens. (Diacquenod et Santi, 2018, p. 33)

### Segmentation et tokenisation
Nous avons défini une fonction `preparer_corpus()` prenant en argument un texte et, de façon optionnelle, un booléen `stopwords` fixé par défaut à `False` pour le filtrage des stopwords.
```python
def preparer_corpus(file:str, stopwords:bool=False) -> list:
    """Lit un fichier, le segmente en phrases, le tokenise et le lemmatise (avec spaCy)
    Filtrage avec NLTK si stopwords=True"""
```
- La tokenisation et la lemmatisation ont été effectuées à l'aide de la librairie `spaCy` :
```python
stopwords_nltk = set(stopwords.words('french'))
```
```python
if not token.is_punct and not token.is_space:
    # Lemmatisation (.lemma) et passage en minuscules (.lower())
    lemme = token.lemma_.lower()
```
- Le filtrage des stopwords (le cas échéant) a été effectué à l'aide de la librairie `NLTK`
```python
if stopwords and lemme in stopwords_nltk:
    continue
```


## Calcul des matrices

```python
def construire_matrice(corpus: list, taille_fenetre: int) -> dict:
    """Calcule une demi-matrice carrée de co-occurrences avec fenêtre glissante."""
    matrice = {}
    
    for phrase in corpus:
        # longueur de la phrase
        longueur = len(phrase)
        for i in range(longueur):
            mot_cible = phrase[i]
            
            # Création d'une entrée pour le mot cible si elle n'existe pas encore
            if mot_cible not in matrice:
                matrice[mot_cible] = {}
            
            # On conserve la valeur la plus petite (min) entre la taille de la fenêtre et la longueur de la phrase
            limite = min(i + 1 + taille_fenetre, longueur)
            
            for j in range(i + 1, limite):
                mot_voisin = phrase[j]
                
                # Création d'une entrée pour le mot voisin
                if mot_voisin not in matrice:
                    matrice[mot_voisin] = {}
                
                # Incrémentation (+ 1)
                # Si la combinaison n'existe pas --> création et mise à 0 avec .get(..., 0)
                matrice[mot_cible][mot_voisin] = matrice[mot_cible].get(mot_voisin, 0) + 1
                matrice[mot_voisin][mot_cible] = matrice[mot_voisin].get(mot_cible, 0) + 1
                
    return matrice
```

### Choix des fenêtres

```python
# MATRICES CDPH_OFFICIEL
## Avec stopwords - fenêtre 2
mat_off_w2 = construire_matrice(corpus_officiel, taille_fenetre=2)

## Avec stopwords - fenêtre 15
mat_off_w15 = construire_matrice(corpus_officiel, taille_fenetre=15)

## Avec stopwords - fenêtre 50
mat_off_w15 = construire_matrice(corpus_officiel, taille_fenetre=50)
```

### Choix des mots cible
Nous avons choisi des mots cibles de façon à couvrir l'ensemble des dimensions sémantiques du corpus :
- acteurs clé : personne, enfant, femme, handicapé ;
- enjeux et notions au cœur de la Convention : dignité, accessibilité, autonomie ;
- concepts juridiques : droit, discrimination, liberté.

Nous partons de l'hypothèse que cette dernière catégorie en particulier, celle des concepts juridiques, devrait donner lieu à de fortes variations entre le corpus « officiel » et le corpus « FALC », car nous supposons que ce sont précisément ces notions juridiques abstraites qui sont vulgarisées pour le grand public dans les versions « faciles à lire et à comprendre ».

```python
mots_cible = ["droit", "personne", "handicapé", "enfant", "femme", "discrimination", "liberté", "dignité", "accessibilité", "autonomie"]
```


## Discussion des résultats




## Bibliographie
> Diacquenod, C. et F. Santi (2018). "La mise en oeuvre du langage facile à lire et à comprendre (FALC) : enjeux, défis et perspectives", Revue suisse de pédagogie spécialisée, 2/2018

> Fondation Internationale de la Recherche Appliquée sur le Handicap (FIRAH). Version facile à lire de la Convention relative aux droits des personnes handicapées. https://www.firah.org/la-convention-relative-aux-droits-des-personnes-handicapees.html

> Haut-Commissariat des Nations Unies aux droits de l'homme (2006). Convention relative aux droits des personnes handicapées https://www.ohchr.org/fr/instruments-mechanisms/instruments/convention-rights-persons-disabilities
