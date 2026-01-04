#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import awkward as ak
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from labels import get_event_details

columns = [
    "nTrueVtx",
    "nRecoVtx",
]

parser = argparse.ArgumentParser()
parser.add_argument("inputs", nargs="+")
parser.add_argument("--output")
args = parser.parse_args()

result = {}

for input in args.inputs:
    event_type, event_details = get_event_details(Path(input).parent.parent.name)
    n = event_details["pu"]
  
    data = uproot.open(input)["vertexing"].arrays(columns, library="pd")

    if event_type not in result:
        result[event_type] = []

    result[event_type].append(
        {
            "n": n,
            "splitting_ratio": np.sum(data["nRecoVtx"] > data["nTrueVtx"])
            / len(data),
        }
    )

fig = plt.figure("vertex splitting ratio over PU", figsize=(12, 8))
fig.suptitle(f"Vertex splitting ratio over PU")
ax = fig.gca()

for event_type, data in result.items():
    data = pd.DataFrame(data)
    data = data.sort_values("n")
    ax.plot(
        data["n"], data["splitting_ratio"], marker="o", alpha=0.5, label=f"{event_type}"
    )

# ax.set_yscale("log")
ax.legend()

if args.output:
    plt.savefig(args.output)
else:
    plt.show()
