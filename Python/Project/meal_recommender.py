"""
meal_recommender.py
-------------------
Meal recommendation engine for the Nutrition EDA Dashboard.

IMPORT THIS FILE IN: app.py  ← only here, alongside other imports.
DO NOT import it in graphs.py.

Dataset assumptions (columns that must exist):
    - "Disease"              : ONE condition per row (pass the exploded `data`
                               DataFrame from app.py, NOT df_raw)
                               e.g. "Diabetes", "Weight Loss", "Hypertension"
    - "Dietary Preference"   : e.g. "Vegan", "Omnivore"
    - "Breakfast Suggestion" : meal text for breakfast
    - "Lunch Suggestion"     : meal text for lunch
    - "Dinner Suggestion"    : meal text for dinner
    - "Snack Suggestion"     : meal text for snacks
    - Nutrient columns       : Calories, Protein, Carbohydrates, Fat, Fiber, Sugar, Sodium

How it works:
    1. User fills in their profile (age, weight, height, activity, conditions, diet).
    2. compute_targets()     → derives personalised daily macro targets (Harris-Benedict).
    3. split_meal_targets()  → splits daily targets into per-meal fractions
                               (Breakfast 25%, Lunch 35%, Snacks 10%, Dinner 30%).
    4. recommend_for_slot()  → filters rows whose Disease field matches the user's
                               conditions AND dietary preference matches, then ranks
                               by weighted Euclidean distance to that slot's nutrient
                               targets. Returns the suggestion text + nutrient info.
    5. render_recommendation_tab() → full Streamlit UI, call from app.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

# Maps each meal slot to its suggestion column in the dataset
MEAL_SLOTS: dict[str, str] = {
    "🌅 Breakfast": "Breakfast Suggestion",
    "☀️ Lunch":     "Lunch Suggestion",
    "🍎 Snacks":    "Snack Suggestion",
    "🌙 Dinner":    "Dinner Suggestion",
}

NUTRIENT_COLS = ["Calories", "Protein", "Carbohydrates", "Fat", "Fiber", "Sugar", "Sodium"]

NUTRIENT_WEIGHTS = {
    "Calories":      3.0,
    "Protein":       2.5,
    "Carbohydrates": 1.5,
    "Fat":           1.5,
    "Fiber":         1.0,
    "Sugar":         1.0,
    "Sodium":        1.0,
}

# Fraction of daily total each slot should cover
MEAL_SPLITS = {
    "🌅 Breakfast": 0.25,
    "☀️ Lunch":     0.35,
    "🍎 Snacks":    0.10,
    "🌙 Dinner":    0.30,
}

MEAL_COLORS = {
    "🌅 Breakfast": "#FFF3CD",
    "☀️ Lunch":     "#D1ECF1",
    "🍎 Snacks":    "#D4EDDA",
    "🌙 Dinner":    "#E2D9F3",
}

ACTIVITY_MULTIPLIERS = {
    "Sedentary":         1.2,
    "Lightly Active":    1.375,
    "Moderately Active": 1.55,
    "Very Active":       1.725,
    "Extremely Active":  1.9,
}

# Disease → per-nutrient target adjustment multipliers
DISEASE_ADJUSTMENTS: dict[str, dict[str, float]] = {
    "Diabetes":      {"Sugar": 0.5,  "Carbohydrates": 0.75, "Fiber": 1.3},
    "Hypertension":  {"Sodium": 0.6, "Fat": 0.85},
    "Heart Disease": {"Fat": 0.8,    "Sodium": 0.65, "Fiber": 1.2},
    "Kidney Disease":{"Protein": 0.7,"Sodium": 0.6,  "Carbohydrates": 1.1},
    "Acne":          {"Sugar": 0.7,  "Fat": 0.85},
    "Weight Gain":   {"Calories": 1.15, "Protein": 1.2},
    "Weight Loss":   {"Calories": 0.8,  "Fat": 0.8, "Sugar": 0.75},
}


# ──────────────────────────────────────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────────────────────────────────────

def compute_targets(
    age: int,
    weight_kg: float,
    height_cm: float,
    gender: str,
    activity_level: str,
    conditions: list[str],
) -> dict[str, float]:
    """
    Derive personalised daily macro targets.
    Harris-Benedict BMR × activity multiplier → 40/30/30 macro split → disease adjustments.
    """
    if gender == "Male":
        bmr = 88.362 + 13.397 * weight_kg + 4.799 * height_cm - 5.677 * age
    else:
        bmr = 447.593 + 9.247 * weight_kg + 3.098 * height_cm - 4.330 * age

    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)

    targets = {
        "Calories":      tdee,
        "Protein":       (tdee * 0.30) / 4,
        "Carbohydrates": (tdee * 0.40) / 4,
        "Fat":           (tdee * 0.30) / 9,
        "Fiber":         25.0 if gender == "Female" else 38.0,
        "Sugar":         50.0,
        "Sodium":        2300.0,
    }

    for condition in conditions:
        for nutrient, factor in DISEASE_ADJUSTMENTS.get(condition, {}).items():
            if nutrient in targets:
                targets[nutrient] *= factor

    return targets


def split_meal_targets(daily_targets: dict[str, float]) -> dict[str, dict[str, float]]:
    """Split daily targets into per-slot targets using MEAL_SPLITS fractions."""
    return {
        slot: {nutrient: value * frac for nutrient, value in daily_targets.items()}
        for slot, frac in MEAL_SPLITS.items()
    }


def recommend_for_slot(
    df: pd.DataFrame,
    slot_name: str,
    suggestion_col: str,
    slot_targets: dict[str, float],
    dietary_preference: str | None,
    conditions: list[str],
    top_n: int,
) -> pd.DataFrame:
    """
    Find the best-matching rows for one meal slot.

    Filtering:
        1. Must have a non-null value in suggestion_col.
        2. Disease column must contain at least one of the user's conditions.
           (If user selected no conditions, skip this filter.)
        3. Dietary preference must match (if not "Any").

    Scoring:
        Weighted normalised Euclidean distance across NUTRIENT_COLS.
        Lower distance → higher Match Score (%).

    Returns DataFrame with columns:
        [suggestion_col, "Match Score (%)", <nutrient cols>, "Dietary Preference", "Disease"]
    """
    result = df.copy()

    # Step 1 — must have a suggestion for this slot
    if suggestion_col in result.columns:
        result = result[result[suggestion_col].notna() & (result[suggestion_col].str.strip() != "")]
    else:
        st.warning(f"Column '{suggestion_col}' not found in dataset.")
        return pd.DataFrame()

    # Step 2 — disease / condition match.
    # df passed here is the exploded `data` DataFrame where each row has
    # exactly ONE disease string — so .isin() gives a precise exact match,
    # not a substring match across a comma-separated cell.
    if conditions:
        disease_mask = result["Disease"].isin(conditions)
        if disease_mask.sum() > 0:
            result = result[disease_mask]
        # if nothing matches, keep full set (graceful fallback)

    # Step 3 — dietary preference
    if dietary_preference and dietary_preference != "Any":
        pref_mask = result["Dietary Preference"].str.lower() == dietary_preference.lower()
        if pref_mask.sum() > 0:
            result = result[pref_mask]

    if result.empty:
        return pd.DataFrame()

    # Step 4 — score by weighted Euclidean distance to slot targets
    available_cols = [c for c in NUTRIENT_COLS if c in result.columns]
    weights      = np.array([NUTRIENT_WEIGHTS[c] for c in available_cols])
    target_vals  = np.array([slot_targets[c] for c in available_cols])
    safe_targets = np.where(target_vals == 0, 1.0, target_vals)

    rows_matrix = result[available_cols].fillna(0).values.astype(float)
    diff        = (rows_matrix - target_vals) / safe_targets
    distances   = np.sqrt((diff ** 2 * weights).sum(axis=1))

    max_dist = distances.max() if distances.max() > 0 else 1.0
    result = result.copy()
    result["Match Score (%)"] = ((1 - distances / max_dist) * 100).round(1)

    # Keep only the columns that matter for display.
    # "Disease" and "Dietary Preference" are intentionally excluded — the user
    # already specified these as inputs, and showing the full Disease string
    # (e.g. "Weight Gain, Hypertension, Kidney Disease") for a row matched on
    # "Weight Gain" only causes confusion.
    keep_cols = ["Match Score (%)", suggestion_col] + available_cols
    keep_cols = list(dict.fromkeys(keep_cols))  # deduplicate, preserve order

    return (
        result[keep_cols]
        .sort_values("Match Score (%)", ascending=False)
        .drop_duplicates(subset=[suggestion_col])   # avoid showing identical suggestions
        .head(top_n)
        .reset_index(drop=True)
    )


def recommend_full_day(
    df: pd.DataFrame,
    daily_targets: dict[str, float],
    dietary_preference: str | None,
    conditions: list[str],
    top_n: int = 5,
) -> dict[str, pd.DataFrame]:
    """
    Run recommendations for all four meal slots.

    Returns:
        { "🌅 Breakfast": DataFrame, "☀️ Lunch": DataFrame, ... }
    """
    per_slot_targets = split_meal_targets(daily_targets)
    return {
        slot: recommend_for_slot(
            df=df,
            slot_name=slot,
            suggestion_col=col,
            slot_targets=per_slot_targets[slot],
            dietary_preference=dietary_preference,
            conditions=conditions,
            top_n=top_n,
        )
        for slot, col in MEAL_SLOTS.items()
    }


# ──────────────────────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────────────────────

def render_recommendation_tab(
    df: pd.DataFrame,
    sidebar_inputs: dict,
) -> None:
    """
    Full Streamlit UI for the Meal Recommendations tab.

    Call inside `with tab_recommend:` in app.py:

        with tab_recommend:
            render_recommendation_tab(df_raw, rec_inputs)

    Args:
        df             — df_raw (unmodified DataFrame from load_from_db())
        sidebar_inputs — dict returned by render_recommendation_sidebar()
    """
    st.subheader("🍽️ Personalised Daily Meal Plan")
    st.caption(
        "Recommendations are drawn directly from the **Breakfast Suggestion**, "
        "**Lunch Suggestion**, **Snack Suggestion**, and **Dinner Suggestion** columns "
        "in the database, filtered by your health conditions and dietary preference, "
        "then ranked by how closely each row's nutrient profile matches your personal targets."
    )

    daily_targets = compute_targets(
        age=sidebar_inputs["age"],
        weight_kg=sidebar_inputs["weight_kg"],
        height_cm=sidebar_inputs["height_cm"],
        gender=sidebar_inputs["gender"],
        activity_level=sidebar_inputs["activity_level"],
        conditions=sidebar_inputs["conditions"],
    )

    # Expandable target table
    with st.expander("📐 Your daily targets & per-meal breakdown", expanded=False):
        per_slot = split_meal_targets(daily_targets)
        summary = {"Nutrient": NUTRIENT_COLS}
        summary["🗓️ Daily Total"] = [round(daily_targets.get(n, 0), 1) for n in NUTRIENT_COLS]
        for slot, targets in per_slot.items():
            summary[slot] = [round(targets.get(n, 0), 1) for n in NUTRIENT_COLS]
        st.dataframe(
            pd.DataFrame(summary).set_index("Nutrient"),
            use_container_width=True,
        )

    if not st.button("🔍 Generate My Daily Meal Plan", type="primary"):
        st.info("👆 Click above to generate your personalised meal plan.")
        return

    with st.spinner("Matching meals to your profile…"):
        all_recs = recommend_full_day(
            df=df,
            daily_targets=daily_targets,
            dietary_preference=sidebar_inputs["dietary_preference"],
            conditions=sidebar_inputs["conditions"],
            top_n=sidebar_inputs["top_n"],
        )

    st.success("✅ Your daily meal plan is ready!")
    st.divider()

    nutrient_disp = [c for c in NUTRIENT_COLS if c in df.columns]
    day_totals: dict[str, list[float]] = {n: [] for n in nutrient_disp}
    per_slot_targets = split_meal_targets(daily_targets)

    # ── One card per meal slot ──
    for slot, recs in all_recs.items():
        col_name    = MEAL_SLOTS[slot]
        slot_cal    = per_slot_targets[slot]["Calories"]
        slot_pct    = int(MEAL_SPLITS[slot] * 100)

        # Coloured header card
        st.markdown(
            f"<div style='background:{MEAL_COLORS[slot]}; padding:12px 16px; "
            f"border-radius:8px; margin-bottom:6px;'>"
            f"<h4 style='margin:0'>{slot}</h4>"
            f"<small>Target: <b>{slot_cal:.0f} kcal</b> · {slot_pct}% of daily total</small>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if recs.empty:
            st.warning(
                f"No matches found for {slot}. "
                "Try selecting fewer conditions or choosing 'Any' for dietary preference."
            )
        else:
            # Rename suggestion column to "Suggested Meal" for clarity
            display = recs.rename(columns={col_name: "Suggested Meal"})

            st.dataframe(
                display.style.background_gradient(subset=["Match Score (%)"], cmap="Greens"),
                use_container_width=True,
                hide_index=True,
            )

            # Top-1 pick for day summary
            top_row = recs.iloc[0]
            for n in nutrient_disp:
                day_totals[n].append(float(top_row.get(n, 0)))

        st.divider()

    # ── Day summary ──
    st.write("### 📊 Day Summary  *(top pick from each slot)*")
    st.caption("How your best-matched meal per slot adds up against your daily targets.")

    if all(len(v) > 0 for v in day_totals.values()):
        summary_df = pd.DataFrame({
            "Nutrient":          nutrient_disp,
            "Your Daily Target": [round(daily_targets.get(n, 0), 1) for n in nutrient_disp],
            "Sum of Top Picks":  [round(sum(day_totals[n]), 1)       for n in nutrient_disp],
        })
        summary_df["Difference (%)"] = (
            (summary_df["Sum of Top Picks"] - summary_df["Your Daily Target"])
            / summary_df["Your Daily Target"].replace(0, 1) * 100
        ).round(1)

        def _colour_diff(val):
            if abs(val) <= 10:  return "color: green"
            if abs(val) <= 20:  return "color: orange"
            return "color: red"

        st.dataframe(
            summary_df.style.applymap(_colour_diff, subset=["Difference (%)"]),
            use_container_width=True,
            hide_index=True,
        )

    # ── CSV download ──
    st.write("### ⬇️ Download Full Plan")
    frames = []
    for slot, recs in all_recs.items():
        if not recs.empty:
            tmp = recs.rename(columns={MEAL_SLOTS[slot]: "Suggested Meal"}).copy()
            tmp.insert(0, "Meal Slot", slot)
            frames.append(tmp)

    if frames:
        csv = pd.concat(frames, ignore_index=True).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download full meal plan as CSV",
            data=csv,
            file_name="daily_meal_plan.csv",
            mime="text/csv",
        )


def render_recommendation_sidebar() -> dict:
    """
    Sidebar controls for the Meal Recommendations tab.

    Call inside the sidebar expander in app.py:

        with st.expander("🍽️ Meal Recommendations", expanded=False):
            rec_inputs = render_recommendation_sidebar()

    Returns:
        dict consumed by render_recommendation_tab().
    """
    age            = st.slider("Age", 10, 90, 30)
    weight_kg      = st.number_input("Weight (kg)",  min_value=30.0,  max_value=200.0, value=70.0,  step=0.5)
    height_cm      = st.number_input("Height (cm)",  min_value=100.0, max_value=250.0, value=170.0, step=0.5)
    gender         = st.selectbox("Gender", ["Male", "Female"])
    activity_level = st.selectbox(
        "Activity Level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
        index=2,
    )
    dietary_preference = st.selectbox(
        "Dietary Preference",
        ["Any", "Vegetarian", "Vegan", "Omnivore", "Pescatarian"],
    )
    conditions = st.multiselect(
        "Your health conditions / goals",
        ["Acne", "Diabetes", "Heart Disease", "Hypertension",
         "Kidney Disease", "Weight Gain", "Weight Loss"],
        help="Rows whose Disease column matches your selections will be prioritised.",
    )
    top_n = st.slider("Results per meal slot", 3, 15, 5)

    return {
        "age":                age,
        "weight_kg":          weight_kg,
        "height_cm":          height_cm,
        "gender":             gender,
        "activity_level":     activity_level,
        "dietary_preference": dietary_preference,
        "conditions":         conditions,
        "top_n":              top_n,
    }
