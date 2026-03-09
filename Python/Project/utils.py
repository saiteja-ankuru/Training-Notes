"""
graphs.py
---------
Reusable plotting and analysis helpers for the Nutrition EDA Dashboard.
All functions render directly into the active Streamlit app.
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from scipy.stats import chi2_contingency, pointbiserialr
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.preprocessing import RobustScaler
from sklearn_extra.cluster import KMedoids

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CATEGORICAL_FEATURES = ["Gender", "Activity Level", "Dietary Preference"]

FEATURE_ORDER: dict[str, list[str] | None] = {
    "Gender": None,
    "Activity Level": [
        "Sedentary",
        "Lightly Active",
        "Moderately Active",
        "Very Active",
        "Extremely Active",
    ],
    "Dietary Preference": ["Vegetarian", "Vegan", "Omnivore", "Pescatarian"],
}

GENDER_PALETTE = {"Male": "#a0c6ff", "Female": "#e6e6fa"}

ACTIVITY_PALETTE = {
    "Sedentary": "#faf2eb",
    "Lightly Active": "#fae0d9",
    "Moderately Active": "#ffa1a1",
    "Very Active": "#ff6f61",
    "Extremely Active": "#ff6347",
}

DIETARY_PALETTE = {
    "Vegetarian": "#a8d8a0",
    "Vegan": "#42ab42",
    "Omnivore": "#8c564b",
    "Pescatarian": "#f5a5b8",
}

PALETTE_MAPPING = {
    "Gender": GENDER_PALETTE,
    "Activity Level": ACTIVITY_PALETTE,
    "Dietary Preference": DIETARY_PALETTE,
}

HIST_COLORS = [
    "purple", "teal", "orange", "crimson", "royalblue",
    "darkgreen", "goldenrod", "magenta", "brown",
]


# ---------------------------------------------------------------------------
# Data utilities
# ---------------------------------------------------------------------------

def show_df_info(df: pd.DataFrame, title: str = "Dataset Information") -> None:
    """Display pandas df.info() inside Streamlit."""
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.subheader(title)
    st.text(buffer.getvalue())


def cap_outliers_iqr(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Clip each column in *cols* at the [Q1 - 1.5·IQR, Q3 + 1.5·IQR] fence.
    Returns a copy — the original DataFrame is not modified.
    """
    df = df.copy()
    for col in cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        df[col] = df[col].clip(lower=q1 - 1.5 * iqr, upper=q3 + 1.5 * iqr)
    return df


def correlation_pvalue(
    df: pd.DataFrame,
    binary_cols: list[str],
    numerical_cols: list[str],
) -> pd.DataFrame:
    """
    Point-biserial correlation between each binary column and each numerical
    column. Returns only statistically significant pairs (p < 0.05), sorted
    by |correlation| descending.
    """
    rows = []
    for b_col in binary_cols:
        for n_col in numerical_cols:
            corr, p = pointbiserialr(df[b_col], df[n_col])
            rows.append(
                {"Binary Column": b_col, "Numerical Column": n_col,
                 "Correlation": corr, "P-value": p}
            )
    results = pd.DataFrame(rows)
    sig = (
        results[results["P-value"] < 0.05]
        .sort_values("Correlation", key=abs, ascending=False)
        .assign(**{"P-value": lambda x: x["P-value"].map(lambda v: f"{v:.4e}")})
    )
    return sig


def cat_num_corr(
    df: pd.DataFrame,
    categorical_cols: list[str],
    binary_cols: list[str],
) -> pd.DataFrame:
    """
    Chi-squared test between each categorical column and each binary column.
    Returns only significant pairs (p < 0.05), sorted by chi-squared descending.
    """
    rows = []
    for cat in categorical_cols:
        for b_col in binary_cols:
            ct = pd.crosstab(df[cat], df[b_col])
            chi2, p, *_ = chi2_contingency(ct)
            rows.append(
                {"Categorical Column": cat, "Binary Column": b_col,
                 "Chi-squared": chi2, "P-value": p}
            )
    results = pd.DataFrame(rows)
    sig = (
        results[results["P-value"] < 0.05]
        .sort_values("Chi-squared", key=abs, ascending=False)
        .assign(**{"P-value": lambda x: x["P-value"].map(lambda v: f"{v:.4e}")})
    )
    return sig


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------

