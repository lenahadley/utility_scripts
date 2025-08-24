#!/usr/bin/env python3

import argparse
import random
from collections import defaultdict

def parse_gff3(file_path):
    genes = defaultdict(list)
    mrna_features = {}
    feature_lines = defaultdict(list)

    with open(file_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) != 9:
                continue
            feature_type = parts[2]
            attr_field = parts[8]
            attr_dict = dict(field.split("=") for field in attr_field.split(";") if "=" in field)

            if feature_type == "mRNA":
                parent_gene = attr_dict.get("Parent")
                mrna_id = attr_dict.get("ID")
                if parent_gene and mrna_id:
                    genes[parent_gene].append(mrna_id)
                    mrna_features[mrna_id] = line.strip()
            elif "Parent" in attr_field:
                parent_ids = []
                for kv in attr_field.split(";"):
                    if kv.startswith("Parent="):
                        parent_ids = kv.replace("Parent=", "").split(",")
                        break
                for pid in parent_ids:
                    feature_lines[pid].append(line.strip())
            elif feature_type == "gene":
                gene_id = attr_dict.get("ID")
                if gene_id:
                    feature_lines[gene_id].append(line.strip())
    return genes, mrna_features, feature_lines

def select_random_isoforms(genes):
    selected = {}
    for gene_id, mrnas in genes.items():
        selected_mrna = random.choice(mrnas)
        selected[gene_id] = selected_mrna
    return selected

def write_selected_gff(output_path, selected, mrna_features, feature_lines):
    with open(output_path, "w") as out:
        out.write("##gff-version 3\n")
        for gene_id, mrna_id in selected.items():
            if gene_id in feature_lines:
                for line in feature_lines[gene_id]:
                    out.write(line + "\n")
            if mrna_id in mrna_features:
                out.write(mrna_features[mrna_id] + "\n")
            for line in feature_lines.get(mrna_id, []):
                out.write(line + "\n")

def main():
    parser = argparse.ArgumentParser(description="Randomly select one isoform per gene from a GFF3.")
    parser.add_argument("--input", required=True, help="Input GFF3 file")
    parser.add_argument("--output", required=True, help="Output GFF3 file with one isoform per gene")
    args = parser.parse_args()

    genes, mrna_features, feature_lines = parse_gff3(args.input)
    selected = select_random_isoforms(genes)
    write_selected_gff(args.output, selected, mrna_features, feature_lines)
    print(f"Selected one isoform per gene and wrote to {args.output}")

if __name__ == "__main__":
    main()
