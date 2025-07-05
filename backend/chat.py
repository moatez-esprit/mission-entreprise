# method 1: using pretrained model for CV ranking

# https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
# https://scikit-learn.org/stable/

import os
import argparse
import fitz 
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf_file(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def load_cv_text(file_path):
    if file_path.endswith('.txt'):
        return read_text_file(file_path)
    elif file_path.endswith('.pdf'):
        return read_pdf_file(file_path)
    else:
        return None
    

# chat.py (à ajouter en bas du fichier)
def match_from_content(job_description: str, cv_files: list):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    job_embedding = model.encode([job_description])
    scores = []

    for file in cv_files:
        filename = file.filename
        content = file.file.read()
        
        # Lire le contenu
        if filename.endswith('.txt'):
            text = content.decode('utf-8')
        elif filename.endswith('.pdf'):
            text = ""
            with fitz.open(stream=content, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        else:
            continue  # Skip unsupported files

        embedding = model.encode([text])
        score = cosine_similarity(job_embedding, embedding)[0][0]
        scores.append({"cv_name": filename, "similarity": round(score, 4)})

    # Tri par similarité décroissante
    return sorted(scores, key=lambda x: x["similarity"], reverse=True)


def main(job_desc_path, cvs_dir):
    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load job description
    job_description = read_text_file(job_desc_path)
    job_embedding = model.encode([job_description])

    # Process CVs
    scores = []
    for filename in tqdm(os.listdir(cvs_dir), desc="Processing CVs"):
        filepath = os.path.join(cvs_dir, filename)
        cv_text = load_cv_text(filepath)
        
        if cv_text:
            cv_embedding = model.encode([cv_text])
            similarity = cosine_similarity(job_embedding, cv_embedding)[0][0]  # 0.5 - 0.9 --> percentage / 100   
            print(f"Processed {filename}: Similarity = {similarity:.4f}")
            scores.append((filename, similarity))
        else:
            print(f"Skipped unsupported file: {filename}")

    # Sort by similarity
    scores.sort(key=lambda x: x[1], reverse=True)

    # Output top 5
    print("\nTop 5 matching CVs:")
    for rank, (filename, score) in enumerate(scores[:5], 1):
        print(f"{rank}. {filename} — Similarity: {score:.4f}")

    return scores

# def main(job_desc_path, cvs_dir):
#     model = SentenceTransformer('all-MiniLM-L6-v2')

#     job_description = read_text_file(job_desc_path)
#     job_embedding = model.encode([job_description])

#     scores = []
#     for filename in tqdm(os.listdir(cvs_dir), desc="Processing CVs"):
#         filepath = os.path.join(cvs_dir, filename)
#         cv_text = load_cv_text(filepath)

#         if cv_text:
#             cv_embedding = model.encode([cv_text])
#             similarity = cosine_similarity(job_embedding, cv_embedding)[0][0]
#             scores.append((filename, similarity))
#         else:
#             print(f"Skipped unsupported file: {filename}")

#     scores.sort(key=lambda x: x[1], reverse=True)

#     # ✅ On retourne une liste de dicts pour l'API
#     return [{"filename": f, "score": round(s, 4)} for f, s in scores]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match CVs to a job description")
    parser.add_argument("--job", required=True, help="Path to job description .txt file")
    parser.add_argument("--cvs", required=True, help="Path to directory containing CVs (.txt or .pdf)")
    args = parser.parse_args()

    main(args.job, args.cvs)


# method 2: using OPENAI API for CV ranking

# import openai
# import os
# import PyPDF2
# import pandas as pd

# openai.api_key = os.getenv("OPENAI_API_KEY")  # or set directly

# def read_pdf(file_path):
#     text = ""
#     with open(file_path, 'rb') as f:
#         reader = PyPDF2.PdfReader(f)
#         for page in reader.pages:
#             text += page.extract_text()
#     return text

# def load_cvs(cv_folder):
#     texts = []
#     names = []
#     for file in os.listdir(cv_folder):
#         if file.endswith(".pdf"):
#             text = read_pdf(os.path.join(cv_folder, file))
#             texts.append(text)
#             names.append(file)
#         elif file.endswith(".csv"):
#             df = pd.read_csv(os.path.join(cv_folder, file))
#             for index, row in df.iterrows():
#                 text = " ".join(map(str, row.values))
#                 texts.append(text)
#                 names.append(f"{file} row {index}")
#     return names, texts

# def score_cv(job_description, cv_text):
#     prompt = f"""
# You are a helpful HR assistant. Your task is to evaluate how well a candidate CV matches a job description.
# Job Description:
# {job_description}

# Candidate CV:
# {cv_text}

# Please respond with a score from 0 (no match) to 10 (perfect match) and a short explanation.
# Respond in JSON format: {{ "score": X, "reason": "..." }}
# """
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         temperature=0.3,
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response['choices'][0]['message']['content']

# def rank_cvs_with_gpt(cv_folder, job_description_path):
#     with open(job_description_path, 'r') as f:
#         job_description = f.read()

#     names, cv_texts = load_cvs(cv_folder)
#     results = []

#     for name, cv_text in zip(names, cv_texts):
#         print(f"Scoring {name}...")
#         result = score_cv(job_description, cv_text[:3000])  # truncate for token limit
#         try:
#             score_json = eval(result)
#             results.append((name, score_json["score"], score_json["reason"]))
#         except:
#             print(f"Failed to parse GPT response for {name}: {result}")
#             continue

#     top_5 = sorted(results, key=lambda x: x[1], reverse=True)[:5]
#     return top_5

# # Usage:
# cv_folder = "./cvs"
# job_path = "./job.txt"
# top_matches = rank_cvs_with_gpt(cv_folder, job_path)

# for name, score, reason in top_matches:
#     print(f"\n{name}:\nScore: {score}\nReason: {reason}\n")
