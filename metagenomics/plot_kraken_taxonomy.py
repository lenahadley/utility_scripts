#!/usr/bin/env python3

__version__ = '0.1'
__date__ = '22-08-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import os
import argparse
import pandas as pd
import plotly.express as px
import plotly.io as pio

###### Misc

# Kraken2 rank mapping including variants
RANK_MAP = {
    'U': 'Unclassified',
    'R': 'Unclassified', 'R1': 'Unclassified', 'R2': 'Unclassified', 'R3': 'Unclassified', 'R4': 'Unclassified', 'R5': 'Unclassified', 'R6': 'Unclassified', 'R7': 'Unclassified',
    'D': 'Domain',  # Not listed but included for completeness
    'K': 'Kingdom', 'K1': 'Kingdom', 'K2': 'Kingdom', 'K3': 'Kingdom', 'K4': 'Kingdom', 'K5': 'Kingdom',
    'P': 'Phylum', 'P1': 'Phylum', 'P2': 'Phylum', 'P3': 'Phylum', 'P4': 'Phylum', 'P5': 'Phylum', 'P6': 'Phylum',
          'P7': 'Phylum', 'P8': 'Phylum', 'P9': 'Phylum', 'P10': 'Phylum', 'P11': 'Phylum', 'P12': 'Phylum',
          'P13': 'Phylum', 'P14': 'Phylum', 'P15': 'Phylum', 'P16': 'Phylum', 'P17': 'Phylum',
    'C': 'Class', 'C1': 'Class', 'C2': 'Class', 'C3': 'Class', 'C4': 'Class', 'C5': 'Class', 'C6': 'Class',
          'C7': 'Class', 'C8': 'Class', 'C9': 'Class', 'C10': 'Class', 'C11': 'Class', 'C12': 'Class', 'C13': 'Class',
    'O': 'Order', 'O1': 'Order', 'O2': 'Order', 'O3': 'Order', 'O4': 'Order', 'O5': 'Order', 'O6': 'Order', 'O7': 'Order',
    'F': 'Family', 'F1': 'Family', 'F2': 'Family', 'F3': 'Family', 'F4': 'Family', 'F5': 'Family', 'F6': 'Family', 'F7': 'Family',
    'G': 'Genus', 'G1': 'Genus', 'G2': 'Genus', 'G3': 'Genus', 'G4': 'Genus', 'G5': 'Genus',
    'S': 'Species', 'S1': 'Species', 'S2': 'Species', 'S3': 'Species'
}

# Ordered taxonomic ranks
RANK_ORDER = [
    'Unclassified', 'Root', 'Domain', 'Kingdom', 'Phylum',
    'Class', 'Order', 'Family', 'Genus', 'Species', 'Other'
]

# Custom colors for ranks
RANK_COLORS = {
    'Unclassified': '#d1cfcf',
    'Domain': '#882255',
    'Kingdom': '#117733',
    'Phylum': '#332288',
    'Class': '#aa4499',
    'Order': '#44aa99',
    'Family': '#88ccee',
    'Genus': '#ddcc77',
    'Species': '#cc6677',   # Bright pink/magenta
    'Other':   '#66c2a5'   # Teal-green
}


###### Functions

def parse_kraken_report(report_path):
    df = pd.read_csv(
        report_path,
        sep="\t",
        header=None,
        names=["perc", "reads_clade", "reads_direct", "rank_code", "taxid", "name"],
        engine="python",
        quoting=3
    )

    df["rank"] = df["rank_code"].map(RANK_MAP).fillna("Other")

    # Only retain rows where reads were assigned directly to this taxon
    df = df[df["reads_direct"] > 0].copy()

    df_ranked = df.groupby("rank")["reads_direct"].sum()
    total = df_ranked.sum()

    df_summary = df_ranked.reset_index(name="reads")
    df_summary["perc"] = (df_summary["reads"] / total * 100).round(2)
    df_summary["rank"] = pd.Categorical(df_summary["rank"], categories=RANK_ORDER, ordered=True)
    df_summary = df_summary.sort_values(by="rank").reset_index(drop=True)

    return df_summary


def parse_all_reports(folder):
    all_data = []
    for file in os.listdir(folder):
        if file.endswith(".report.txt"):
            path = os.path.join(folder, file)
            sample_name = os.path.splitext(file)[0]
            sample_label = "_".join(sample_name.split("_")[:3])
            df = parse_kraken_report(path)
            df["sample"] = sample_label
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)


def insert_spacers(df):
    # Build a list of (sample, group_key) pairs
    sample_group_pairs = []
    for sample in df["sample"].unique():
        parts = sample.split("_")
        if len(parts) >= 3:
            group_key = "_".join(parts[1:3])  # Group by 2nd and 3rd fields
        else:
            group_key = "unknown"
        sample_group_pairs.append((sample, group_key))

    # Sort first by group key, then sample name
    sample_group_pairs.sort(key=lambda x: (x[1], x[0]))

    sample_order = []
    last_group_key = None
    spacer_idx = 0

    for sample, group_key in sample_group_pairs:
        if last_group_key is not None and group_key != last_group_key:
            spacer = f"__spacer_{spacer_idx}__"
            sample_order.append(spacer)
            spacer_idx += 1
        sample_order.append(sample)
        last_group_key = group_key

    # Create spacer rows (invisible, but needed for layout)
    spacer_rows = []
    for s in sample_order:
        if s.startswith("__spacer_"):
            spacer_rows.append({
                "sample": s,
                "rank": "Species",  # Assign to Species arbitrarily to keep bar structure
                "reads": 0,
                "perc": 0
            })

    spacer_df = pd.DataFrame(spacer_rows)
    df_out = pd.concat([df, spacer_df], ignore_index=True)

    return df_out, sample_order


def plot_stacked_bar(df, output_file):
    df, sample_order = insert_spacers(df)

    fig = px.bar(
        df,
        x="sample",
        y="perc",
        color="rank",
        category_orders={"rank": RANK_ORDER, "sample": sample_order},
        color_discrete_map=RANK_COLORS,
        custom_data=["reads", "perc", "rank"]
    )

    fig.update_traces(
        hovertemplate=
        "<b>Rank</b>: %{customdata[2]}<br>"
        "<b>Reads</b>: %{customdata[0]}<br>"
        "<b>%</b>: %{customdata[1]:.2f}<extra></extra>"
    )

    fig.update_layout(
        title="<b>Lowest possible taxonomic rank assignment</b>",
        yaxis_title="<b>Total reads (%)</b>",
        xaxis_title=None,
        plot_bgcolor="white",
        yaxis=dict(showline=True, linecolor="black"),
        xaxis=dict(
            showline=True,
            linecolor="black",
            tickangle=45,
            tickfont=dict(size=10),
            tickmode='array',
            tickvals=[s for s in sample_order if not s.startswith("__spacer_")],
            ticktext=[s for s in sample_order if not s.startswith("__spacer_")]
        ),
        bargap=0.1
    )

    pio.write_html(fig, output_file)
    print(f"✅ Plot saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Visualize lowest taxonomic ranks from Kraken2 reports")
    parser.add_argument("-i", "--input", required=True, help="Input directory with Kraken2 .report files")
    parser.add_argument("-o", "--output", required=True, help="Output HTML file")
    args = parser.parse_args()

    df_all = parse_all_reports(args.input)
    plot_stacked_bar(df_all, args.output)


if __name__ == "__main__":
    main()
