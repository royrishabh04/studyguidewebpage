
import io
import streamlit as st
from typing import List, Tuple
from PyPDF2 import PdfReader

from ai import summarize_text, generate_flashcards, sanitize_text
from pdf_utils import export_flashcards_pdf

st.set_page_config(page_title="AI Flashcards & Summary", page_icon="🃏", layout="wide")

st.title("🃏 AI Flashcards & Summary")
st.caption("Filter notes → Summarize → Generate flashcards → Export duplex-ready PDF")

with st.sidebar:
    st.header("Settings")
    max_summary_sents = st.slider("Summary sentences", 3, 15, 7, 1)
    num_cards = st.slider("Flashcards to generate", 4, 64, 24, 1)
    cols = st.slider("Cards per row", 1, 4, 2, 1)
    rows = st.slider("Cards per column", 1, 6, 4, 1)
    margin = st.number_input("Page margin (mm)", 6.0, 30.0, 12.0, 1.0)
    gutter = st.number_input("Card gutter (mm)", 2.0, 20.0, 6.0, 1.0)
    draw_borders = st.checkbox("Draw card borders", True)
    q_font = st.slider("Question font size", 8, 20, 12, 1)
    a_font = st.slider("Answer font size", 8, 20, 12, 1)

uploaded = st.file_uploader("Upload notes as .txt or .pdf", type=["txt", "pdf"])
text_input = st.text_area("...or paste notes here", height=200)

def read_pdf(file) -> str:
    reader = PdfReader(file)
    out = []
    for page in reader.pages:
        try:
            out.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(out)

notes = ""

if uploaded is not None:
    if uploaded.name.lower().endswith(".pdf"):
        notes = read_pdf(uploaded)
    else:
        notes = uploaded.read().decode("utf-8", errors="ignore")

if not notes and text_input:
    notes = text_input

notes = sanitize_text(notes)

if notes:
    st.subheader("Input Preview")
    st.write(notes[:1500] + ("..." if len(notes) > 1500 else ""))

col1, col2 = st.columns(2)

summary_text = ""
flashcards: List[Tuple[str, str]] = []

with col1:
    if st.button("Generate Summary", use_container_width=True):
        with st.spinner("Summarizing..."):
            summary_text = summarize_text(notes, max_sentences=max_summary_sents)
        st.success("Summary ready!")
        st.text_area("Summary", value=summary_text, height=240)

with col2:
    if st.button("Generate Flashcards", use_container_width=True):
        with st.spinner("Creating flashcards..."):
            flashcards = generate_flashcards(notes, num_cards=num_cards)
        st.success(f"Generated {len(flashcards)} flashcards.")
        if flashcards:
            for i, (q, a) in enumerate(flashcards, 1):
                with st.expander(f"Card {i}"):
                    st.markdown(f"**Q:** {q}")
                    st.markdown(f"**A:** {a}")

# Persist in session so user can export even if created in previous action
if "flashcards" not in st.session_state:
    st.session_state["flashcards"] = []
if flashcards:
    st.session_state["flashcards"] = flashcards

st.divider()
st.subheader("Export")

if st.session_state["flashcards"]:
    if st.button("Export PDF (A4, duplex-ready)", type="primary"):
        buf = io.BytesIO()
        export_flashcards_pdf(
            st.session_state["flashcards"],
            output_path=buf,
            cols=cols,
            rows=rows,
            margin_mm=margin,
            gutter_mm=gutter,
            draw_borders=draw_borders,
            question_font_size=q_font,
            answer_font_size=a_font,
        )
        buf.seek(0)
        st.download_button(
            "Download PDF",
            data=buf.read(),
            file_name="flashcards_duplex_A4.pdf",
            mime="application/pdf"
        )
else:
    st.info("Generate flashcards to enable PDF export.")
