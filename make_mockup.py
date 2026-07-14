"""
Render a Tableau-style Global Superstore Profitability dashboard mockup (PNG)
from the generated data: a world profit map plus KPIs, category/sub-category
profit, trend, and country rankings.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.cm import ScalarMappable
from matplotlib.colors import TwoSlopeNorm

df = pd.read_csv("data/global_superstore.csv", parse_dates=["OrderDate"])

latlon = {
 "United States":(39.8,-98.6),"Canada":(56,-106),"United Kingdom":(54,-2),"Germany":(51,10),
 "France":(46,2),"Spain":(40,-4),"Italy":(42,12),"Netherlands":(52,5),"Australia":(-25,133),
 "Japan":(36,138),"India":(22,79),"China":(35,104),"Singapore":(1.3,103.8),"Brazil":(-10,-52),
 "Mexico":(23,-102),"Argentina":(-38,-63),"South Africa":(-30,25),"Nigeria":(9,8),"Egypt":(26,30),
 "United Arab Emirates":(24,54),"Saudi Arabia":(24,45),
}

tot_s=df.Sales.sum(); tot_p=df.Profit.sum(); pr=tot_p/tot_s
by_c=df.groupby("Country").agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
by_c["PR"]=by_c.Profit/by_c.Sales
n_loss=(by_c.Profit<0).sum()

BG="#f7f7f7"; CARD="#ffffff"; INK="#2a2a2a"; MUT="#6f6f6f"; EDGE="#e6e6e6"
ORANGE="#e8762c"; BLUE="#4c78a8"; GREEN="#2f8f4e"; RED="#c4432b"; GREY="#767676"
plt.rcParams.update({"font.family":"DejaVu Sans"})
fig=plt.figure(figsize=(16,9),dpi=100); fig.patch.set_facecolor(BG)

def panel(x,y,w,h,fc=CARD):
    ax=fig.add_axes([x,y,w,h]); ax.set_facecolor(fc)
    for s in ax.spines.values(): s.set_visible(False)
    ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle="round,pad=0,rounding_size=0.02",
                 transform=ax.transAxes,fc=fc,ec=EDGE,lw=1.1,zorder=-1,clip_on=False))
    ax.set_xticks([]); ax.set_yticks([]); return ax

# header
hb=fig.add_axes([0,0.935,1,0.065]); hb.axis("off")
hb.text(0.012,0.55,"Global Superstore  —  Profitability Dashboard",fontsize=20,fontweight="bold",color=INK,va="center")
hb.text(0.013,0.08,"FY2021–FY2024  ·  21 countries  ·  6 markets",fontsize=9.5,color=MUT,va="center")
for i,l in enumerate(["Market: All","Category: All","Segment: All"]):
    hb.add_patch(FancyBboxPatch((0.66+i*0.115,0.24),0.108,0.5,boxstyle="round,pad=0.02,rounding_size=0.4",fc="#fff",ec="#d5d5d5",lw=1))
    hb.text(0.66+i*0.115+0.054,0.5,l,fontsize=8.6,color=INK,ha="center",va="center")

# KPI cards
kpis=[("Total Sales",f"${tot_s/1e6:.1f}M",BLUE),("Total Profit",f"${tot_p/1e6:.2f}M",GREEN if tot_p>0 else RED),
      ("Profit Ratio",f"{pr*100:.1f}%",ORANGE),("Loss-Making Countries",f"{n_loss}",RED),
      ("Orders",f"{len(df)//1000}K",INK)]
x0=0.012; cw=0.190; g=0.007
for i,(t,v,c) in enumerate(kpis):
    ax=panel(x0+i*(cw+g),0.79,cw,0.13)
    ax.add_patch(plt.Rectangle((0,0),0.02,1,color=c,transform=ax.transAxes))
    ax.text(0.09,0.66,t,fontsize=9.3,color=MUT,transform=ax.transAxes)
    ax.text(0.09,0.28,v,fontsize=21,fontweight="bold",color=c,transform=ax.transAxes)

# ---- world profit map (bubble/symbol map) ----
ax=panel(0.012,0.375,0.60,0.40)
ax.text(0.02,0.94,"Profit Ratio by Country   (bubble size = sales)",fontsize=11,fontweight="bold",color=INK,transform=ax.transAxes)
m=fig.add_axes([0.03,0.40,0.565,0.31]); m.set_facecolor("#eaf1f6")
m.set_xlim(-170,195); m.set_ylim(-58,82)
for gx in range(-160,200,40): m.axvline(gx,color="#d5e0e8",lw=0.6,zorder=0)
for gy in range(-40,90,30): m.axhline(gy,color="#d5e0e8",lw=0.6,zorder=0)
norm=TwoSlopeNorm(vmin=by_c.PR.min(),vcenter=0,vmax=by_c.PR.max())
cmap=plt.cm.RdYlGn
for country,(la,lo) in latlon.items():
    row=by_c.loc[country]
    m.scatter(lo,la,s=40+ (row.Sales/by_c.Sales.max())*900, c=[cmap(norm(row.PR))],
              edgecolor="#33333350",linewidth=0.6,zorder=3)
m.set_xticks([]); m.set_yticks([])
for s in m.spines.values(): s.set_color("#cfd9e0")
sm=ScalarMappable(norm=norm,cmap=cmap); sm.set_array([])
cb=fig.colorbar(sm,ax=m,fraction=0.03,pad=0.01); cb.ax.tick_params(labelsize=7)
cb.set_label("Profit ratio",fontsize=8)

# ---- profit by category (diverging bars) ----
cat=df.groupby("Category").Profit.sum().sort_values()
ax=panel(0.628,0.375,0.36,0.40)
ax.text(0.04,0.94,"Profit by Category",fontsize=11,fontweight="bold",color=INK,transform=ax.transAxes)
axc=fig.add_axes([0.70,0.44,0.26,0.22]); axc.set_facecolor(CARD)
cols=[RED if v<0 else GREEN for v in cat.values]
axc.barh(cat.index,cat.values/1e3,color=cols)
for i,v in enumerate(cat.values/1e3):
    axc.text(v,i,f" {v:,.0f}K" if v>=0 else f"{v:,.0f}K ",va="center",ha="left" if v>=0 else "right",fontsize=8,color=INK)
axc.axvline(0,color="#999",lw=0.8)
for s in ["top","right","left"]: axc.spines[s].set_visible(False)
axc.spines["bottom"].set_color("#ccc"); axc.tick_params(colors=MUT,labelsize=8.5); axc.set_xticks([])

# ---- profit by sub-category (bottom-left) ----
sc=df.groupby("SubCategory").Profit.sum().sort_values()
ax=panel(0.012,0.03,0.36,0.325)
ax.text(0.03,0.93,"Profit by Sub-Category",fontsize=11,fontweight="bold",color=INK,transform=ax.transAxes)
axs=fig.add_axes([0.055,0.06,0.30,0.24]); axs.set_facecolor(CARD)
cols=[RED if v<0 else GREEN for v in sc.values]
axs.barh(sc.index,sc.values/1e3,color=cols); axs.axvline(0,color="#999",lw=0.8)
for s in ["top","right","left"]: axs.spines[s].set_visible(False)
axs.spines["bottom"].set_color("#ccc"); axs.tick_params(colors=MUT,labelsize=7.5); axs.set_xticks([])

# ---- profit trend (bottom-mid) ----
tr=df.groupby(df.OrderDate.dt.to_period("Q")).Profit.sum(); tr.index=tr.index.to_timestamp()
ax=panel(0.384,0.03,0.30,0.325)
ax.text(0.04,0.93,"Quarterly Profit Trend",fontsize=11,fontweight="bold",color=INK,transform=ax.transAxes)
axt=fig.add_axes([0.42,0.07,0.23,0.21]); axt.set_facecolor(CARD)
axt.fill_between(tr.index,tr.values/1e3,0,color=BLUE,alpha=0.12)
axt.plot(tr.index,tr.values/1e3,color=BLUE,lw=2)
axt.axhline(0,color="#bbb",lw=0.8)
for s in ["top","right"]: axt.spines[s].set_visible(False)
axt.spines["left"].set_color("#ccc"); axt.spines["bottom"].set_color("#ccc")
axt.tick_params(colors=MUT,labelsize=7.5)

# ---- worst countries (bottom-right) ----
worst=by_c.sort_values("Profit").head(6)
ax=panel(0.69,0.03,0.30,0.325)
ax.text(0.04,0.93,"Biggest Profit Drains (Countries)",fontsize=10.5,fontweight="bold",color=INK,transform=ax.transAxes)
yy=0.76
for name,row in worst.iterrows():
    ax.text(0.06,yy,name,color=INK,fontsize=9,transform=ax.transAxes,va="center")
    ax.text(0.97,yy,f"${row.Profit/1e3:,.0f}K",color=RED,fontsize=9,ha="right",transform=ax.transAxes,va="center")
    yy-=0.135

fig.savefig("dashboard_mockup.png",dpi=100,facecolor=BG)
print("saved dashboard_mockup.png")
