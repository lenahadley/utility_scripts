#!/usr/bin/env python

__version__ = '0.1'
__date__ = '09-04-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import argparse
import pandas as pd
import numpy as np
from sklearn.metrics import adjusted_rand_score
from itertools import combinations


###### Functions

# Determine if input file is comma or tab separated
def detect_delimiter(file_path):
	with open(file_path, 'r') as file:
		first_line = file.readline()
		if ',' in first_line:
			return ','
		elif '\t' in first_line:
			return '\t'
		else:
			raise ValueError("Unknown file format. File must be CSV or TSV.")


# Creates a dict mapping samples to cluster IDs
def read_clustering(file_path):
	delimiter = detect_delimiter(file_path)
	clustering = pd.read_csv(file_path, delimiter=delimiter, header=None, names=['sample', 'cluster_ID'])
	return clustering.set_index('sample').to_dict()['cluster_ID']


# Computes Adjusted Rand Index, pairwise, use only common samples
def compute_ari(clusterings, files):
	aris = []
	for (i, j) in combinations(range(len(clusterings)), 2):
		common_samples = set(clusterings[i].keys()).intersection(clusterings[j].keys())
		labels1 = [clusterings[i][sample] for sample in common_samples]
		labels2 = [clusterings[j][sample] for sample in common_samples]
		if len(labels2) <2 or len(labels1) <2:
			break
		ari = adjusted_rand_score(labels1, labels2)
		aris.append((files[i], files[j], ari))
	return aris


# Parse arguments from the command line.
def parse_args():
	description = 'Calculate Adjusted Rand Index between multiple clustering schemes. Version: %s, Date: %s, Author: %s' % (__version__, __date__, __author__)
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('files', nargs='+', help="Paths to the clustering files (CSV or TSV).")
	parser.add_argument('--matrix-output', default='ari_matrix.csv', help="Output file for pairwise ARI matrix.")
	parser.add_argument('--list-output', default='ari_list.csv', help="Output file for ARI values list.")
	parser.add_argument("--version", action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


###### Main
def main():
	args = parse_args()

	if len(args.files) < 2:
		raise ValueError("At least two clustering files are required.")

	# Read clusterings
	clusterings = [read_clustering(file) for file in args.files]

	# Compute ARIs
	aris = compute_ari(clusterings, args.files)

	num_files = len(args.files)
	ari_matrix = np.empty((num_files, num_files))
	ari_matrix[:] = np.nan

	for (file1, file2, ari) in aris:
		i = args.files.index(file1)
		j = args.files.index(file2)
		ari_matrix[i, j] = ari_matrix[j, i] = ari

	# Write ARI matrix to file
	ari_matrix_df = pd.DataFrame(ari_matrix, index=args.files, columns=args.files)
	for i in range(num_files):
		ari_matrix[i,i] = 1.0
	ari_matrix_df.to_csv(args.matrix_output)

	# Write ARI list to file
	with open(args.list_output, 'w') as f:
		f.write("File1,File2,ARI\n")
		for (file1, file2, ari) in aris:
			f.write(f"{file1},{file2},{ari:.4f}\n")

	print(f"Pairwise ARI matrix saved to {args.matrix_output}")
	print(f"List of ARI values saved to {args.list_output}")

if __name__ == "__main__":
	main()
