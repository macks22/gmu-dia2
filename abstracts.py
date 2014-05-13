"""
This module contains functions for working with the abstracts
for each award and paring them up with the PIs that worked on
those awards. The envisioned purpose of the functionality is
to enable topic modelling approaches by translating abstracts
into BoW representations and assembling a representative BoW
vector for each PI.

This will allow community detection via topic modelling approaches.

Abstracts are treated as documents. They can be represented in 3
different forms:

    1. raw strings
    2. word vectors
    3. Bag of words (BoW)

The raw strings are simply utf-8 encoded forms of the data pulled
from the JSON files. The word vectors are created from the raw
strings using the vectorize() function in the doctovec module. Please
see the docstrings there for more information on the preprocessing
methods used. The BoW represntation is parsed from the word vectors
using gensim, which is a highly optimized topic modelling library.

The documentation of gensim is not the clearest, so its important to
understand that a L{gensim.corpora.dictionary.Dictionary} is not a
BoW. Rather, it is intended that to construct a BoW, a Dictionary
instance will be created from the entire corpus of documents being
analyzed (all abstracts in this case). Then the Dictionary instance
is used to parse subsequent documents into BoW representations using
the doc2bow() method.

The BoW documents can then be used with the various models in
L{gensim.models}, such as the L{gensim.models.LdaModel} to perform
topic modelling and compute document similarity measures.

"""
import os
import itertools
import cPickle as pickle

import gensim
import pandas as pd

import data
import doctovec


class Abstracts(object):
    """Manage award abstracts in their string form."""

    def __init__(self):
        """
        Parse the data into data frames.

            1. award/abstract pairings
            2. pi/award pairings

        It is useful to keep these separate to avoid significant duplication.
        Since there will be multiple instances of each award in the pi/award
        pairings, tacking the abstracts onto that frame would store quite a
        few of the abstracts multiple times in the frame, increasing memory
        overhead significantly.

        """
        awd_abstract_pairings = []
        pi_awd_pairings = []
        for award_data in data.awards():
            award_id = str(award_data['awardID'])
            pi_list = [str(pi_id) for pi_id in award_data['PIcoPI']]
            abstract = award_data['abstract'].encode('utf-8')
            title = award_data['title'].encode('utf-8')

            # add a record for the award/abstract pairing
            abstract_frame_columns = ['award_id', 'abstract', 'title']
            awd_abstract_pairings.append((award_id, abstract, title))

            # add a record for each pi/award pairing
            pi_frame_columns = ['pi_id', 'award_id']
            for pi_id in pi_list:
                pi_awd_pairings.append((pi_id, award_id))

        self._pi_frame = pd.DataFrame(pi_awd_pairings,
                columns=pi_frame_columns)
        self._abstract_frame = pd.DataFrame(awd_abstract_pairings,
                columns=abstract_frame_columns)

        self.abstracts = self._abstract_frame['abstract'].values
        self.award_ids = self._abstract_frame['award_id'].values

    def __getitem__(self, award_id):
        """
        Look up an abstract by the id of the award it was written for.

        @param award_id: id of the award to look up an abstract for
        @type  award_id: str, unicode, or int

        @raises KeyError: if the award id is not in the data parsed

        """
        selector = self._abstract_frame['award_id'] == str(award_id)
        result = self._abstract_frame[selector]['abstract'].values
        if len(result) == 1:
            return unicode(result[0])
        else:
            raise KeyError('unknown award id')

    def for_pi(self, pi_id):
        """
        Get all abstracts for a particular PI. This gets a list
        of all the abstracts for each award this PI has worked on.

        @param pi_id: id of the PI to get abstracts for.
        @type  pi_id: str, unicode, or int

        @returns: array of abstracts
        @rtype:   L{numpy.ndarray} of str

        """
        selector = self._pi_frame['pi_id'] == str(pi_id)
        selected = self._pi_frame[selector]
        joined = selected.merge(self._abstract_frame, on='award_id')
        return joined['abstract'].values

    def __iter__(self):
        for abstract in self._abstract_frame['abstract'].values:
            yield abstract

    def __len__(self):
        return len(self._abstract_frame)

    def __str__(self):
        msg = 'Corpus of {} abstracts for NSF grant awards.'
        return msg.format(self.__len__())

    def awards_for_pi(self, pi_id):
        """
        Retrieve the list of all awards for the PI.

        @param pi_id: id of the PI to get awards for
        @type  pi_id: str, unicode, or int

        """
        selector = self._pi_frame['pi_id'] == str(pi_id)
        return self._pi_frame[selector]['award_id'].values

    def pi_document(self, pi_id):
        """
        For the given PI, retrieve abstracts for all grant awards he/she has
        worked on and combine them into a single document (string). This can
        be considered the "representative document" for this PI.

        @param pi_id: id of the PI to
        @type  pi_id: str, unicode, or int

        @returns: the representative document for the given PI id
        @rtype:   str

        """

        # get awards for this PI
        selector = self._pi_frame['pi_id'] == str(pi_id)
        awards = self._pi_frame[selector]['award_id'].values

        # get abstracts from award ids
        selector = self._abstract_frame['award_id'].isin(awards)
        abstracts = self._abstract_frame[selector]['abstract'].values

        return u' '.join(abstracts)


