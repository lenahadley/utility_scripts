#!/usr/bin/env python

__version__ = '0.1'
__date__ = '22-08-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import argparse

###### Misc

plot_colors = [
    "#ff4a24", "#19D3F3", "#F58518", "#e60019", "#006fdf", "#FECB52", "#636EFA",
    "#80ba5a", "#b596ed", "#009b3b", "#bc80bd", "#882255", "#117733", "#88ccee",
    "#ff0b6e", "#00d395", "#f2b701", "#999933", "#E45756", "#332288", "#cf1c90",
    "#FFA15A", "#ccebc5", "#80b1d3", "#FF9DA6", "#002b90", "#008695", "#11a579"
]

###### Functions

# Extract sample ID and group label (now include 3 fields for full sample label)
def extract_sample_info(filename):
    name = os.path.splitext(filename)[0]
    parts = name.split("_")
    sample_id = parts[0]
    # Full label is first 3 parts joined by underscore if available
    full_label = "_".join(parts[:3]) if len(parts) >= 3 else name
    group_label = "_".join(parts[1:3]) if len(parts) >= 3 else "NA"
    return sample_id, group_label, full_label

# Read and process Bracken-style file
def process_bracken_file(filepath):
    df = pd.read_csv(filepath, sep="\t")
    if "taxonomy_lvl" not in df.columns or "new_est_reads" not in df.columns:
        raise ValueError(f"Unexpected format in file: {filepath}")
#    df = df[df["taxonomy_lvl"] == "S"]
    df = df.rename(columns={"new_est_reads": "count"})
    df = df[["name", "count", "taxonomy_lvl"]]   # keep taxonomy_lvl
    
    sample_id, group_label, full_label = extract_sample_info(os.path.basename(filepath))
    df["sample"] = sample_id
    df["group_label"] = group_label
    df["full_sample"] = full_label
    return df

# Combine all TSVs
def combine_all_files(directory):
    combined_df = pd.DataFrame()
    for file in os.listdir(directory):
        if file.endswith(".bracken.tsv"):
            filepath = os.path.join(directory, file)
            df = process_bracken_file(filepath)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

# Insert spacer samples between groups to create gaps in x-axis
def insert_spacers(df):
    # Unique samples with their groups and full labels, ordered
    samples = df[['sample', 'group_label', 'full_sample']].drop_duplicates()
    
    # Sort by group_label then sample
    samples = samples.sort_values(['group_label', 'sample']).reset_index(drop=True)
    
    new_samples = []
    last_group = None
    spacer_name = "__spacer__"
    spacer_count = 0
    
    for idx, row in samples.iterrows():
        current_group = row['group_label']
        if last_group is not None and current_group != last_group:
            # Insert a spacer between different groups
            new_samples.append({'sample': f'{spacer_name}_{spacer_count}', 'group_label': None, 'full_sample': ''})
            spacer_count += 1
        new_samples.append({'sample': row['sample'], 'group_label': current_group, 'full_sample': row['full_sample']})
        last_group = current_group
    
    samples_with_spacers = pd.DataFrame(new_samples)
    sample_order = samples_with_spacers['sample'].tolist()
    
    # Add spacer rows with zero counts and empty species for plot
    spacer_rows = []
    for spacer_sample in samples_with_spacers[samples_with_spacers['group_label'].isna()]['sample']:
        spacer_rows.append({
            'name': '',
            'count': 0,
            'sample': spacer_sample,
            'group_label': None,
            'full_sample': ''
        })
    spacer_df = pd.DataFrame(spacer_rows)
    
    df_spaced = pd.concat([df, spacer_df], ignore_index=True)
    
    return df_spaced, samples_with_spacers

# Shared formatting
def format_fig(fig):
    fig.update_layout(
        plot_bgcolor="white",
        xaxis_title=None,
        yaxis=dict(showline=True, linecolor="black"),
        xaxis=dict(showline=True, linecolor="black"),
        legend_title_text="<b>Species</b>"
    )
    return fig

