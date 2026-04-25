"""
E-commerce Sales Dashboard - Streamlit Application
====================================================
ACC102 Mini Assignment - Track 4: Interactive Data Analysis Tool

An interactive dashboard for analysing e-commerce sales data with filters
for category, region, and time period. Built on the Brazilian E-Commerce
Public Dataset by Olist (Kaggle).

Author: [Your Name]
Date: 2026
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import io

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a polished look
st.markdown(
    """
    <style>
    /* Main container */
    .main > div { padding-top: 1rem; }

    /* KPI metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fb 0%, #eef1f6 100%);
        border: 1px solid #e1e5ee;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #5a6374;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1f36;
    }

    /* Section dividers */
    h2 { border-bottom: 2px solid #eef1f6; padding-bottom: 8px; margin-top: 1.5rem; }
    h3 { color: #2d3748; margin-top: 1.2rem; }

    /* Insight callout boxes */
    .insight-box {
        background: #f0f7ff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 0.95rem;
    }
    .insight-box strong { color: #1e40af; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #fafbfc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 2. PATHS (use relative paths — rubric requirement)
# ============================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_sales.csv"

# Consistent color palette used across charts
COLORS = {
    "primary": "#3b82f6",
    "secondary": "#10b981",
    "accent": "#f59e0b",
    "danger": "#ef4444",
    "neutral": "#6b7280",
    "sequence": px.colors.qualitative.Set2,
}


# ============================================================
# 3. DATA LOADING (cached for performance)
# ============================================================
@st.cache_data(show_spinner="Loading sales data...")
def load_data(path: Path) -> pd.DataFrame:
    """
    Load the cleaned sales data from CSV.
    Expected columns: order_id, order_purchase_timestamp,
    product_category_name_english, price, freight_value, total_value,
    customer_state, customer_city, review_score
    """
    df = pd.read_csv(path, parse_dates=["order_purchase_timestamp"])

    # Derived time features
    df["year"] = df["order_purchase_timestamp"].dt.year
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["weekday"] = df["order_purchase_timestamp"].dt.day_name()
    df["hour"] = df["order_purchase_timestamp"].dt.hour

    # Safety fallback: if total_value missing, calculate it
    if "total_value" not in df.columns:
        df["total_value"] = df["price"] + df["freight_value"]

    return df


def show_data_instructions():
    """Display setup instructions when data file is missing."""
    st.error("⚠️ Data file not found")
    st.markdown(
        f"""
        The app expects the cleaned dataset at **`{CLEANED_DATA_PATH.relative_to(BASE_DIR)}`**.

        ### How to get the data
        1. Download the **Brazilian E-Commerce Dataset by Olist** from
           [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
        2. Run the data preparation notebook: `notebooks/01_data_cleaning.ipynb`.
        3. This produces `data/cleaned_sales.csv`, which this app reads.

        ### Expected schema
        | Column | Type | Description |
        |--------|------|-------------|
        | `order_id` | str | Unique order identifier |
        | `order_purchase_timestamp` | datetime | When the order was placed |
        | `product_category_name_english` | str | Product category (English) |
        | `price` | float | Item price in BRL |
        | `freight_value` | float | Shipping cost in BRL |
        | `total_value` | float | price + freight_value |
        | `customer_state` | str | Brazilian state code (e.g. SP, RJ) |
        | `customer_city` | str | Customer city |
        | `review_score` | float | Customer rating (1–5) |
        """
    )


# ============================================================
# 4. REUSABLE HELPERS
# ============================================================
def apply_filters(
    df: pd.DataFrame,
    date_range: tuple,
    categories: list,
    states: list,
) -> pd.DataFrame:
    """Apply global filters to the dataframe."""
    mask = (
        (df["order_purchase_timestamp"].dt.date >= date_range[0])
        & (df["order_purchase_timestamp"].dt.date <= date_range[1])
    )
    if categories:
        mask &= df["product_category_name_english"].isin(categories)
    if states:
        mask &= df["customer_state"].isin(states)
    return df[mask].copy()


def insight(text: str):
    """Render a highlighted insight box."""
    st.markdown(f'<div class="insight-box">💡 <strong>Insight:</strong> {text}</div>',
                unsafe_allow_html=True)


def format_brl(value: float) -> str:
    """Format a number as Brazilian Real currency."""
    return f"R$ {value:,.0f}"


def download_button(df: pd.DataFrame, filename: str, label: str = "Download filtered data"):
    """Provide a CSV download button for a dataframe."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 {label}",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )


# ============================================================
# 5. PAGE: OVERVIEW
# ============================================================
def page_overview(df: pd.DataFrame):
    st.title("📊 Sales Overview")
    st.caption("Top-level KPIs and temporal trends across the filtered period.")

    if df.empty:
        st.warning("No data matches the current filters. Try widening your selection.")
        return

    # --- KPI cards ---
    total_revenue = df["total_value"].sum()
    total_orders = df["order_id"].nunique()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    n_categories = df["product_category_name_english"].nunique()
    avg_rating = df["review_score"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue", format_brl(total_revenue))
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Avg. Order Value", format_brl(avg_order_value))
    c4.metric("Active Categories", f"{n_categories}")
    c5.metric("Avg. Rating", f"{avg_rating:.2f} ⭐" if not np.isnan(avg_rating) else "—")

    st.divider()

    # --- Monthly revenue trend ---
    st.subheader("Monthly Revenue Trend")
    monthly = (
        df.groupby("year_month", as_index=False)
        .agg(revenue=("total_value", "sum"), orders=("order_id", "nunique"))
        .sort_values("year_month")
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["year_month"], y=monthly["revenue"],
        mode="lines+markers", name="Revenue",
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Revenue: R$ %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        height=380, hovermode="x unified",
        xaxis_title="Month", yaxis_title="Revenue (BRL)",
        margin=dict(t=30, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    if len(monthly) > 1:
        peak = monthly.loc[monthly["revenue"].idxmax()]
        trough = monthly.loc[monthly["revenue"].idxmin()]
        growth = (monthly["revenue"].iloc[-1] - monthly["revenue"].iloc[0]) / \
                 max(monthly["revenue"].iloc[0], 1) * 100
        insight(
            f"Peak month was <b>{peak['year_month']}</b> with {format_brl(peak['revenue'])} "
            f"in revenue. Lowest activity was in <b>{trough['year_month']}</b>. "
            f"From first to last month in this window, revenue changed by "
            f"<b>{growth:+.1f}%</b>."
        )

    # --- Weekday and hour heatmap ---
    st.subheader("When Do Customers Order?")
    c1, c2 = st.columns(2)

    with c1:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
        weekday = df.groupby("weekday")["order_id"].nunique().reindex(weekday_order)
        fig = px.bar(
            x=weekday.index, y=weekday.values,
            labels={"x": "Day of Week", "y": "Orders"},
            color=weekday.values, color_continuous_scale="Blues",
        )
        fig.update_layout(height=320, showlegend=False, coloraxis_showscale=False,
                          margin=dict(t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        hour = df.groupby("hour")["order_id"].nunique()
        fig = px.line(
            x=hour.index, y=hour.values,
            labels={"x": "Hour of Day", "y": "Orders"},
        )
        fig.update_traces(line=dict(color=COLORS["secondary"], width=3),
                          fill="tozeroy", fillcolor="rgba(16,185,129,0.15)")
        fig.update_layout(height=320, margin=dict(t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    busiest_day = weekday.idxmax()
    busiest_hour = hour.idxmax()
    insight(
        f"Customers order most on <b>{busiest_day}s</b> and around "
        f"<b>{busiest_hour}:00</b>. Marketing pushes and customer-service "
        f"staffing should be aligned with these peak windows."
    )


# ============================================================
# 6. PAGE: CATEGORY ANALYSIS
# ============================================================
def page_category(df: pd.DataFrame):
    st.title("🏷️ Category Analysis")
    st.caption("Which product categories drive revenue, and how are they rated?")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    # Controls
    top_n = st.slider("Show top N categories", 5, 30, 10)

    cat_stats = (
        df.groupby("product_category_name_english")
        .agg(
            revenue=("total_value", "sum"),
            orders=("order_id", "nunique"),
            avg_price=("price", "mean"),
            avg_rating=("review_score", "mean"),
        )
        .sort_values("revenue", ascending=False)
        .reset_index()
    )

    # --- Pareto chart: revenue + cumulative % ---
    st.subheader(f"Top {top_n} Categories by Revenue (Pareto View)")
    top = cat_stats.head(top_n).copy()
    top["cum_pct"] = top["revenue"].cumsum() / cat_stats["revenue"].sum() * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["product_category_name_english"], y=top["revenue"],
        name="Revenue", marker_color=COLORS["primary"],
        hovertemplate="<b>%{x}</b><br>Revenue: R$ %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=top["product_category_name_english"], y=top["cum_pct"],
        name="Cumulative %", yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["accent"], width=3),
    ))
    fig.update_layout(
        height=450,
        yaxis=dict(title="Revenue (BRL)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                    range=[0, 105], ticksuffix="%"),
        xaxis=dict(tickangle=-40),
        margin=dict(t=40, b=120),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Pareto insight
    share_topn = top["revenue"].sum() / cat_stats["revenue"].sum() * 100
    insight(
        f"The top {top_n} categories account for <b>{share_topn:.1f}%</b> of total "
        f"revenue in this period. Inventory and promotion budgets should prioritise "
        f"the leading tier — classic Pareto concentration."
    )

    st.divider()

    # --- Treemap of revenue share ---
    st.subheader("Revenue Composition — Treemap")
    fig = px.treemap(
        cat_stats.head(20),
        path=["product_category_name_english"],
        values="revenue",
        color="avg_rating",
        color_continuous_scale="RdYlGn",
        range_color=[3, 5],
        hover_data={"orders": True, "avg_price": ":.2f"},
    )
    fig.update_layout(height=450, margin=dict(t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # --- Rating vs revenue scatter ---
    st.subheader("Quality vs Revenue")
    scatter_data = cat_stats.head(30).dropna(subset=["avg_rating"])
    fig = px.scatter(
        scatter_data,
        x="avg_rating", y="revenue", size="orders",
        color="avg_price",
        hover_name="product_category_name_english",
        color_continuous_scale="Viridis",
        labels={"avg_rating": "Average Review Score",
                "revenue": "Revenue (BRL)",
                "avg_price": "Avg Price"},
    )
    fig.update_layout(height=420, margin=dict(t=30, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # Find categories that are high revenue but low-rated (red flag)
    median_rev = cat_stats["revenue"].median()
    risky = cat_stats[
        (cat_stats["revenue"] > median_rev)
        & (cat_stats["avg_rating"] < 3.8)
    ].sort_values("revenue", ascending=False).head(3)
    if not risky.empty:
        names = ", ".join(risky["product_category_name_english"].tolist())
        insight(
            f"⚠️ Watch list — these high-revenue categories have below-average "
            f"ratings: <b>{names}</b>. Customer satisfaction issues here could "
            f"hurt retention."
        )

    with st.expander("📋 Full category statistics table"):
        st.dataframe(
            cat_stats.style.format({
                "revenue": "R$ {:,.0f}",
                "avg_price": "R$ {:,.2f}",
                "avg_rating": "{:.2f}",
            }),
            use_container_width=True,
        )


# ============================================================
# 7. PAGE: REGIONAL ANALYSIS
# ============================================================
def page_regional(df: pd.DataFrame):
    st.title("🌎 Regional Analysis")
    st.caption("How does performance vary across Brazilian states?")

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    state_stats = (
        df.groupby("customer_state")
        .agg(
            revenue=("total_value", "sum"),
            orders=("order_id", "nunique"),
            avg_order_value=("total_value", "mean"),
            avg_freight=("freight_value", "mean"),
            avg_rating=("review_score", "mean"),
        )
        .reset_index()
    )
    state_stats["freight_pct"] = (
        state_stats["avg_freight"] / state_stats["avg_order_value"] * 100
    )
    state_stats = state_stats.sort_values("revenue", ascending=False)

    # --- Choropleth map of Brazil ---
    st.subheader("Revenue by State")
    metric_choice = st.radio(
        "Metric to display",
        ["revenue", "orders", "avg_order_value", "avg_rating"],
        horizontal=True,
        format_func=lambda x: {
            "revenue": "Total Revenue",
            "orders": "Order Count",
            "avg_order_value": "Avg Order Value",
            "avg_rating": "Avg Rating",
        }[x],
    )

    # Brazil GeoJSON (official IBGE simplified version, hosted on GitHub)
    BRAZIL_GEOJSON = (
        "https://raw.githubusercontent.com/codeforgermany/click_that_hood/"
        "main/public/data/brazil-states.geojson"
    )

    try:
        fig = px.choropleth(
            state_stats,
            geojson=BRAZIL_GEOJSON,
            locations="customer_state",
            featureidkey="properties.sigla",
            color=metric_choice,
            color_continuous_scale="Blues",
            hover_data={"revenue": ":,.0f", "orders": True},
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=500, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        # Fallback: simple bar chart if map cannot load
        st.info("Map view unavailable — showing bar chart instead.")
        fig = px.bar(state_stats.head(15), x="customer_state", y=metric_choice)
        st.plotly_chart(fig, use_container_width=True)

    top_state = state_stats.iloc[0]
    top_3_share = state_stats.head(3)["revenue"].sum() / state_stats["revenue"].sum() * 100
    insight(
        f"<b>{top_state['customer_state']}</b> leads with "
        f"{format_brl(top_state['revenue'])} in revenue "
        f"({top_state['orders']:,} orders). The top-3 states together contribute "
        f"<b>{top_3_share:.1f}%</b> of total revenue — suggesting strong geographic "
        f"concentration, typical for Brazilian e-commerce (São Paulo axis)."
    )

    st.divider()

    # --- Freight burden analysis ---
    st.subheader("Shipping Cost Burden by State")
    st.markdown("Higher freight-to-order ratios indicate geographic disadvantage — "
                "these states may need free-shipping promotions.")

    freight_view = state_stats.sort_values("freight_pct", ascending=False).head(15)
    fig = px.bar(
        freight_view,
        x="freight_pct", y="customer_state", orientation="h",
        color="freight_pct", color_continuous_scale="Reds",
        labels={"freight_pct": "Avg Freight as % of Order Value",
                "customer_state": "State"},
    )
    fig.update_layout(height=500, yaxis=dict(autorange="reversed"),
                      coloraxis_showscale=False, margin=dict(t=20, b=40))
    st.plotly_chart(fig, use_container_width=True)

    worst = freight_view.iloc[0]
    best = state_stats.sort_values("freight_pct").iloc[0]
    insight(
        f"In <b>{worst['customer_state']}</b>, shipping eats up "
        f"<b>{worst['freight_pct']:.1f}%</b> of the average order value, "
        f"versus only <b>{best['freight_pct']:.1f}%</b> in "
        f"<b>{best['customer_state']}</b>. Subsidised-shipping campaigns could "
        f"unlock growth in remote states."
    )

    with st.expander("📋 Full state statistics table"):
        st.dataframe(
            state_stats.style.format({
                "revenue": "R$ {:,.0f}",
                "avg_order_value": "R$ {:,.2f}",
                "avg_freight": "R$ {:,.2f}",
                "freight_pct": "{:.1f}%",
                "avg_rating": "{:.2f}",
            }),
            use_container_width=True,
        )


# ============================================================
# 8. PAGE: DATA EXPLORER (with file upload — BONUS feature)
# ============================================================
def page_explorer(df: pd.DataFrame):
    st.title("🔍 Data Explorer")
    st.caption("Explore the raw data, filter rows, or upload your own CSV.")

    # --- Data source selector ---
    source = st.radio(
        "Data source",
        ["Use project dataset", "Upload my own CSV"],
        horizontal=True,
    )

    if source == "Upload my own CSV":
        uploaded = st.file_uploader(
            "Upload a CSV file (must include a date column and numeric columns)",
            type=["csv"],
        )
        if uploaded is None:
            st.info("👆 Upload a CSV to begin. You can download a template below.")
            template = df.head(100)
            download_button(template, "sample_template.csv", "Download sample template")
            return
        try:
            working = pd.read_csv(uploaded)
            st.success(f"Loaded {len(working):,} rows × {working.shape[1]} columns.")
        except Exception as e:
            st.error(f"Could not read file: {e}")
            return
    else:
        working = df

    # --- Summary stats ---
    st.subheader("Dataset Snapshot")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(working):,}")
    c2.metric("Columns", f"{working.shape[1]}")
    missing = working.isna().sum().sum()
    c3.metric("Missing cells", f"{missing:,}")

    # --- Column types ---
    with st.expander("📑 Column types and missing values"):
        col_info = pd.DataFrame({
            "dtype": working.dtypes.astype(str),
            "missing": working.isna().sum(),
            "missing_pct": (working.isna().sum() / len(working) * 100).round(2),
            "unique": working.nunique(),
        })
        st.dataframe(col_info, use_container_width=True)

    # --- Numeric distributions ---
    numeric_cols = working.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        st.subheader("Distribution of a Numeric Column")
        col_to_plot = st.selectbox("Choose a numeric column", numeric_cols)
        fig = px.histogram(
            working, x=col_to_plot, nbins=50,
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig.update_layout(height=350, margin=dict(t=20, b=30))
        st.plotly_chart(fig, use_container_width=True)

        stats = working[col_to_plot].describe()
        insight(
            f"<b>{col_to_plot}</b> — mean: {stats['mean']:.2f}, "
            f"median: {stats['50%']:.2f}, std: {stats['std']:.2f}. "
            f"{'Right-skewed distribution.' if stats['mean'] > stats['50%'] else 'Roughly symmetric distribution.'}"
        )

    # --- Data preview ---
    st.subheader("Raw Data Preview")
    n_rows = st.slider("Rows to display", 10, 500, 50)
    st.dataframe(working.head(n_rows), use_container_width=True)

    # --- Download ---
    download_button(working, "exported_data.csv")


# ============================================================
# 9. MAIN APP
# ============================================================
def main():
    # Header
    st.sidebar.title("🛒 E-commerce Dashboard")
    st.sidebar.caption("ACC102 Mini Assignment — Track 4")

    # Load data
    if not CLEANED_DATA_PATH.exists():
        show_data_instructions()
        st.stop()

    df = load_data(CLEANED_DATA_PATH)

    # --- Sidebar: Navigation ---
    st.sidebar.divider()
    page = st.sidebar.radio(
        "📂 Navigate",
        ["Overview", "Category Analysis", "Regional Analysis", "Data Explorer"],
        label_visibility="collapsed",
    )

    # --- Sidebar: Global Filters ---
    st.sidebar.divider()
    st.sidebar.subheader("🎛️ Global Filters")

    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Categories
    all_cats = sorted(df["product_category_name_english"].dropna().unique())
    cat_default = all_cats[:0]  # start empty = means "all"
    selected_cats = st.sidebar.multiselect(
        "Categories (empty = all)",
        options=all_cats,
        default=cat_default,
    )

    # States
    all_states = sorted(df["customer_state"].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "States (empty = all)",
        options=all_states,
        default=[],
    )

    # Apply filters (except for Explorer, which has its own flow)
    if page != "Data Explorer":
        filtered = apply_filters(df, (start_date, end_date), selected_cats, selected_states)
        st.sidebar.caption(f"**Filtered rows:** {len(filtered):,} of {len(df):,}")
    else:
        filtered = df

    # --- Sidebar: Export ---
    st.sidebar.divider()
    if page != "Data Explorer":
        with st.sidebar:
            download_button(filtered, "filtered_sales.csv", "Export filtered data")

    # Footer in sidebar
    st.sidebar.divider()
    st.sidebar.caption(
        "📚 **Data**: Olist Brazilian E-commerce\n\n"
        "🔗 [Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)\n\n"
        "🎓 Built for XJTLU ACC102, 2026"
    )

    # --- Render selected page ---
    if page == "Overview":
        page_overview(filtered)
    elif page == "Category Analysis":
        page_category(filtered)
    elif page == "Regional Analysis":
        page_regional(filtered)
    elif page == "Data Explorer":
        page_explorer(df)


if __name__ == "__main__":
    main()
