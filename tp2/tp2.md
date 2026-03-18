# TP2 - Influence de la taille du contexte
**Morgane Bona-Pellissier**, Master 1 pluriTAL  
morgane@bona-pellissier.net  

L’ensemble de ce projet est disponible sur le dépôt suivant : `https://github.com/crispyfunicular/semantique-distributionnelle/tp2`

## Choix du corpus
### Choix des textes
Pour ce travail, nous avons choisi d’étudier, outre l’influence de la taille du contexte sur la similarité cosinus, l’éventuelle incidence de la rédaction de textes en « facile à lire et à comprendre » (FALC) sur les résultats obtenus.  
Nous avons donc élaboré un corpus parallèle constitué des quelques textes institutionnels disposant d’une version en FALC, en l’occurrence :
- la Charte des droits fondamentaux de l’Union européenne (CDFUE) ;
- la Convention internationale sur les Droits des personnes handicapées (CDPH) ;
- la Circulaire du 10-7-2024 relative aux droits des étudiants en situation de handicap ou avec un trouble de santé invalidant.

L’ensemble des corpus « officiels », d’une part, et l’ensemble des corpus « FALC », d’autre part, ont été fusionnés en deux corpus `officiel.txt` et `FALC.txt`, respectivement.  
S’il est vrai que ce corpus peut sembler peu étoffé, nous avons fait le choix, compte tenu de la difficulté à trouver des documents institutionnels « traduits » en FALC, de privilégier la qualité d’un corpus strictement parallèle à la quantité d’un corpus comparable plus vaste mais thématiquement hétérogène. 

### Hypothèse
Nous partons de l’hypothèse que, si les deux corpus partagent un référentiel sémantique strictement identique, ils mobilisent pourtant des stratégies syntaxiques et lexicales opposées. En effet, le corpus officiel devrait se caractériser par une forte densité conceptuelle et des phrases complexes, tandis que la version FALC devrait s’appuyer sur une syntaxe courte et un vocabulaire concret et non ambigu.

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


## Structure de la pipeline
> Voir `tp2.py`
### Segmentation, tokenisation et filtrage des mots vides
Nous avons défini une fonction `preparer_corpus()` prenant en argument un texte et, de façon optionnelle, un booléen `stopwords` fixé par défaut à `False` pour le filtrage des stopwords. Afin de privilégier l’émergence de relations sémantiques pertinentes et de réduire le bruit statistique, l’analyse finale présentée dans ce rapport se concentre exclusivement sur les matrices construites après le filtrage des mots vides (*stopwords*)

```python
def preparer_corpus(file:str, stopwords:bool=False) -> list:
    """Lit un fichier, le segmente en phrases, le tokenise et le lemmatise (avec spaCy)
    Filtrage avec NLTK si stopwords=True"""
```
La tokenisation et la lemmatisation ont été effectuées à l’aide de la librairie `spaCy` (modèle « large » `lg` pour éviter les erreurs de lemmatisation du type *« spécialemer ») :
```python
nlp = spacy.load("fr_core_news_lg")
stopwords_nltk = set(stopwords.words('french'))
```
```python
if not token.is_punct and not token.is_space:
    # Lemmatisation (.lemma) et passage en minuscules (.lower())
    lemme = token.lemma_.lower()
```
Le filtrage des stopwords (le cas échéant) a été effectué à l’aide de la librairie `NLTK`
```python
if stopwords and lemme in stopwords_nltk:
    continue
```

### Choix des fenêtres
Nous avons retenu trois tailles de fenêtres distinctes pour observer l’évolution des voisinages :
- Fenêtre étroite (`f3`) : pour capter la syntaxe immédiate (collocations, relations Sujet-Verbe-Objet).
- Fenêtre moyenne (`f10`) : pour capter l’échelle d’une phrase simple ou d’une proposition.
- Fenêtre large (`f25`) : pour capter l’échelle d’une phrase complexe ou d’un réseau thématique élargi.

Nous nous attendons à ce que cette augmentation progressive de la largeur de la fenêtre fasse apparaître un effet de plateau sur le corpus FALC. En raison de la syntaxe courte caractéristique de ces textes, les résultats devraient cesser d'évoluer au-delà d’une certaine largeur de fenêtre, probablement `f10`.

