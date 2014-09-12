"""
This module contains functions for parsing documents to vectors.
Functions for word cleaning and stemming are also included.

:var set PUNCT:  The set of punctuation to be filtered from documents.
:var set STOPWORDS: The set of stopwords to be filtered from documents.

:type STEMMER: L{nltk.PorterStemmer}
:var  STEMMER: stemmer instance used to stem words in documents.

"""
import string
import nltk


PUNCT = set(string.punctuation)
STOPWORDS = set(nltk.corpus.stopwords.words('english'))
STOPWORDS.add('br')  # get rid of </br> html tags (hackish)
STOPWORDS.add('')  # makes the pipeline squeaky clean (ass-covering)
STEMMER = nltk.PorterStemmer()


def tokenize(doc):
    return nltk.tokenize.word_tokenize(doc)

def remove_punctuation(word):
    return ''.join([char for char in word if char not in PUNCT])

def is_stopword(word):
    return word in STOPWORDS

def starts_with_digits(word):
    return word[0].isdigit() or word.isdigit()

def clean_word(word):
    """Remove punctuation, lowercase, and strip whitespace from the word.

    :param str word: The word to clean.
    :return: The cleaned word.
    """
    return remove_punctuation(word).lower().strip()

def word_is_not_junk(word):
    """Applies a set of conditions to filter out junk words.

    :param str word: The word to test.
    :param int min_length: Drop words shorter than this; set to 0 to disable.
    :return: False if the word is junk, else True.

    """
    too_short = lambda word: len(word) < 1
    if (not word or
        is_stopword(word) or
        starts_with_digits(word) or
        too_short(word)):
        return False
    else:
        return True

def preprocess(wordlist, stopwords=True, digits=True, stem=True):
    """Perform preprocessing on the list of words. Always removes punctuation,
    lowercases the word, and strips whitespace before other preprocessing.

    :param bool stopwords: If True, remove stopwords.
    :param bool digits: If True, remove words that start with digits.
    :param bool stem: If True, stem words using a Porter stemmer.
    """
    cleaned = [w for w in map(clean_word, wordlist) if w]
    if stopwords: cleaned = [w for w in cleaned if not is_stopword(w)]
    if digits: cleaned = [w for w in cleaned if not starts_with_digits(w)]
    if stem: cleaned = map(STEMMER.stem_word, cleaned)
    return cleaned

def clean_word_list(word_list):
    """The following cleaning operations are performed:

        1. punctuation removed
        2. word lowercased
        3. whitespace stripped

    Then words meeting these filtering criteria are removed:

        1. empty or only 1 character
        2. stopword
        3. all digits
        4. starts with digit

    Finally, all words are stemmed.

    :param (list of str) word_list: The list of words to clean.
    :rtype:  list of str
    :return: The cleaned, stemmed, filtered, list of words.
    """
    cleaned_words = [clean_word(w) for w in word_list]
    filtered_words = filter(word_is_not_junk, cleaned_words)
    stemmed_words = [STEMMER.stem_word(word) for word in filtered_words]
    return stemmed_words

def vectorize(doc):
    """Convert a document (string/unicode) into a filtered, cleaned,
    stemmed, list of words.

    :param str doc: The document to vectorize.
    :rtype:  list of str
    :return: The filtered, cleaned, stemmed, list of words.
    """
    word_list = nltk.tokenize.word_tokenize(doc)
    return clean_word_list(word_list)

def write_vec(vec, filepath):
    """ Write a list of words to a txt file, seperated by newlines.

    :param (list of str) vec: The word vector to write to a file.
    :param str filepath: The absolute path of the file to write to.
    """
    with open(filepath, 'w') as f:
        for word in vec:
            f.write('{}\n'.format(word))
