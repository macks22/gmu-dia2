import os
import ast
import itertools

import igraph

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
        file_limit=None):
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

    @param year_start: first year in range to get
    @type  year_start: int

    @param year_end: last year in range to get
    @type  year_end: int

    @param month_start: first month in range to get
    @type  month_start: int

    @param month_end: last month in range to get
    @type  month_end: int

    """
    g = igraph.Graph()

    # parse the list of JSON files from the data directory
    json_data_file_list = data.filter_files(year_start, year_end,
            month_start, month_end)

    pis_seen_set = set()
    files_parsed = 0
    for json_filepath in json_data_file_list:
        print "Parsing file {}".format(json_filepath)

        json_data = data.load_json(json_filepath)
        for doc_id in json_data.keys():
            award_data = json_data[doc_id]

            # get list of PIs from JSON data; add all to graph
            pi_set = set()
            for pi_id in award_data['PIcoPI']:
                pi_id = str(pi_id)
                pi_set.add(pi_id)

                if pi_id not in pis_seen_set:
                    g.add_vertex(pi_id, label=pi_id, id=pi_id)
                    pis_seen_set.add(pi_id)

            # pair up every PI with every other for this award
            pi_combos = itertools.combinations(pi_set, 2)

            # TODO: there's sometimes more than one dir, div, pgm set
            funding_agent = award_data['fundingAgent'][0]
            award_id = str(award_data['awardID'])

            # Yes, this is quite a lot of duplicate information being
            # added to the graph. It is yet to be seen whether or not
            # it is truly useful to do this. It is mostly for
            # convenience. It would be better to only add 'awardID' and
            # 'label', then look up the rest in tables.
            edge_attributes = {
                'awardID': award_id,
                'label': award_id,
                'abstract': award_data['abstract'].encode('utf-8'),
                'title': award_data['title'].encode('utf-8'),
                'effectiveDate': award_data['effectiveDate'],
                'expirationDate': award_data['expirationDate'],
                'PO': award_data['PO'],
                'dir': funding_agent['dir']['id'],
                'div': funding_agent['div']['id'],
                'pgm': funding_agent['pgm']['id']
            }

            for edge in pi_combos:
                g.add_edge(edge[0], edge[1], **edge_attributes)

            #print "award_id: {}".format(award_id)
            #print "pi list: {}".format(pi_list)
            #print "new edge list: {}".format(pi_combos)
            #print "number of vertices: {}".format(len(g.vs))
            #print "number of edges: {}".format(len(g.es))

        files_parsed += 1
        if file_limit is not None and (files_parsed) > file_limit:
            break

    print "Number of files parsed: {}".format(files_parsed)
    return g


def parse_all_files_for_pivalues():
    """
    This parses all files for IDs of all PIs and coPIs. Both are
    treated the same since we have no way to distinguish between the
    two.

    @returns: list of all PI and coPI IDs found
    @rtype:   list of int

    """
    json_data_file_list = data.all_files()
    pi_list = []
    for filename in json_data_file_list:
        json_data = data.load_json(filename)
        for key in json_data.keys():
            pi_list += [int(pi_id) for pi_id in json_data[key]['PIcoPI']]

    return pi_list


if __name__ == "__main__":
    save_graphs_for_each_year()

