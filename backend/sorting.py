import os
import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RESUME_FOLDER="Resume"
def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])


def load_resumes():
    resumes = []
    filenames = []

    for file in os.listdir(RESUME_FOLDER):
        
        file_path = os.path.join(RESUME_FOLDER, file)

        if file.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        elif file.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)

        elif file.endswith(".docx"):
            text = extract_text_from_docx(file_path)

        else:
            continue

        if text.strip():  
            resumes.append(text)
            filenames.append(file)

    return resumes, filenames


def rank_resumes(query):
    
    resumes, filenames = load_resumes()
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