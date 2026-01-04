#!/usr/bin/env python3

import argparse
from pathlib import Path
import uproot  # 用于读取 ROOT 文件的 Python 库
import numpy as np
import pandas as pd
import awkward as ak # 用于处理不规则数组（Jagged Arrays），虽然这里转成了 pandas
import matplotlib.pyplot as plt

# --- 依赖库注意 ---
# 这行代码引用了一个自定义模块 mycommon.labels。
# 它的作用是从文件路径字符串（如 ".../ttbar_pu200/..."）中提取信息。
# 如果你没有这个 python 文件，脚本会报错。你需要自己写一个简单的替换函数。
from labels import  get_event_details

# --- 定义要读取的 TTree 分支 (Branches) ---
columns = [
    "vertex_primary",    # 是否为主顶点 (通常 1 为是)
    "vertex_secondary",  # 是否为次级顶点
    "nRecoVtx",          # 重建出的顶点总数
    "nMergedVtx",        # 发生合并(Merged)的顶点数 (两个真顶点被重建为一个)
    "nSplitVtx",         # 发生分裂(Split)的顶点数 (一个真顶点被重建为两个)
    "nTrueVtx",          # 真实的顶点总数 (Truth info)
    "nVtxReconstructable", # 理论上可被重建的顶点数
]

# --- 命令行参数解析 ---
parser = argparse.ArgumentParser()
# 脚本要求必须传入四组文件列表，分别对应不同的算法或配置
# nargs="+" 表示可以接受多个文件路径（例如：file_pu10.root file_pu60.root ...）
parser.add_argument(
    "--inputs-tvf", required=True, nargs="+", help="input files truth finder (基于真值的查找器)"
)
parser.add_argument(
    "--inputs-gauss", required=True, nargs="+", help="input files gauss finder (高斯查找器)"
)
parser.add_argument(
    "--inputs-wot", required=True, nargs="+", help="input files without time (不带时间信息的算法)"
)
parser.add_argument(
    "--inputs-wt", required=True, nargs="+", help="input files with time (带时间信息的算法)"
)
parser.add_argument(
    "--inputs-ivf", required=True, nargs="+", help="input files with time (ivf算法)"
)

parser.add_argument("--output") # 输出图片的文件名
args = parser.parse_args()

# --- 检查输入完整性 ---
# 确保每种算法传入的文件数量是一样的（例如都传入了 5 个 PU 点的文件）
assert (
    len(args.inputs_tvf) == len(args.inputs_wot) == len(args.inputs_wt)
), "equal number of inputs required"

# --- 提取元数据 ---
# 获取第一个文件所在的父目录名（例如 "ttbar_pu10"）
event_label = Path(args.inputs_wot[0]).parent.parent.name
# 使用自定义函数解析标签，获取事件类型（如 ttbar）
#event_label, simulation_label = split_event_sim_label(event_sim_label)
event_type, _ = get_event_details(event_label)

# --- 组织输入数据 ---
# 将命令行参数映射到一个字典中，方便后面循环处理
# 这里的 keys ("without time" 等) 将作为图例 (Legend) 的标签
inputs = {
    "without time": args.inputs_wot,
    "with time": args.inputs_wt,
    "gauss": args.inputs_gauss,
    "truth": args.inputs_tvf,
    "ivf":args.inputs_ivf,
}

# --- 初始化绘图 ---
# 创建一个画布，包含 3 个子图 (subplots)，共享 X 轴
fig = plt.figure("Vertex efficiency over PU", figsize=(8, 6))
fig.suptitle(f"Vertex efficiency for {event_type} over PU")
axs = fig.subplots(3, 1, sharex=True)

# 用于存储处理后的结果数据
results = {input_type: [] for input_type in inputs.keys()}

