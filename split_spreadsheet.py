#!/usr/bin/env python

# Splits Excel spreadsheets with multiple tabs into individual CSV or TSV files. 

__version__ = '0.1'
__date__ = '03-03-2024'
__author__ = 'D.J.BERGER'


###### Imports
import pandas as pd
import os
import argparse


###### Functions

# Removes spaces from sheet names
def sanitize_sheet_name(sheet_name):
	return sheet_name.replace(" ", "")


# Takes Excel spreasheet and writes each sheet to an individual file, in an output directory.
def split_excel(excel_file_path, output_directory, output_format):
	# Read the Excel file
	excel_data = pd.ExcelFile(excel_file_path)

	# Create output directory if it doesn't exist
	os.makedirs(output_directory, exist_ok=True)

	# Determine the file extension and separator based on the output format
	if output_format == 'csv':
		file_extension = '.csv'
		separator = ','
	elif output_format == 'tsv':
		file_extension = '.tsv'
		separator = '\t'
	else:
		raise ValueError("Invalid output format. Please choose 'csv' or 'tsv'.")

	# Iterate over each sheet and save it as a CSV or TSV file
	for sheet_name in excel_data.sheet_names:
		df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
		sanitized_sheet_name = sanitize_sheet_name(sheet_name)
		output_file_path = os.path.join(output_directory, f'{sanitized_sheet_name}{file_extension}')
		df.to_csv(output_file_path, index=False, sep=separator)

	print(f"All sheets have been successfully saved as {output_format.upper()} files.")


# Parse arguments from the command line.
def parse_args():
	parser = argparse.ArgumentParser(description='Split an Excel spreadsheet into individual CSV or TSV files.')
	parser.add_argument('-e', '--excel_file_path', type=str, required=True, help='Path to the Excel file.')
	parser.add_argument('-o', '--output_directory', type=str, required=True, help='Directory to save the output files.')
	parser.add_argument('-f', '--format', type=str, choices=['csv', 'tsv'], default='csv', help='Output format: csv or tsv (default: csv)')
	parser.add_argument('-v', '--version', action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


###### Main
def main():

	args = parse_args()
	split_excel(args.excel_file_path, args.output_directory, args.format)

if __name__ == '__main__':
	main()
