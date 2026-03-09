"""
app.py
------
Nutrition EDA Dashboard — interactive, tab-based Streamlit app.
Users select features from the sidebar; only the chosen plots render.

Run with:
    streamlit run app.py
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

import utils
from db_ingestion import load_from_db
from meal_recommender import render_recommendation_sidebar, render_recommendation_tab


# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Nutrition EDA Dashboard",
    page_icon="🥗",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

CONTINUOUS_COLS = [
    "Ages", "Height", "Weight", "Daily Calorie Target",
    "Protein", "Sugar", "Sodium", "Calories",
    "Carbohydrates", "Fiber", "Fat",
]
NUTRIENT_COLS = [
    "Daily Calorie Target", "Protein", "Sugar",
    "Sodium", "Calories", "Carbohydrates", "Fiber", "Fat",
]
BINARY_COLS = [
    "Acne", "Diabetes", "Heart Disease", "Hypertension",
    "Kidney Disease", "Weight Gain", "Weight Loss",
]
CATEGORICAL_COLS = ["Gender", "Activity Level", "Dietary Preference"]
SKEWED_COLS = ["Protein", "Sugar", "Sodium", "Calories", "Carbohydrates", "Fiber", "Fat"]
CLUSTER_ALGO_OPTIONS = ["K-Means", "K-Medoids", "Agglomerative", "DBSCAN"]

# ──────────────────────────────────────────────────────────────────────────────
# Data loading & preprocessing  (cached so it only runs once)
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
        df_raw          — original CSV, no modifications
        df_transformed  — outliers capped, skewed cols log-transformed,
                          Disease column exploded into binary indicator columns
    """
    df = load_from_db()

    # Explode multi-label Disease column
    data = df.copy()
    data["Disease"] = data["Disease"].str.split(", ")
    data = data.explode("Disease")

    for disease in data["Disease"].value_counts().index:
        data[disease] = (data["Disease"] == disease).astype(int)

    # Cap outliers
    data = utils.cap_outliers_iqr(data, CONTINUOUS_COLS)

    # Log-transform skewed nutrient columns
    for col in SKEWED_COLS:
        data[col] = np.log1p(data[col])

    return df, data


df_raw, data = load_data()

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar — global filters
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🥗 Dashboard Controls")
    st.caption("Select features and options for each section.")

    st.divider()

    # ── Overview tab controls ──
    with st.expander("📋 Overview", expanded=False):
        show_head = st.checkbox("Show first rows", value=True)
        show_tail = st.checkbox("Show last rows", value=False)
        show_describe = st.checkbox("Show describe()", value=True)
        show_info = st.checkbox("Show df.info()", value=False)
        show_unique = st.checkbox("Show unique value counts", value=False)

    # ── Distribution tab controls ──
    with st.expander("📊 Distributions", expanded=False):
        dist_cols = st.multiselect(
            "Numeric columns to plot",
            options=CONTINUOUS_COLS,
            default=CONTINUOUS_COLS[:4],
        )
        show_cat_dist = st.checkbox("Show categorical distributions", value=True)

    # ── Outlier tab controls ──
    with st.expander("📦 Outliers", expanded=False):
        outlier_cols = st.multiselect(
            "Columns to inspect",
            options=CONTINUOUS_COLS,
            default=CONTINUOUS_COLS[:5],
        )

    # ── Nutrient vs Disease tab controls ──
    with st.expander("🩺 Nutrients vs Disease", expanded=False):
        selected_nutrients = st.multiselect(
            "Nutrients",
            options=NUTRIENT_COLS,
            default=NUTRIENT_COLS[:3],
        )
        selected_diseases_nd = st.multiselect(
            "Diseases / Goals",
            options=BINARY_COLS,
            default=BINARY_COLS[:3],
        )

    # ── Correlations tab controls ──
    with st.expander("🔗 Correlations", expanded=False):
        corr_num_cols = st.multiselect(
            "Numerical columns",
            options=CONTINUOUS_COLS,
            default=CONTINUOUS_COLS,
        )
        corr_bin_cols = st.multiselect(
            "Disease / binary columns",
            options=BINARY_COLS,
            default=BINARY_COLS,
        )
        show_heatmap = st.checkbox("Show full correlation heatmap", value=True)
        show_corr_table = st.checkbox("Show point-biserial table", value=True)
        show_chi2_table = st.checkbox("Show chi-squared table", value=True)

    # ── Lifestyle tab controls ──
    with st.expander("🏃 Lifestyle vs Disease", expanded=False):
        lifestyle_diseases = st.multiselect(
            "Diseases / Goals to compare",
            options=BINARY_COLS,
            default=BINARY_COLS[:3],
        )
        show_dietary = st.checkbox("Dietary Preference breakdown", value=True)
        show_activity = st.checkbox("Activity Level breakdown", value=True)

    # ── Boxplot grid tab controls ──
    with st.expander("📐 Boxplot Grid", expanded=False):
        boxplot_num_cols = st.multiselect(
            "Numeric columns",
            options=CONTINUOUS_COLS,
            default=CONTINUOUS_COLS[:4],
        )

    # ── Clustering tab controls ──
    with st.expander("🔵 Clustering", expanded=False):
        cluster_features = st.multiselect(
            "Features to cluster on",
            options=CONTINUOUS_COLS,
            default=["Calories", "Protein", "Fat", "Carbohydrates", "Fiber"],
        )
        cluster_algo = st.selectbox("Algorithm", CLUSTER_ALGO_OPTIONS)
        n_clusters = st.slider("Number of clusters (k)", min_value=2, max_value=10, value=3)
        balance_clusters = st.checkbox("Balance classes before clustering", value=True)
        balance_n = st.slider("Max rows per disease group", 500, 3000, 1000, step=250)
        cluster_x = st.selectbox(
            "X-axis feature", CONTINUOUS_COLS,
            index=CONTINUOUS_COLS.index("Calories"),
        )
        cluster_y = st.selectbox(
            "Y-axis feature", CONTINUOUS_COLS,
            index=CONTINUOUS_COLS.index("Protein"),
        )
        show_elbow = st.checkbox("Show Elbow / Silhouette plot", value=True)

    # ── Meal Recommendation tab controls ──
    with st.expander("🍽️ Meal Recommendations", expanded=False):
        rec_inputs = render_recommendation_sidebar()

