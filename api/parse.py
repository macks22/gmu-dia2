"""
This module contains functions for parsing data from the raw JSON
files and loading parsed data from saved pickle files. It is meant
to act as the main parsing interface on top of the raw data.
Eventually, the vision is to have each "Data object" be retreivable
via two possible methods: parse & load. The parsing functionality
will be present in this module, while the loading functionality
will exist in the L{data} module.

Currently, things are a bit more messy than that, and there is
some of both parsing and loading functionality in this module.

"""
import os
import string
import itertools

import nltk
import igraph
import pandas as pd

import data


def save_graphs_for_each_year():
    """
    Create a graph for each year of data and save the graphs in
    GraphML format.

    """
    for year in data.available_years():
        g = pi_award_graph(year)
        filename = str(year)
        data.save_graph(g, filename)


def pi_award_graph(year_start, year_end=None, month_start=None, month_end=None,
        file_limit=None, all_edge_attributes=True):
    """
    Parse the json files for the given years/months into an igraph
    Graph object. The graph is constructed by creating a vertex for
    every PIcoPI ID and an edge for every collaborative effort
    between PIs. In particular, for each awardID, if there is more
    than 1 PIcoPI, an edge is formed between each PI for that awardID
    to every other PI for that awardID.  coPIs are treated the same
    as PIs.

    If a year_start is included but no year_end, only files for
    year_start will be selected. Same goes for month_start. Note that
    if month_end is given but not month_start, it will be ignored
    silently.

    Note that the range of months given will be used for each year.
    This function does not allow you to pick different months for
    each year in the range.

    @type  year_start: int
    @param year_start: First year in range to parse.

    @type  year_end: int
    @param year_end: Last year in range to parse.

    @type  month_start: int
    @param month_start: First month in range to parse.

    @type  month_end: int
    @param month_end: Last month in range to parse.

    @type  file_limit: int
    @param file_limit: Limits the number of files parsed; note
        this option overrides the year/month params

    @type  all_edge_attributes: bool
    @param all_edge_attributes: If False, only the awardID is added
        as an attribute for each, otherwise
        everything is; default is True.

    @rtype:   L{igraph.Graph}
    @returns: Graph constructed from JSON data files parsed.

    """
    g = igraph.Graph()

    # parse the list of JSON files from the data directory
    awards = data.filter_files(year_start, year_end,
                month_start, month_end, file_limit)

    pis_seen_set = set()
    for award_data in awards:

        # get list of PIs from JSON data; add all to graph
        pi_set = set()
        for pi_id in award_data['PIcoPI']:
            pi_id = str(pi_id)
            pi_set.add(pi_id)

            if pi_id not in pis_seen_set:
                g.add_vertex(pi_id, label=pi_id)
                pis_seen_set.add(pi_id)

        # pair up every PI with every other for this award
        pi_combos = itertools.combinations(pi_set, 2)
        award_id = str(award_data['awardID'])

        # Yes, this is quite a lot of duplicate information being
        # added to the graph. It is yet to be seen whether or not
        # it is truly useful to do this. It is mostly for
        # convenience. It may be better to only add 'awardID' and
        # 'label', then look up the rest in tables.
        if all_edge_attributes:

            # TODO: add all funding agents rather than just 05
            for agent in award_data['fundingAgent']:
                if agent['dir']['id'].strip() == '05':
                    funding_agent_dir = '05'
                    funding_agent_div = agent['div']['id']
                    funding_agent_pgm = agent['pgm']['id']
                    break

            edge_attributes = {
                'awardID': award_id,
                'label': award_id,
                'abstract': award_data['abstract'].encode('utf-8'),
                'title': award_data['title'].encode('utf-8'),
                'effectiveDate': award_data['effectiveDate'],
                'expirationDate': award_data['expirationDate'],
                'PO': award_data['PO'],
                'dir': funding_agent_dir,
                'div': funding_agent_div,
                'pgm': funding_agent_pgm
            }
        else:
            edge_attributes = {
                'awardID': award_id,
                'label': award_id
            }

        for edge in pi_combos:
            g.add_edge(edge[0], edge[1], **edge_attributes)

        #print "award_id: {}".format(award_id)
        #print "pi set: {}".format(pi_set)
        #print "new edge list: {}".format(pi_combos)
        #print "number of vertices: {}".format(len(g.vs))
        #print "number of edges: {}".format(len(g.es))

    return g


