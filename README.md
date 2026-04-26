# E-commerce Sales Dashboard 🛒

> An interactive Streamlit dashboard for analysing Brazilian e-commerce data — built for category, region, and time-period exploration.

**ACC102 Mini Assignment — Track 4: Interactive Data Analysis Tool**
*Xi'an Jiaotong-Liverpool University, 2026*

---

## 📌 Quick Links

- 🎬 **Demo Video**: 【#XJTLU#ACC102-哔哩哔哩】 https://b23.tv/5jAOAe5
- 📊 **Live Walkthrough**: see screenshots below https://github.com/YutongSun2402/ACC102/blob/main/app.py
- 📓 **Analysis Notebook**: [`Notebook.ipynb`](Notebook.ipynb)
- 📄 **Reflective Report**: https://github.com/YutongSun2402/ACC102/blob/main/Reflective_Report.docx

---

## 1. Project Overview

### The Problem

E-commerce operations managers face the same questions every week, but for different slices of the business:

- **Which product categories** drive the majority of revenue, and which are underperforming?
- **Where are the customers** geographically, and which regions are most profitable after shipping costs?
- **When do customers order** — and can staffing and marketing be aligned to those peaks?
- **Are there high-revenue categories with quality problems** (low ratings) that threaten retention?

A static report answers these questions once. An **interactive dashboard answers them every time the filter changes** — which is why this project is the right deliverable for an operations team.

### Target Users

- **E-commerce operations managers** — for inventory, pricing, and promotion decisions
- **Marketplace sellers** — for product strategy and competitive benchmarking
- **Business analysts** — for data-driven reporting

### What This Tool Delivers

A 4-page Streamlit dashboard with **global filters** (date range, categories, states), automatic **business insight generation**, and **CSV export** of any filtered view.

---

## 2. Dataset

| Field | Value |
| --- | --- |
| **Dataset** | Brazilian E-Commerce Public Dataset by Olist |
| **Publisher** | Olist Store (Brazilian e-commerce platform) |
| **Host** | Kaggle |
| **URL** | https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce |
| **Access date** | 2026-04-25 |
| **License** | CC BY-NC-SA 4.0 |
| **Coverage** | ~100,000 orders, 2016-09 to 2018-10 |
| **Geographic scope** | 27 Brazilian states |

### Cleaned Schema (used by the app)

The notebook produces a single tidy file `data/cleaned_sales.csv` with these columns:

| Column | Type | Description |
| --- | --- | --- |
| `order_id` | str | Unique order identifier |
| `customer_id` | str | Anonymised customer identifier |
| `product_id` | str | Unique product identifier |
| `product_category_name_english` | str | Product category (translated to English) |
| `price` | float | Item price in BRL |
| `freight_value` | float | Shipping cost in BRL |
| `total_value` | float | `price + freight_value` |
| `customer_state` | str | Brazilian state code (SP, RJ, etc.) |
| `customer_city` | str | Customer city |
| `review_score` | float | Customer rating (1–5) |
| `order_purchase_timestamp` | datetime | When the order was placed |
| `year`, `month`, `year_month`, `weekday`, `hour` | derived | Time features for the dashboard |

