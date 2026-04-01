# Résultats GloVe — Synthèse comparative (Kipling + Conrad)

**Corpus** : `corpus_lemmes.txt` — 1 386 212 tokens (Kipling + Conrad)  
**Modèle** : GloVe via *mittens*, fenêtre=10, dimensions=100, max_iter=100  
**Filtres** : stopwords NLTK anglais, hapax (min_freq=5)  
**Deux runs** indépendants (local / machine distante) pour évaluer la stabilité.  
Les résultats marqués ✅ sont stables entre les deux runs.

---

## 1. Hiérarchie coloniale — Inde (Kipling)

### `sahib - english + native` ✅
| Run local | Run distant |
|---|---|
| yunkum, lurgan, yankling, petersen, dipty | dipty, yankling, colonel, lone |

> Le modèle associe à l'équivalent indigène du *sahib* des termes issus du vocabulaire militaro-administratif indien (*dipty* = député indigène, *subadar*, *lurgan* = personnage de *Kim*). Le réseau sémantique de `native` gravite donc autour des intermédiaires de la colonisation, pas d'une humanité autonome.

### `servant - native + english` ✅
| Run local | Run distant |
|---|---|
| fluent, thy, slave, weakling | slave, fluent, thy |

> `slave` apparaît dans les deux runs comme proche sémantique du « serviteur indigène vu depuis la position anglaise » — glissement lexical révélateur.

### `child - native + english` ✅
| Run local | Run distant |
|---|---|
| woman, talk, laugh, little, girl | woman, little, mother, girl, talk |

> L'enfant anglais est reconduit vers un univers de féminité et de domesticité — pas vers l'autorité. Le corpus réduit les deux catégories (enfant, natif) à un même registre de dépendance.

### `master - english + native`
| Run local | Run distant |
|---|---|
| dowd, dancing, sign, order | dancing, jungle, station, dowd |

> Résultats peu cohérents entre les deux runs. `jungle` en position 2 (run distant) suggère que le « maître indigène » est ancré dans un espace sauvage. Faible score (~0.52), à interpréter avec prudence.

---

## 2. Loi, ordre, empire (Kipling)

### `law - english + india` / `law - white + brown` ✅
| Analogie | Run local | Run distant |
|---|---|---|
| `law - english + india` | jungle, courts, barrister, baloo | jungle, viceroy, baloo, recite, courts |
| `law - white + brown` | baloo, barrister, recite | baloo, barrister, recite, jungle |

> Convergence forte : la loi applicable aux non-Blancs renvoie à la *loi de la jungle* (`baloo`, `jungle`) et aux cadres juridiques coloniaux (`barrister`, `courts`, `viceroy`). L'opposition Loi/Jungle comme métaphore de la frontière civilisationnelle est encodée dans les vecteurs.

### `empire - english + india` ✅
| Run local | Run distant |
|---|---|
| date, **rubber**, indian, east | **rubber**, appreciatively, indian, viceroy |

> `rubber` (caoutchouc) apparaît dans les **deux** runs comme voisin d'`empire`. Signal clair de la contamination sémantique par Conrad (*Heart of Darkness*) : l'empire renvoie autant au pillage congolais qu'à l'administration indienne.

### `rule - english + native`
| Run local | Run distant |
|---|---|
| drab, administer, states, englishmen | drab, states, prove |

> `administer` et `englishmen` en run local suggèrent que la règle exercée sur les natifs est perçue comme une fonction administrative anglaise. `drab` (terme de couleur pâle / terme argotique militaire) revient systématiquement — probable artefact du vocabulaire militaire kipling-ien.

---

## 3. Espaces coloniaux

### `city - english + jungle` ✅
| Run local | Run distant |
|---|---|
| night, dreadful, rock, live, mourner | night, rock, kill, mourner, bagheera |

> La « ville des natifs » renvoie à la nuit, au dreadful, à la mort (*mourner*, *kill*). `bagheera` (la panthère de *Jungle Book*) confirme que l'espace jungle/natif est animalisé et menaçant dans les représentations distributionnelles.

### `sea - jungle + river` ✅
| Run local | Run distant |
|---|---|
| ship, steamer, boat, travel, water | boat, shore, ship, water, steamer |

> Analogie introduite pour le corpus Conrad. La cohérence est remarquable : la rivière congolaise est sémantiquement proche de la mer (navigation, embarcation). Montre que Conrad ancre le fleuve dans un univers maritime.

---

## 4. Lumière, ténèbres, humanité (Conrad)

