import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from extractor.pipeline import extract_invoice

st.set_page_config(page_title="Structured Data Extractor", layout="wide")
st.title("Structured Data Extractor")

left, right = st.columns(2)
with left:
    text = st.text_area("Paste unstructured text", height=450)
    run = st.button("Extract", type="primary")

with right:
    if run and text.strip():
        with st.spinner("Extracting..."):
            result = extract_invoice(text)
        if result.needs_review:
            st.warning("Needs review: " + " ".join(result.warnings))
        st.caption(f"Attempts: {result.attempts}")
        st.json(result.model_dump())
