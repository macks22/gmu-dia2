"""
This module contains functions for working with the abstracts for each award
and pairing them up with the PIs that worked on those awards. The envisioned
purpose of the functionality is to enable topic modeling approaches by
translating abstracts into BoW representations and assembling a representative
BoW vector for each PI. This will allow community detection via topic modeling
approaches.

Abstracts are treated as documents. They can be represented in 3
different forms:

    1. raw strings
    2. word vectors
    3. Bag of words (BoW) -- list of tuples of (id, word frequency)

The raw strings are simply utf-8 encoded forms of the data pulled from the JSON
files. The word vectors are created from the raw strings using
L{doctovec.vectorize}. Please see the docstrings there for more information on
the preprocessing methods used. The BoW representation is parsed from the word
vectors using gensim, which is a highly optimized topic modeling library.

The documentation of gensim is not the clearest, so its important to understand
that a L{gensim.Dictionary} is not a BoW. Rather, it is intended that to
construct a BoW, a Dictionary instance will be created from the entire corpus of
documents being analyzed (all abstracts in this case). This tags each unique
word with an ID that is unique to the Dictionary instance. Then the Dictionary
instance is used to parse subsequent documents into BoW representations using
the I{doc2bow} method.

The BoW documents can then be used with the various models in L{gensim.models},
such as the L{gensim.models.LdaModel} to perform topic modeling and compute
document similarity measures.

"""
import os
import itertools
import cPickle as pickle

import gensim
import pandas as pd
import numpy as np

import data
import doctovec


