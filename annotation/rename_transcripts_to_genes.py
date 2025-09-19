#!/usr/bin/env python

__version__ = '0.1'
__date__ = '19-09-2025'
__author__ = 'L.O.HADLEY'

###### Imports

import argparse
from pathlib import Path

###### Functions

def parse_gff3(gff3_file):
    """
    Parse GFF3 file and return dict mapping transcript IDs -> gene IDs.
    """
    transcript_to_gene = {}
    with open(gff3_file, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            if len(fields) < 9:
                continue

            feature_type = fields[2]
            attributes = fields[8]

            if feature_type == "mRNA":
                attrs = dict(
                    field.split("=") for field in attributes.split(";") if "=" in field
                )
                transcript_id = attrs.get("ID")
                gene_id = attrs.get("Parent")
                if transcript_id and gene_id:
                    transcript_to_gene[attrs.get("Name", transcript_id)] = gene_id
                    transcript_to_gene[transcript_id] = gene_id
    return transcript_to_gene


def replace_in_file(input_file, output_file, transcript_to_gene):
    """
    Replace transcript IDs with gene IDs by raw string replacement.
    """
    text = Path(input_file).read_text()

    for transcript, gene in transcript_to_gene.items():
        if transcript in text:
            text = text.replace(transcript, gene)

    Path(output_file).write_text(text)
    print(f"Output written to {output_file} ; Warning this approach uses string replacement, it does not account for substrings!!!!!")


def main():
    parser = argparse.ArgumentParser(description="Replace transcript IDs with gene IDs using a GFF3 file.")
    parser.add_argument("gff3", help="Path to the GFF3 annotation file")
    parser.add_argument("input", help="Input file (any text format)")
    parser.add_argument("output", help="Output file path")
    args = parser.parse_args()

    mapping = parse_gff3(args.gff3)
    print(f"[DEBUG] Loaded {len(mapping)} transcript→gene mappings")

    replace_in_file(args.input, args.output, mapping)


if __name__ == "__main__":
    main()