class AbstractVectors(object):
    """Manage award abstracts as vectors of words."""

    def __init__(self, abstracts=None, parse=False):
        """
        If parse is True, the abstracts are parsed from the full abstracts.
        Otherwise, they are loaded from the pickle files.

        @param parse: whether to parse abstracts from loaded abstracts or
                      load from pickle files
        @type  parse: bool

        """
        self._abstracts = Abstracts() if abstracts is None else abstracts
        self.award_ids = self._abstracts.award_ids
        self.parse = parse

    def __iter__(self):
        if self.parse:
            for abstract in self._abstracts:
                yield doctovec.vectorize(abstract)
        else:
            for award_id in self.award_ids:
                yield data.load_abstract_vec(award_id)

    def __getitem__(self, award_id):
        """
        Look up an abstract by the id of the award it was written for.

        @param award_id: id of the award to look up an abstract for
        @type  award_id: str, unicode, or int

        @raises KeyError: if the award id is not in the data parsed

        """
        abstract = self._abstracts[award_id]  # safeguard
        if self.parse:
            return doctovec.vectorize(abstract)
        else:
            return data.load_abstract_vec(award_id)

    def __len__(self):
        return len(self._abstracts)

    def __str__(self):
        msg = "Corpus of {} abstracts from NSF grant awards."
        return msg.format(self.__len__())

    def save_vector(self, award_id):
        """
        Save the vector for the abstract associated with the given award id
        to a pickle file for quick loading later.

        @param award_id: id of the award to save the abstract word vector for
        @type  award_id: str, unicode, or int

        @raises KeyError: if the award id is not in the data parsed

        """
        vector = self.__getitem__(award_id)
        data.save_abstract_vector(vector, award_id)

    def write_vector(self, award_id):
        """
        Write the vector for the abstract associated with the given award id
        to a text file (one word per line).

        @param award_id: id of the award to write the abstract word vector for
        @type  award_id: str, unicode, or int

        @raises KeyError: if the award id is not in the data parsed

        """
        vector = self.__getitem__(award_id)
        data.write_abstract_vector(vector, award_id)

    def awards_for_pi(self, pi_id):
        """
        Retrieve the list of all awards for the PI.

        @param pi_id: id of the PI to get awards for
        @type  pi_id: str, unicode, or int

        """
        return self._abstracts.awards_for_pi(pi_id)

    def for_pi(self, pi_id):
        """
        Get all abstracts for a particular PI. This gets a list
        of all the abstracts for each award this PI has worked on,
        where each abstract is in its word vector form.

        @param pi_id: id of the PI to get abstracts for.
        @type  pi_id: str, unicode, or int

        @returns: list of abstract word vectors
        @rtype:   list of (list of str)

        """
        abstracts = self._abstracts.for_pi(pi_id)
        return [doctovec.vectorize(abstract) for abstract in abstracts]

    def pi_document(self, pi_id):
        """
        Return the representative document for the given PI as a word vector.

        @param pi_id: id of the PI to
        @type  pi_id: str, unicode, or int

        @returns: the representative document for the given PI id
        @rtype:   list of str

        """
        document_string = self._abstracts.pi_document(pi_id)
        return doctovec.vectorize(document_string)


