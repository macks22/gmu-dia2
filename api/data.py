"""
This module contains methods used for parsing through the data
by year, month, awardID, etc. It's basically just here to help
with retrieving the files of interest to a particular analysis.

"""
import os
import gensim
import cPickle as pickle

import igraph

try:
    # roughly 2x faster
    import ujson as json
except ImportError:
    # builtin
    import json


# -----------------------------------------------------------------------------
# MODULE SETUP
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.getcwd(), 'data')
JSON_DIR = os.path.join(DATA_DIR, 'json')
GRAPH_SAVE_DIR = os.path.join(DATA_DIR, 'pi-award-graphs')
PICKLE_DIR = os.path.join(DATA_DIR, 'pickle')
BOW_DIR = os.path.join(DATA_DIR, 'bow')
WORDLE_DIR = os.path.join(DATA_DIR, 'wordle')
JSON_FILES = {}


def _parse_all_data():
    """
    Parse data directory for list of JSON files.
    This is designed to set up the global variables in this module.

    """
    for filename in os.listdir(JSON_DIR):
        path = os.path.join(JSON_DIR, filename)
        if os.path.isfile(path) and path.endswith('.json'):
            without_extension = filename.split('.')[0]
            _, year, month = without_extension.split('-')

            year = int(year)
            month = int(month)

            if not JSON_FILES.has_key(year):
                JSON_FILES[year] = {month: path}
            else:
                JSON_FILES[year][month] = path


# parse data directory for list of JSON files
_parse_all_data()

# -----------------------------------------------------------------------------


def available_years():
    """
    Get the list of all years there is data for.

    @rtype:  list of str
    @return: A chronologically ordered list of all years there is
        data for.

    """
    return JSON_FILES.keys()


def available_months(year):
    """
    Get the list of all months there is data for in a particular
    year.

    @type  year: str
    @param year: The year to check available months for.

    @rtype:  list of str
    @return: A list of all months for which there is data in the
        given year; will be empty if none are available.

    """
    if JSON_FILES.has_key(year):
        return JSON_FILES[year].keys()
    else:
        return []


def awards():
    """
    A generator that parses each JSON file and yields each subsequent
    chunk of award data. JSON files are read chronologically. Files
    are parsed one at a time (lazy loaded), so that the maximum
    memory used at any point is bounded by the size of the largest
    JSON data file.

    @rtype:  iterator yielding dict
    @return: An iterator which yields award dictionaries parsed from
        the raw JSON files.

    """
    for year in JSON_FILES:
        for month in JSON_FILES[year]:
            json_filepath = JSON_FILES[year][month]
            print "Parsing file {}".format(json_filepath)
            json_data = load_json(json_filepath)

            # 1:1 mapping for document IDs and award IDs
            for doc_id in json_data:
                yield json_data[doc_id]


def abstracts():
    """
    A generator that parses each JSOn file and yields each subsequent
    abstract as it is encountered. JSON files are read chronologically.
    Files are lazy loaded in order to conserve memory. See L{awards}
    for more detail.

    @rtype:  iterator yielding str
    @return: An iterator which yields abstracts as they are read from
        the awards, which are read from the JSON files in
        chronological order.

    """
    for award in awards():
        yield award['abstract']


def all_files():
    """
    Return a list of absolute paths for all files in the data
    directory.

    @rtype:   list of str
    @returns: A list of absolute paths for all JSON files in the data
        directory.

    """
    file_list = []
    for year in JSON_FILES:
        for month in JSON_FILES[year]:
            file_list.append(JSON_FILES[year][month])

    return file_list