### Choix des mots cible
Nous avons choisi des mots cibles de façon à couvrir l’ensemble des domaines thématiques  du corpus :
- acteurs clé : personne, enfant, femme, handicapé ;
- enjeux et notions thématiques : dignité, accessibilité, autonomie ;
- concepts juridiques : droit, discrimination, liberté.
- Mots du quotidien : argent, chose.

Nous partons de l’hypothèse que la catégorie des concepts juridiques devrait donner lieu à de fortes variations entre le corpus officiel et le corpus FALC, car nous supposons que ce sont précisément ces notions juridiques abstraites qui sont vulgarisées pour le grand public dans les versions « faciles à lire et à comprendre ». Afin de mettre spécifiquement l'accent sur la démarche de simplification dont font l'objet les textes en français facile, nous avons isolé deux termes présents dans le corpus FALC mais absents du corpus officiel, à savoir « argent » et « chose ».

```python
mots_cible = ["droit", "personne", "handicapé", "enfant", "femme", "discrimination", "liberté", "dignité", "accessibilité", "autonomie", "argent", "chose"]
```


## Discussion des résultats
> Voir `resultats.md`

### Mots absents de l’un des corpus : abstrait vs. concret
#### Mots absents du corpus officiel : « argent » et « chose »

Les mots « argent » et « chose », absents du corpus officiel, appartiennent au langage courant et désignent des réalités *concrètes et pragmatiques* du quotidien, dépourvues de définition technique propre au langage de spécialité juridique. Leur présence exclusive dans le corpus FALC confirme la stratégie de simplification consistant à substituer aux concepts abstraits des termes accessibles et compréhensibles par toustes. D’ailleurs, en `f3`, « argent » est associé à « situation », « vie » et « handicap », tandis qu’en `f10`, il apparaît dans un réseau financier concret (« bourse », « bcs », « mérite », « somme »), ce qui témoigne d’un ancrage dans la réalité matérielle du lecteur.

#### Mots du champ philosophique : « dignité » et « autonomie »

À l’inverse, la différence de traitement des mots « dignité » et « autonomie » entre les deux corpus est très contrastée. Dans le corpus officiel, « dignité » est associée en `f3` à un vocabulaire juridique technique (« inhérent », « intrinsèque »), tandis que, dans le corpus FALC, elle coïncide avec des termes concrets (« humain », « esclave »). De même, « autonomie » gravite autour de « commission », « indépendance » et « dignité » dans le corpus officiel, quand le FALC l’ancre dans les domaines médical et administratif (« médecin », « cdaph », « contact »), qui renvoient là encore à des réalités tangibles de la vie réelle dont le public visé aura probablement déjà fait l'expérience. Ces résultats viennent confirmer le fait que ce sont précisément les noms abstraits qui donnent lieu de manière quasi systématique à des reformulations pour faciliter la compréhension du lectorat (Eshkol-Taravella et Grabar, 2018).

### Incidence de la taille de la fenêtre
#### Fenêtre étroite (`f3`)
- **Collocations juridiques dans le corpus officiel**

Avec une fenêtre étroite, la similarité cosinus est calculée sur les voisins immédiats (trois mots), ce qui permet de capturer les collocations et les expressions figées propres au français juridique. Ainsi, pour « discrimination », on retrouve « fonder » et « approprier » (pour l’expression « mesures appropriées fondées sur... »), tandis que « dignité » est associée à « inhérent » et « intrinsèque », autant de collocations caractéristiques des textes institutionnels. De la même manière, le mot « liberté » s'associe avec « fondamental », « droit » et « homme », qui font directement référence aux « droits fondamentaux de l'homme », garant des droits et *libertés* (précisément) de tout individu. Ces résultats montrent donc que la fenêtre étroite est sensible aux conventions lexicales et syntaxiques propres aux langages de spécialité, notamment au jargon institutionnel.

- **Syntaxe directe du FALC : actions et réalités concrètes**