# Absolute counts
def plot_absolute(df, top_n, output):
    top_species = df.groupby("name")["count"].sum().nlargest(top_n).index
    df_filtered = df[df["name"].isin(top_species)].copy()

    # Infer rank from taxonomy_lvl column, default Species
    if "taxonomy_lvl" in df_filtered.columns and not df_filtered["taxonomy_lvl"].isnull().all():
        rank_code = df_filtered["taxonomy_lvl"].mode()[0]  # most common level
        rank_map = { "S": "Species", "G": "Genera", "F": "Families", "O": "Orders", "C": "Classes", "P": "Phyla", "D": "Domains" }
        rank = rank_map.get(rank_code.upper(), "Species")
    else:
        rank = "Species"

    df_filtered["name"] = df_filtered["name"].str.replace("_", " ").apply(lambda x: f"<i>{x}</i>")

    # Insert spacers and get ordered samples with full labels
    df_spaced, samples_with_spacers = insert_spacers(df_filtered)

    fig = px.bar(
        df_spaced,
        x="sample",
        y="count",
        color="name",
        barmode="stack",
        color_discrete_sequence=plot_colors,
        custom_data=["name", "count", "group_label"]
    )
    
    fig.update_traces(
        hovertemplate=
        "<b>Species</b>: %{customdata[0]}<br>"
        "<b>Reads</b>: %{customdata[1]}<br>"
        "<b>Group</b>: %{customdata[2]}<extra></extra>"
    )

    format_fig(fig)

    # Prepare ticks: show full_sample labels except for spacers (empty string)
    tickvals = samples_with_spacers['sample'].tolist()
    ticktext = [label if not sample.startswith("__spacer__") else "" 
                for sample, label in zip(samples_with_spacers['sample'], samples_with_spacers['full_sample'])]

    fig.update_layout(
        title=f"<b>Top {top_n} {rank} (Read Counts)</b>",
        yaxis_title="<b>Reads (count)</b>",
        xaxis=dict(
            categoryorder="array",
            categoryarray=tickvals,
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=45,
            tickfont=dict(weight="bold")
        )
    )
    pio.write_html(fig, output, full_html=True)
    print(f"✅ Absolute plot saved to: {output}")

# Relative abundance
def plot_relative(df, top_n, output):
    top_species = df.groupby("name")["count"].sum().nlargest(top_n).index
    df_filtered = df[df["name"].isin(top_species)].copy()

    # Infer rank from taxonomy_lvl column, default Species
    if "taxonomy_lvl" in df_filtered.columns and not df_filtered["taxonomy_lvl"].isnull().all():
        rank_code = df_filtered["taxonomy_lvl"].mode()[0]
        rank_map = { "S": "Species", "G": "Genera", "F": "Families", "O": "Orders", "C": "Classes", "P": "Phyla", "D": "Domains" }
        rank = rank_map.get(rank_code.upper(), "Species")
    else:
        rank = "Species"

    df_filtered["fraction"] = df_filtered.groupby("sample")["count"].transform(lambda x: x / x.sum())
    df_filtered["percent"] = df_filtered["fraction"] * 100

    df_filtered["name"] = df_filtered["name"].str.replace("_", " ").apply(lambda x: f"<i>{x}</i>")

    # Insert spacers and get ordered samples with full labels
    df_spaced, samples_with_spacers = insert_spacers(df_filtered)

    fig = px.bar(
        df_spaced,
        x="sample",
        y="percent",
        color="name",
        barmode="stack",
        color_discrete_sequence=plot_colors,
        custom_data=["name", "count", "percent", "group_label"]
    )

    fig.update_traces(
        hovertemplate=
        "<b>Species</b>: %{customdata[0]}<br>"
        "<b>Reads</b>: %{customdata[1]}<br>"
        "<b>%</b>: %{customdata[2]:.2f}<br>"
        "<b>Group</b>: %{customdata[3]}<extra></extra>"
    )

    format_fig(fig)

    tickvals = samples_with_spacers['sample'].tolist()
    ticktext = [label if not sample.startswith("__spacer__") else "" 
                for sample, label in zip(samples_with_spacers['sample'], samples_with_spacers['full_sample'])]

    fig.update_layout(
        title=f"<b>Top {top_n} {rank} (Proportions)</b>",
        yaxis_title="<b>% of Total Reads</b>",
        xaxis=dict(
            categoryorder="array",
            categoryarray=tickvals,
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=45,
            tickfont=dict(weight="bold")
        )
    )
    pio.write_html(fig, output, full_html=True)
    print(f"✅ Relative plot saved to: {output}")

def main():
    parser = argparse.ArgumentParser(description="Generate barplots from Bracken files")
    parser.add_argument("-i", "--input", required=True, help="Input directory with Bracken TSV files")
    parser.add_argument("-o", "--output_prefix", required=True, help="Prefix for output files")
    parser.add_argument("-n", "--top_n", type=int, default=10, help="Number of top species to plot")
    args = parser.parse_args()

    combined_df = combine_all_files(args.input)
    plot_absolute(combined_df, args.top_n, args.output_prefix + "_absolute.html")
    plot_relative(combined_df, args.top_n, args.output_prefix + "_relative.html")

if __name__ == "__main__":
    main()