def filter_files(year_start, year_end=None, month_start=None, month_end=None,
        file_limit=None):
    """
    Filter the list of JSON files by year and month, allowing
    for a possible range of dates based on month/year.

    If a year_start is included but no year_end, only files for
    year_start will be selected. Same goes for month_start. Note
    that if month_end is given but not month_start, it will be
    ignored silently.

    Note that the range of months given will be used for each
    year. This function does not allow you to pick different
    months for each year in the range.

    @type  year_start: int
    @param year_start: First year in range to parse.

    @type  year_end: int
    @param year_end: Last year in range to parse.

    @type  month_start: int
    @param month_start: First month in range to parse.

    @type  month_end: int
    @param month_end: Last month in range to parse.

    @rtype:  list of str
    @return: The list of filepaths in the given range of
        years/months.

    """
    if year_end is None:
        years = [year_start]
    else:
        years = range(year_start, year_end + 1)

    # 4 possible combos for month_start and month_end
    # silently ignore month_end when no month_start is given
    if month_end is None and month_start is not None:
        months = [month_start]
    elif month_start is None:
        months = range(1,13)
    else:
        months = range(month_start, month_end + 1)

    files_parsed = 0
    for year in years:
        for month in months:
            filepath = get_file(year, month)
            if filepath:
                print "Parsing file {}".format(filepath)
                json_data = load_json(filepath)
                for doc_id in json_data:
                    yield json_data[doc_id]

                files_parsed += 1
                if file_limit is not None and (files_parsed) > file_limit:
                    break

    print "Number of files parsed: {}".format(files_parsed)


def get_file(year, month=None):
    """
    Retreive the data file path from the month and year.

    @type  year: int
    @param year: The year to search for.

    @type  month: int
    @param month: The month to search for.

    @rtype:   str
    @returns: The absolute path of the file found, or an empty string if
        there is no data file for that month/year combo.

    """
    if JSON_FILES.has_key(year):
        if month is not None:
            if JSON_FILES[year].has_key(month):
                return JSON_FILES[year][month]
        else:
            return JSON_FILES[year].values()

    return ""


def load_json(filepath):
    """
    Load a JSON string from a file.

    @type  filepath: str
    @param filepath: The path of the JSON file to parse.

    @rtype:   dict
    @returns: Dictionary parsed from JSON file.

    """
    with open(filepath) as json_file:
        return json.load(json_file)


def save_graph(graph, filename):
    """
    Save the graph to the appropriate data directory using
    GraphML format.

    @type  graph: L{igraph.Graph}
    @param graph: The graph instance to be saved.

    @type  filename: str
    @param filename: The name of the file to save the graph to.

    """
    with_extension = filename + '.graphml'
    graph_file = os.path.join(GRAPH_SAVE_DIR, with_extension)
    with open(graph_file, 'w') as f:
        print 'Saving graph to file.'
        print 'Graph:\n{}\nFile: {}'.format(graph.summary(), graph_file)
        graph.save(f, format='graphml')


def load_graph(filename):
    """
    Load a graph from its saved GraphML file.

    @type  filename: str
    @param filename: The name of the file to load the graph from.

    @rtype:  L{igraph.Graph}
    @return: The graph instance loaded from the file.

    """
    with_extension = filename + '.graphml'
    graph_file = os.path.join(GRAPH_SAVE_DIR, with_extension)
    with open(graph_file, 'r') as f:
        return igraph.load(graph_file)


def load_full_graph():
    """
    Load the complete directorate 5 data graph from its pickle file.

    @rtype:   L{igraph.Graph}
    @return: The graph for all directorate 5 data, with vertices
        for each PI and an edge for each shared awardID.

    """
    graph_path = os.path.join(PICKLE_DIR, 'dir05-graph.pickle')
    return igraph.load(graph_path)


def save_full_graph(g):
    """
    Save the full directorate 05 graph to a pickle file.

    @type  g: L{igraph.Graph}
    @param g: The graph instance to save

    """
    graph_path = os.path.join(PICKLE_DIR, 'dir05-graph.pickle')
    g.write_pickle(graph_path)


#TODO: add exception handling for no file found
def load_abstract_vec(award_id):
    """
    Load the pickled abstract vector for the given award id.

    @type  award_id: str, unicode, or int
    @param award_id: The award id to load the abstract for.

    @rtype:   list of str
    @returns: The loaded abstract vector.

    """
    filename = 'award-{}.pickle'.format(award_id)

    path = os.path.join(PICKLE_DIR, 'bow/{}'.format(filename))
    with open(path, 'r') as f:
        return pickle.load(f)