> 📝 **Note on data files**: The cleaned file is committed to this repository for reproducibility. The original 9 raw CSV files from Kaggle are placed in `data/raw/` after download — see [How to Run](#5-how-to-run) below.

---

## 3. Methods

### Data Pipeline

```
9 raw Olist CSV files (~45 MB)
        ↓
notebooks/01_data_cleaning_and_analysis.ipynb
   • Filter to delivered orders only
   • Translate product categories to English
   • Aggregate multi-review orders
   • Inner-join orders × items × products × customers
   • Left-join reviews (preserve revenue rows)
   • Build derived time features
   • Trim sparse months (<1000 orders)
        ↓
data/cleaned_sales.csv (~107K rows, ~20 MB)
        ↓
app.py (this dashboard)
```

### Key Analytical Techniques

- **Pareto analysis** for category concentration (the 80/20 rule visualised with a dual-axis chart)
- **Treemap** for revenue composition with rating-based colour encoding
- **Quality–Revenue scatter** to flag categories with high revenue but low satisfaction (retention risk)
- **Choropleth map** of Brazilian states using official IBGE GeoJSON
- **Freight-burden ratio** (freight as % of order value) to identify shipping-disadvantaged regions
- **Weekday × hour heatmap** for operational staffing insights

### Tech Stack

- **Python 3.13** with `pandas` and `numpy` for data wrangling
- **Streamlit** for the interactive web layer
- **Plotly** for all interactive visualisations (Pareto chart, choropleth map, treemap, scatter)
- **Matplotlib + Seaborn** in the notebook for static EDA visuals

---

## 4. Dashboard Pages

### 🏠 Overview
Top-level KPIs (revenue, orders, AOV, categories, rating) and temporal trends. Includes a **monthly revenue trend** and a **weekday × hour heatmap** showing when customers actually order.

> *Insight example*: "Peak month was 2017-11 with R$ 1.14M in revenue (Black Friday spike). Customers order most on weekday evenings between 14:00 and 22:00."

### 🏷️ Category Analysis
- **Top-N slider** to focus the view
- **Pareto chart** with cumulative-percentage line — quantifies the 80/20 concentration
- **Treemap** with revenue size and rating-based colour
- **Quality vs Revenue scatter** to identify retention risks
- **Full statistics table** (expandable)

### 🌎 Regional Analysis
- **Interactive Brazil choropleth** with switchable metrics (revenue / orders / AOV / rating)
- **Top-15 state ranking**
- **Freight-burden chart** highlighting where shipping costs eat into order value
- **Full statistics table** (expandable)

### 🔍 Data Explorer (with file upload — bonus feature)
- **Use the project dataset** OR **upload your own CSV** (`st.file_uploader`)
- Column-types and missing-value summary
- Distribution histogram for any numeric column
- Live data preview with adjustable row count
- **CSV export** of the active dataset

---

## 5. How to Run

### Prerequisites

- Python 3.10 or higher (Anaconda recommended)
- ~500 MB free disk space
- A modern browser (Chrome, Safari, Firefox, Edge)

### Step-by-step Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ecommerce-dashboard.git
cd ecommerce-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get the data
#    Option A: cleaned_sales.csv is already committed — skip to step 5
#    Option B: regenerate from raw data:
#       (i)   Download the dataset from Kaggle:
#             https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
#       (ii)  Unzip and move all 9 CSV files into data/raw/
#       (iii) Run the notebook to regenerate data/cleaned_sales.csv:

# 4. (Optional) Re-run the data pipeline
jupyter notebook notebooks/01_data_cleaning_and_analysis.ipynb
# Then click "Run All Cells"

# 5. Launch the dashboard
streamlit run app.py
```

The browser opens automatically at **http://localhost:8501**. Press `Ctrl + C` in the terminal to stop the app.

### Project Structure

```
ecommerce-dashboard/
├── app.py                                      # Streamlit dashboard (main entry point)
├── requirements.txt                            # Python dependencies
├── README.md                                   # This file
├── data/
│   ├── raw/                                    # 9 original Kaggle CSVs (after download)
│   ├── cleaned_sales.csv                       # Cleaned analytical table (~20 MB)
│   └── sample_data.csv                         # Small sample for the upload demo
├── notebooks/
│   └── 01_data_cleaning_and_analysis.ipynb     # Full data pipeline + EDA
└── reflective_report.pdf                       # Reflective report with AI disclosure
```

### Troubleshooting

| Problem | Solution |
| --- | --- |
| `Data file not found` on launch | Run the notebook first (step 4) to generate `cleaned_sales.csv` |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt` |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| Map page shows fallback bar chart | The remote GeoJSON failed to load — the app degrades gracefully |

---

## 6. Key Findings

These findings were produced by the notebook and can be reproduced interactively in the dashboard:

### 🚀 Growth
Revenue grew steadily through 2017–2018, with a sharp **Black Friday 2017** spike (peak of R$ 1.14M in November). 2018 monthly revenue ran consistently above 2017 levels — the platform was in growth mode.

### 📦 Category Concentration
Classic Pareto: a small fraction of categories produces ~80% of revenue. The top 10 categories alone account for the majority of orders, dominated by **bed_bath_table**, **health_beauty**, and **sports_leisure**.

### 🌎 Geographic Concentration
**São Paulo (SP), Rio de Janeiro (RJ), and Minas Gerais (MG)** — the south-eastern economic corridor — together generate the bulk of revenue. By contrast, northern states carry **freight costs exceeding 30% of order value**, making them prime targets for free-shipping promotions rather than price competition.

### ⚠️ Quality Red Flags
A handful of high-revenue categories sit below a 3.8-star rating threshold. These are priority candidates for quality investigation, since dissatisfaction here directly threatens retention.

### 🕐 Ordering Patterns
Peak orders come on **weekday afternoons (14:00–22:00)**, especially Mondays and Tuesdays. Weekends are noticeably quieter. This has direct implications for customer-service staffing and the timing of marketing pushes.

---

## 7. Limitations

1. **Historical & geographically bounded**: 2016–2018 Brazilian data is illustrative of a real marketplace but is not a forecast for 2026 or another market.
2. **Revenue ≠ profit**: Our `total_value` proxy is `price + freight_value` — what the customer pays, not gross margin. True profitability would require cost data Olist does not publish.
3. **Self-selected reviews**: Customers who leave reviews are not necessarily representative of all customers. Treat the "quality red-flag" list as **hypotheses**, not conclusions.
4. **Category granularity**: Olist's ~70 categories include narrow ones (e.g. *bed_bath_table*) and catch-alls (e.g. *housewares*), making strict comparisons unfair.
5. **No inflation adjustment**: Values are raw BRL; multi-year growth should be read with that caveat.

---

## 8. Tech & Design Notes

- **Relative paths everywhere** — the project runs unchanged after cloning, no path edits needed
- **Streamlit caching** (`@st.cache_data`) keeps interaction snappy by avoiding repeated CSV reads
- **Custom CSS** for KPI cards, insight callouts, and section dividers (avoids the default Streamlit grey-on-grey)
- **Graceful degradation**: if the remote GeoJSON for the Brazil map fails, the page falls back to a bar chart
- **Defensive coding**: every page handles the empty-filter case with a friendly warning instead of a crash

---

## 9. References & Acknowledgements

- **Dataset**: Olist (2018), *Brazilian E-Commerce Public Dataset*, Kaggle. CC BY-NC-SA 4.0
- **Brazil GeoJSON**: IBGE simplified states, hosted by [click_that_hood](https://github.com/codeforgermany/click_that_hood)
- **Frameworks**: Streamlit, Plotly, pandas — all open source
- **Course**: ACC102, XJTLU, 2025–2026 academic year

---

## 10. AI Disclosure

This project used AI assistance during development. Full disclosure is in `reflective_report.pdf`. In short: AI was used to draft documentation structure, suggest visualisation patterns, and review code for clarity. **All code was run, verified, and interpreted by the author.** All findings reported here were validated against the actual data.

---

*Built for portfolio and learning. Not affiliated with Olist or Kaggle.*
*Topics: `xjtlu` `acc102` `python` `data-analysis` `streamlit` `ecommerce`*