class Abstracts(object):
    """Manage award abstracts in their string form."""

    def __init__(self):
        """Parse the data into data frames.

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
        data_manager = data.DataDirectory()
        for award_data in data_manager.awards():
            award_id = str(award_data['awardID'])
            pi_list = [str(pi_id) for pi_id in award_data['PIcoPI']]
            abstract = unicode(award_data['abstract'])
            title = unicode(award_data['title'])

            # add a record for the award/abstract pairing
            abstract_frame_columns = ['award_id', 'abstract', 'title']
            awd_abstract_pairings.append((award_id, abstract, title))

            # add a record for each pi/award pairing
            pi_frame_columns = ['pi_id', 'award_id']
            for pi_id in pi_list:
                pi_awd_pairings.append((pi_id, award_id))

        self._pi_frame = pd.DataFrame(
            pi_awd_pairings,
            columns=pi_frame_columns)
        self._abstract_frame = pd.DataFrame(
            awd_abstract_pairings,
            columns=abstract_frame_columns)

        self.select_columns = ['abstract', 'title']
        self.abstracts = self._abstract_frame['abstract'].values
        self.award_ids = self._abstract_frame['award_id'].values

        # include set of PI IDs for convenience
        self.pis = self._pi_frame['pi_id'].unique()

    def __getitem__(self, award_id):
        """Look up an abstract by the id of the award it was written for.

        :type  award_id: str or int
        :param award_id: ID of the award to look up an abstract for.
        :raises KeyError: If the award id is not in the data parsed.

        """
        selector = self._abstract_frame['award_id'] == str(award_id)
        result = self._abstract_frame[selector]
        if len(result) == 1:
            arr = result[self.select_columns].values
            return u' '.join(arr[0])
        else:
            raise KeyError('unknown award id')

    def for_pi(self, pi_id):
        """Get all abstracts for a particular PI. This gets a list
        of all the abstracts for each award this PI has worked on.

        :type  pi_id: str or int
        :param pi_id: ID of the PI to get abstracts for.
        :rtype:   L{numpy.ndarray} of str
        :returns: array of abstracts

        """
        selector = self._pi_frame['pi_id'] == str(pi_id)
        selected = self._pi_frame[selector]
        joined = selected.merge(self._abstract_frame, on='award_id')
        awd_arr = joined[self.select_columns].values
        return np.array([np.unicode_.join(u' ', parts) for parts in awd_arr])

    def __iter__(self):
        """Yield each abstract string in turn by iterating through the
        underlying L{pandas.DataFrame}.

        """
        for docparts in self._abstract_frame[self.select_columns].values:
            yield np.unicode_.join(u' ', docparts)

    def __len__(self):
        """Return the number of abstracts in the corpus."""
        return len(self._abstract_frame)

    def __str__(self):
        msg = 'Corpus of {} abstracts for NSF grant awards.'
        return msg.format(self.__len__())

    def awards_for_pi(self, pi_id):
        """Retrieve the list of all awards for the PI.

        :type  pi_id: str or int
        :param pi_id: ID of the PI to get awards for.
        :rtype:  L{numpy.ndarray}
        :return: Array of ids for all awards this PI has worked on.

        """
        selector = self._pi_frame['pi_id'] == str(pi_id)
        return self._pi_frame[selector]['award_id'].values

    def pi_document(self, pi_id):
        """For the given PI, retrieve abstracts for all grant awards he/she has
        worked on and combine them into a single document (string). This can
        be considered the "representative document" for this PI.

        :type  pi_id: str or int
        :param pi_id: ID of the PI to get a representative document for.
        :rtype:   str
        :return:  The representative document for the given PI id.

        """
        # get awards for this PI
        selector = self._pi_frame['pi_id'] == str(pi_id)
        awards = self._pi_frame[selector]['award_id'].values
        if len(awards) != 1:
            raise KeyError('unknown pi_id')

        # get abstracts from award ids
        selector = self._abstract_frame['award_id'].isin(awards)
        doc_frame = self._abstract_frame[selector]
        doc_arr = doc_frame[self.select_columns].values
        flattened = np.concatenate(doc_arr)
        return np.unicode_.join(u' ', flattened)


class AbstractVectors(object):
    """Manage award abstracts as vectors of words."""

    def __init__(self, abstracts=None, parse=False):
        """If parse is True, the abstracts are parsed from the full abstracts.
        Otherwise, they are loaded from the pickle files.

        :param bool parse: whether to parse abstracts from loaded abstracts or
            load from pickle files

        """
        self._abstracts = Abstracts() if abstracts is None else abstracts
        self.award_ids = self._abstracts.award_ids
        self.pis = self._abstracts.pis
        self.parse = parse

        # set defaults for document vectorization preprocessing steps
        self.remove_stopwords = True
        self.remove_digits = True
        self.stem_words = True

    def vectorize(self, doc):
        return doctovec.doctovec(doc, self.remove_stopwords,
                self.remove_digits, self.stem_words)

    def __iter__(self):
        """Yield each abstract in turn, either by parsing the abstract
        strings from the underlying L{Abstracts} instance, or by
        loading them from the saved abstract vector files, depending
        on the value of L{AbstractVectors.parse}.

        """
        for pi in self.pis:
            yield self.pi_document(pi)
        #if self.parse:
        #    for abstract in self._abstracts:
        #        yield self.vectorize(abstract)
        # else:
        #     for award_id in self.award_ids:
        #         yield data.load_abstract_vec(award_id)

    def __getitem__(self, pi_id):
        return self.pi_document(pi_id)

    def get_award_abstract(self, award_id):
        """Look up an abstract by the id of the award it was written for.

        :type  award_id: str or int
        :param award_id: id of the award to look up an abstract for.
        :raises KeyError: If the award id is not in the data parsed.

        """
        abstract = self._abstracts[award_id]  # safeguard
        if self.parse:
            return self.vectorize(abstract)
        else:
            return data.load_abstract_vec(award_id)

    def __len__(self):
        """Return the number of abstracts in the corpus."""
        return len(self._abstracts)

    def __str__(self):
        return "Corpus of {} abstracts from NSF grant awards.".format(
            self.__len__())

    def save_vector(self, award_id):
        """Save the vector for the abstract associated with the given
        award id to a pickle file for quick loading later.

        :type  award_id: str or int
        :param award_id: id of the award to save the abstract word vector for.
        :raises KeyError: If the award id is not in the data parsed.

        """
        vector = self.__getitem__(award_id)
        data.save_abstract_vector(vector, award_id)

    def write_vector(self, award_id):
        """Write the vector for the abstract associated with the given
        award id to a text file (one word per line).

        :type  award_id: str or int
        :param award_id: id of the award to write the abstract word vector for
        :raises KeyError: If the award id is not in the data parsed.

        """
        vector = self.__getitem__(award_id)
        data.write_abstract_vector(vector, award_id)

    def awards_for_pi(self, pi_id):
        """Retrieve the list of all awards for the PI.

        :type  pi_id: str or int
        :param pi_id: id of the PI to get awards for
        :rtype:  list of str
        :return: List of ids for all awards the PI has worked on.

        """
        return self._abstracts.awards_for_pi(pi_id)

    def for_pi(self, pi_id):
        """Get all abstracts for a particular PI. This gets a list of all the
        abstracts for each award this PI has worked on, where each abstract is
        in its word vector form.

        :type  pi_id: str or int
        :param pi_id: ID of the PI to get abstracts for.
        :rtype:  list of (list of str)
        :return: List of abstract word vectors.

        """
        abstracts = self._abstracts.for_pi(pi_id)
        return [self.vectorize(abstract) for abstract in abstracts]

    def pi_document(self, pi_id):
        """Return the representative document for the given PI as a word vector.

        :type  pi_id: str or int
        :param pi_id: ID of the PI to get a representative document for.
        :rtype:  list of str
        :return: The representative document for the given PI id.

        """
        pi_doc = self._abstracts.pi_document(pi_id)
        return self.vectorize(pi_doc)


class AbstractBoWs(object):
    """Manage award abstracts as BoWs."""

    def __init__(self, **kwargs):
        """Load BoW dictionaries for all PIs and combine them to form a BoW for
        the complete dataset (all abstracts). An instance of this class can be
        instantiated with no parameters, in which case it will parse through the
        raw JSON data to build the abstracts corpus, vectorize each abstract,
        then convert the vectors into their BoW representations.

        If an instance of L{AbstractVectors} or L{Abstracts} already exists, it
        can be passed as a parameter to avoid parsing through the JSON files.

        :type  abstracts: L{Abstracts}
        :keyword abstracts: Abstracts instance to use as the underlying
            corpus; if none is passed and no I{abstract_vectors}
            instance is passed, instantiate a new instance,
            which parses the raw JSON files to build the abstracts
            corpus.

        :type  abstract_vectors: L{AbstractVectors}
        :keyword abstract_vectors: AbstractVectors instance to use as
            the underlying corpus; if none is passed, a new instance
            will be instantiated, passing the I{abstracts} param to
            it directly. Otherwise the I{abstracts} param will be
            ignored.

        :keyword bool parse: see L{AbstractVectors.__init__}
        :keyword bool filter_extremes: see L{gensim.corpora.dictionary}

        """
        abstract_vectors = kwargs.get('abstract_vectors', None)
        abstracts = kwargs.get('abstracts', None)
        parse = kwargs.get('parse', False)

        if abstract_vectors is None:
            self._abstract_vectors = AbstractVectors(abstracts, parse)
        else:
            self._abstract_vectors = abstract_vectors

        self.dictionary = gensim.corpora.dictionary.Dictionary(
            self._abstract_vectors)
        if kwargs.get('filter_extremes', False):
            self.dictionary.filter_extremes()

        self.award_ids = self._abstract_vectors.award_ids
        self.pis = self._abstract_vectors.pis

    @property
    def num_docs(self):
        return self.dictionary.num_docs

    @property
    def num_terms(self):
        return len(self.dictionary)

    @property
    def num_nnz(self):
        return self.dictionary.num_nnz

    def __iter__(self):
        """Yield each abstract in turn by iterating through the underlying
        L{AbstractVectors} instance and converting each abstract vector into its
        BoW representation.

        :rtype:  iterator yielding BoW (list of tuples)
        :return: An iterator which yields BoW abstracts.

        """
        for pi in self.pis:
            yield self.pi_document(pi)

    def __getitem__(self, pi_id):
        return self.pi_document(pi_id)

    def get_award_abstract(self, award_id):
        """Get the BoW representation of the abstract associated with the given
        award id.

        :type  award_id: str, unicode, or int
        :param award_id: ID of the award to look up an abstract for.
        :raises KeyError: If the award id is not in the data parsed.

        """
        return self.dictionary.doc2bow(self._abstract_vectors[award_id])

    def __len__(self):
        """Return the number of abstracts in the corpus."""
        return len(self._abstract_vectors)

    def __str__(self):
        msg = 'BoW Abstracts corpus with {} abstracts.'
        return msg.format(self.__len__())

    def save_mmformat(self, fpath):
        """Save in matrix market format to given file path."""
        gensim.corpora.MmCorpus.serialize(fpath, self,
            id2token=self.dictionary.id2token)

    def awards_for_pi(self, pi_id):
        """Retrieve the list of all awards for the PI.

        :type  pi_id: str, unicode, or int
        :param pi_id: id of the PI to get awards for
        :rtype:  list of str
        :return: The list of award IDs for awards the PI has worked on.

        """
        return self._abstract_vectors.awards_for_pi(pi_id)

    def for_pi(self, pi_id):
        """Get all abstracts for a particular PI. This gets a list of all the
        abstracts for each award this PI has worked on, where each abstract is
        in its BoW form.

        :type  pi_id: str, unicode, or int
        :param pi_id: id of the PI to get abstracts for.
        :rtype:  list of BoWs
        :return: The list of abstract BoWs for the given PI.

        """
        abstract_vectors = self._abstract_vectors.for_pi(pi_id)
        return [self.dictionary.doc2bow(vec) for vec in abstract_vectors]

    def pi_document(self, pi_id):
        """Return the representative document for the given PI as a BoW.

        :type  pi_id: str, unicode, or int
        :param pi_id: id of the PI to get a representative document for
        :rtype:  BoW
        :return: the representative document for the given PI id

        """
        document_vector = self._abstract_vectors.pi_document(pi_id)
        return self.dictionary.doc2bow(document_vector)


class LdaModel(object):
    """Run LDA using abstracts corpus (BoW)."""

    def __init__(self, num_topics=96, bow_corpus=None, parse=False):
        """
        :param int num_topics: The number of topics to use when training
            the LDA model.

        :type  bow_corpus: L{AbstractBoWs}
        :param bow_corpus: The corpus of abstract documents in BoW
            format; if none is passed a new instance will be
            instantiated, which loads all abstracts from their saved
            word vector files by default.

        :param bool parse: If True, load the model instance from a pickle
            file, otherwise train a new model.

        """
        # TODO: data.load_bow_corpus
        if bow_corpus is None:
            self._bow_corpus = AbstractBoWs(parse=parse)
        else:
            self._bow_corpus = bow_corpus

        self._dict = self._bow_corpus.dictionary

        if parse:
            self._model = gensim.models.LdaModel(
                self._bow_corpus,
                num_topics=num_topics,
                id2word=self._dict)
        else:
            self._model = data.load_lda_model()

        # expose pi set for convenience
        self.pis = self._bow_corpus.pis

    def __getitem__(self, pi_id):
        """Allow [] indexing using pi_ids to run the LDA model on the
        abstracts for that pi. This is cool and you know it.

        :type  pi_id: str or int
        :param pi_id: The ID of the PI to run the LDA model for.
        :rtype:  list of tuples
        :return: The topic distribution for the given PI.

        """
        pi_bow = self._bow_corpus.pi_document(pi_id)
        topic_distribution = self._model[pi_bow]
        return sorted(topic_distribution,
            reverse=True, key=lambda topic: topic[1])

    def save(self):
        """Save this LDA model to a pickle file.

        :param str filepath: The path of the file to save the model to.

        """
        with open(filepath, 'w') as f:
            pickle.dump(self, f)

    @classmethod
    def load(self, filepath):
        """Load an L{LdaModel} instance from a pickle file.

        :param str filepath: Path of pickle file to load from.

        """
        with open(filepath, 'r') as f:
            return pickle.load(f)

    def show_topic(self, topic_id, topn=10):
        """Show a particular topic in the form of a list of terms with relative
        representativeness scores, sorted from most representative to least.

        :param int topic_id: ID of topic to show.
        :param int topn: Number of words to show; these will be the top n
            most representative of the topic; 10 are shown by default.

        """
        return self._model.show_topic(topic_id, topn)

    def top_topics_for_pi(self, pi_id, topn=5):
        membership = self.__getitem__(pi_id)

        # sanity check
        if len(membership) < topn:
            topn = len(membership)

        membership.sort(key=lambda topic: topic[1])
        top_topics = [membership.pop() for _ in range(topn)]
        return top_topics

    def write_wordle(self, topic_num, topn=40):
        """Write a wordle file for the given topic number in the format:

            lda-wordle-topic<topic_num>.txt

        :param int topic_num: The number of the topic to write a wordle
            file for.
        :param int topn: The number of words to include in the wordle file;
            top n most important/frequent words.

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
    """Read the corpus of abstracts from the raw JSON files, parse them into
    word vectors, then parse those into their BoW representations, then train an
    LDA model using that corpus of BoW abstracts and return it.

    :rtype:  L{gensim.models.LdaModel}
    :return: The LDA model trained from the abstracts corpus.

    """
    bow_corpus = AbstractBoWs()
    return gensim.models.LdaModel(bow_corpus, id2word=bow_corpus.dictionary)


def write_wordle_files(lda_model, num_topics=10, topn=40):
    """Write files in a format which can be copy/pasted into wordle.net
    to generate word clouds. The format is really quite simple::

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

    :type  lda_model: L{gensim.models.LdaModel}
    :param lda_model: The trained LDA model to parse topics from.

    :param int num_topics: The number of topics to write wordle files for.
    :param int topn: The number of words to represent each topic with;
        n most frequent.

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


if __name__ == "__main__":
    corpus = AbstractBoWs()
    tfidf = gensim.models.TfidfModel(corpus)
