"""
This module contains functions for working with the abstracts
for each award and paring them up with the PIs that worked on
those awards. The envisioned purpose of the functionality is
to enable topic modelling approaches by translating abstracts
into BoW representations and assembling a representative BoW
vector for each PI.

This will allow community detection via topic modelling approaches.

"""
import os
import cPickle as pickle

import gensim
import pandas as pd

import data
import doctovec


# -----------------------------------------------------------------------------
# MODULE SETUP
# -----------------------------------------------------------------------------
def _setup_module():
    """
    Parse the data into data frames.

        1. award/abstract pairings
        2. pi/award pairings

    """
    awd_abstract_pairings = []
    pi_awd_pairings = []
    for award_data in data.awards():
        award_id = str(award_data['awardID'])
        pi_list = [str(pi_id) for pi_id in award_data['PIcoPI']]
        abstract = award_data['abstract'].encode('utf-8')

        # add a record for the award/abstract pairing
        awd_abstract_pairings.append((award_id, abstract))

        # add a record for each pi/award pairing
        for pi_id in pi_list:
            pi_awd_pairings.append((pi_id, award_id))

    pi_awd_frame = pd.DataFrame(pi_awd_pairings,
            columns=['pi_id', 'award_id'])
    awd_abstract_frame = pd.DataFrame(awd_abstract_pairings,
            columns=['award_id', 'abstract'])

    return pi_awd_frame, awd_abstract_frame


PI_AWD_FRAME, AWD_ABSTRACT_FRAME = _setup_module()
# -----------------------------------------------------------------------------


def get_abstracts(pi_id):
    """
    Get all abstracts for a particular PI. This gets a list
    of all the abstracts for each award this PI has worked on.

    @param pi_id: ID of the PI to get abstracts for.
    @type  pi_id: str, unicode, or int

    @returns: list of abstracts
    @rtype:   L{numpy.ndarray} of str

    """
    selector = PI_AWD_FRAME['pi_id'] == str(pi_id)
    joined = PI_AWD_FRAME[selector].merge(AWD_ABSTRACT_FRAME, on='award_id')
    return joined['abstract'].values


def awards_for_pi(pi_id):
    """
    Retrieve the list of all awards for the PI.

    @param pi_id: ID of the PI to get awards for
    @type  pi_id: str, unicode, or int

    """
    selector = PI_AWD_FRAME['pi_id'] == pi_id
    return PI_AWD_FRAME[selector]['award_id'].values


def vectorize(awards=None, write_vec=False, pickle_vec=True):
    """
    Lookup abstracts based on the awards they were written for.  For
    each award in the list, parse the abstract into a vector of words
    (tokenized, cleaned, and stemmed). Store all in a dictionary
    indexed by award ids.

    If no list of award IDs is passed in, all will be used.
    Optionally write each vector to a text file.
    Optionally pickle each vector for quick loading later.

    @param awards: list of award IDs to parse abstracts for
    @type  awards: list of str

    @param write_vec: whether or not to write the abstract vectors
    @type  write_vec: bool

    @param pickle_vec: whether or not to pickle the abstract vectors
    @type  pickle_vec: bool

    @returns: dictionary of (award: vectorized abstract) pairs
    @rtype:   dict of (list of str)

    """
    if awards is not None:
        selector = AWD_ABSTRACT_FRAME['award_id'].isin(awards)
        df = AWD_ABSTRACT_FRAME[selector]
    else:
        df = AWD_ABSTRACT_FRAME

    for award_id, abstract in df.values:
        vec = doctovec.vectorize(abstract)
        records[award_id] = vec

        if write_vec:
            data.write_abstract_vec(vec, award_id)

        if pickle_vec:
            data.save_abstract_vec(vec, award_id)

        abstracts_parsed +=1
        print abstracts_parsed

    print "Total # abstracts parsed: {}".format(abstracts_parsed)
    return records


