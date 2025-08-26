
from typing import List, Tuple, Dict
import re
from tqdm import tqdm

# Local NLP tools
from rake_nltk import Rake
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from nltk.corpus import stopwords
import nltk

LANG = "english"

def ensure_nltk():
    # Attempt to download required resources silently if missing
    try:
        _ = stopwords.words(LANG)
    except LookupError:
        nltk.download("stopwords")
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger")
    except LookupError:
        nltk.download("averaged_perceptron_tagger")


def sanitize_text(text: str) -> str:
    # Remove excessive whitespace, headers/footers heuristics
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers like "- 12 -" or "(12)"
    text = re.sub(r'[\-\( ]\s*\d{1,4}\s*[\-\) ]', ' ', text)
    # Collapse multiple spaces
    return re.sub(r' {2,}', ' ', text).strip()


def extract_keywords(text: str, max_keywords: int = 50) -> List[str]:
    ensure_nltk()
    r = Rake(language=LANG)
    r.extract_keywords_from_text(text)
    ranked = r.get_ranked_phrases()  # already scored by RAKE
    return ranked[:max_keywords]


def summarize_text(text: str, max_sentences: int = 7) -> str:
    ensure_nltk()
    text = sanitize_text(text)
    parser = PlaintextParser.from_string(text, Tokenizer(LANG))
    summarizer = TextRankSummarizer(Stemmer(LANG))
    summarizer.stop_words = set(stopwords.words(LANG))
    summary_sents = summarizer(parser.document, max_sentences)
    return " ".join(str(s) for s in summary_sents)


def split_sentences(text: str) -> List[str]:
    ensure_nltk()
    from nltk.tokenize import sent_tokenize
    return [s.strip() for s in sent_tokenize(text) if s.strip()]


def _make_cloze(sentence: str, keywords: List[str]) -> Tuple[str, str]:
    """
    Build a cloze-style Q/A: replace a top keyword with a blank in the question.
    Return (question, answer). If no keyword hit, turn sentence into Why/What question.
    """
    for kw in keywords:
        # choose a keyword that actually appears
        pattern = re.compile(r'\b' + re.escape(kw) + r'\b', flags=re.I)
        if pattern.search(sentence):
            q = pattern.sub("____", sentence)
            a = sentence
            return (q, a)
    # fallback: prefix with "What is the key idea?"
    return ("What is the key idea in: " + sentence, sentence)


def dedupe_qa(pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen = set()
    out = []
    for q, a in pairs:
        k = (q.lower(), a.lower())
        if k not in seen:
            seen.add(k)
            out.append((q, a))
    return out


def generate_flashcards(text: str, num_cards: int = 24) -> List[Tuple[str, str]]:
    """
    Generate up to num_cards (Q, A) pairs.
    Heuristic approach: RAKE keywords + sentence-level cloze deletion.
    """
    text = sanitize_text(text)
    if not text:
        return []
    keywords = extract_keywords(text, max_keywords=80)
    sents = split_sentences(text)
    # Favor informative, longer sentences but cap length
    sents = [s for s in sents if 40 <= len(s) <= 240]
    scored = []
    # Simple score: count keyword hits + sentence length weight
    kw_set = set([k.lower() for k in keywords])
    for s in sents:
        score = sum(1 for k in kw_set if re.search(r'\b' + re.escape(k) + r'\b', s, flags=re.I))
        score += min(len(s) / 80.0, 2.0)
        scored.append((score, s))
    scored.sort(reverse=True)
    top = [s for _, s in scored[: num_cards * 3]]  # oversample then dedupe

    pairs = []
    for s in top:
        q, a = _make_cloze(s, keywords)
        pairs.append((q, a))

    pairs = dedupe_qa(pairs)
    return pairs[:num_cards]


# ------------------ ADVANCED_AI (Optional) ------------------
# If you want to integrate an external LLM, replace the functions above
# or add a second path that calls your API and falls back to local.
#
# Example interface:
#
# def summarize_text_llm(text: str, system_prompt: str = "...") -> str:
#     # call your LLM here
#     return summarize_text(text)  # fallback
#
# def generate_flashcards_llm(text: str, count: int) -> List[Tuple[str, str]]:
#     # call your LLM then fallback
#     return generate_flashcards(text, count)
#
# Streamlit app uses the local versions by default for reliability.