Dans le corpus FALC, la même fenêtre `f3` permet de mettre en évidence la structure syntaxique simplifiée « sujet-verbe-objet » (S-V-O) caractéristique des textes en français facile et, ainsi, de faire ressortir la priorité donnée par ces textes à l’action concrète. Par exemple, là où la « dignité » officielle s’entoure d'adjectifs conceptuels (« inhérent », « intrinsèque »), la fenêtre `f3` du FALC l’associe immédiatement à des verbes d’action et des réalités tangibles : « respecter », « humain », « esclave ». De même, le concept abstrait d’« autonomie » est directement traduit en démarches pratiques avec les voisins « contact », « diriger » et « médecin ». Ce résultat met en évidence le fait que, là où le texte officiel encadre le mot par des formules juridiques, le FALC l’associe à des actions concrètes et des réalités directement perceptibles.

#### Fenêtre moyenne (`f10`)
- **Émergence du cadre normatif dans le corpus officiel**

La fenêtre de dix mots permet de dépasser les collocations immédiates et de capturer le cadre normatif dans lequel s’insèrent les concepts. Ainsi, « droit » gagne « reconnaître » et « liberté » et « enfant » à « égalité ». Pour le mot « handicapé », on voit apparaître une nomenclature précise de la population concernée : « enfant », « travailleur », « personne ».

- **Ancrage du FALC dans la vie quotidienne**

À la même échelle de dix mots, le corpus FALC fait apparaître un réseau sémantique ancré dans le quotidien. Le concept d’« autonomie » renvoie aux professions médicales et administratives « de terrain » et aux démarches liées : « médecin », « cdaph », « choisir », « rencontre ». Ainsi, la méthode de simplification ne modifie pas seulement la forme mais recentre également le champ sémantique sur les expériences concrètes de la vie réelle du lectorat.

#### Fenêtre large (`f25`)

L’observation des variations entre les fenêtres moyenne (`f10`) et large (`f25`) valide mathématiquement l’hypothèse structurelle du FALC, à savoir la règle des phrases courtes (règle 14).

- **Effet de plateau (FALC)**

Pour de nombreux termes, la liste des co-occurrences reste strictement identique ou quasi identique entre `f10` et `f25`. C’est le cas pour « autonomie » (dont les cinq voisins « médecin », « cdaph », « choisir », « commission » et « rencontre » sont strictement identiques), pour « accessibilité », pour « argent » (où seul un léger réordonnement est observable) et pour « liberté » (mêmes termes avec une substitution marginale). Il semblerait donc que l’algorithme se heurte aux limites physiques de la phrase courte car le fait d'élargir la fenêtre sémantique de 10 à 25 mots n’apporte plus d’information nouvelle. Ce phénomène confirme l’hypothèse avancée plus haut : la fenêtre glissante de 25 mots dépasse les frontières de la phrase dans le corpus FALC, et le voisinage sémantique se trouve borné par la syntaxe.

| Mot cible     | `f10` (FALC)                                     | `f25` (FALC)                                     | Δ        |
|:--------------|:-------------------------------------------------|:-------------------------------------------------|:---------|
| autonomie     | médecin, cdaph, choisir, commission, rencontre   | médecin, cdaph, choisir, commission, rencontre   | = 0/5    |
| accessibilité | autour, cvec, améliorer, commun, culturel        | autour, cvec, améliorer, campus, culturel        | ≈ 1/5    |
| argent        | bcs, bourse, mérite, faire, somme                | bcs, bourse, mérite, somme, récompenser          | ≈ 1/5    |
| liberté       | fondamental, droit, art, souhaiter, union        | fondamental, droit, européen, union, art         | ≈ 1/5    |

- **Expansion thématique du corpus officiel**

À l’opposé, la complexité des phrases officielles empêche toute stagnation. La fenêtre de 25 mots a l’espace nécessaire pour relier le concept de départ à ses implications juridiques et capturer des réseaux thématiques plus larges. le terme « accessibilité », limité en `f3` aux acteurs de terrain (« étudiant », « établissement »), voit apparaître en `f25` la source juridique encadrant ce droit, à savoir la « directive ».

