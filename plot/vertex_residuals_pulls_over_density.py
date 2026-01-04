#!/usr/bin/env python3

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import uproot
import numpy as np
import awkward as ak
import pandas as pd
from scipy.stats import binned_statistic

from labels import  get_event_details
from stats import robust_std, robust_std_std, line_fit

variable_types = ["x", "y", "z", "t"]

residuals = ["resX", "resY", "resZ", "resT"]
pulls = ["pullX", "pullY", "pullZ", "pullT"]
columns = (
    [
        "vertex_primary",
        "vertex_secondary",
        "nTrueVtx",
        "recoVertexClassification",
        "truthPrimaryVertexDensity",
        "recoVertexContamination",
    ]
    + residuals
    + pulls
)

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["residual", "pull"], required=True)
parser.add_argument(
    "--inputs-tvf", required=True, nargs="+", help="input files truth finder"
)
parser.add_argument(
    "--inputs-wot", required=True, nargs="+", help="input files without time"
)
parser.add_argument(
    "--inputs-wt", required=True, nargs="+", help="input files with time"
)
parser.add_argument("--output")
parser.add_argument("--line-fit", action="store_true")
args = parser.parse_args()

assert (
    len(args.inputs_tvf) == len(args.inputs_wot) == len(args.inputs_wt)
), "equal number of inputs required"

#event_sim_label = Path(args.inputs_wot[0]).parent.name
#event_label, simulation_label = split_event_sim_label(event_sim_label)
event_label = Path(args.inputs_wot[0]).parent.parent.name
event_type, _ = get_event_details(event_label)

inputs = {
    "without time": args.inputs_wot,
    "with time": args.inputs_wt,
    "truth": args.inputs_tvf,
}

title = "Vertex resolution" if args.mode == "residual" else "Vertex pull sigma"
variables = residuals if args.mode == "residual" else pulls

results = {
    input_type: {variable: [] for variable in variables} for input_type in inputs.keys()
}

for input_type, inputs_list in inputs.items():
    for input in inputs_list:
        #event_sim_label = Path(input).parent.name
        #event_label, simulation_label = split_event_sim_label(event_sim_label)
        event_label = Path(input).parent.parent.name
        pu = get_event_details(event_label)[1]["pu"]

        vertexing = uproot.open(input)["vertexing"].arrays(columns, library="pd")
           

        # filter for first primary vertex which is the HS vertex by design
        vertexing = vertexing[
            (vertexing["vertex_primary"] == 1)
            & (vertexing["vertex_secondary"] == 0)
            & (vertexing["recoVertexClassification"] == 1)
        ]

        for variable_type, variable in zip(variable_types, variables):
            if input_type == "without time" and variable_type == "t":
                continue

            vertexing["pu"] = pu
            results[input_type][variable].append(vertexing)

fig = plt.figure(f"{title} over density", figsize=(12, 8))
fig.suptitle(f"{title} over density for {event_type}")
axs = fig.subplots(2, 2)
axs = [item for sublist in axs for item in sublist]

for i, (input_type, result) in enumerate(results.items()):
    for variable_type, variable, ax in zip(variable_types, variables, axs):
        if input_type == "without time" and variable_type == "t":
            ax.errorbar(
                np.nan,
                np.nan,
                np.nan,
                marker="o",
                linestyle="",
                alpha=0.5,
                label=f"{input_type}",
            )
            continue

        data = pd.concat(result[variable])

        bins = 6
        sigma, density_edges, _ = binned_statistic(
            data["truthPrimaryVertexDensity"],
            data[variable],
            bins=bins,
            range=None,
            statistic=robust_std,
        )
        sigma_err, _, _ = binned_statistic(
            data["truthPrimaryVertexDensity"],
            data[variable],
            bins=bins,
            range=None,
            statistic=robust_std_std,
        )
        density_mid = 0.5 * (density_edges[:-1] + density_edges[1:])

        ax.errorbar(
            density_mid,
            sigma,
            sigma_err,
            marker="o",
            linestyle="",
            color=f"C{i}",
            alpha=0.5,
            label=f"{input_type}",
        )

        if args.line_fit:
            # replace 0 with NaN to avoid division by zero
            sigma_err[sigma_err == 0] = 1
            params, cov, p_value = line_fit(density_mid, sigma, sigma_err)

            ax.plot(
                density_mid,
                params[0] * density_mid + params[1],
                marker="",
                linestyle="--",
                color=f"C{i}",
                alpha=0.5,
                label=f"fit: {params[0]:.2f} * density + {params[1]:.2f}, p-value: {p_value:.2f}",
            )

for variable, ax in zip(variables, axs):
    ax.set_title(variable)
    ax.legend()

if args.output:
    plt.savefig(args.output)
else:
    plt.show()
