#!/usr/bin/env python3

# Calculates assembly statistics for each assembled genome in a directory or a single file.

__version__ = '0.1'
__date__ = '01-05-2025'
__author__ = 'L.O.HADLEY'

###### Imports

import argparse
from Bio import SeqIO
import statistics
import re

###### Functions

def parse_fasta_lengths(fasta_path):
    lengths = []
    genes = set()
    total_bp = 0

    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_len = len(record.seq)
        lengths.append(seq_len)
        total_bp += seq_len
        if args.trinity:
            match = re.match(r"(\S+?g\d+)", record.id)
            if match:
                genes.add(match.group(1))
    return lengths, total_bp, genes

def n50(lengths):
    lengths_sorted = sorted(lengths, reverse=True)
    total = sum(lengths_sorted)
    cum = 0
    for l in lengths_sorted:
        cum += l
        if cum >= total / 2:
            return l
    return 0

def main(args):
    print(f"Parsing: {args.fasta}")
    
    # Handle either protein or transcript mode
    if args.protein:
        print("Protein mode: processing protein FASTA...")
    else:
        print("Transcript mode: processing transcript FASTA...")

    lengths, total_bp, genes = parse_fasta_lengths(args.fasta)
    n_sequences = len(lengths)

    print("📊 Calculating metrics...")
    print(f"Total sequences: {n_sequences}")
    print(f"Total size (bp): {total_bp}")
    print(f"Mean sequence length: {round(statistics.mean(lengths), 2)}")
    print(f"Median sequence length: {statistics.median(lengths)}")
    print(f"Sequence N50: {n50(lengths)}")

    if args.trinity:
        print(f"Total Trinity genes: {len(genes)}")

###### Main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get basic stats for a transcriptome or protein assembly.")
    parser.add_argument("-f", "--fasta", required=True, help="Transcript or protein FASTA file")
    parser.add_argument("--trinity", action="store_true", help="Parse Trinity-style gene names (for transcript mode)")
    parser.add_argument("--protein", action="store_true", help="Switch to protein mode (calculates in amino acids)")
    args = parser.parse_args()
    main(args)