### `light - white + black` ✅
| Run local | Run distant |
|---|---|
| dark, glow, sun, lamp, fire | dark, **shadow**, **darkness**, lamp, star |

> En run distant : `darkness` et `shadow` apparaissent directement comme voisins de « la lumière des Noirs » — la blackness est encodée dans le champ sémantique des ténèbres. Signal de biais fort, cohérent avec *Heart of Darkness*.

### `human - white + black` ✅
| Run local | Run distant |
|---|---|
| divine, nature, bunker, misty | divine, poignant, nature, outline, earth |

> `divine` premier résultat dans les deux runs : l'humanité associée au monde noir est reconduite vers le registre du sublime/sacré, pas vers la socialité ordinaire. Biais de déshumanisation indirect.

### `soul - white + black` ✅
| Run local | Run distant |
|---|---|
| body, yearning, **patronize**, torment | **patronize**, body, heart, yearning |

> `patronize` premier résultat (run distant) ou troisième (run local) : l'âme noire est associée à la condescendance. Résultat analytiquement fort et stable.

### `soul - white + savage`
| Run local | Run distant |
|---|---|
| **patronize**, indestructible, yearning | **patronize**, familiarly, acutely |

> `patronize` revient encore, encore plus haut. La substitution `black→savage` renforce le signal. Convergence entre les deux runs.

### `ivory - white + black` ✅
| Run local | Run distant |
|---|---|
| carving, creamy, purr, panther | carving, creamy, solid |

> `carving` et `creamy` dans les deux runs : l'ivoire noir garde ses qualités matérielles (sculpture, couleur ivoire). Cohérent avec la thématique du pillage dans Conrad.

### `heart - white + black` ✅
| Run local | Run distant |
|---|---|
| death, earth, though, hard, love | hard, break, love, earth, sinking |

> *Heart of Darkness* explicitement encodé : le cœur noir renvoie à la mort, à la dureté, à la brisure. `love` présent dans les deux — ambivalence Conrad.

---

## 5. Monde marin et identité (Conrad)

### `captain - ship + sea` / `captain - crew + sailor` ✅
| Analogie | Run local | Run distant |
|---|---|---|
| `captain - ship + sea` | macwhirr, gadsby, jukes, allistoun | macwhirr, gadsby, jukes, lingard |
| `captain - crew + sailor` | jukes, seaman, lingard, macwhirr | gadsby, macwhirr, jukes, allistoun, lingard |

> Résultats les plus stables de tout le jeu. Les **noms propres de capitaines** de Conrad et Kipling (*MacWhirr* = Typhoon, *Allistoun* = Narcissus, *Lingard* = Outcast, *Gadsby* = Kipling) émergent directement. Le modèle a appris la catégorie « commandant maritime » avec une grande précision.

### `truth - honour + lie` ✅
| Run local | Run distant |
|---|---|
| speak, still, see, seem, could | still, see, could, seem, speak |

> Résultat quasi-identique entre les deux runs. Sémantiquement cohérent : vérité/mensonge s'ancrent dans les actes de langage (*speak*, *see*, *seem*) — univers moral conradien.

### `silence - death + life` ✅
| Run local | Run distant |
|---|---|
| seem, **profound**, short, moment | **profound**, seem, moment, yet |

> `profound` en tête dans le run distant, second en local. « Le silence de la mort dans la vie » = silence profond — formule conradienne encodée fidèlement.

---

## 6. Analogies peu concluantes (écartées)

Les analogies suivantes ont produit des résultats **instables** entre les deux runs et/ou des scores trop faibles (<0.45) pour être interprétables :

| Analogie | Problème |
|---|---|
| `man - english + native` | Résultats génériques (make, come, would) — trop haute fréquence |
| `horror - white + black` | Scores faibles, voisins incohérents (pudding, bust) |
| `brave - jim + coward` | Instable, hapax régionaux |
| `fate/conscience/act - honour + disgrace` | Scores <0.45, voisins divergents |
| `warrior - native + english` | Résultats trop bruités |

---

## Bilan

| Thème | Signal de biais | Stabilité |
|---|---|---|
| Hiérarchie sahib/servant | Fort | ✅ |
| Loi de la jungle (law) | Très fort | ✅ |
| Empire → rubber (pillage) | Fort, corpus mixte | ✅ |
| Darkness/light (Conrad) | Fort | ✅ |
| Humanité/divin (human) | Fort | ✅ |
| Patronize (soul/savage) | Très fort | ✅ |
| Capitaines par nom propre | Très stable | ✅ |
| Silence profond | Stable | ✅ |
