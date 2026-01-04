#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import awkward as ak
import matplotlib.pyplot as plt

columns = [
    "vertex_primary",
    "vertex_secondary",
    "nRecoVtx",
    "nMergedVtx",
    "nSplitVtx",
    "nTrueVtx",
    "nVtxReconstructable",
]

efficiency_range = (0, 1)

parser = argparse.ArgumentParser()
parser.add_argument("input", nargs="+")
parser.add_argument("--output")
args = parser.parse_args()

event_label = Path(args.input[0]).parent.parent.name

fig = plt.figure("vertex pulls", figsize=(8, 6))
fig.suptitle(f"Vertex efficiency for {event_label}")
axs = fig.subplots(3, 1, sharex=True)

for input in args.input:
    vertexing = uproot.open(input)
    vertexing = vertexing["vertexing"].arrays(columns, library="pd")
        
  

    # filter for first primary vertex which is the HS vertex by design
    vertexing = vertexing[
        (vertexing["vertex_primary"] == 1) & (vertexing["vertex_secondary"] == 0)
    ]

    axs[0].hist(
        vertexing["nRecoVtx"] / vertexing["nVtxReconstructable"],
        30,
        range=efficiency_range,
        density=True,
        histtype="step",
        label=Path(input).parent.name,
    )

    axs[1].hist(
        vertexing["nMergedVtx"] / vertexing["nVtxReconstructable"],
        30,
        range=efficiency_range,
        density=True,
        histtype="step",
        label=Path(input).parent.name,
    )

    axs[2].hist(
        vertexing["nSplitVtx"] / vertexing["nVtxReconstructable"],
        30,
        range=efficiency_range,
        density=True,
        histtype="step",
        label=Path(input).parent.name,
    )

axs[0].legend()
axs[0].set_xlabel("Reconstruction rate")
axs[0].set_ylabel("a.u.")

axs[1].legend()
axs[1].set_xlabel("Merging rate")
axs[1].set_ylabel("a.u.")

axs[2].legend()
axs[2].set_xlabel("Splitting rate")
axs[2].set_ylabel("a.u.")

if args.output:
    fig.savefig(args.output)
else:
    plt.show()
