import sys
import subprocess

import streamlit as st
import matplotlib.pyplot as plt

from recommender.sens import (
    load_pro_csv,
    nearest_pro_examples,
    choose_target_cm360,
    sens_from_cm360,
    compute_edpi,
    compute_cm360,
)

st.set_page_config(page_title="Valorant Sensitivity Recommender", page_icon="🎯", layout="wide")

st.title("🎯 Valorant Sensitivity Recommender")
st.caption("Explainable sensitivity recommendations using pro player settings (Liquipedia).")

# --- Load dataset ---
df = load_pro_csv("data/pro_sens.csv")

# --- Dataset stats (top info) ---
st.caption(
    f"Dataset size: {len(df)} players • "
    f"Median eDPI: {df['edpi'].median():.0f} • "
    f"10–90%: {df['edpi'].quantile(0.10):.0f}–{df['edpi'].quantile(0.90):.0f}"
)

# --- Inputs ---
st.subheader("Your settings")

dpi = st.number_input("Mouse DPI", min_value=100, max_value=3200, value=800, step=50)
aim_style = st.selectbox("Aim style", ["wrist", "hybrid", "arm"], index=1)
goal = st.selectbox("Goal", ["balanced", "precision", "speed"], index=0)
pad = st.selectbox("Mousepad size", ["small", "medium", "large"], index=1)

st.divider()

# --- Compute recommendation ---
low_cm, high_cm = choose_target_cm360(aim_style, goal, pad)
mid_cm = (low_cm + high_cm) / 2.0

# lower cm/360 => faster => higher sens
rec_low_sens = sens_from_cm360(dpi, high_cm)  # slower end
rec_high_sens = sens_from_cm360(dpi, low_cm)  # faster end

mid_sens = sens_from_cm360(dpi, mid_cm)
mid_edpi = compute_edpi(dpi, mid_sens)

# --- Output ---
st.subheader("Recommendation")
st.write(f"**Target cm/360:** {low_cm:.1f} – {high_cm:.1f}")
st.write(f"**Suggested sensitivity (at {int(dpi)} DPI):** {rec_low_sens:.3f} – {rec_high_sens:.3f}")
st.write(f"**Try first (midpoint):** **{mid_sens:.3f}**  •  **eDPI {mid_edpi:.0f}**")
st.caption("This is a starting point based on pro data — small adjustments are normal.")

st.divider()

# --- Compare section ---
st.subheader("Compare to your current sensitivity (optional)")

compare = st.checkbox("Compare to my current sensitivity", value=True, key="compare_checkbox")

current_sens = None
cur_edpi = None
cur_cm = None

if compare:
    current_sens = st.number_input(
        "Current in-game sensitivity",
        min_value=0.05,
        max_value=2.0,
        value=0.35,
        step=0.01,
        key="current_sens_input",
    )
    cur_edpi = compute_edpi(dpi, current_sens)
    cur_cm = compute_cm360(dpi, current_sens)

    st.write(f"Your current: **sens {current_sens:.3f}** • **eDPI {cur_edpi:.0f}** • ~{cur_cm:.1f} cm/360")

st.divider()

# --- Export block ---
st.subheader("Copy your settings")

export_text = (
    f"DPI: {int(dpi)}\n"
    f"Recommended sens (midpoint): {mid_sens:.3f}\n"
    f"Recommended eDPI: {mid_edpi:.0f}\n"
    f"Target cm/360: {low_cm:.1f}–{high_cm:.1f}\n"
)

if compare and current_sens is not None and cur_edpi is not None:
    export_text += (
        f"\nYour current sens: {current_sens:.3f}\n"
        f"Your current eDPI: {cur_edpi:.0f}\n"
    )

st.code(export_text, language="text")

st.subheader("How to dial it in (simple plan)")
st.markdown(
    f"""
- Start at **{mid_sens:.3f}** for 2–3 days.
- If it feels **too slow**, increase by ~5% → **{mid_sens * 1.05:.3f}**
- If it feels **too fast**, decrease by ~5% → **{mid_sens * 0.95:.3f}**
- Keep your DPI fixed while testing.
"""
)

st.divider()

# --- Closest pros ---
st.subheader("Closest pros (by eDPI)")

mode = st.radio("Compare pros to:", ["Recommended midpoint", "My current"], horizontal=True, key="compare_mode")

if mode == "My current" and compare and cur_edpi is not None:
    target_edpi = cur_edpi
    st.caption("Sorted by distance from your current eDPI.")
else:
    target_edpi = mid_edpi
    st.caption("Sorted by distance from the recommended midpoint eDPI.")

st.dataframe(nearest_pro_examples(df, target_edpi, k=10), use_container_width=True)

st.divider()

# --- Distribution chart (smaller + clearer) ---
st.subheader("Where you sit vs pros (eDPI distribution)")

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(df["edpi"].dropna(), bins=30, alpha=0.7, label="Pro players")

ax.axvline(mid_edpi, linewidth=2, linestyle="--", label="Recommended midpoint")

if compare and cur_edpi is not None:
    ax.axvline(cur_edpi, linewidth=2, linestyle="-", label="Your current eDPI")

ax.set_xlabel("eDPI")
ax.set_ylabel("Number of pros")
ax.legend()

st.pyplot(fig, clear_figure=True)
st.caption("Left = slower / more control • Right = faster / more speed")

with st.expander("How this works"):
    st.markdown(
        """
- Pulls pro player settings from Liquipedia and saves a cleaned dataset (player, sens, eDPI)
- Applies sanity filters to remove unrealistic values
- Chooses a target cm/360 range based on your aim style + goal + mousepad size
- Converts cm/360 into a Valorant sensitivity value for your DPI
- Compares you to pros by absolute eDPI distance (closest eDPI = most similar overall speed)
        """.strip()
    )

st.divider()
with st.expander("Developer tools"):
    st.caption("Refresh the pro dataset (runs the fetch + cleaning script).")
    if st.button("Refresh pro dataset", key="refresh_dataset_btn"):
        with st.spinner("Updating pro dataset from Liquipedia..."):
            subprocess.run([sys.executable, "scripts/fetch_pro_sens_liquipedia.py"], check=True)
        st.success("Updated data/pro_sens.csv ✅")
        st.rerun()