def plot_outlier_boxplot(df: pd.DataFrame) -> None:
    """Boxplots for all numeric columns — quick outlier scan."""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, ax=ax)
    ax.set_title("Boxplots for Numeric Columns")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close(fig)


def plot_numeric_distributions(
    df: pd.DataFrame,
    numeric_cols: list[str],
) -> None:
    """
    Histogram + KDE for each numeric column arranged in a 4×3 grid.
    Vertical lines mark Q1, Q3, mean, and median.
    """
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(4, 3, figsize=(18, 12))
    axes = axes.flatten()

    for idx, col in enumerate(numeric_cols[:12]):
        ax = axes[idx]
        sample = df[col].dropna()
        color = HIST_COLORS[hash(col) % len(HIST_COLORS)]

        sns.histplot(sample, kde=True, color=color, alpha=0.5, ax=ax)
        for val, ls, alpha in [
            (sample.quantile(0.25), "--", 0.8),
            (sample.quantile(0.75), "--", 0.8),
            (sample.mean(), "-",  0.8),
            (sample.median(), "-", 0.4),
        ]:
            ax.axvline(val, color=color, linestyle=ls, linewidth=1, alpha=alpha)

        ax.set_title(col)
        ax.set_xlabel("")
        ax.set_ylabel("")

    for j in range(len(numeric_cols[:12]), 12):
        fig.delaxes(axes[j])

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_categorical_distributions(df: pd.DataFrame) -> None:
    """Count-plot for each categorical feature rendered side-by-side."""
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, feature in enumerate(CATEGORICAL_FEATURES):
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.countplot(
            ax=ax,
            data=df,
            x=feature,
            order=FEATURE_ORDER.get(feature),
            palette=PALETTE_MAPPING.get(feature),
        )
        ax.tick_params(axis="x", rotation=45)
        with cols[i]:
            st.pyplot(fig)
        plt.close(fig)


def plot_boxplot_grid(df: pd.DataFrame, numerical_cols: list[str]) -> None:
    """
    Grid of boxplots: one row per numeric column, one column per categorical
    feature.
    """
    if not CATEGORICAL_FEATURES or not numerical_cols:
        st.warning("No categorical or numerical features provided.")
        return

    n_rows, n_cols = len(numerical_cols), len(CATEGORICAL_FEATURES)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(5 * n_cols, 4 * n_rows),
        constrained_layout=True,
    )

    # Normalise axes to always be 2-D
    if n_rows == 1 and n_cols == 1:
        axes = np.array([[axes]])
    elif n_rows == 1:
        axes = np.array([axes])
    elif n_cols == 1:
        axes = np.array([[ax] for ax in axes])

    for i, num_col in enumerate(numerical_cols):
        for j, cat_col in enumerate(CATEGORICAL_FEATURES):
            ax = axes[i, j]
            if df[[cat_col, num_col]].dropna().empty:
                ax.set_visible(False)
                continue
            sns.boxplot(
                ax=ax, data=df, x=cat_col, y=num_col,
                order=FEATURE_ORDER.get(cat_col),
                palette=PALETTE_MAPPING.get(cat_col, "pastel"),
            )
            ax.set_title(f"{num_col} by {cat_col}", fontsize=10)
            ax.set_xlabel(cat_col, fontsize=9)
            ax.set_ylabel(num_col, fontsize=9)
            ax.tick_params(axis="x", rotation=45)

    fig.suptitle("Boxplots of Numerical Features by Categorical Variables", fontsize=16)
    st.pyplot(fig)
    plt.close(fig)


