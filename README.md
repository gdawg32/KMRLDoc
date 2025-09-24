# KMRL Document Intelligence System

A web-based platform for managing, classifying, summarizing, and analyzing documents for **Kochi Metro Rail Limited (KMRL)**. This system leverages **Django**, **Machine Learning**, and **AI-based summarization** to provide insights, filtering, and document management capabilities.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Features

- Upload and manage PDF, Word, and text documents.
- Automatic language detection and optional translation.
- Machine learning-based multi-label classification of documents.
- AI-powered document summarization using Google Generative AI.
- Search documents by title, content, or keywords.
- Filter documents by category or priority using interactive chips.
- Document modal view showing summary and key information.
- Download documents directly from the interface.
- Visual indicators for new, high-priority, and uncategorized documents.

---

## Tech Stack

- **Backend:** Django, Django REST Framework  
- **Frontend:** HTML, TailwindCSS, JavaScript  
- **Machine Learning / NLP:** scikit-learn, joblib, PyPDF2, python-docx, pandas, numpy  
- **AI Integration:** Google Generative AI for summarization  
- **Utilities:** pdfplumber, tqdm, requests, python-magic  

---

Live Demo: [KMRLDoc](https://kmrldoc.pythonanywhere.com/)
