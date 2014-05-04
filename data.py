"""
This module contains methods used for parsing through the data
by year, month, awardID, etc. It's basically just here to help
with retrieving the files of interest to a particular analysis.

"""
import os
import json


DATA_DIR = os.path.join(os.getcwd(), 'data')
GRAPH_SAVE_DIR = os.path.join(DATA_DIR, 'pi-award-graphs')
JSON_FILES = {}

# parse data directory for list of JSON files
for filename in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, filename)
    if os.path.isfile(path) and path.endswith('.json'):
        without_extension = filename.split('.')[0]
        _, year, month = without_extension.split('-')

        year = int(year)
        month = int(month)

        if not JSON_FILES.has_key(year):
            JSON_FILES[year] = {month: path}
        else:
            JSON_FILES[year][month] = path


def available_years():
    return JSON_FILES.keys()


def available_months(year):
    if JSON_FILES.has_key(year):
        return JSON_FILES[year].keys()
    else:
        return []


def all_files():
    """
    Return a list of absolute paths for all files in the data directory.

    @returns: list of absolute paths for all JSON files in the data directory.
    @rtype:   list of str

    """
    file_list = []
    for year in JSON_FILES:
        for month in JSON_FILES[year]:
            file_list.append(JSON_FILES[year][month])

    return file_list


def filter_files(year_start, year_end=None, month_start=None, month_end=None):
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

    @param year_start: first year in range to get
    @type  year_start: int

    @param year_end: last year in range to get
    @type  year_end: int

    @param month_start: first month in range to get
    @type  month_start: int

    @param month_end: last month in range to get
    @type  month_end: int

    @returns: the list of filepaths in the given range of years/months
    @rtype:   list of str

    """
    file_list = []

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

    for year in years:
        for month in months:
            filepath = get_file(year, month)
            if filepath:
                file_list.append(filepath)

    return file_list


def get_file(year, month=None):
    """
    Retreive the data file path from the month and year.

    @param year: the year to search for
    @type  year: int

    @param month: the month to search for
    @type  month: int

    @returns: the absolute path of the file found, or an empty string if
              there is no data file for that month/year combo
    @rtype:   str

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

    @param filepath: path of the JSON file to parse.
    @type  filepath: str

    @returns: dict parsed from JSON file
    @rtype:   dict

    """
    with open(filepath) as json_file:
        return json.load(json_file)


def save_graph(graph, filename):
    """
    Save the graph to the appropriate data directory using
    graphml format.

    """
    with_extension = filename + '.graphml'
    graph_file = os.path.join(GRAPH_SAVE_DIR, with_extension)
    with open(graph_file, 'w') as f:
        print 'Saving graph to file.'
        print 'Graph:\n{}\nFile: {}'.format(graph.summary(), graph_file)
        graph.save(f, format='graphml')


def load_graph(filename):
    """
    Load a graph from its saved graphml file.

    """
    with_extension = filename + '.graphml'
    graph_file = os.path.join(GRAPH_SAVE_DIR, with_extension)
    with open(graph_file, 'r') as f:
        return igraph.load(graph_file)