class AbstractBoWs(object):
    """Manage abstracts as BoWs."""

    def __init__(self, abstracts=None, abstract_vectors=None, parse=False):
        """
        Load BoW dictionaries for all PIs and combine them to form a BoW
        for the complete dataset (all abstracts).

        """
        if abstract_vectors is None:
            self._abstract_vectors = AbstractVectors(abstracts, parse)
        else:
            self._abstract_vectors = abstract_vectors

        self._dictionary = gensim.corpora.dictionary.Dictionary(
                self._abstract_vectors)
        self.award_ids = self._abstract_vectors.award_ids

    def __iter__(self):
        for abstract in self._abstract_vectors:
            yield self._dictionary.doc2bow(abstract)

    def __getitem__(self, award_id):
        """
        Get the BoW representation of the abstract associated with the given
        award id.

        @param award_id: id of the award to look up an abstract for
        @type  award_id: str, unicode, or int

        @raises KeyError: if the award id is not in the data parsed

        """
        return self._dictionary.doc2bow(self._abstract_vectors[award_id])

    def __len__(self):
        return len(self._abstract_vectors)

    def __str__(self):
        msg = 'BoW Abstracts corpus with {} abstracts.'
        return msg.format(self.__len__())

    def awards_for_pi(self, pi_id):
        """
        Retrieve the list of all awards for the PI.

        @param pi_id: id of the PI to get awards for
        @type  pi_id: str, unicode, or int

        """
        return self._abstract_vectors.awards_for_pi(pi_id)

    def for_pi(self, pi_id):
        """
        Get all abstracts for a particular PI. This gets a list
        of all the abstracts for each award this PI has worked on,
        where each abstract is in its BoW form.

        @param pi_id: id of the PI to get abstracts for.
        @type  pi_id: str, unicode, or int

        @returns: list of abstract BoWs
        @rtype:   list of BoWs

        """
        abstract_vectors = self._abstract_vectors.for_pi(pi_id)
        return [self._dictionary.doc2bow(vec) for vec in abstract_vectors]

    def pi_document(self, pi_id):
        """
        Return the representative document for the given PI as a BoW.

        @param pi_id: id of the PI to get a representative document for
        @type  pi_id: str, unicode, or int

        @returns: the representative document for the given PI id
        @rtype:   BoW (list of tuples of (id, word frequency))

        """
        document_vector = self._abstract_vectors.pi_document(pi_id)
        return self._dictionary.doc2bow(document_vector)


