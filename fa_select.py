#!/usr/bin/env python

__version__ = '0.1'
__date__ = '09-04-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import argparse
import sys

###### Functions

# Get FASTA headers to keep or exclude
def read_headers(filename):
	with open(filename, 'r') as file:
		headers = {line.strip().lstrip('>') for line in file}
	return headers


# Open FASTA saves headers and sequences to lists
def read_fasta(filename):
	with open(filename, 'r') as file:
		fasta_records = []
		header = None
		sequence = []
		for line in file:
			line = line.strip()
			if line.startswith(">"):
				if header is not None:
					fasta_records.append((header, "".join(sequence)))
				header = line[1:]
				sequence = []
			else:
				sequence.append(line)
		if header is not None:
			fasta_records.append((header, "".join(sequence)))
	return fasta_records


# Write processed FASTA to file
def write_fasta(records, output_handle):
	for header, sequence in records:
		output_handle.write(f">{header}\n")
		output_handle.write(f"{sequence}\n")


# Process FASTA
def process_fasta(args):
	records = read_fasta(args.file)
	if args.length:
		records = [rec for rec in records if len(rec[1]) >= args.length]

	if args.include:
		include_headers = read_headers(args.include)
		records = [rec for rec in records if rec[0] in include_headers]

	if args.exclude:
		exclude_headers = read_headers(args.exclude)
		records = [rec for rec in records if rec[0] not in exclude_headers]

	if args.sort:
		records = sorted(records, key=lambda rec: rec[0])

	if args.prefix:
		records = [(f"{args.prefix}.{header}", sequence) for header, sequence in records]

	try:
		if args.output:
			with open(args.output, 'w') as output_handle:
				write_fasta(records, output_handle)
		else:
			write_fasta(records, sys.stdout)

	except BrokenPipeError:
		sys.stderr.close()


# Parse arguments from the command line.
def parse_args():
	description = 'Process FASTA files. Version: %s, Date: %s, Author: %s' % (__version__, __date__, __author__)
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('-f', '--file', required=True, help="Input FASTA file")
	parser.add_argument('-s', '--sort', action='store_true', help="Sort by header name")
	parser.add_argument('-l', '--length', type=int, help="Keep only contigs longer than the specified length")
	parser.add_argument('-p', '--prefix', help="Append prefix to each contig header followed by a delimiter (period)")
	parser.add_argument('-i', '--include', help="File with list of contig headers to include")
	parser.add_argument('-e', '--exclude', help="File with list of contig headers to exclude")
	parser.add_argument('-o', '--output', help="Output file name")
	parser.add_argument('-v', '--version', action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


###### Main
def main():
	args = parse_args()
	process_fasta(args)

if __name__ == "__main__":
	main()
