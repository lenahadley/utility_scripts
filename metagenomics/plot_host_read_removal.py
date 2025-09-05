#!/usr/bin/env python3

__version__ = '0.1'
__date__ = '19-08-2024'
__author__ = 'L.O.HADLEY'

###### Imports

import os
import argparse
import pandas as pd
import plotly.express as px
import plotly.io as pio


###### Misc

BAR_COLORS = {
    "Initial": "#e76f51",         # Blue
    "Post-decontamination": "#2a9d8f",  # Orange
    "Retained %": "#264653"           # Green (for proportion plot)
}

###### Functions

def insert_spacers(df, label_col="simple_id", group_col="group_prefix"):
    sorted_df = df.sort_values(by=group_col)
    sample_order = []
    spacer_rows = []
    spacer_idx = 0
    last_group = None

    for _, row in sorted_df.iterrows():
        sample = row[label_col]
        group = row[group_col]
        if last_group is not None and group != last_group:
            spacer_id = f"__spacer_{spacer_idx}__"
            sample_order.append(spacer_id)
            spacer_rows.append({label_col: spacer_id, "Metric": "Initial", "Reads": 0})
            spacer_rows.append({label_col: spacer_id, "Metric": "Post-decontamination", "Reads": 0})
            spacer_idx += 1
        sample_order.append(sample)
        last_group = group

    df_spacers = pd.DataFrame(spacer_rows)
    df_out = pd.concat([df, df_spacers], ignore_index=True)
    return df_out, sample_order


def plot_read_counts(df, output_file):
    df_long = pd.melt(
        df,
        id_vars=["SampleID", "simple_id", "group_prefix"],
        value_vars=["Initial_read_count", "Postdecontamination_read_count"],
        var_name="Metric",
        value_name="Reads"
    )
    df_long["Metric"] = df_long["Metric"].map({
        "Initial_read_count": "Initial",
        "Postdecontamination_read_count": "Post-decontamination"
    })

    df_long, sample_order = insert_spacers(df_long)

    fig = px.bar(
        df_long,
        x="simple_id",
        y="Reads",
        color="Metric",
        barmode="group",
        category_orders={"simple_id": sample_order},
        color_discrete_map=BAR_COLORS
    )

    fig.update_layout(
        title="<b>Read Counts Before and After Host Removal</b>",
        xaxis_title=None,
        yaxis_title="<b>Read Count</b>",
        plot_bgcolor="white",
        yaxis=dict(showline=True, linecolor="black"),
        xaxis=dict(showline=True, linecolor="black"),
        xaxis_tickangle=45,
        xaxis_tickfont=dict(size=10)
    )

    # Hide spacer tick labels
    fig.update_xaxes(
        tickvals=sample_order,
        ticktext=[s if not s.startswith("__spacer_") else "" for s in sample_order]
    )

    pio.write_html(fig, output_file)
    print(f"✅ Read count plot saved to: {output_file}")


def plot_host_proportion(df, output_file):
    df["Retained %"] = (df["Postdecontamination_read_count"] / df["Initial_read_count"]) * 100

    df_prop = df[["simple_id", "group_prefix", "Retained %"]].copy()
    df_prop["Metric"] = "Retained %"
    df_prop.rename(columns={"Retained %": "Percent"}, inplace=True)


    df_prop, sample_order = insert_spacers(df_prop, label_col="simple_id", group_col="group_prefix")

    fig = px.bar(
        df_prop,
        x="simple_id",
        y="Percent",
        color="Metric",
        category_orders={"simple_id": sample_order},
        color_discrete_map=BAR_COLORS
    )

    fig.update_layout(
        xaxis_title=None,
        title="<b>Proportion of Reads Retained After Host Removal</b>",
        yaxis_title="<b>% Reads Retained</b>",
        plot_bgcolor="white",
        yaxis=dict(showline=True, linecolor="black"),
        xaxis=dict(showline=True, linecolor="black"),
        xaxis_tickangle=45,
        xaxis_tickfont=dict(size=10),
        showlegend=False
    )

    fig.update_xaxes(
        tickvals=sample_order,
        ticktext=[s if not s.startswith("__spacer_") else "" for s in sample_order]
    )

    pio.write_html(fig, output_file)
    print(f"Host proportion plot saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Plot read counts before and after host removal")
    parser.add_argument("-i", "--input", required=True, help="Input CSV file")
    parser.add_argument("-o1", "--output_reads", required=True, help="Output HTML file for read counts")
    parser.add_argument("-o2", "--output_host", required=True, help="Output HTML file for host proportion")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    df["simple_id"] = df["SampleID"].apply(lambda x: "_".join(x.split("|")[0].split("_")[:3]))
    df["group_prefix"] = df["SampleID"].apply(lambda x: "_".join(x.split("|")[0].split("_")[1:3]))

    plot_read_counts(df.copy(), args.output_reads)
    plot_host_proportion(df.copy(), args.output_host)


if __name__ == "__main__":
    main()
