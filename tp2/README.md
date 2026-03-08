# TP2 - Influence de la taille du contexte
**Morgane Bona-Pellissier**, Master 1 pluriTAL  
morgane@bona-pellissier.net  

L’ensemble de ce projet est disponible sur le dépôt suivant : `https://github.com/crispyfunicular/semantique-distributionnelle/tp2`

## Consignes
https://www.linguist.univ-paris-diderot.fr/~amsili/Ens/LZSET06/

1. choix d’un corpus pas trop gros, segmentation et tokenisation ;
2. calcul d’une matrice terme-terme (demi-matrice carrée) pour une taille de fenêtre donnée ;
3. choix de 10 mots variés apparaissant dans le corpus ;
4. pour chacun des mots choisis, identification des 10 mots les plus voisins par similarité cosinus.


## Choix du corpus
### Choix des textes
Pour ce travail, nous avons choisi d’étudier, outre l’influence de la taille du contexte sur la similarité cosinus, l’éventuelle incidence de la rédaction de textes en « facile à lire et à comprendre » (FALC) sur les résultats obtenus.  
Notre choix de corpus s’est donc porté sur la *Convention relative aux droits des personnes handicapées* (CDPH), à la fois dans sa version française officielle que dans sa version « officiellement reconnue » en français FALC.

### Hypothèse
Nous partons de l’hypothèse que, si les deux textes partagent un référentiel sémantique strictement identique, ils mobilisent pourtant des stratégies syntaxiques et lexicales opposées. En effet, le texte officiel devrait se caractériser par une forte densité conceptuelle et des phrases complexes, tandis que la version FALC devrait s’appuyer sur une syntaxe courte et un vocabulaire concret et désambiguïsé.

Parmi les « Règles européennes pour une information facile à lire et à comprendre » (Inclusion Europe, 2009), les recommandations suivantes nous intéressent particulièrement pour ce travail :
```text
6.  Utilisez des mots faciles à comprendre  
    c’est-à-dire des mots que les gens connaissent bien.
7.  N’utilisez pas de mots difficiles.
14. Faites toujours des phrases courtes.
17. Utilisez des phrases actives plutôt que des phrases passives
    quand vous le pouvez
18. Placez toujours vos informations
    dans un ordre facile à comprendre et facile à suivre.
```
Il nous a par conséquent semblé pertinent de comparer les résultats obtenus pour chacun de ces textes.


### Segmentation et tokenisation
Nous avons défini une fonction `preparer_corpus()` prenant en argument un texte et, de façon optionnelle, un booléen `stopwords` fixé par défaut à `False` pour le filtrage des stopwords.
```python
def preparer_corpus(file:str, stopwords:bool=False) -> list:
    """Lit un fichier, le segmente en phrases, le tokenise et le lemmatise (avec spaCy)
    Filtrage avec NLTK si stopwords=True"""
```
- La tokenisation et la lemmatisation ont été effectuées à l’aide de la librairie `spaCy` :
```python
stopwords_nltk = set(stopwords.words('french'))
```
```python
if not token.is_punct and not token.is_space:
    # Lemmatisation (.lemma) et passage en minuscules (.lower())
    lemme = token.lemma_.lower()
```
- Le filtrage des stopwords (le cas échéant) a été effectué à l’aide de la librairie `NLTK`
```python
if stopwords and lemme in stopwords_nltk:
    continue
```

### Filtrage des mots vides (stopwords)
Afin de privilégier l’émergence de relations sémantiques pertinentes et de réduire le bruit statistique, l’analyse finale présentée dans ce rapport se concentre exclusivement sur les matrices construites après le filtrage des mots vides (stopwords)

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
Nous avons choisi des mots cibles de façon à couvrir l’ensemble des dimensions sémantiques du corpus :
- acteurs clé : personne, enfant, femme, handicapé ;
- enjeux et notions au cœur de la Convention : dignité, accessibilité, autonomie ;
- concepts juridiques : droit, discrimination, liberté.

Nous partons de l’hypothèse que cette dernière catégorie en particulier, celle des concepts juridiques, devrait donner lieu à de fortes variations entre le corpus « officiel » et le corpus « FALC », car nous supposons que ce sont précisément ces notions juridiques abstraites qui sont vulgarisées pour le grand public dans les versions « faciles à lire et à comprendre ».

```python
mots_cible = ["droit", "personne", "handicapé", "enfant", "femme", "discrimination", "liberté", "dignité", "accessibilité", "autonomie"]
```


## Discussion des résultats
> Voir `resultats_analyse.md`

### Mots absents de l’un des corpus : abstrait vs. concret
#### Mots absents du corpus officiel : "argent" et "chose"

Les mots absents du corpus officiel, et donc présents dans le corpus FALC uniquement, appartiennent au langage courant et désignent des réalités matérielles *concrètes* du quotidien, dépourvues de définition technique propre au langage de spécialité (en l’espèce, le droit).