# --- 主循环：处理每种算法 ---
for input_type, inputs_list in inputs.items():
    # --- 内层循环：处理该算法下的每一个文件（即每一个 PU 点）---
    for input in inputs_list:
        # 1. 解析当前文件的 PU 值
        # 这一步非常关键：它假设文件路径包含父文件夹，且父文件夹名包含 PU 信息
        event_label = Path(input).parent.parent.name
        # event_label, simulation_label = split_event_sim_label(event_sim_label)
        pu = get_event_details(event_label)[1]["pu"] # 获取 PU 值 (例如 200)

        # 2. 读取 ROOT 文件中的 "vertexing" Tree
        # library="ak" 读取为 awkward array，然后转为 pandas DataFrame
#        data = ak.to_dataframe(
#            uproot.open(input)["vertexing"].arrays(columns, library="ak"),
#            how="outer",
#        )
        data = uproot.open(input)["vertexing"].arrays(columns, library="pd")
        # 3. 数据筛选
        # 仅保留 Primary Vertex (主顶点) 且非 Secondary 的条目
        # 这通常是为了关注 Hard Scatter (HS) 顶点的重建情况
        data = data[(data["vertex_primary"] == 1) & (data["vertex_secondary"] == 0)]

        # 4. 计算统计量 (均值和标准差)
        results[input_type].append(
            {
                "pu": pu, # x轴坐标
                "n_true": data["nTrueVtx"].mean(),
                "n_reconstructable": data["nVtxReconstructable"].mean(),
                "n_reco": data["nRecoVtx"].mean(), # 平均重建顶点数
                "n_reco_err": data["nRecoVtx"].std(), # 重建数标准差（作为误差棒）
                "n_merged": data["nMergedVtx"].mean(),
                "n_merged_err": data["nMergedVtx"].std(),
                "n_split": data["nSplitVtx"].mean(),
                "n_split_err": data["nSplitVtx"].std(),
            }
        )

# --- 绘图循环 ---
for input_type in inputs.keys():
    # 将列表转换为 DataFrame 方便绘图
    data = pd.DataFrame(results[input_type])

    # 子图 1: 重建顶点数 vs PU
    axs[0].errorbar(
        data["pu"],
        data["n_reco"],
        data["n_reco_err"], # y轴误差棒
        marker="o",
        linestyle="",
        alpha=0.5,
        label=f"{input_type}",
    )

    # 子图 2: 合并顶点数 vs PU
    axs[1].errorbar(
        data["pu"],
        data["n_merged"],
        marker="o",
        linestyle="",
        alpha=0.5,
        label=f"{input_type}",
    )

    # 子图 3: 分裂顶点数 vs PU
    axs[2].errorbar(
        data["pu"],
        data["n_split"],
        marker="o",
        linestyle="",
        alpha=0.5,
        label=f"{input_type}",
    )

# --- 添加参考线 ("Optimal") ---

# 子图 1 参考线: y = x + 1 (或者是 y ~ PU)
# 这里的 data["pu"] + 1 暗示理想情况下重建顶点数应该等于 PU 数 + 1 (HS)
axs[0].plot(
    data["pu"],
    data["pu"] + 1,
    linestyle="--",
    color="black",
    label="optimal",
)

# 子图 2 参考线: y = 0 (理想情况下没有合并)
axs[1].plot(
    data["pu"],
    np.zeros(data["pu"].shape),
    linestyle="--",
    color="black",
    label="optimal",
)

# 子图 3 参考线: y = 0 (理想情况下没有分裂)
axs[2].plot(
    data["pu"],
    np.zeros(data["pu"].shape),
    linestyle="--",
    color="black",
    label="optimal",
)

# --- 格式化设置 ---
axs[0].grid()
axs[0].legend()
axs[0].set_ylabel("Reconstructed vertices") # y轴标签

axs[1].grid()
axs[1].legend()
axs[1].set_ylabel("Merged vertices")

axs[2].grid()
axs[2].legend()
axs[2].set_xlabel("PU") # x轴标签
axs[2].set_ylabel("Split vertices")

# --- 保存或显示 ---
if args.output:
    fig.savefig(args.output)
else:
    plt.show()