def parse_full_graph():
    """
    Parse through all data and save it to a pickle file.

    @rtype:  L{igraph.Graph}
    @return: The graph which was parsed from the full dataset.

    """
    years = data.available_years()
    g = pi_award_graph(min(years), max(years))
    data.save_full_graph(g)
    return g


def all_pi_ids_from_files():
    """
    This parses all files for IDs of all PIs and coPIs. Both are
    treated the same since we have no way to distinguish between the
    two.

    @rtype:   list of int
    @return:  List of all PI IDs found.

    """
    json_data_file_list = data.all_files()
    pi_ids = set()
    for filename in json_data_file_list:
        json_data = data.load_json(filename)
        for key in json_data.keys():
            for pi_id in json_data[key]['PIcoPI']:
                pi_ids.add(str(pi_id))

    return pi_ids


def all_pi_ids(g):
    """
    Parse the graph to get the set of all PI IDs.

    @type  g: L{igraph.Graph}
    @param g: Graph to parse for PI IDs.

    @rtype:   set
    @returns: Set of all PI IDs in the graph (for all vertices).

    """
    return set([v['name'] for v in g.vs])


def parse_funding_agents():
    """
    Parse all funding agents from the JSON files. We can't use
    the graph for this, because awards with only one PI do not
    have edges in the pi_award_graph.

    The following 10 fields are included for each funding agent record:

        1.  pi_id    : PIcoPI ID
        2.  award_id : award ID
        3.  dir_id   : directoarte ID
        4.  dir_name : directorate name
        5.  dir_abbr : directorate name abbreviation
        6.  div_id   : division ID
        7.  div_name : division name
        8.  div_abbr : division name abbreviation
        9.  pgm_id   : program ID
        10. pgm_name : program name


    @rtype:   L{pandas.DataFrame}
    @return:  A data frame with the 10 fields listed above.

    """
    all_records = []
    columns = [
        'pi_id', 'award_id',
        'dir_id', 'dir_name', 'dir_abbr',
        'div_id', 'div_name', 'div_abbr',
        'pgm_id', 'pgm_name'
    ]

    # parse the list of JSON files from the data directory
    for award_data in data.awards():
        records_for_award = _parse_funding_agent(award_data)
        all_records += records_for_award

    return pd.DataFrame(all_records, columns=columns)


def _parse_funding_agent(award_data):
    records = []
    pi_ids = [str(pi_id) for pi_id in award_data['PIcoPI']]

    # add a record for every funding agent / PI combo
    for agent in award_data['fundingAgent']:
        agent_dir = agent['dir']
        agent_div = agent['div']
        agent_pgm = agent['pgm']

        record = [
            str(award_data['awardID']),
            agent_dir['id'],
            agent_dir['name'],
            agent_dir['abbr'],
            agent_div['id'],
            agent_div['name'],
            agent_div['abbr'],
            agent_pgm['id'],
            agent_pgm['name']
        ]

        for pi_id in pi_ids:
            records.append([pi_id] + record)

    return records


def frame_pi_award_pairings():
    """
    Return a data frame with records for each PI for each award they
    worked on.

    @rtype:   L{pandas.DataFrame}
    @return:  DataFrame with pi_id and award_id columns.

    """
    records = []
    for award_data in data.awards():
        award_id = str(award_data['awardID'])
        pi_list = [str(pi_id) for pi_id in award_data['PIcoPI']]
        for pi_id in pi_list:
            records.append((pi_id, award_id))

    return pd.DataFrame(records, columns=['pi_id', 'award_id'])


def frame_abstracts():
    """
    Parse all abstracts into a DataFrame, indexed by award ids.

    @rtype:   L{pandas.DataFrame}
    @return:  DataFrame of abstracts, indexed by award ids.

    """
    records = []
    for award_data in data.awards():
        award_id = str(award_data['awardID'])
        abstract = award_data['abstract'].encode('utf-8')
        records.append((award_id, abstract))

    df = pd.DataFrame(records.items(), columns=['award_id', 'abstract'])
    return df.set_index('award_id')


if __name__ == "__main__":
    save_graphs_for_each_year()