def plot_dietary_vs_diseases(
    df: pd.DataFrame,
    binary_cols: list[str],
) -> None:
    """Count + normalised bar chart for each disease by dietary preference."""
    order = FEATURE_ORDER["Dietary Preference"]
    n_rows = len(binary_cols)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(n_rows, 2, figsize=(13, 5 * n_rows))
    if n_rows == 1:
        axes = np.array([axes])

    for i, disease in enumerate(binary_cols):
        if disease not in df.columns:
            continue

        sns.countplot(
            data=df, x="Dietary Preference", hue=disease,
            order=order, palette={0: "#A9A9A9", 1: "dodgerblue"},
            ax=axes[i, 0],
        )
        axes[i, 0].set_title(f"{disease} on Dietary Preference")
        axes[i, 0].set_ylabel("Count")
        axes[i, 0].tick_params(axis="x", rotation=45)

        proportions = (
            df.groupby(["Dietary Preference", disease])
            .size()
            .unstack()
            .fillna(0)
            .pipe(lambda d: d.div(d.sum(axis=1), axis=0))
        )
        if 1 in proportions.columns:
            sns.barplot(
                x=proportions.index, y=proportions[1],
                order=order, palette="Blues", ax=axes[i, 1],
            )
            axes[i, 1].set_title(f"{disease} by Dietary Preference (Normalised)")
            axes[i, 1].set_ylabel("Proportion")
        else:
            axes[i, 1].set_visible(False)
        axes[i, 1].tick_params(axis="x", rotation=45)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_activity_vs_diseases(
    df: pd.DataFrame,
    binary_cols: list[str],
) -> None:
    """Count + normalised bar chart for each disease by activity level."""
    order = FEATURE_ORDER["Activity Level"]
    binary_cols = [c for c in binary_cols if c in df.columns]
    if not binary_cols:
        st.warning("No valid disease columns found.")
        return

    n_rows = len(binary_cols)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(n_rows, 2, figsize=(13, 5 * n_rows))
    if n_rows == 1:
        axes = np.array([axes])

    for i, disease in enumerate(binary_cols):
        sns.countplot(
            data=df, x="Activity Level", hue=disease,
            order=order, palette={0: "#A9A9A9", 1: "dodgerblue"},
            ax=axes[i, 0],
        )
        axes[i, 0].set_title(f"{disease} on Activity Level")
        axes[i, 0].set_ylabel("Count")
        axes[i, 0].tick_params(axis="x", rotation=45)

        proportions = (
            df.groupby(["Activity Level", disease])
            .size()
            .unstack()
            .fillna(0)
            .pipe(lambda d: d.div(d.sum(axis=1), axis=0))
        )
        if 1 in proportions.columns:
            sns.barplot(
                x=proportions.index, y=proportions[1],
                order=order, palette=ACTIVITY_PALETTE, ax=axes[i, 1],
            )
            axes[i, 1].set_title(f"{disease} by Activity Level (Normalised)")
            axes[i, 1].set_ylabel("Proportion")
        else:
            axes[i, 1].set_visible(False)
        axes[i, 1].tick_params(axis="x", rotation=45)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def correlation_heatmap(df: pd.DataFrame) -> None:
    """Correlation heatmap for the core continuous numerical features."""
    numerical_cols = [
        "Ages", "Height", "Weight", "Daily Calorie Target",
        "Protein", "Sugar", "Sodium", "Calories",
        "Carbohydrates", "Fiber", "Fat",
    ]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        df[numerical_cols].corr(),
        annot=True, fmt=".2f", cmap="RdBu", cbar=True, ax=ax,
    )
    ax.set_title("Correlation Matrix for Continuous Numerical Features")
    st.pyplot(fig)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def plot_elbow_silhouette(
    df: pd.DataFrame,
    features: list[str],
    k_range: range = range(2, 10),
) -> None:
    """
    Plot the Elbow curve (inertia) and Silhouette scores side-by-side
    to help choose the optimal number of clusters for K-Means.
    """
    from sklearn.metrics import silhouette_score

    X = RobustScaler().fit_transform(df[features])
    inertias, scores = [], []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(X)
        inertias.append(km.inertia_)
        scores.append(silhouette_score(X, km.labels_))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(list(k_range), inertias, marker="o", color="steelblue")
    ax1.set_title("Elbow Curve")
    ax1.set_xlabel("k (number of clusters)")
    ax1.set_ylabel("Inertia")

    ax2.plot(list(k_range), scores, marker="o", color="seagreen")
    ax2.set_title("Silhouette Score")
    ax2.set_xlabel("k (number of clusters)")
    ax2.set_ylabel("Score (higher = better)")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _scatter_clusters(
    df: pd.DataFrame,
    x_feature: str,
    y_feature: str,
    title: str,
) -> None:
    """Internal helper: scatter plot coloured by the 'Cluster' column."""
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.scatterplot(
        data=df, x=x_feature, y=y_feature,
        hue="Cluster", palette="Set2", s=60, ax=ax,
    )
    ax.set_title(title)
    ax.margins(0.05)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _apply_labels(
    cluster_ids: np.ndarray,
    cluster_labels: dict | None,
    noise_label: str | None = None,
) -> list:
    if cluster_labels:
        return [cluster_labels.get(c, f"Cluster {c}") for c in cluster_ids]
    if noise_label is not None:
        return [noise_label if c == -1 else f"Cluster {c}" for c in cluster_ids]
    return [f"Cluster {c}" for c in cluster_ids]


