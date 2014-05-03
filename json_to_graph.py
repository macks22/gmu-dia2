import os
import ast
import json
import itertools

import igraph


DATA_DIR = "./data"


def main():

    # parse the list of JSON files from the data directory
    json_data = get_json_files(DATA_DIR)
    g = igraph.Graph()

    files_parsed = 0
    for filename in json_data:
        data = parse_json_file(filename)
        for key in data.keys():

            # get list of PIs from JSON data; add all to graph
            pi_list = [int(pi_id) for pi_id in data[key]['PIcoPI']]
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
            award_id = int(data[key]['awardID'])
            new_eids = g.get_eids(pi_combos)
            for eid in new_eids:
                new_edge = g.es.find(eid)
                new_edge['awardID'] = award_id
                new_edge['label'] = award_id  # add label for graphing

            #print "award_id: {}".format(award_id)
            #print "pi list: {}".format(pi_list)
            #print "new edge list: {}".format(pi_combos)
            #print "number of vertices: {}".format(len(g.vs))
            #print "number of edges: {}".format(len(g.es))

        files_parsed += 1
        if (files_parsed) > 100:
            break

    return g


def parse_all_files_for_pivalues(json_data):
    """
    This parses all files for pivalues.

    """
    pi_list = []
    for filename in json_data:
        data = parse_json_file(filename)
        first_layer_keys = [key for key in data.keys()]
        for i in first_layer_keys:
            for j in pi_value:
                pi_list.append(j)
    print "Number of PIs: {}".format(len(pi_list))


def get_json_files(directory):
    json_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.json'):
            json_files.append(filename)
    return json_files


def parse_json_file(filename):
    with open(os.path.join(DATA_DIR,filename)) as f:
        print("Parsing: {0}".format(filename))
        data = json.load(f)
        return data


if __name__ == "__main__":
    g = main()
    print type(g)
    print g.summary()
    igraph.plot(g, bbox=(0,0,1000,1000), layout=g.layout('kk')).show()

