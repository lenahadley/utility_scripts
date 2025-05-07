#!/usr/bin/env python3

import argparse
import os
import re
from Bio import SeqIO

__version__ = '0.1'
__date__ = '2025-05-07'
__author__ = 'Lena Hadley'


# Find gaps in a sequence, return as BED entries
def find_gaps_in_seq(record, min_gap_length):
	gaps = []
	for match in re.finditer(r'[Nn]{%d,}' % min_gap_length, str(record.seq)):
		start = match.start()
		end = match.end()
		gaps.append((record.id, start, end))
	return gaps

# Write gaps to a BED file
def write_gaps_to_bed(gaps, output_file):
	with open(output_file, 'w') as out:
		for chrom, start, end in gaps:
			out.write(f"{chrom}\t{start}\t{end}\n")

# Process single FASTA file
def process_fasta_file(fasta_path, min_gap_length, output_prefix):
	all_gaps = []
	for record in SeqIO.parse(fasta_path, "fasta"):
		gaps = find_gaps_in_seq(record, min_gap_length)
		all_gaps.extend(gaps)
	outfile_name = f"{output_prefix}_{os.path.basename(fasta_path)}.bed"
	write_gaps_to_bed(all_gaps, outfile_name)
	print(f"Written: {outfile_name}")


###### Main
def main():
	args = parse_args()

	# Process a single FASTA file
	if args.fasta:
		process_fasta_file(args.fasta, args.gap, args.output)

	# Process multiple FASTA files in a directory
	elif args.fasta_dir:
		for file_name in os.listdir(args.fasta_dir):
			if file_name.endswith('.fasta') or file_name.endswith('.fa'):
				fasta_path = os.path.join(args.fasta_dir, file_name)
				process_fasta_file(fasta_path, args.gap, args.output)


# Parse arguments from the command line.
def parse_args():
	description = 'Reports gaps (runs of Ns) in FASTA sequences in BED format'
	parser = argparse.ArgumentParser(description=description)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--fasta_dir', help='Directory containing FASTA files')
	group.add_argument('--fasta', help='Single FASTA file')
	parser.add_argument('--gap', type=int, help="Minimum gap length to report (default: 1)", default=1)
	parser.add_argument('--output', help="Output file prefix (optional) ['gaps']", default="gaps")
	parser.add_argument("--version", action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


if __name__ == "__main__":
	main()