| Mot cible     | `f10` (Officiel)                                 | `f25` (Officiel)                                  |
|:--------------|:-------------------------------------------------|:--------------------------------------------------|
| handicapé     | enfant, personne, travailleur, handicaper, être  | personne, enfant, mesure, handicaper, autre       |
| enfant        | handicapé, droit, personne, tout, égalité        | handicapé, droit, personne, égalité, famille      |
| femme         | fille, violence, autre, tout, handicaper         | fille, souvent, courir, violence, politique       |

L’élargissement à `f25` fait glisser le champ lexical des *acteurs immédiats* en `f10` aux *enjeux sociétaux et institutionnels* en `f25`. Cette évolution illustre la capacité des longues phrases juridiques à relier la règle de droit à ses implications lointaines au sein d’une même unité syntaxique.

## Conclusion

L’analyse sémantique comparative entre les textes officiels et leur traduction en FALC a permis de montrer que, si l'ouverture progressive de la fenêtre a bien une incidence sur les résultats obtenus, celle-ci varie fortement selon le type de texte étudié. D'un côté, c'est la fenêtre étroite (`f3`) qui s’est avérée optimale pour le corpus FALC, dont elle a capturé l'essence grâce à la syntaxe courte « S-V-O » caractéristique de ces textes, là où elle reste « piégée » dans les collocations figées du corpus officiel. À l’inverse, une fenêtre bien plus large (`f25`) s'est révélée nécessaire pour embrasser la macro-syntaxe et les enjeux sociétaux des textes institutionnels officiels, tandis qu'elle s'est heurtée à un « effet plafond » sur le FALC. Qui plus est, cette étude illustre mathématiquement la démarche de simplification du FALC, qui ramène l’information essentielle dans un périmètre syntaxique restreint.

Ces résultats corroborent tout à fait ceux de Hill et al. (2013), qui ont montré que « les fenêtre les plus petites fonctionn[ai]ent mieux pour mesurer la similarité concrète des noms, alors que les fenêtres plus larges fonctionn[ai]ent mieux pour les noms abstraits » (notre traduction).

Cette étude présente néanmoins certaines limites qu'il convient de souligner. Les résultats discutés dans ce rapport reposent sur une sélection d'extraits choisis pour leur capacité à illustrer notre hypothèse initiale, ce qui introduit un biais de confirmation certain. D'autres termes étudiés n'ont pas révélé de variations aussi nettes ou exploitables face aux changements de fenêtres.

## Bibliographie
> Association métropolitaine et départementale des parents et amis de personnes handicapées mentales (Adapei 69) (2024). https://www.adapei69.fr/sites/default/files/2024-04/Charte%20Droits%20UE_%20FALC_Adapei%2069.pdf 

> Eshkol-Taravella, I. et N. Grabar (2018). « La reformulation comme un moyen de clarification des noms abstraits ». Les catégories abstraites et la référence, 6, ÉPURE-Éditions et Presses universitaires de Reims. halshs-01968306

> Fondation Internationale de la Recherche Appliquée sur le Handicap (FIRAH). « Version facile à lire de la Convention relative aux droits des personnes handicapées ». https://www.firah.org/la-convention-relative-aux-droits-des-personnes-handicapees.html

> Haut-Commissariat des Nations Unies aux droits de l’homme (2006). « Convention relative aux droits des personnes handicapées ». https://www.ohchr.org/fr/instruments-mechanisms/instruments/convention-rights-persons-disabilities

> Hill, F., D. Kiela, et A. Korhonen (2013). Concreteness and Corpora: A Theoretical and Practical Analysis. *Proceedings of ACL 2013, Workshop onCognitive Modelling and Computational Linguistics*, Sofia, Bulgarie.

> Inclusion Europe (2009). « Règles européennes pour une information facile à lire et à comprendre ». https://www.inclusion-europe.eu/easy-to-read-standards-guidelines/ 

> Ministère de l’Enseignement supérieur et de la Recherche (2024). Circulaire du 10-7-2024 relative aux droits des étudiants en situation de handicap ou avec un trouble de santé invalidant. Bulletin officiel de l’Enseignement supérieur et de la Recherche. https://www.enseignementsup-recherche.gouv.fr/fr/bo/2024/Hebdo28/ESRS2418046C

> Parlement européen. Charte des droits fondamentaux de l’Union européenne. https://www.europarl.europa.eu/charter/pdf/text_fr.pdf