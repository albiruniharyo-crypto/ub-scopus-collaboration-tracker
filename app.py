from __future__ import annotations
import pandas as pd
import streamlit as st
from db import load_candidates

st.set_page_config(page_title="UB Scopus Collaboration Tracker", layout="wide")
st.title("UB Scopus Collaboration Tracker")
st.caption("Profesor patologi anatomi veteriner dan bidang berdekatan — data dari Elsevier/Scopus API.")

df = load_candidates()
if df.empty:
    st.info("Database masih kosong. Jalankan pipeline.py terlebih dahulu.")
    st.stop()

for col in ["h_index", "citation_count", "document_count", "current_doc_count", "relevance_score"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

c1, c2, c3 = st.columns(3)
min_h = c1.number_input("H-index minimum", min_value=0, value=35, step=1)
countries = sorted(x for x in df["country"].dropna().unique() if x)
selected_countries = c2.multiselect("Negara", countries)
keyword = c3.text_input("Kata kunci nama/institusi/subjek")

filtered = df[df["h_index"] >= min_h].copy()
if selected_countries:
    filtered = filtered[filtered["country"].isin(selected_countries)]
if keyword:
    needle = keyword.lower()
    mask = (
        filtered["full_name"].fillna("").str.lower().str.contains(needle)
        | filtered["affiliation"].fillna("").str.lower().str.contains(needle)
        | filtered["subject_areas"].fillna("").str.lower().str.contains(needle)
    )
    filtered = filtered[mask]

filtered = filtered.sort_values(
    ["relevance_score", "h_index", "citation_count"],
    ascending=False
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Kandidat", len(filtered))
m2.metric("H-index median", int(filtered["h_index"].median()) if len(filtered) else 0)
m3.metric("Sitasi total", f"{int(filtered['citation_count'].sum()):,}")
m4.metric("Negara", filtered["country"].nunique())

display_cols = [
    "full_name", "affiliation", "country", "h_index", "citation_count",
    "document_count", "current_doc_count", "relevance_score",
    "subject_areas", "orcid", "author_id", "last_updated"
]
st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

st.subheader("Kandidat tertinggi")
chart_df = filtered.head(20).set_index("full_name")[["h_index", "relevance_score"]]
st.bar_chart(chart_df)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Unduh hasil CSV",
    data=csv,
    file_name="ub_scopus_candidates.csv",
    mime="text/csv",
)
