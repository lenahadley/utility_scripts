#!/usr/bin/env python3

from collections import defaultdict
import sys

def parse_attributes(attr_string):
    return dict(pair.split('=') for pair in attr_string.strip().split(';') if '=' in pair)

def get_id(attr):
    return parse_attributes(attr).get("ID")

def get_parent(attr):
    return parse_attributes(attr).get("Parent")

def collect_features(gff_lines):
    gene_to_mrnas = defaultdict(set)
    mrna_to_exon_count = defaultdict(int)
    mrna_to_gene = {}
    feature_lines = defaultdict(list)

    for line in gff_lines:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.strip().split('\t')
        if len(parts) != 9:
            continue

        feature_type = parts[2]
        attrs = parts[8]

        if feature_type == "gene":
            gene_id = get_id(attrs)
            feature_lines[gene_id].append(line)

        elif feature_type == "mRNA":
            mrna_id = get_id(attrs)
            gene_id = get_parent(attrs)
            gene_to_mrnas[gene_id].add(mrna_id)
            mrna_to_gene[mrna_id] = gene_id
            feature_lines[mrna_id].append(line)

        elif feature_type == "exon":
            mrna_id = get_parent(attrs)
            mrna_to_exon_count[mrna_id] += 1
            feature_lines[mrna_id].append(line)

        else:
            parent_id = get_parent(attrs)
            if parent_id:
                feature_lines[parent_id].append(line)

    return gene_to_mrnas, mrna_to_exon_count, mrna_to_gene, feature_lines

def write_filtered_gff(gff_lines, output_file):
    gene_to_mrnas, mrna_to_exon_count, mrna_to_gene, feature_lines = collect_features(gff_lines)

    with open(output_file, 'w') as out:
        for gene_id, mrna_ids in gene_to_mrnas.items():
            # Keep gene only if at least one mRNA has >1 exon
            multi_exon_mrnas = [m for m in mrna_ids if mrna_to_exon_count.get(m, 0) > 1]
            if not multi_exon_mrnas:
                continue

            for line in feature_lines[gene_id]:
                out.write(line)

            for mrna_id in multi_exon_mrnas:
                for line in feature_lines[mrna_id]:
                    out.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python filter_multi_exon_genes.py input.gff3 output.gff3")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path) as f:
        gff_lines = f.readlines()

    write_filtered_gff(gff_lines, output_path)
