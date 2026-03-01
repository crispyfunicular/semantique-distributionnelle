import spacy

# Chargement du modèle linguistique français
nlp = spacy.load("fr_core_news_sm")

def preparer_corpus(file):
    """Lit un fichier, le segmente en phrases, le tokenise et le lemmatise."""
    
    # Ouverture et lecture du fichier
    with open(file, "r", encoding="utf-8") as f:
        texte = f.read()
    
    # analyse de l'ensemble du texte
    doc = nlp(texte)
    
    corpus = []
    
    # Segmentation en phrases (doc.sents)
    for phrase in doc.sents:
        phrase_lemmatisee = []
        
        # Tokenisation
        for token in phrase:
            # Filtrage de la ponctuation (token.is_punct) et des espaces vides (token.is_space)
            if not token.is_punct and not token.is_space:
                # Lemmatisation (.lemma) et passage en minuscules (.lower())
                lemme = token.lemma_.lower()
                phrase_lemmatisee.append(lemme)
        
        # Filtrage des phrases de moins 2 mots
        # (pour ne pas mettre en échec la fenêtre glissante)
        if len(phrase_lemmatisee) > 1:
            corpus.append(phrase_lemmatisee)
            
    return corpus


def main():
    corpus_falc = preparer_corpus("corpus/CDPH_falc.txt")
    corpus_officiel = preparer_corpus("corpus/CDPH_officiel.txt")
