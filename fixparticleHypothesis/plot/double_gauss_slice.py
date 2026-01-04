#切片双高斯
import ROOT
import sys

INPUT_FILE = "/eos/user/r/reyu/full_chain_odd/fixparticleHypothesis/selection100Mev/n1500_pion/tracksummary_ckf.root"
TREE_NAME = "tracksummary"

PT_MIN = 0.8
PT_MAX = 12

HIST_X_MIN, HIST_X_MAX = -0.01, 0.01
HIST_BINS = 100

FIT_RANGE_MIN, FIT_RANGE_MAX = -0.005,0.005

f = ROOT.TFile.Open(INPUT_FILE)
t = f.Get(TREE_NAME)

c_slice = ROOT.TCanvas("c_slice", "Slice Inspection", 800, 600)
c_slice.SetGrid() 

ROOT.gStyle.SetOptFit(1111)
ROOT.gStyle.SetOptStat(10) 

hist_name = "h_slice_resT"
hist_title = f"res_eTHETA_fit Slice: {PT_MIN:.1f} < t_pT < {PT_MAX:.1f} GeV;mm;Entries / bin"
h_slice = ROOT.TH1D(hist_name, hist_title, HIST_BINS, HIST_X_MIN, HIST_X_MAX)

full_cut = f"t_pT > {PT_MIN} && t_pT < {PT_MAX} "
print("-" * 60)
print(f"{full_cut}")
print("-" * 60)
t.Draw(f"res_eTHETA_fit >> {hist_name}", full_cut)

entries = h_slice.GetEntries()

#fit_func = ROOT.TF1("gaus", "gaus", FIT_RANGE_MIN, FIT_RANGE_MAX)

func_str = "[0]*exp(-0.5*((x-[1])/[2])^2) + [3]*exp(-0.5*((x-[1])/[4])^2)"
fit_func = ROOT.TF1("double_gaus", func_str, FIT_RANGE_MIN, FIT_RANGE_MAX)
total_amp = h_slice.GetMaximum()
mean_est  = h_slice.GetMean()
rms_est   = h_slice.GetRMS()

# [0] Core 高度：假设占总高度的 80%
fit_func.SetParameter(0, total_amp * 0.8)

# [1] Mean：设为直方图的均值
fit_func.SetParameter(1, mean_est)

# [2] Core Sigma：设得比 RMS 小一点 (比如 1/3 RMS)
fit_func.SetParameter(2, rms_est * 0.3)
fit_func.SetParLimits(2, 0.001, rms_est) # 限制 Core Sigma 不能太大

# [3] Tail 高度：假设占总高度的 20%
fit_func.SetParameter(3, total_amp * 0.2)

# [4] Tail Sigma：设得比 RMS 大一点
fit_func.SetParameter(4, rms_est * 1.5)
fit_func.SetLineColor(ROOT.kRed) 
fit_func.SetLineWidth(3)


print(f"fit in  [{FIT_RANGE_MIN}, {FIT_RANGE_MAX}] ")

fit_status = h_slice.Fit(fit_func, "R") 
#fit_status = h_slice.Fit("gaus", "", "", FIT_RANGE_MIN, FIT_RANGE_MAX)
h_slice.SetMarkerStyle(20) 
h_slice.SetMarkerSize(0.8)
h_slice.SetLineColor(ROOT.kBlack)

h_slice.Draw("E")
c_slice.Update()

st = h_slice.FindObject("stats")
if st:
    st.SetX1NDC(0.65) 
    st.SetX2NDC(0.90) 
    st.SetY1NDC(0.60) 
    st.SetY2NDC(0.90) 
#output_filename = f"SliceFit_{PT_MIN}to{PT_MAX}GeV.png"
#c_slice.SaveAs(output_filename)

c_slice.Draw()

