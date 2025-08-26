#!/usr/bin/env python

# 

__version__ = '0.1'
__date__ = '19-08-2024'
__author__ = 'L.O.HADLEY'

###### Imports
import os
import csv
import argparse
from collections import defaultdict
from Bio import SeqIO
import subprocess

##### Misc

# TE-related InterPro IDs
TE_INTERPRO_IDS = {
    "IPR001207",  # Reverse transcriptase
    "IPR000477",  # Integrase catalytic domain
    "IPR002559",  # Transposase
    "IPR018289",  # Retrotransposon GAG protein
    "IPR001584",  # RNase H
    "IPR038717",  # Ty3
    "IPR036397",  # DDE superfamily
    "IPR010994",  # Harbinger transposase
    "IPR027122",  # Transposable element
}

# Trusted InterProScan sources/databases
TRUSTED_SOURCES = {
    "Pfam",
    "SMART",
    "SUPERFAMILY",
    "PROSITE",
    "ProSiteProfiles",
    "PANTHER",
    "Gene3D",
    "SFLD",
    "HAMAP",
    # Add or remove sources as per your trust level
}


###### Functions

def parse_gff3(gff_file):
    transcripts = {}
    with open(gff_file) as f:
        for line in f:
            if line.startswith("#"): continue
            fields = line.strip().split("\t")
            if len(fields) != 9: continue
            chrom, source, feature_type, start, end, score, strand, phase, attributes = fields
            attr_dict = {k: v for k, v in (field.split("=") for field in attributes.split(";") if "=" in field)}
            if feature_type == "mRNA":
                ID = attr_dict.get("ID", None)
                Parent = attr_dict.get("Parent", None)
                if not ID or not Parent: continue
                transcripts[ID] = {
                    "GeneID": Parent,
                    "Chrom": chrom,
                    "Start": int(start),
                    "End": int(end),
                    "Strand": strand,
                    "Exons": [],
                    "CDS": [],
                    "UTR5": [],
                    "UTR3": []
                }
            elif feature_type == "exon":
                Parent = attr_dict.get("Parent", None)
                if Parent in transcripts:
                    transcripts[Parent]["Exons"].append((int(start), int(end)))
            elif feature_type == "CDS":
                Parent = attr_dict.get("Parent", None)
                if Parent in transcripts:
                    transcripts[Parent]["CDS"].append((int(start), int(end)))
            elif feature_type == "five_prime_UTR":
                Parent = attr_dict.get("Parent", None)
                if Parent in transcripts:
                    transcripts[Parent]["UTR5"].append((int(start), int(end)))
            elif feature_type == "three_prime_UTR":
                Parent = attr_dict.get("Parent", None)
                if Parent in transcripts:
                    transcripts[Parent]["UTR3"].append((int(start), int(end)))
    return transcripts

def get_protein_lengths(fasta_file):
    return {record.id: len(record.seq) for record in SeqIO.parse(fasta_file, "fasta")}

def parse_interproscan(interpro_file):
    """
    Parse InterProScan TSV file and return a dict of protein_id -> set of (source, ipr_id).
    """
    protein_hits = defaultdict(set)
    with open(interpro_file) as f:
        for line in f:
            if line.strip() == "":
                continue
            fields = line.strip().split("\t")
            if len(fields) >= 12:
                protein_id = fields[0]
                source = fields[3]
                ipr_id = fields[11]
                protein_hits[protein_id].add((source, ipr_id))
    print(f"Parsed InterProScan hits for {len(protein_hits)} proteins")
    return protein_hits

def count_te_domains(protein_hits):
    """
    Returns set of protein IDs with >=1 TE-related domain from TE_INTERPRO_IDS.
    """
    return {pid for pid, hits in protein_hits.items() if any(ipr in TE_INTERPRO_IDS for _, ipr in hits)}

