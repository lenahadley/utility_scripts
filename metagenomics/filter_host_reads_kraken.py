#!/usr/bin/env python3

__version__ = '0.1'
__date__ = '19-08-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import argparse
import gzip
from collections import defaultdict
from Bio import SeqIO

###### Functions

def parse_args():
    parser = argparse.ArgumentParser(description="Filter host reads using lineage tracing with gzip output and removal summary.")
    parser.add_argument('--kraken', required=True, help='Kraken2 read classification file')
    parser.add_argument('--nodes', required=True, help='nodes.dmp from NCBI taxonomy')
    parser.add_argument('--reads', required=True, help='Original read file (.fq, .fa, .fq.gz, .fa.gz)')
    parser.add_argument('--output_prefix', required=True, help='Prefix for output filtered reads')
    parser.add_argument('--host_taxids', nargs='+', default=['9606', '9989'], help='List of host root taxids')
    return parser.parse_args()

def load_nodes(nodes_file):
    taxid_to_parent = {}
    with open(nodes_file) as f:
        for line in f:
            parts = line.strip().split('\t|\t')
            taxid = int(parts[0].strip())
            parent = int(parts[1].strip())
            taxid_to_parent[taxid] = parent
    return taxid_to_parent

def build_classification_map(kraken_file):
    read_to_taxid = {}
    with open(kraken_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if parts[0] == 'C' or parts[0] == 'U':
                read_id = parts[1]
                taxid = int(parts[2])
                read_to_taxid[read_id] = taxid
    return read_to_taxid

def is_host(taxid, host_roots, taxid_to_parent, removal_counts):
    original_taxid = taxid
    while taxid != 1:
        if taxid in host_roots:
            removal_counts[taxid] += 1
            return True
        taxid = taxid_to_parent.get(taxid, 1)
    return False

def detect_format(reads_file):
    if reads_file.endswith('.fq.gz') or reads_file.endswith('.fastq.gz'):
        return 'fastq'
    elif reads_file.endswith('.fa.gz') or reads_file.endswith('.fasta.gz'):
        return 'fasta'
    elif reads_file.endswith('.fq') or reads_file.endswith('.fastq'):
        return 'fastq'
    elif reads_file.endswith('.fa') or reads_file.endswith('.fasta'):
        return 'fasta'
    else:
        raise ValueError("Unknown file extension for reads file")

def filter_reads(reads_file, read_to_taxid, taxid_to_parent, host_roots, output_prefix):
    fmt = detect_format(reads_file)
    output_file = f"{output_prefix}_filtered.{fmt}.gz"

    open_in = gzip.open if reads_file.endswith('.gz') else open
    open_out = gzip.open

    kept = 0
    total = 0
    removal_counts = defaultdict(int)

    with open_in(reads_file, 'rt') as infile, open_out(output_file, 'wt') as outfile:
        for record in SeqIO.parse(infile, fmt):
            total += 1
            taxid = read_to_taxid.get(record.id)
            if taxid is None or not is_host(taxid, host_roots, taxid_to_parent, removal_counts):
                SeqIO.write(record, outfile, fmt)
                kept += 1

    print(f"Filtering done. Kept {kept:,}/{total:,} reads.")
    total_removed = total - kept
    print(f"Total host reads removed: {total_removed:,}")
    print("Breakdown of reads removed by host taxid:")
    for taxid in host_roots:
        print(f"  Taxid {taxid}: {removal_counts[taxid]:,} reads")

def main():
    args = parse_args()
    host_roots = set(int(tid) for tid in args.host_taxids)
    taxid_to_parent = load_nodes(args.nodes)
    read_to_taxid = build_classification_map(args.kraken)
    filter_reads(args.reads, read_to_taxid, taxid_to_parent, host_roots, args.output_prefix)

if __name__ == "__main__":
    main()
