# this ml feature
import os
import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pdf2image import convert_from_path
import pytesseract

# Set path to tesseract (IMPORTANT for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def extract_text_with_ocr(pdf_path):
    text = ""

    try:
        images = convert_from_path(pdf_path, poppler_path=r"C:/poppler/Library/bin")
        for img in images:
            text += pytesseract.image_to_string(img)

    except Exception as e:
        print("OCR failed:", e)

    return text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME_FOLDER = os.path.join(BASE_DIR, "Resume")

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

                # OCR fallback if no text found
                if not text.strip() or len(text.strip()) < 50:
                    print(f"OCR used for: {filename}")
                    text = extract_text_with_ocr(file_path)

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
if __name__ == "__main__":
    query = input("Enter job role: ")
    ranked = rank_resumes(query)

    for filename, score in ranked:
        print(f"{filename} -> {100*score:.0f}")