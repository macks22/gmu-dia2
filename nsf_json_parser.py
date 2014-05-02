import json, ast
import os
from StringIO import StringIO
from pprint import pprint
from igraph import *

DIR = "./"

def main():
	pi_dict = {}
	json_data = get_json_files(DIR)
	g = Graph()
#	pprint(json_data)

	for filename in json_data:
		data = parse_file(filename)
		for key in data.keys():
			length = len(data[key]['PIcoPI'])
			print length
			for pi in data[key]['PIcoPI']:
				if type(pi) != int:
					pi = int(pi)
				if pi_dict.has_key(pi) == False:
					pi_dict[pi] = [int(data[key]['awardID'])]
					g.add_vertex(pi)
				else:
					pi_dict.get(pi).append(int(data[key]['awardID']))


	#		pprint(data[key]['awardID'])
	print g
#	pprint(pi_dict)

	#second_layer_keys = []
	#for i in first_layer_keys:
#		second_layer_keys.append(data[i].keys())

def parse_all_files_for_pivalues(json_data):
	pi_list = []
	for filename in json_data:
		data = parse_file(filename)
		first_layer_keys = build_key_list(data)
		for i in first_layer_keys:
			pi_dict
			for j in pi_value:
				pi_list.append(j)
	print len(pi_list)
	print len(list(set(pi_list)))	

def build_key_list(data):
	my_list = []
	for i in data.keys():
		my_list.append(i)
	return my_list

def get_json_files(directory):
	return [file for file in os.listdir(directory) if file.lower().endswith('.json')]
	
def parse_file(filename):
	with open(os.path.join(DIR,filename)) as f:
		print("Parsing: {0}".format(filename))
		data = json.load(f)
		return data

if __name__=="__main__": 
	main()