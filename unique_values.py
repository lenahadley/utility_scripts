#!/usr/bin/env python

__version__ = '0.1'
__date__ = '09-06-2024'
__author__ = 'D.J.BERGER'

###### Imports

import argparse
import random
import csv


###### Functions

# Read file and subset rows
def parse_file(file_path, col, mode):
	unique_values = {}
	with open(file_path, 'r') as file:
		reader = csv.DictReader(file, delimiter='\t')
		for row in reader:
			value = row[col]
			if value not in unique_values:
				unique_values[value] = row
			elif mode == 'random':
				if random.choice([True, False]):
					unique_values[value] = row
	return list(unique_values.values())



# Parse arguments from the command line.
def parse_args():
	parser = argparse.ArgumentParser(description='Parse a tab-separated file and return unique rows based on a specified column.')
	parser.add_argument('--input', required=True, help='Path to the input file')
	parser.add_argument('--col', required=True, help='Column name to find unique values')
	parser.add_argument('--mode', required=True, choices=['first', 'random'], help='Mode to select unique values: "first" or "random"')

	return parser.parse_args()


###### Main

def main():
	args = parse_args()

	unique_rows = parse_file(args.input, args.col, args.mode)

	for row in unique_rows:
		print('\t'.join([row[col] for col in row]))

if __name__ == '__main__':
	main()