# ──────────────────────────────────────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────────────────────────────────────

st.title("🥗 Nutrition EDA Dashboard")

(
    tab_overview,
    tab_dist,
    tab_outlier,
    tab_nutrient,
    tab_corr,
    tab_lifestyle,
    tab_boxgrid,
    tab_cluster,
    tab_recommend,
) = st.tabs([
    "📋 Overview",
    "📊 Distributions",
    "📦 Outliers",
    "🩺 Nutrients vs Disease",
    "🔗 Correlations",
    "🏃 Lifestyle vs Disease",
    "📐 Boxplot Grid",
    "🔵 Clustering",
    "🍽️ Meal Recommendations",
])

# ──────────────────────────────────────────────────────────────────────────────
# Tab 1 — Overview
# ──────────────────────────────────────────────────────────────────────────────

with tab_overview:
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{df_raw.shape[0]:,}")
    col2.metric("Columns", df_raw.shape[1])
    col3.metric("Diseases / Goals", df_raw["Disease"].str.split(", ").explode().nunique())

    st.divider()

    if show_head:
        st.write("**First rows**")
        st.dataframe(df_raw.head(), use_container_width=True)

    if show_tail:
        st.write("**Last rows**")
        st.dataframe(df_raw.tail(), use_container_width=True)

    if show_describe:
        st.write("**Statistical summary**")
        st.dataframe(df_raw.describe(), use_container_width=True)

    if show_info:
        buffer = io.StringIO()
        df_raw.info(buf=buffer)
        st.write("**df.info()**")
        st.text(buffer.getvalue())

    if show_unique:
        summary = pd.DataFrame({
            "Column": data.columns,
            "Unique Values": [data[c].nunique() for c in data.columns],
            "Null Count": [data[c].isna().sum() for c in data.columns],
            "Dtype": [str(data[c].dtype) for c in data.columns],
        })
        st.write("**Column summary (transformed dataset)**")
        st.dataframe(summary, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# Tab 2 — Distributions
# ──────────────────────────────────────────────────────────────────────────────

with tab_dist:
    st.subheader("Distribution Analysis")
    st.caption("Showing log-transformed values for skewed nutrient columns.")

    if show_cat_dist:
        st.write("#### Categorical Feature Distributions")
        utils.plot_categorical_distributions(data)

    if dist_cols:
        st.write("#### Numeric Distributions")
        utils.plot_numeric_distributions(data, dist_cols)
    else:
        st.info("Select at least one numeric column in the sidebar → Distributions.")

# ──────────────────────────────────────────────────────────────────────────────
# Tab 3 — Outliers
# ──────────────────────────────────────────────────────────────────────────────

with tab_outlier:
    st.subheader("Outlier Inspection")
    st.caption("Boxplots on the **raw** (non-transformed) data before IQR capping.")

    if outlier_cols:
        fig, ax = plt.subplots(figsize=(max(8, len(outlier_cols) * 1.2), 5))
        sns.boxplot(data=df_raw[outlier_cols], ax=ax, palette="Set2")
        ax.set_title("Boxplots — Raw Data")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close(fig)

        st.write("**After IQR capping (transformed dataset)**")
        fig2, ax2 = plt.subplots(figsize=(max(8, len(outlier_cols) * 1.2), 5))
        sns.boxplot(data=data[outlier_cols], ax=ax2, palette="Set3")
        ax2.set_title("Boxplots — After IQR Cap + Log Transform")
        plt.xticks(rotation=45)
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("Select at least one column in the sidebar → Outliers.")

# ──────────────────────────────────────────────────────────────────────────────
# Tab 4 — Nutrients vs Disease
# ──────────────────────────────────────────────────────────────────────────────

with tab_nutrient:
    st.subheader("Nutrient Intake vs Disease / Goal")

    if not selected_nutrients or not selected_diseases_nd:
        st.info("Select nutrients and diseases in the sidebar → Nutrients vs Disease.")
    else:
        subset = data[data["Disease"].isin(selected_diseases_nd)]

        # Boxplots
        st.write("#### Distribution of Selected Nutrients Across Selected Diseases")
        n = len(selected_nutrients)
        ncols = 2
        nrows = (n + 1) // 2
        fig, axes = plt.subplots(nrows, ncols, figsize=(13, 5 * nrows))
        axes = np.array(axes).flatten()

        for i, nutrient in enumerate(selected_nutrients):
            sns.boxplot(
                data=subset, x="Disease", y=nutrient,
                palette="Set3", ax=axes[i],
            )
            axes[i].set_title(f"{nutrient} Across Diseases")
            axes[i].tick_params(axis="x", rotation=45)

        for j in range(n, len(axes)):
            axes[j].set_visible(False)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Average nutrient table
        st.write("#### Average Nutrient Intake per Disease / Goal")
        grouped = (
            subset[["Disease"] + selected_nutrients]
            .groupby("Disease")
            .mean()
            .sort_values(selected_nutrients[0], ascending=False)
        )
        st.dataframe(grouped.style.background_gradient(cmap="YlOrRd"), use_container_width=True)

        # Bar chart
        st.write("#### Bar Chart — Average Intake")
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        grouped.plot(kind="bar", ax=ax2, colormap="tab10")
        ax2.set_title("Average Suggested Nutrient Intake by Disease / Goal")
        ax2.set_ylabel("Average Value (log-transformed)")
        ax2.tick_params(axis="x", rotation=45)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

# ──────────────────────────────────────────────────────────────────────────────
# Tab 5 — Correlations
# ──────────────────────────────────────────────────────────────────────────────

with tab_corr:
    st.subheader("Correlation Analysis")

    if show_heatmap and corr_num_cols:
        st.write("#### Full Correlation Heatmap (Numerical Features)")
        fig, ax = plt.subplots(
            figsize=(max(8, len(corr_num_cols) * 0.9), max(6, len(corr_num_cols) * 0.8))
        )
        sns.heatmap(
            data[corr_num_cols].corr(),
            annot=True, fmt=".2f", cmap="RdBu", cbar=True, ax=ax,
        )
        ax.set_title("Correlation Matrix")
        st.pyplot(fig)
        plt.close(fig)

    if show_heatmap and corr_bin_cols and corr_num_cols:
        st.write("#### Nutrients + Disease Binary Correlation Heatmap")
        cols_for_heatmap = corr_num_cols + corr_bin_cols
        fig2, ax2 = plt.subplots(
            figsize=(max(10, len(cols_for_heatmap) * 0.8), max(8, len(cols_for_heatmap) * 0.7))
        )
        sns.heatmap(
            data[cols_for_heatmap].corr(),
            annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax2,
        )
        st.pyplot(fig2)
        plt.close(fig2)

    if show_corr_table and corr_bin_cols and corr_num_cols:
        st.write("#### Point-Biserial Correlation (Binary vs Numerical, p < 0.05)")
        corr_df = utils.correlation_pvalue(data, corr_bin_cols, corr_num_cols)
        if corr_df.empty:
            st.warning("No significant correlations found for selected columns.")
        else:
            st.dataframe(corr_df, use_container_width=True)

    if show_chi2_table and corr_bin_cols:
        st.write("#### Chi-Squared Test (Categorical vs Binary, p < 0.05)")
        chi_df = utils.cat_num_corr(data, CATEGORICAL_COLS, corr_bin_cols)
        if chi_df.empty:
            st.warning("No significant associations found for selected columns.")
        else:
            st.dataframe(chi_df, use_container_width=True)

    if not corr_num_cols and not corr_bin_cols:
        st.info("Select columns in the sidebar → Correlations.")

# ──────────────────────────────────────────────────────────────────────────────
# Tab 6 — Lifestyle vs Disease
# ──────────────────────────────────────────────────────────────────────────────

with tab_lifestyle:
    st.subheader("Lifestyle Feature vs Disease Breakdown")

    if not lifestyle_diseases:
        st.info("Select diseases in the sidebar → Lifestyle vs Disease.")
    else:
        if show_dietary:
            st.write("#### Dietary Preference vs Selected Diseases")
            utils.plot_dietary_vs_diseases(data, lifestyle_diseases)

        if show_activity:
            st.write("#### Activity Level vs Selected Diseases")
            utils.plot_activity_vs_diseases(data, lifestyle_diseases)

# ──────────────────────────────────────────────────────────────────────────────
# Tab 7 — Boxplot Grid
# ──────────────────────────────────────────────────────────────────────────────

with tab_boxgrid:
    st.subheader("Numeric Features × Categorical Features — Boxplot Grid")
    st.caption("Rows = selected numeric columns; columns = Gender, Activity Level, Dietary Preference.")

    if boxplot_num_cols:
        utils.plot_boxplot_grid(data, boxplot_num_cols)
    else:
        st.info("Select at least one numeric column in the sidebar → Boxplot Grid.")

# ──────────────────────────────────────────────────────────────────────────────
# Tab 8 — Clustering
# ──────────────────────────────────────────────────────────────────────────────

with tab_cluster:
    st.subheader("Meal / Patient Clustering")

    if len(cluster_features) < 2:
        st.info("Select at least 2 features in the sidebar → Clustering.")
    else:
        # ── Build clustering dataset ──
        if balance_clusters:
            cluster_df = (
                data
                .groupby("Disease", group_keys=False)
                .apply(lambda g: g.sample(min(len(g), balance_n), random_state=42))
                .reset_index(drop=True)
            )
            st.caption(
                f"Using balanced dataset: up to **{balance_n}** rows per disease group "
                f"→ **{len(cluster_df):,}** rows total."
            )
        else:
            cluster_df = data.copy()
            st.caption(f"Using full dataset: **{len(cluster_df):,}** rows.")

        # ── Elbow / Silhouette ──
        if show_elbow:
            st.write("#### Elbow & Silhouette — Choose the Right k")
            utils.plot_elbow_silhouette(cluster_df, cluster_features)

        # ── DBSCAN extra params ──
        if cluster_algo == "DBSCAN":
            c1, c2 = st.columns(2)
            eps_val = c1.slider("DBSCAN eps", 0.1, 3.0, 0.5, step=0.05)
            min_samp = c2.slider("DBSCAN min_samples", 2, 20, 5)

        # ── Run selected algorithm ──
        st.write(f"#### {cluster_algo} Clustering (k = {n_clusters})")

        common_kwargs = dict(
            features=cluster_features,
            x_feature=cluster_x,
            y_feature=cluster_y,
            title=f"{cluster_algo} Clusters (k={n_clusters})",
        )

        if cluster_algo == "K-Means":
            clustered = utils.cluster_meals(cluster_df, n_clusters=n_clusters, **common_kwargs)
        elif cluster_algo == "K-Medoids":
            clustered = utils.cluster_meals_kmedoids(cluster_df, n_clusters=n_clusters, **common_kwargs)
        elif cluster_algo == "Agglomerative":
            clustered = utils.agglomerative_clustering(cluster_df, n_clusters=n_clusters, **common_kwargs)
        else:  # DBSCAN
            clustered = utils.dbscan_clustering(
                cluster_df, eps=eps_val, min_samples=min_samp, **common_kwargs
            )

        # ── Cluster profiles ──
        st.write("#### Cluster Profiles (mean | median | std)")
        profiles = (
            clustered.groupby("Cluster")[cluster_features]
            .agg(["mean", "median", "std"])
            .round(3)
        )
        st.dataframe(profiles, use_container_width=True)

        # ── Cluster sizes ──
        st.write("#### Cluster Sizes")
        sizes = clustered["Cluster"].value_counts().reset_index()
        sizes.columns = ["Cluster", "Count"]
        fig, ax = plt.subplots(figsize=(6, 3))
        sns.barplot(data=sizes, x="Cluster", y="Count", palette="Set2", ax=ax)
        ax.set_title("Rows per Cluster")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

# ──────────────────────────────────────────────────────────────────────────────
# Tab 9 — Meal Recommendations
# ──────────────────────────────────────────────────────────────────────────────

with tab_recommend:
    render_recommendation_tab(df_raw, rec_inputs)