#### Mots absents du corpus FALC : "liberté", "dignité" et "autonomie"

Les mots absents du corpus FALC, et donc présents dans le corpus officiel uniquement, recouvrent des concepts philosophiques *abstraits* pouvant être difficiles à appréhender par l’homme de la rue. En effet, ce sont précisément les noms abstraits qui donnent lieu de manière quasi systématique à des reformulations pour faciliter la compréhension du lectorat (Eshkol-Taravella et Grabar, 2018).

### Incidence de la taille de la fenêtre
#### Fenêtre étroite (`f2`)
- **Expressions figées et langage de spécialité (jargon)**

Avec une fenêtre étroite, la similarité cosinus est calculée uniquement sur les voisins immédiats. Ce paramètre permet donc de capturer les collocations et les expressions figées, notamment celles propres au français juridique. C’est ainsi que l’on retrouve, pour "handicapé", les mots "intérêt" et "supérieur", pour le concept juridique d’"intérêt supérieur". Il est intéressant de noter qu’à l’ordinaire (et c’est effectivement le cas de notre corpus officiel), l’expression "intérêt supérieur" est *in extenso* "intérêt supérieur de l’enfant". Or, ici, ce n’est pas avec "enfant" (pourtant dans la liste des mots étudiés) mais avec "handicapé" que l’expression apparaît. Cela s’explique par un effet de "dilution de la représentation" mathématique : le mot "handicapé" croise l’expression "intérêt supérieur" dans un contexte très restreint. En revanche, le mot "enfant" est si central dans la Convention qu’il apparaît dans une multitude de contextes variés. En raison de son omniprésence, son vecteur de voisinages devient gigantesque et le poids de l’expression "intérêt supérieur" s’y retrouve totalement dilué et ne figure pas parmi les plus fortes similarités.

- **Considérants du corpus officiel**

Pour certains mots étudiés, et pour le corpus officiel uniquement, la fenêtre `f2` fait apparaître des verbes au participe présent ou passé qui introduisent chacun des considérants, formules répétitives qui précèdent le texte de la plupart des conventions internationales : "convaincus (que)", "estimant (que)"... Leur répétition tout au long des considérants crée un voisinage fort avec les mots clés de la convention. Une fenêtre étroite permet ainsi de mettre en évidence non seulement le jargon institutionnel, mais aussi la syntaxe figée propre aux textes institutionnels.

- **Syntaxe : subordonnées vs. S-V-O strict**

Parmi les mots mis en évidence par la fenêtre de deux mots pour le corpus FALC (uniquement), figurent des verbes d’action et des adjectifs épithètes directement associés au mot cible. Ainsi, le mot "argent" est associé aux mots "emprunter", "garder" et "contrôler", verbes dont il est l’objet direct et le dépendant, et le mot "handicapé" est associé aux mots "marier" et "aveugle", dont il est le gouverneur direct du point de vue syntaxique. Ce résultat met en évidence le fait que, là où le texte officiel sépare le sujet de l’action par des subordonnées complexes, le FALC utilise une structure sujet-verbe-objet (SVO) stricte, conformément aux règles 17 et 18 ci-dessus.

#### Fenêtre moyenne (`f15`)
- **Verbes d’obligation étatique**

Pour le corpus officiel, la fenêtre de quinze mots associe les mots "handicapé", "personne" et "enfant" à des verbes d’obligation, tels que "engager", "prévenir", "garantir", "promouvoir" et "reconnaître". Cette fenêtre est donc suffisamment large pour mettre en évidence les débiteurs de l’obligation édictée dans le texte, à savoir l’État.

- **Ancrage du corpus FALC dans la vie quotidienne**

À la même échelle de 15 mots, le texte FALC ne parle pas du tout d’obligations d’État, mais de la vraie vie. En effet, les voisins de "handicapé" et "enfant" sont, entre autres, "élever", "traiter" "parent", "famille", "traiter", "égal". Ainsi, là où le texte officiel de la Convention encadre la personne par le droit, le FALC l’encadre par ses relations sociales directes. Le sujet juridique désincarné devient un individu doté de *parents* et d’une *famille*, qui doit être *élevé* et *traité* de manière *égale*. La fenêtre de quinze mots montre donc que la méthode de simplification ne modifie pas seulement la forme, elle recentre le champ sémantique sur la sphère intime et quotidienne du lecteur.

#### Fenêtre large (`f50`)
- **Effet plafond du corpus FALC**

On remarque qu’entre les fenêtres `f15` et `f50`, les résultats pour le corpus FALC demeurent strictement inchangés, ce qui confirme l’usage de phrases courtes dans les formulations FALC, conformément aux recommandations mentionnées plus haut. En effet, la règle d’accessibilité imposant de limiter la longueur des phrases, la fenêtre glissante de 50 mots se heurte aux frontières de la phrase. Le voisinage sémantique se trouve ainsi borné par la syntaxe.

