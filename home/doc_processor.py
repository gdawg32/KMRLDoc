# doc_processor.py
import os
import re
import csv
import json
import datetime
from typing import Dict, Any, List, Tuple

import pandas as pd
import PyPDF2
import docx
import numpy as np
from joblib import load
import google.generativeai as genai


# -----------------------
# KEYWORD BOOSTING
# -----------------------
KEYWORD_BOOSTS = {
    "Financial": ["budget", "invoice", "revenue", "expenditure", "tax", "fund", "financial", "audit", "cost", "profit", "loss"],
    "Operational": ["maintenance", "schedule", "operation", "logistics", "shift", "inspection"],
    "Administrative": ["policy", "HR", "HR Policy", "approval", "circular", "order", "governance", "hiring", "payroll", "holiday", "leave", "employees", "HR"],
    "Regulatory": ["compliance", "regulation", "audit", "regulation", "legal", "licence", "permission", "certification", "dispute", "fine", "penalty", "court", "law", "Conﬁdential"],
    "Technical": ["engineering", "design", "specification", "system", "component", "technical", "drawing", "fixing", "installation", "repair", "maintenance"],
    "Executive": ["board", "chairman", "executive", "decision", "leadership", "minutes","board", "chairman", "executive", "decision", "leadership", "minutes" ],
}
BOOST_VALUE = 0.15 


# -----------------------
# FILE EXTRACTION
# -----------------------
def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
    """Extract text from PDF and return text + page count"""
    text = []
    pages = 0
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            pages = len(reader.pages)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception:
        pass
    return "\n".join(text), pages

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_csv(file_path: str) -> str:
    text = []
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                text.append(", ".join(row))
    except Exception:
        pass
    return "\n".join(text)

def extract_text_from_excel(file_path: str) -> str:
    text = []
    try:
        dfs = pd.read_excel(file_path, sheet_name=None)
        for sheet, df in dfs.items():
            text.append(f"--- Sheet: {sheet} ---")
            text.append(df.to_string(index=False))
    except Exception:
        pass
    return "\n\n".join(text)

def extract_text_from_json(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return ""

def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def extract_document(file_path: str) -> Dict[str, Any]:
    """Extract text and metadata from any supported file type."""
    ext = os.path.splitext(file_path)[1].lower()
    text_extractors = {
        ".pdf": extract_text_from_pdf,
        ".docx": extract_text_from_docx,
        ".csv": extract_text_from_csv,
        ".xls": extract_text_from_excel,
        ".xlsx": extract_text_from_excel,
        ".json": extract_text_from_json,
        ".txt": extract_text_from_txt,
    }

    if ext not in text_extractors:
        raise ValueError(f"Unsupported file type: {ext}")

    # Extract text and optional PDF page count
    if ext == ".pdf":
        text, pages = text_extractors[ext](file_path)
    else:
        text = text_extractors[ext](file_path)
        pages = None

    metadata = {
        "filename": os.path.basename(file_path),
        "extension": ext,
        "size_bytes": os.path.getsize(file_path),
        "extraction_timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "pages": pages,
    }

    return {"text": text.strip(), "metadata": metadata}

# -----------------------
# GEMINI TRANSLATION / SUMMARIZATION
# -----------------------
def setup_gemini(api_key: str, model_name="gemini-2.5-flash-lite"):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def translate_to_english(model, text: str) -> str:
    prompt = (
        "Translate the following text to English. "
        "Return only the translated text without any extra commentary:\n\n"
        f"{text}"
    )
    response = model.generate_content(prompt)
    return response.text.strip()

def summarise_text(model, text: str) -> str:
    prompt = (
        "Summarise the following document into 10 concise sentences. "
        "Include all key points (events, actions, financials, responsibilities, etc.). "
        "Avoid filler, repetition, or extra commentary.\n\n"
        f"{text}"
    )
    response = model.generate_content(prompt)
    return response.text.strip()

# -----------------------
# CLASSIFIER
# -----------------------
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def load_artifacts(artifacts_dir: str):
    vect = load(os.path.join(artifacts_dir, "tfidf_vectorizer.joblib"))
    clf = load(os.path.join(artifacts_dir, "ovr_logreg.joblib"))
    mlb = load(os.path.join(artifacts_dir, "label_binarizer.joblib"))

    thr_path = os.path.join(artifacts_dir, "thresholds.json")
    if os.path.exists(thr_path):
        with open(thr_path, "r", encoding="utf-8") as f:
            thresholds = json.load(f)
    else:
        thresholds = {label: 0.5 for label in mlb.classes_}

    labels = mlb.classes_.tolist()
    thr_arr = np.array([float(thresholds.get(l, 0.5)) for l in labels], dtype=float)
    return vect, clf, mlb, labels, thr_arr

def classify_text(text: str, vect, clf, labels, thr_arr, top_k_fallback=2):
    t = clean_text(text)
    probs_arr = clf.predict_proba(vect.transform([t]))[0]

    # --- Keyword boosting ---
    lower_text = t.lower()
    for i, label in enumerate(labels):
        if label in KEYWORD_BOOSTS:
            for kw in KEYWORD_BOOSTS[label]:
                if kw.lower() in lower_text:
                    probs_arr[i] = min(1.0, probs_arr[i] + BOOST_VALUE)
                    break  # only boost once per label

    # Apply thresholds
    chosen = [labels[i] for i in range(len(labels)) if probs_arr[i] >= thr_arr[i]]

    if not chosen:
        topk_idx = np.argsort(probs_arr)[::-1][:top_k_fallback]
        chosen = [labels[i] for i in topk_idx]

    probs_map = dict(zip(labels, probs_arr.tolist()))
    sorted_probs = sorted(probs_map.items(), key=lambda x: x[1], reverse=True)
    return chosen, sorted_probs

# -----------------------
# FULL PIPELINE FOR DJANGO
# -----------------------
def process_and_classify(
    file_path: str,
    artifacts_dir: str,
    gemini_api_key: str,
    translate: bool = False
) -> Dict[str, Any]:
    """
    Extracts, optionally translates, summarises, classifies, and returns all fields.
    Returns dictionary suitable for saving to Document model.
    """
    # Step 1: Extract
    doc_result = extract_document(file_path)
    raw_text = doc_result["text"]
    metadata = doc_result["metadata"]

    # Step 2: Setup Gemini
    model = setup_gemini(gemini_api_key)

    translated_text = None
    if translate:
        try:
            translated_text = translate_to_english(model, raw_text)
        except Exception:
            translated_text = raw_text  # fallback

    # Step 3: Summarise
    try:
        text_for_summary = translated_text if translated_text else raw_text
        summary = summarise_text(model, text_for_summary)
    except Exception:
        summary = text_for_summary

    # Step 4: Load artifacts + classify
    vect, clf, mlb, labels, thr_arr = load_artifacts(artifacts_dir)
    chosen_labels, sorted_probs = classify_text(summary, vect, clf, labels, thr_arr)

    # Prepare final dict for saving to Document model
    return {
        "extracted_text": raw_text,
        "translated_text": translated_text,
        "summary": summary,
        "predicted_labels": chosen_labels,
        "probabilities": sorted_probs,
        "metadata": metadata
    }
