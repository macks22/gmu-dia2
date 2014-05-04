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

    # parse the list of JSON files from the data directory
    json_data_file_list = data.filter_files(year_start, year_end,
            month_start, month_end)
    g = igraph.Graph()

    files_parsed = 0
    for json_filepath in json_data_file_list:
        json_data = data.load_json(json_filepath)
        for key in json_data.keys():
            award_data = json_data[key]

            # get list of PIs from JSON data; add all to graph
            pi_list = [int(pi_id) for pi_id in award_data['PIcoPI']]
            g.add_vertices(pi_list)

            # get ids of vertices we just added
            pi_vertex_ids = []
            for pi_id in pi_list:
                vertex = g.vs.find(name_eq=pi_id)
                vertex['label'] = pi_id  # add label for graphing
                pi_vertex_ids.append(vertex.index)

            # we now have the actual vertex ids of each PI; we want to
            # add an edge for each with the awardId as an attribute, so
            # we get all possible combinations of 2 (n choose 2), then
            # add an edge for each
            vid_iterator = itertools.combinations(pi_vertex_ids, 2)
            pi_combos = [vid for vid in vid_iterator]
            g.add_edges(pi_combos)

            # now add the award id as an attribute on each new edge
            award_id = int(award_data['awardID'])
            new_eids = g.get_eids(pi_combos)
            for eid in new_eids:
                new_edge = g.es.find(eid)

                new_edge['awardID'] = award_id
                new_edge['label'] = award_id  # add label for graphing

                new_edge['abstract'] = award_data['abstract'].encode('utf-8')
                new_edge['title'] = award_data['title'].encode('utf-8')
                new_edge['effectiveDate'] = award_data['effectiveDate']
                new_edge['expirationDate'] = award_data['expirationDate']
                new_edge['PO'] = award_data['PO']

                # TODO: there's sometimes more than one dir, div, pgm set
                funding_agent = award_data['fundingAgent'][0]
                new_edge['dir'] = funding_agent['dir']['id']
                new_edge['div'] = funding_agent['div']['id']
                new_edge['pgm'] = funding_agent['pgm']['id']

            #print "award_id: {}".format(award_id)
            #print "pi list: {}".format(pi_list)
            #print "new edge list: {}".format(pi_combos)
            #print "number of vertices: {}".format(len(g.vs))
            #print "number of edges: {}".format(len(g.es))

        files_parsed += 1
        if file_limit is not None and (files_parsed) > file_limit:
            break

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

