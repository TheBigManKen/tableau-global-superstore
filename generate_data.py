"""
Generate a Global Superstore sales dataset for the Tableau profitability dashboard.
One flat orders table (Tableau likes a single tidy extract) with geography fields
Tableau auto-geocodes (Country / ISO3), plus category, segment, sales, discount, profit.
Reproducible via a fixed seed.
"""
import numpy as np, pandas as pd, os
rng = np.random.default_rng(42)
os.makedirs("data", exist_ok=True)

# country -> (Market, ISO3, demand weight, base margin modifier)
countries = {
    "United States": ("US", "USA", 0.20, 0.02), "Canada": ("US", "CAN", 0.05, 0.01),
    "United Kingdom": ("Europe", "GBR", 0.08, 0.01), "Germany": ("Europe", "DEU", 0.08, 0.02),
    "France": ("Europe", "FRA", 0.06, 0.0), "Spain": ("Europe", "ESP", 0.04, -0.02),
    "Italy": ("Europe", "ITA", 0.04, -0.02), "Netherlands": ("Europe", "NLD", 0.03, 0.01),
    "Australia": ("APAC", "AUS", 0.05, 0.01), "Japan": ("APAC", "JPN", 0.05, 0.02),
    "India": ("APAC", "IND", 0.06, -0.04), "China": ("APAC", "CHN", 0.07, -0.03),
    "Singapore": ("APAC", "SGP", 0.02, 0.02),
    "Brazil": ("LATAM", "BRA", 0.04, -0.05), "Mexico": ("LATAM", "MEX", 0.03, -0.03),
    "Argentina": ("LATAM", "ARG", 0.02, -0.06),
    "South Africa": ("Africa", "ZAF", 0.02, -0.04), "Nigeria": ("Africa", "NGA", 0.02, -0.05),
    "Egypt": ("Africa", "EGY", 0.02, -0.04),
    "United Arab Emirates": ("Middle East", "ARE", 0.02, 0.0), "Saudi Arabia": ("Middle East", "SAU", 0.02, -0.01),
}
cnames = list(countries); cw = np.array([countries[c][2] for c in cnames]); cw = cw/cw.sum()

cats = {
    "Furniture": {"Bookcases":(150,900,0.08), "Chairs":(80,600,0.10),
                  "Tables":(200,1200,-0.06), "Furnishings":(20,200,0.14)},
    "Office Supplies": {"Binders":(5,80,0.16), "Storage":(30,300,0.10), "Art":(5,60,0.12),
                        "Paper":(6,50,0.20), "Appliances":(40,500,0.06), "Labels":(3,30,0.22)},
    "Technology": {"Phones":(100,1400,0.13), "Machines":(200,2500,0.04),
                   "Accessories":(15,300,0.18), "Copiers":(300,2000,0.17)},
}
segments = ["Consumer","Corporate","Home Office"]

N = 20000
dates = pd.date_range("2021-01-01","2024-12-31",freq="D")
mw = {m: (0.8 if m in (1,2) else 1.9 if m in (11,12) else 1.0) for m in range(1,13)}
dw = np.array([mw[d.month]*(1+0.1*(d.year-2021)) for d in dates]); dw=dw/dw.sum()
order_dates = rng.choice(dates, N, p=dw)

country = rng.choice(cnames, N, p=cw)
cat = rng.choice(list(cats), N, p=[0.33,0.42,0.25])
segment = rng.choice(segments, N, p=[0.52,0.30,0.18])

subcat=np.empty(N,dtype=object); sales=np.empty(N); base_margin=np.empty(N)
for i in range(N):
    subs = cats[cat[i]]
    sc = rng.choice(list(subs))
    lo,hi,m = subs[sc]
    subcat[i]=sc; sales[i]=round(float(rng.uniform(lo,hi)),2); base_margin[i]=m

qty = rng.integers(1,9,N)
sales = np.round(sales*qty,2)
# discounts: heavier for Furniture/Tables and emerging markets
disc = rng.choice([0,0.1,0.2,0.3,0.4], N, p=[0.45,0.22,0.18,0.10,0.05])
cmarg = np.array([countries[c][3] for c in country])
# profit = sales * (base_margin + country_mod - discount_penalty) ; discounts crush margin
margin = base_margin + cmarg - disc*0.6 + rng.normal(0,0.03,N)
profit = np.round(sales*margin,2)

df = pd.DataFrame({
    "OrderID": ["ORD-"+str(100000+i) for i in range(N)],
    "OrderDate": pd.DatetimeIndex(order_dates).normalize(),
    "Market": [countries[c][0] for c in country],
    "Country": country,
    "ISO3": [countries[c][1] for c in country],
    "Segment": segment,
    "Category": cat, "SubCategory": subcat,
    "Quantity": qty, "Discount": disc,
    "Sales": sales, "Profit": profit,
}).sort_values("OrderDate").reset_index(drop=True)
df.to_csv("data/global_superstore.csv", index=False)

# headline numbers
tot_s=df.Sales.sum(); tot_p=df.Profit.sum(); pr=tot_p/tot_s
by_country=df.groupby(["Country","ISO3"]).agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
by_country["PR"]=by_country.Profit/by_country.Sales
loss=by_country[by_country.Profit<0].sort_values("Profit")
by_cat=df.groupby("Category").agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
by_cat["PR"]=by_cat.Profit/by_cat.Sales
tbl=df[df.SubCategory=="Tables"].Profit.sum()
print(f"Rows: {len(df):,}")
print(f"Total sales: ${tot_s/1e6:.2f}M | Profit: ${tot_p/1e6:.2f}M | Profit ratio: {pr*100:.1f}%")
print(f"Loss-making countries: {len(loss)}")
print("Worst 5 by profit:\n"+loss.head(5).round(0).to_string())
print("\nBy category:\n"+by_cat.round({'PR':3}).to_string())
print(f"\nTables sub-category profit: ${tbl:,.0f}")
with open("data/_headline.txt","w") as f:
    f.write(f"Total sales: ${tot_s/1e6:.2f}M\nTotal profit: ${tot_p/1e6:.2f}M\nProfit ratio: {pr*100:.1f}%\n")
    f.write(f"Loss-making countries: {len(loss)}\nTables profit: ${tbl:,.0f}\n")
    f.write("By category:\n"+by_cat.round({'PR':3}).to_string())
print("\nWrote data/global_superstore.csv")
