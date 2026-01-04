#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot
import numpy as np
import pandas as pd
import awkward as ak
import matplotlib.pyplot as plt

from labels import  get_event_details

columns = [
    "vertex_primary",
    "vertex_secondary",
    "truthPrimaryVertexDensity",
    "recoVertexContamination",
]

parser = argparse.ArgumentParser()
parser.add_argument("--inputs", nargs="+", help="input files")
parser.add_argument("--output")
args = parser.parse_args()

#event_sim_label = Path(args.inputs[0]).parent.name
#event_label, simulation_label = split_event_sim_label(event_sim_label)
event_label = Path(args.inputs[0]).parent.parent.name
event_type, _ = get_event_details(event_label)

fig = plt.figure("Vertex density over PU", figsize=(8, 6))
fig.suptitle(f"Vertex density for {event_type} over PU")
axs = fig.subplots(2, 1, sharex=True)

datas = []
pus = []

for input in args.inputs:
   # event_sim_label = Path(input).parent.name
   # event_label, simulation_label = split_event_sim_label(event_sim_label)
    event_label = Path(input).parent.parent.name
    pu = get_event_details(event_label)[1]["pu"]

    data = uproot.open(input)["vertexing"].arrays(columns, library="pd")
        
    

    # filter for first primary vertex which is the HS vertex by design
    data = data[(data["vertex_primary"] == 1) & (data["vertex_secondary"] == 0)]

    pus.append(pu)
    data["pu"] = pu
    datas.append(data)

datas = pd.concat(datas)
pus = np.unique(np.sort(np.array(pus)))
pus_edges = np.concatenate([[pus[0]], 0.5 * (pus[:-1] + pus[1:]), [pus[-1]]])

axs[0].hist2d(datas["pu"], datas["truthPrimaryVertexDensity"], bins=(pus_edges, 6))

axs[1].hist2d(datas["pu"], datas["recoVertexContamination"], bins=(pus_edges, 6))

axs[0].grid()
axs[0].set_ylabel("density")

axs[1].grid()
axs[1].set_xlabel("PU")
axs[1].set_ylabel("contamination")

if args.output:
    fig.savefig(args.output)
else:
    plt.show()
