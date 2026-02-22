import os
import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_FOLDER = os.path.join(BASE_DIR, "resume-uploads")

def extract_text_from_pdf(path):
    chunks = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                chunks.append(page_text)
    return "\n".join(chunks)

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text)

def load_resumes():
    resumes = []
    filenames = []

    if not os.path.exists(RESUME_FOLDER):
        return resumes, filenames

    for filename in os.listdir(RESUME_FOLDER):
        file_path = os.path.join(RESUME_FOLDER, filename)

        try:
            if filename.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file_path)

            elif filename.lower().endswith(".docx"):
                text = extract_text_from_docx(file_path)

            else:
                continue
        except Exception:
            # Skip files that fail to parse
            continue

        if text and text.strip():
            resumes.append(text)
            filenames.append(filename)

    return resumes, filenames

def rank_resumes(query):
    resumes, filenames = load_resumes()

    if not resumes:
        return []

    documents = resumes + [query]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    query_vector = tfidf_matrix[-1]
    resume_vectors = tfidf_matrix[:-1]

    similarities = cosine_similarity(query_vector, resume_vectors)[0]

    results = list(zip(filenames, similarities))
    results.sort(key=lambda x: x[1], reverse=True)

    return results