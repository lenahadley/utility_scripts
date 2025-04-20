#!/usr/bin/env python

# Calculates assembly statistics for each assembled genome in a directory or a single file.

__version__ = '0.1'
__date__ = '09-06-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import argparse
import os
import csv
from Bio import SeqIO
from Bio.Seq import Seq

###### Functions

# Scaffold stats
def scaffold_statistics(fasta_path):
	sequences = list(SeqIO.parse(fasta_path, "fasta"))
	num_scaffolds = len(sequences)
	total_length = sum(len(seq.seq) for seq in sequences)
	seq_lengths = [len(seq.seq) for seq in sequences]
	seq_lengths.sort(reverse=True)
	gc_content = sum(seq.seq.upper().count("G") + seq.seq.upper().count("C") for seq in sequences)
	base_content = sum(seq.seq.upper().count("G") + seq.seq.upper().count("C") + seq.seq.upper().count("T") + seq.seq.upper().count("A") for seq in sequences)
	gc_percentage = round((gc_content/base_content)*100, 2)
	n50 = next((length for length in seq_lengths if sum(seq_lengths[:seq_lengths.index(length) + 1]) >= total_length * 0.5), None)
	n90 = next((length for length in seq_lengths if sum(seq_lengths[:seq_lengths.index(length) + 1]) >= total_length * 0.9), None)
	num_gaps = sum(seq.seq.count("N") for seq in sequences)
	gap_percentage = round((num_gaps/total_length)*100, 2)

	return num_scaffolds, n50, num_gaps, total_length, n90, gc_percentage, gap_percentage


# Contig stats
def contig_statistics(fasta_path, gap_threshold):
	sequences = [seq for seq in SeqIO.parse(fasta_path, "fasta")]
	contig_sequences = []
	for seq in sequences:
		sequence_string = str(seq.seq)
		contigs = sequence_string.split("N" * int(gap_threshold))  # Split on gaps and create new records for split contigs
		for contig in contigs:
			if len(contig) > 0 and "N" not in contig:
				new_seq = seq[:]
				new_seq.seq = Seq(contig)
				contig_sequences.append(new_seq)
	num_contigs = len(contig_sequences)
	num_new_gaps = len(contig_sequences) - len(sequences)
	total_contig_length = sum(len(seq.seq) for seq in contig_sequences)
	contig_lengths = [len(seq.seq) for seq in contig_sequences]
	contig_lengths.sort(reverse=True)
	contig_n50 = next((length for length in contig_lengths if sum(contig_lengths[:contig_lengths.index(length) + 1]) >= total_contig_length * 0.5), None)
	contig_n90 = next((length for length in contig_lengths if sum(contig_lengths[:contig_lengths.index(length) + 1]) >= total_contig_length * 0.9), None)

	return num_contigs, contig_n50, num_new_gaps, contig_n90


# Write results to csv file
def save_stats_to_csv(file_name, num_scaffolds, n50, num_contigs, contig_n50, num_new_gaps, num_gaps, total_length, n90, contig_n90, gc_percentage, gap_percentage, csv_output):
	sample_id = os.path.splitext(file_name)[0]
	csv_writer = csv.writer(csv_output)
	csv_writer.writerow([sample_id, total_length, num_scaffolds, n50, n90, num_contigs, contig_n50, contig_n90, gc_percentage, num_new_gaps, num_gaps, gap_percentage])


# Parse arguments from the command line.
def parse_args():
	description = 'Calculates assembly statistics for each assembled genome in a directory or a single file. Version: %s, Date: %s, Author: %s' % (__version__, __date__, __author__)
	parser = argparse.ArgumentParser(description=description)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--fasta_dir', help='Directory containing FASTA files')
	group.add_argument('--fasta', help='Single FASTA file')
	parser.add_argument('--gap', help="Minimum gap length to be considered a scaffold (optional) [2]", default=2)
	parser.add_argument('--output', help="Output file prefix (optional) ['sample']", default="sample")
	parser.add_argument("--version", action="version", version='Version: %s' % (__version__))

	return parser.parse_args()


###### Main
def main():
	args = parse_args()
	with open(args.output + '.assembly_stats.csv', 'w', newline='') as csv_output:
		csv_writer = csv.writer(csv_output)
		csv_writer.writerow(["sampleid", "assembly_length_bp", "scaffold_count", "scaffold_N50_bp", "scaffold_N90_bp", "contig_count", "contig_N50_bp", "contig_N90_bp", "GC_perc", "gaps_count", "gaps_sum_bp", "gaps_perc"])

		# Process a single FASTA file if provided
		if args.fasta:
			file_name = os.path.basename(args.fasta)
			num_scaffolds, n50, num_gaps, total_length, n90, gc_percentage, gap_percentage = scaffold_statistics(args.fasta)
			num_contigs, contig_n50, num_new_gaps, contig_n90 = contig_statistics(args.fasta, args.gap)
			save_stats_to_csv(file_name, num_scaffolds, n50, num_contigs, contig_n50, num_new_gaps, num_gaps, total_length, n90, contig_n90, gc_percentage, gap_percentage, csv_output)

		# Find and process FASTA files in the directory if provided
		elif args.fasta_dir:
			for file_name in os.listdir(args.fasta_dir):
				if file_name.endswith('.fasta') or file_name.endswith('.fa'):
					fasta_path = os.path.join(args.fasta_dir, file_name)
					num_scaffolds, n50, num_gaps, total_length, n90, gc_percentage, gap_percentage = scaffold_statistics(fasta_path)
					num_contigs, contig_n50, num_new_gaps, contig_n90 = contig_statistics(fasta_path, args.gap)
					save_stats_to_csv(file_name, num_scaffolds, n50, num_contigs, contig_n50, num_new_gaps, num_gaps, total_length, n90, contig_n90, gc_percentage, gap_percentage, csv_output)

if __name__ == "__main__":
	main()