def save_abstract_vector(vec, award_id):
    """
    Save the vectorized abstract for the given award_id by pickling it. The
    award ID is required because the filename convention is based on the award
    ID::

        award-<award_id>.pickle

    @type  vec: list of str
    @param vec: The vectorized abstract.

    @type  award_id: str
    @param award_id: The award id to base the filename off of.

    """
    filename = 'award-{}.pickle'.format(award_id)
    path = os.path.join(PICKLE_DIR, 'bow/{}'.format(filename))
    with open(path, 'w') as f:
        pickle.dump(vec, f)


def write_abstract_vector(vec, award_id):
    """
    Save the vectorized abstract for the given award_id by writing it to a text
    file. The award ID is required because the filename convention is based on
    the award ID::

        award-<award_id>.txt

    @type  vec: list of str
    @param vec: The vectorized abstract to write to a file.

    @type  award_id: str
    @param award_id: The award id to base the filename off of.

    """
    filename = 'award-{}.txt'.format(award_id)
    path = os.path.join(BOW_DIR, filename)
    with open(path, 'w') as f:
        for word in vec:
            f.write('{}\n'.format(word))


#TODO: add exception handling for no file found
def read_abstract_vector(award_id):
    """
    Read the abstract vector for the given award id.

    @type  award_id: str, unicode, or int
    @param award_id: The award id to read the abstract for.

    @rtype:  list of str
    @return: The loaded abstract vector.

    """
    filename = 'award-{}.txt'.format(award_id)
    path = os.path.join(BOW_DIR, filename)
    with open(path, 'r') as f:
        content = f.read()

    return content.split('\n')


def write_bow(bow, pi_id):
    """
    Write the BoW frequency distribution for the given PI to a text
    file.

    @type  bow: L{gensim.Dictionary}
    @param bow: The BoW to write.

    @type  pi_id: str
    @param pi_id: ID of the PI this BoW represents.

    """
    filename = 'pi-{}.txt'.format(pi_id)
    path = os.path.join(BOW_DIR, filename)
    bow.save_as_text(path)


def read_bow(pi_id):
    """
    Read the BoW frequency distribution for the given PI.

    @type  pi_id: str
    @param pi_id: ID of the PI to read BoW for

    @rtype:  list of (tuple of (int, int))
    @return: The BoW read for the given PI.

    """
    filename = 'pi-{}.txt'.format(pi_id)
    path = os.path.join(BOW_DIR, filename)
    return gensim.corpora.dictionary.Dictionary.load_from_text(path)


def load_lda_model():
    """
    Load the gensim LDA model for the directorate 05 dataset abstracts
    from its pickle file in the data directory.

    @rtype:   L{gensim.models.LdaModel}
    @returns: The loaded LDA model.

    """
    filename = 'lda-model-from-abstracts.pickle'
    path = os.path.join(PICKLE_DIR, filename)
    return gensim.models.LdaModel.load(path)


def write_wordle_file(topic_num, topic):
    """
    Write a word frequency file which can be copy/pasted into wordle.net
    given a topic, which is a list of the form::

        [('electron', 50), ('molecule', 20)]

    Specifically, the topic is a list of tuples, where the first element
    of each tuple is the word and the second is the frequency of the word.

    @type  topic_num: int
    @param topic_num: The number of the topic from the LDA model.

    @type  topic: list of (tuple of (str, int))
    @param topic: The topic to write to a wordle-recognizable text
        file.

    """
    filename = 'lda-topic{}.txt'.format(topic_num)
    path = os.path.join(WORDLE_DIR, filename)
    with open(path, 'w') as f:
        for word_and_freq in topic:
            f.write('{}:{}\n'.format(word_and_freq[0], word_and_freq[1]))