def cluster_meals(
    df: pd.DataFrame,
    features: list[str],
    n_clusters: int = 3,
    cluster_labels: dict | None = None,
    x_feature: str = "Calories",
    y_feature: str = "Protein",
    title: str = "Meal Clusters (K-Means)",
) -> pd.DataFrame:
    """K-Means clustering. Returns df with an added 'Cluster' column."""
    df = df.copy()
    X = RobustScaler().fit_transform(df[features])
    ids = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto").fit_predict(X)
    df["Cluster"] = _apply_labels(ids, cluster_labels)
    _scatter_clusters(df, x_feature, y_feature, title)
    return df


def cluster_meals_kmedoids(
    df: pd.DataFrame,
    features: list[str],
    n_clusters: int = 3,
    cluster_labels: dict | None = None,
    x_feature: str = "Calories",
    y_feature: str = "Protein",
    title: str = "Meal Clusters (K-Medoids)",
) -> pd.DataFrame:
    """K-Medoids clustering. Returns df with an added 'Cluster' column."""
    df = df.copy()
    X = RobustScaler().fit_transform(df[features])
    ids = KMedoids(n_clusters=n_clusters, random_state=42).fit_predict(X)
    df["Cluster"] = _apply_labels(ids, cluster_labels)
    _scatter_clusters(df, x_feature, y_feature, title)
    return df


def dbscan_clustering(
    df: pd.DataFrame,
    features: list[str],
    eps: float = 0.5,
    min_samples: int = 5,
    cluster_labels: dict | None = None,
    x_feature: str = "Calories",
    y_feature: str = "Protein",
    title: str = "Meal Clusters (DBSCAN)",
) -> pd.DataFrame:
    """
    DBSCAN clustering.
    
    NOTE: DBSCAN is density-based and will label points that don't fit any
    cluster as 'Outlier' (-1). Tune *eps* and *min_samples* if most points
    are being labelled as noise.
    """
    df = df.copy()
    X = RobustScaler().fit_transform(df[features])
    ids = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)
    df["Cluster"] = _apply_labels(ids, cluster_labels, noise_label="Outlier")
    _scatter_clusters(df, x_feature, y_feature, title)
    return df


def agglomerative_clustering(
    df: pd.DataFrame,
    features: list[str],
    n_clusters: int = 3,
    linkage: str = "ward",
    cluster_labels: dict | None = None,
    x_feature: str = "Calories",
    y_feature: str = "Protein",
    title: str = "Meal Clusters (Agglomerative)",
) -> pd.DataFrame:
    """
    Agglomerative (hierarchical) clustering.
    *linkage='ward'* minimises within-cluster variance and works well with
    scaled numeric features.
    """
    df = df.copy()
    X = RobustScaler().fit_transform(df[features])
    ids = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage).fit_predict(X)
    df["Cluster"] = _apply_labels(ids, cluster_labels)
    _scatter_clusters(df, x_feature, y_feature, title)
    return df
