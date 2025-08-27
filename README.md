
# AI Flashcards & Summary Web App (Streamlit)

A simple, local-first Streamlit app that:
- Filters and summarizes long notes.
- Generates flashcards (Q/A) automatically.
- Exports flashcards as a duplex-friendly **A4 PDF** with **multiple cards per sheet**:
  - **Questions** on the front page
  - **Answers** on the back page (mirrored across the vertical axis for long-edge duplex printing).

> No external API required. Works offline using classical NLP (NLTK + RAKE + Sumy).
> If you want to plug in your own LLM, see `ai.py` (search for `ADVANCED_AI` sections).

## Quick Start

1. **Create & activate a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
   .venv/bin/python -m nltk.downloader punkt punkt_tab stopwords averaged_perceptron_tagger

Windows 
.\.venv\Scripts\python.exe -m nltk.downloader punkt punkt_tab stopwords averaged_perceptron_tagger

   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Use it**
   - Upload a **.txt** or **.pdf** of your notes (English).
   - Pick summary length and number of flashcards.
   - Click **Generate Summary** / **Generate Flashcards**.
   - Click **Export PDF** to download an A4, multi-card, duplex-ready PDF.

## Duplex Printing Notes

- In your printer dialog, choose **Two-sided**/**Duplex**, **Long Edge** binding.
- The app mirrors the back (answers) layout so each answer aligns with the question on the opposite side.
- Default layout is **2 columns × 4 rows** (8 cards per sheet). You can tweak in the sidebar.

## Project Structure

```
app.py            # Streamlit UI
ai.py             # Text filtering, summarization, and flashcard generation
pdf_utils.py      # A4 multi-card PDF exporter (front/back mirrored pages)
requirements.txt  # Python deps
```

## Optional: Use your own LLM

In `ai.py`, find the `ADVANCED_AI` section. You can integrate your model (OpenAI, Gemini, etc.).
We keep a **deterministic local fallback** (RAKE + Sumy + heuristics) so the app works offline.

---

Made for quick study workflows: summarize → generate → print → flip & quiz.
