# Setup & publish notes

How this workbook is built and how it goes live on Tableau Public.

## Build it (Tableau Public Desktop, free, runs on Mac)
1. Download **Tableau Public** from public.tableau.com and open it.
2. Connect to `data/global_superstore.csv` (Text file connector).
3. Confirm geographic roles: `Country` should have the globe icon (Country/Region).
   If not, right-click it → Geographic Role → Country/Region. `ISO3` is a backup.
4. Create the calculated fields from `calculated_fields.txt`.

## Sheets to build
- **World profit map**: drag `Country` to the view, switch marks to Filled Map (or Symbol
  Map), color by `Profit Ratio` (red-green diverging), size by `SUM(Sales)`.
- **Profit by Category** and **Profit by Sub-Category**: bar charts of `SUM(Profit)`, colored
  by `Loss Flag` so losses go red. Sort ascending.
- **Quarterly Profit Trend**: `SUM(Profit)` by `QUARTER(OrderDate)` as a line.
- **Biggest Profit Drains**: `Country` sorted by `SUM(Profit)` ascending, top 6.
- **KPI tiles**: text sheets for Total Sales, Total Profit, Profit Ratio, Loss-making countries.

## Dashboard
Combine the sheets on a dashboard sized ~1600x900 to match `dashboard_mockup.png`. Add
Market, Category, and Segment as filters and apply them across all sheets (Use as Filter).

## Publish to the web (this is the part you asked about)
1. Sign in to Tableau Public (free account, a personal email like Gmail works).
2. In Tableau Public Desktop: **File → Save to Tableau Public As…**
3. It uploads the workbook and opens the live, public URL in your browser.
4. Copy that URL into this repo's About, your portfolio, resume, and LinkedIn Featured.

That save-to-public step is the whole publish flow — no server or hosting needed.