def bow_for_pi(pi_id, parse=False):
    """
    Get the representative BoW frequency distribution for the PI. By
    default, load the BoW from a saved file. This can be overriden by
    setting `parse` = True.

    @param pi_id: the ID of the PI to parse the BoW for
    @type  pi_id: str

    @param parse: whether or not to parse the BoW from the raw data; by
                  default, this is False, which means the BoW is loaded
                  from a saved file.
    @type  parse: bool

    @returns: the BoW frequency distribution parsed
    @rtype:   L{gensim.corpora.dictionary.Dictionary}

    """
    abstracts = []
    awards = awards_for_pi(pi_id)

    if parse:

        # get all pre-parsed abstracts from their pickle files
        for award_id in awards:
            abstracts.append(data.load_abstract_vec(award_id))

        # parse documents into BoW representation
        bow = gensim.corpora.dictionary.Dictionary(abstracts)
    else:
        bow = data.read_bow(pi_id)

    return bow


def parse_bow(pi_ids=None, write=True):
    """
    For each PI in the dataset, parse out the list of abstracts (one for each
    award worked on) into a BoW frequency distribution. Optionally write the
    BoW to a text file.

    @param pi_ids: list of PI IDs to parse BoWs for; if none is passed, all
                   will be used
    @type  pi_ids: list of str

    @param write: whether or not to write the abstract vectors
    @type  write: bool

    """
    if pi_ids is not None:
        selector = PI_AWD_FRAME['pi_id'].isin(pi_ids)
        df = PI_AWD_FRAME[selector]
    else:
        df = PI_AWD_FRAME

    pis_parsed = 0
    for pi_id in df.values:
        abstracts = []
        awards = awards_for_pi(pi_id)

        # get all pre-parsed abstracts from their pickle files
        for award_id in awards:
            abstracts.append(data.load_abstract_vec(award_id))

        # parse documents into BoW representation
        bow = gensim.corpora.dictionary.Dictionary(abstracts)

        # write BoW to text files for this PI
        if write:
            data.write_bow(bow, pi_id)

        pis_parsed += 1
        print pis_parsed

    print "Total # PIs parsed: {}".format(pis_parsed)


def full_bow():
    """
    Load BoW dictionaries for all PIs and combine them to form a BoW
    for the complete dataset (all abstracts).

    @returns: the full BoW
    @rtype:   L{gensim.corpora.dictionary.Dictionary}

    """
    corpus = AbstractsCorpus()
    return gensim.corpora.dictionary.Dictionary(corpus)


class AbstractsCorpus(object):
    """Corpus class that yields abstracts as documents."""

    def __init__(self, parse=False):
        """
        If parse is True, the abstracts are parsed from the full abstracts.
        Otherwise, they are loaded from the pickle files.

        @param parse: whether to parse abstracts from loaded abstracts or
                      load from pickle files
        @type  parse: bool

        """
        self._parse = parse
        self._abstracts = AWD_ABSTRACT_FRAME['abstract'].values
        self._award_ids = AWD_ABSTRACT_FRAME['award_id'].values
        self._df = AWD_ABSTRACT_FRAME

    def __iter__(self):
        if self._parse:
            for abstract in self._abstracts:
                yield doctovec.vectorize(abstract)
        else:
            for award_id in self._award_ids:
                yield data.load_abstract_vec(award_id)

    def __getitem__(self, i):
        return self._abstracts[i]

    def __len__(self):
        return len(self._abstracts)

    def __str__(self):
        msg = "Corpus of {} abstracts from NSF grant awards."
        return msg.format(self.__len__())

    def head(self, num):
        return self._abstracts[:num]

    def tail(self, num):
        return self._abstracts[-num:]

    def award(self, award_id):
        selector = self._df['award_id'] == str(award_id)
        result = self._df[selector]['abstract'].values
        if len(result) == 1:
            return result[0]
        else:
            return ''


class BoWCorpusWrapper(object):
    """Wrap up a corpus to return BoW representations of documents."""

    def __init__(self, corpus):
        self._corpus = corpus
        self._dictionary = gensim.corpora.dictionary.Dictionary(corpus)

    def __iter__(self):
        for doc in self._corpus:
            yield self._dictionary.doc2bow(doc)


def run_lda():
    corpus = AbstractsCorpus()
    bow_corpus = BoWCorpusWrapper(corpus)
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

    The files are written to the world data directory using the topic
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


if __name__ == "__main__":
    parse_bow()

