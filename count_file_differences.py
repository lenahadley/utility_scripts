#!/usr/bin/env python

# Compares pairwise difference between files to count changes in rows and columns

__version__ = '0.1'
__date__ = '09-04-2024'
__author__ = 'D.J.BERGER'


###### Imports

import os
import pandas as pd
import numpy as np
import argparse


###### Functions

# Compare files pairwise
def compare_files(file1, file2):
	df1 = pd.read_csv(file1, sep=None, engine='python')
	df2 = pd.read_csv(file2, sep=None, engine='python')

	df1, df2 = df1.align(df2, join='outer', axis=0, fill_value=np.nan)
	df1, df2 = df1.align(df2, join='outer', axis=1, fill_value=np.nan)

	diff_rows = []
	diff_cols = []

	# Compare rows
	df_diff = df1.compare(df2)
	diff_rows = df_diff.index.tolist()

	# Compare columns
	for col in df1.columns:
		if not df1[col].equals(df2[col]):
			diff_cols.append(col)

	return len(diff_rows), len(diff_cols), diff_rows, diff_cols


# Create matrix of differences
def generate_comparison_matrix(file_list1, file_list2, metric):
	matrix = np.zeros((len(file_list1), len(file_list2)), dtype=int)
	
	for i, file1 in enumerate(file_list1):
		for j, file2 in enumerate(file_list2):
			row_diffs, col_diffs, diff_rows, diff_cols = compare_files(file1, file2)
			if metric == "rows":
				matrix[i, j] = row_diffs
			elif metric == "cols":
				matrix[i, j] = col_diffs

	return matrix


# Parse arguments from the command line.
def parse_args():
	description = 'Compare CSV/TSV files in two directories. Version: %s, Date: %s, Author: %s' % (__version__, __date__, __author__)
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument("--dir1", type=str, help="Path to the first directory")
	parser.add_argument("--dir2", type=str, help="Path to the second directory")
	parser.add_argument("--output", type=str, help="Output TSV file for comparison results")
  parser.add_argument('--version', action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


###### Main
def main():
	args = parse_args()
	files1 = [os.path.join(args.dir1, f) for f in os.listdir(args.dir1) if f.endswith('.csv') or f.endswith('.tsv')]
	files2 = [os.path.join(args.dir2, f) for f in os.listdir(args.dir2) if f.endswith('.csv') or f.endswith('.tsv')]

	with open(args.output + '.tsv', 'w') as out:
		out.write("File1\tFile2\tRowDifferences\tColDifferences\tRowNames\tColNames\n")
		
		for file1 in files1:
			for file2 in files2:
				row_diffs, col_diffs, diff_rows, diff_cols = compare_files(file1, file2)
				row_names = ",".join(map(str, diff_rows))
				col_names = ",".join(diff_cols)
				out.write(f"{os.path.basename(file1)}\t{os.path.basename(file2)}\t{row_diffs}\t{col_diffs}\t{row_names}\t{col_names}\n")
	
	row_diff_matrix = generate_comparison_matrix(files1, files2, "rows")
	col_diff_matrix = generate_comparison_matrix(files1, files2, "cols")

	pd.DataFrame(row_diff_matrix, index=[os.path.basename(f) for f in files1], columns=[os.path.basename(f) for f in files2]).to_csv(args.output+'.row_diff_matrix.tsv', sep='\t')
	pd.DataFrame(col_diff_matrix, index=[os.path.basename(f) for f in files1], columns=[os.path.basename(f) for f in files2]).to_csv(args.output+'.col_diff_matrix.tsv', sep='\t')

if __name__ == "__main__":
	main()