def compute_repeat_overlap(transcripts, repeat_gff, tmp_bed):
    with open(tmp_bed, "w") as out:
        for tid, info in transcripts.items():
            out.write(f"{info['Chrom']}\t{info['Start'] - 1}\t{info['End']}\t{tid}\n")
    cmd = f"bedtools coverage -a {tmp_bed} -b {repeat_gff} -mean"
    result = subprocess.check_output(cmd, shell=True, text=True)
    return {
        line.split("\t")[3]: float(line.strip().split("\t")[-1])
        for line in result.strip().split("\n") if line
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gff", required=True)
    parser.add_argument("--proteins", required=True)
    parser.add_argument("--interpro", required=True)
    parser.add_argument("--repeat_gff", required=True)
    parser.add_argument("--output_dir", default="annotation_metrics")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Parsing GFF3: {args.gff}")
    transcripts = parse_gff3(args.gff)
    print(f"Extracted {len(transcripts)} transcripts")

    print(f"Parsing protein FASTA: {args.proteins}")
    protein_lengths = get_protein_lengths(args.proteins)

    print(f"Parsing InterProScan file: {args.interpro}")
    protein_hits = parse_interproscan(args.interpro)
    te_hits = count_te_domains(protein_hits)
    print(f"Found TE domain counts for {len(te_hits)} proteins")

    print(f"Computing repeat coverage...")
    tmp_bed = os.path.join(args.output_dir, "temp.bed")
    repeat_cov = compute_repeat_overlap(transcripts, args.repeat_gff, tmp_bed)

    detailed_file = os.path.join(args.output_dir, "annotation.detailed.csv")
    summary_file = os.path.join(args.output_dir, "annotation.summary.csv")

    summary = {
        "total_transcripts": 0,
        "single_exon": 0,
        "in_repeat": 0,
        "high_conf": 0,
        "low_conf": 0,
        "no_annotation": 0,
        "has_5utr": 0,
        "has_3utr": 0,
        "has_te_domain": 0
    }

    with open(detailed_file, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow([
            "TranscriptID", "GeneID", "Chrom", "Start", "End", "Strand",
            "ExonCount", "SingleExon", "CDS_Length", "Protein_Length",
            "In_Repeat", "High_Confidence", "Low_Confidence", "No_Annotation",
            "Has_5UTR", "Has_3UTR", "TE_Domain_Count"
        ])

        for tid, info in transcripts.items():
            summary["total_transcripts"] += 1

            gene = info["GeneID"]
            exon_count = len(info["Exons"])
            single_exon = exon_count == 1
            cds_len = sum(end - start + 1 for start, end in info["CDS"])
            prot_len = protein_lengths.get(tid, 0)
            repeat = repeat_cov.get(tid, 0.0)
            in_repeat = repeat > 0.5
            has_5utr = bool(info["UTR5"])
            has_3utr = bool(info["UTR3"])

            hits = protein_hits.get(tid, set())

            if not hits:
                no_annot = True
                low_conf = False
                high_conf = False
            else:
                sources = {src for src, ipr in hits}
                trusted = sources.intersection(TRUSTED_SOURCES)
                if trusted:
                    high_conf = True
                    low_conf = False
                    no_annot = False
                else:
                    high_conf = False
                    low_conf = True
                    no_annot = False

            te_count = sum(1 for _, ipr in hits if ipr in TE_INTERPRO_IDS)

            if single_exon: summary["single_exon"] += 1
            if in_repeat: summary["in_repeat"] += 1
            if high_conf: summary["high_conf"] += 1
            if low_conf: summary["low_conf"] += 1
            if no_annot: summary["no_annotation"] += 1
            if has_5utr: summary["has_5utr"] += 1
            if has_3utr: summary["has_3utr"] += 1
            if te_count >= 1: summary["has_te_domain"] += 1

            writer.writerow([
                tid, gene, info["Chrom"], info["Start"], info["End"], info["Strand"],
                exon_count, single_exon, cds_len, prot_len,
                round(repeat, 3), high_conf, low_conf, no_annot,
                has_5utr, has_3utr, te_count
            ])

    with open(summary_file, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["Metric", "Count"])
        for k, v in summary.items():
            writer.writerow([k, v])

    print(f"Wrote detailed per-transcript info to {detailed_file}")
    print(f"Wrote summary metrics to {summary_file}")

if __name__ == "__main__":
    main()