- **Expansion thématique du corpus officiel**

À l’inverse, les phrases du texte officiel de la Convention étant particulièrement longues et complexes, structurées parfois en listes à puce, la fenêtre de 50 mots a l’espace nécessaire pour capturer des réseaux thématiques beaucoup plus larges. Ainsi, "l’angle de vision" du contexte de chaque mot s’élargit et capture des thèmes plus vastes.

| Mot cible     | `f15`                                                 | `f50`                                                     |
|:--------------|:------------------------------------------------------|:----------------------------------------------------------|
| accessibilité |minimal, elaborer, transport, installation, ouvrir     |transport, identification, voirie, école, électronique     |
| enfant        | handicapé, droit, famille, tout, garantir             | handicapé, âge, naissance, famille, opinion               |
| dignité       | respect, jouissance, pleine, diversité, promouvoir    | significatif, profond, désavantage, contribuer, remédier  |

Comme l’illustre ce tableau, l’élargissement à `f50` fait glisser le champ lexical de l’*action réglementaire immédiate* en `f15` (les verbes "élaborer", "garantir", "promouvoir") aux *domaines d’application concrets* et aux *enjeux sociétaux* en `f50` ("voirie", "école", "naissance", "désavantage"). Cette évolution prouve la capacité des longues phrases juridiques à lier la règle de droit à ses implications lointaines au sein d’une même unité syntaxique.

## Conclusion

L’analyse sémantique comparative entre la version officielle de la Convention et sa traduction en FALC démontre que l’architecture syntaxique dicte la pertinence du paramétrage algorithmique. En effet, l’efficacité des fenêtres glissantes s’est révélée diamétralement opposée selon le corpus étudié.

### Efficacité de la fenêtre étroite (`f2`) pour le FALC vs. limites de l’officiel
Dans le corpus FALC, la fenêtre `f2` s’avère extrêmement performante pour capturer le cœur sémantique des concepts. En raison de sa structure syntaxique simplifiée et directe (sujet-verbe-objet), l’environnement immédiat des mots révèle directement l’action concrète ou la définition pédagogique (par exemple, "argent" directement associé à "emprunter" et "garder"). À l’inverse, pour le corpus officiel, cette même fenêtre `f2` s’avère sémantiquement pauvre : elle reste "piégée" dans la rhétorique institutionnelle, capturant quasi-exclusivement des collocations juridiques figées (comme "intérêt supérieur") ou des formules de préambule ("estimant", "convaincus"), sans parvenir à atteindre l’action ou le sens profond du droit édicté.

### Efficacité de la fenêtre large (`f50`) pour l’officiel vs. effet plafond du FALC
À l’opposé, la fenêtre large `f50` révèle toute sa pertinence sur le texte officiel. C’est à cette échelle macro-syntaxique que l’algorithme parvient à embrasser la complexité des longues phrases juridiques et des listes à puces. Elle permet de franchir le mur du jargon réglementaire pour révéler les enjeux sociétaux et les réalités systémiques du texte (reliant par exemple "dignité" au "désavantage", ou "accessibilité" à l’"école" et la "voirie"). Appliquée au corpus FALC, cette même fenêtre `f50` est en revanche inutile : elle se heurte à un "effet plafond" algorithmique imposé par la règle des phrases courtes. L’information stagne dès `f15`, la fenêtre de 50 mots dépassant largement les frontières physiques de la proposition.

En définitive, cette étude prouve mathématiquement le succès de la démarche de simplification du FALC. En ramenant l’information essentielle dans un périmètre syntaxique extrêmement restreint (capturable dès `f2`), le FALC supprime la charge cognitive nécessaire pour lier des concepts éloignés, une charge qui caractérise le corpus officiel et qui requiert, algorithmiquement comme humainement, une fenêtre de lecture beaucoup plus large (`f50`).


## Bibliographie
> Eshkol-Taravella, I. et N. Grabar (2018). « La reformulation comme un moyen de clarification des noms abstraits ». Les catégories abstraites et la référence, 6, ÉPURE-Éditions et Presses universitaires de Reims. halshs-01968306

> Fondation Internationale de la Recherche Appliquée sur le Handicap (FIRAH). « Version facile à lire de la Convention relative aux droits des personnes handicapées ». https://www.firah.org/la-convention-relative-aux-droits-des-personnes-handicapees.html

> Haut-Commissariat des Nations Unies aux droits de l’homme (2006). « Convention relative aux droits des personnes handicapées ». https://www.ohchr.org/fr/instruments-mechanisms/instruments/convention-rights-persons-disabilities

> Inclusion Europe (2009). « Règles européennes pour une information facile à lire et à comprendre ». https://www.inclusion-europe.eu/easy-to-read-standards-guidelines/ 
