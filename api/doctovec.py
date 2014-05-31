"""
This module contains functions for parsing documents to vectors.
Functions for word cleaning and stemming are also included.

@type PUNCT: set
@var  PUNCT:  The set of punctuation to be filtered from documents.

@type STOPWORDS: set
@var  STOPWORDS: The set of stopwords to be filtered from documents.

@type STEMMER: L{nltk.PorterStemmer}
@var  STEMMER: stemmer instance used to stem words in documents.

"""
import string

import nltk


PUNCT = set(string.punctuation)
STOPWORDS = set(nltk.corpus.stopwords.words('english'))
STOPWORDS.add('br')  # get rid of </br> html tags (hackish)
STEMMER = nltk.PorterStemmer()


def keep_word(word):
    """
    Applies a set of conditions to filter out junk words.

    @type  word: str
    @param word: The word to test.

    @rtype:  bool
    @return: False if the word is junk, else True.

    """
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
    """
    Remove punctuation, lowercase, and strip whitespace from the word.
    Note that this will remove all characters from the word in cases
    where it consists only of whitespace and/or punctuation.

    @type  word: str
    @param word: The word to clean.

    @rtype:  str
    @return: The cleaned word.

    """
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
        2. stopword
        3. all digits
        4. starts with digit

    Finally, all words are stemmed.

    @type  word_list: list of str
    @param word_list: The list of words to clean.

    @rtype:  list of str
    @return: The cleaned, stemmed, filtered, list of words.

    """
    cleaned_words = [clean_word(w) for w in word_list]
    filtered_words = filter(keep_word, cleaned_words)
    stemmed_words = [STEMMER.stem_word(word) for word in filtered_words]
    return stemmed_words


def vectorize(doc):
    """
    Convert a document (string/unicode) into a filtered, cleaned,
    stemmed, list of words.

    @type  doc: str
    @param doc: The document to vectorize.

    @rtype:  list of str
    @return: The filtered, cleaned, stemmed, list of words.

    """
    word_list = nltk.tokenize.word_tokenize(doc)
    return clean_word_list(word_list)


def write_vec(vec, filepath):
    """
    Write a list of words to a txt file.
    Separate words by newlines.

    @type  vec: list of str
    @param vec: The word vector to write to a file.

    @type  filepath: str
    @param filepath: The absolute path of the file to write to.

    """
    with open(filepath, 'w') as f:
        for word in vec:
            f.write('{}\n'.format(word))