class LdaModel(object):
    """Run LDA using abstracts corpus (BoW)."""

    def __init__(self, num_topics=96, bow_corpus=None, parse=False):
        # TODO: data.load_bow_corpus
        if bow_corpus is None:
            self._bow_corpus = AbstractBoWs(parse=parse)
        else:
            self._bow_corpus = bow_corpus

        self._dict = self._bow_corpus._dictionary

        if parse:
            self._model = gensim.models.LdaModel(self._bow_corpus,
                    num_topics=num_topics, id2word=self._dict)
        else:
            self._model = data.load_lda_model()

    def __getitem__(self, pi_id):
        """
        Allow [] indexing using pi_ids to run the LDA model on the
        abstracts for that pi. This is cool and you know it.

        """
        pi_bow = self._bow_corpus.pi_document(pi_id)
        return self._model[pi_bow]

    def save(self, filepath):
        """
        Save this LDA model to a pickle file.

        @param filepath: the path of the file to save it to
        @type  filepath: str

        """
        with open(filepath, 'w') as f:
            pickle.dump(self, f)

    @classmethod
    def load(self, filepath):
        """
        Load from pickle file.

        @param filepath: path of pickle file to load from
        @type  filepath: str

        """
        with open(filepath, 'r') as f:
            return pickle.load(f)

    def show_topic(self, topic_num):
        self._model.show_topic(topic_num)

    def top_topics_for_pi(self, pi_id, topn=5):
        membership = self.__getitem__(pi_id)

        # sanity check
        if len(membership) < topn:
            topn = len(membership)

        membership.sort(key=lambda item: item[1])
        top_topics = [membership.pop() for _ in range(topn)]
        return top_topics

    def write_wordle(self, topic_num, topn=40):
        """
        Write a wordle file for the given topic number.

        @param topic_num: the number of the topic to write a wordle file for
        @type  topic_num: int

        @param topn: the number of words to include in the wordle
                     file; to n most important/frequent
        @type  topn: int

            lda-wordle-topic<topic_num>.txt

        """
        topic = self._model.show_topic(topic_num, topn)

        # parse into (word, freq) pairs
        word_freqs = [(pair[1], pair[0] * 1000) for pair in topic]
        filename = 'lda-wordle-topic{}-top{}.txt'.format(topic_num, topn)
        path = os.path.join(data.WORDLE_DIR, filename)
        with open(path, 'w') as f:
            for word_freq in word_freqs:
                f.write('{}:{}\n'.format(word_freq[0], word_freq[1]))


def build_lda():
    bow_corpus = AbstractBoWs()
    return gensim.models.LdaModel(bow_corpus, id2word=bow_corpus._dictionary)


def write_wordle_files(lda_model, num_topics=10, topn=40):
    """
    Write files in a format which can be copy/pasted into wordle.net
    to generate word clouds. The format is really quite simple:

        word1:freq(word1)
        word2:freq(word2)

    where freq(word) is the prominence of that word in the model
    multiplied by 1000. In other words, if a word has a weight of
    .017 in the LDA model, the freq will be calculated as 17.

    The files are written to the wordle data directory using the topic
    number from the LDA model for file naming. See
    L{data.write_wordle_file} for more details on file naming.

    One thing to note is that previously written files with the same
    topic number will be overwritten without warning

    @param lda_model: the trained LDA model to parse topics from
    @type  lda_mdoel: L{gensim.models.LdaModel}

    @param num_topics: number of topics to write wordle files for
    @type  num_topics: int

    @param topn: number of words to represent each topic with;
                 n most frequent
    @type  topn: int

    """
    # sanity check number of topics requested: cannot exceed # topics in model
    if num_topics > lda_model.num_topics:
        num_topics = lda_mode.num_topics

    # The raw format looks like:
    #   ['0.051*electron + 0.040*molecular',
    #    '0.023*molecul + 0.020*magnet']
    # Each topic is a string of the form seen above,
    # so the output of show_topics is a list of these strings
    raw_topics = lda_model.show_topics(topics=num_topics, topn=topn)

    # we want to get the form
    #     [[(electron, 51), (molecular, 40)],
    #      [(molecul, 23), (magnet, 20)]]
    for topic_num, raw_topic in enumerate(raw_topics):
        topic = []

        pairs = [pair.split('*') for pair in raw_topic.split(' + ')]
        # ['0.051', 'electron] --> ('electron', 51)
        for pair in pairs:
            topic.append((pair[1], int(float(pair[0]) * 1000)))

        data.write_wordle_file(topic_num, topic)

