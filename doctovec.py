"""
This module contains functions for parsing documents to vectors.
In particular, the primary ways the documents can be represented
are as frequency distributions of words and as bags of words.

Functions for word cleaning and stemming are also included.

"""
import string

import nltk
import gensim


PUNCT = set(string.punctuation)
STOPWORDS = set(nltk.corpus.stopwords.words('english'))
STOPWORDS.add('br')  # get rid of </br> html tags (hackish)
STEMMER = nltk.PorterStemmer()


# for use in filtering out junk words
def test_word(word):
    if not word:
        return False
    elif word in STOPWORDS:
        return False
    elif word[0].isdigit():
        return False
    elif word.isdigit():
        return False
    elif len(word) == 1:
        return False
    else:
        return True


def clean_word(word):
    word = ''.join([char for char in word if char not in PUNCT])
    return word.lower().strip()


def clean_word_list(word_list):
    """
    The following cleaning operations are performed:

        1. punctuation removed
        2. word lowercased
        3. whitespace stripped

    Then words meeting these filtering criteria are removed:

        1. empty or only 1 character
        2  stopword
        3. all digits
        4. starts with digit

    Finally, all words are stemmed.

    """
    cleaned_words = [clean_word(w) for w in word_list]
    filtered_words = filter(test_word, cleaned_words)
    stemmed_words = [STEMMER.stem_word(word) for word in filtered_words]
    return stemmed_words


def vectorize(doc):
    """
    Convert a document (string/unicode) into a filtered, cleaned,
    stemmed, list of words.

    @param doc: the document to vectorize
    @type  doc: string or unicode

    @return: filtered, cleaned, stemmed, list of words
    @rtype:  list of str

    """
    word_list = nltk.tokenize.word_tokenize(doc)
    return clean_word_list(word_list)


def write_vec(vec, filepath):
    """
    Write a list of words to a txt file.
    Separate words by newlines.

    """
    with open(filepath, 'w') as f:
        for word in vec:
            f.write('{}\n'.format(word))


def bow(docs):
    """
    Process a list of document into a BoW vector.

    """
    token_lists = []
    for doc in docs:
        word_list = nltk.tokenize.word_tokenize(doc)
        token_lists.append(clean_word_list(word_list))

    dictionary = gensim.corpora.dictionary.Dictionary(token_lists)
    return dictionary


def _slow_freqdist(doc):
    fdist = nltk.FreqDist()
    word_list = nltk.tokenize.word_tokenize(doc)
    for word in clean_word_list(word_list):
        fdist.inc(word)

    return fdist


def _fast_doctovec(doc):
    pass



if __name__ == "__main__":
    import data
    awards = data.awards()
    abstracts = []

    for _ in range(5):
        a = awards.next()['abstract']
        print a
        abstracts.append(awards.next()['abstract'])

    d = bow(abstracts)

