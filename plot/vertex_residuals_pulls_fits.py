#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import uproot
import awkward as ak
import scipy.stats
import matplotlib.pyplot as plt

from labels import  get_event_details
from stats import robust_gauss_fit

residuals = [
    "resX",
    "resY",
    "resZ",
    "resT",
]
pulls = [
    "pullX",
    "pullY",
    "pullZ",
    "pullT",
]
columns = (
    [
        "vertex_primary",
        "vertex_secondary",
        "nTrueVtx",
    ]
    + residuals
    + pulls
)

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["residual", "pull"], required=True)
parser.add_argument("--input", help="input file")
parser.add_argument("--output")
args = parser.parse_args()

title = "Vertex resolution" if args.mode == "residual" else "Vertex pull sigma"
variables = residuals if args.mode == "residual" else pulls

#event_sim_label = Path(args.input).parent.name
#event_label, simulation_label = split_event_sim_label(event_sim_label)
event_label = Path(args.input).parent.parent.name
event_type, _ = get_event_details(event_label)

vertexing = uproot.open(args.input)["vertexing"].arrays(columns, library="pd")

# filter for first primary vertex which is the HS vertex by design
vertexing = vertexing[
    (vertexing["vertex_primary"] == 1) & (vertexing["vertex_secondary"] == 0)
]

fig = plt.figure(f"{title}", figsize=(12, 8))
fig.suptitle(f"{title} for {event_label}")
axs = fig.subplots(2, 2)
axs = [item for sublist in axs for item in sublist]

for variable, ax in zip(
    variables,
    axs,
):
    data = vertexing[variable].dropna()
    (mu, sigma), cov = robust_gauss_fit(data)

    range = (mu - 5 * sigma, mu + 5 * sigma)

    n, bins, patches = ax.hist(
        vertexing[variable],
        100,
        range=range,
        density=True,
        label=variable,
    )

    x = np.linspace(range[0], range[1], 100)
    ax.plot(
        x,
        scipy.stats.norm.pdf(x, mu, sigma),
        label=f"mu={mu:.2f}, sigma={sigma:.2f}",
    )

    ax.set_title(variable)
    ax.legend()

if args.output:
    plt.savefig(args.output)
else:
    plt.show()
