import fitz 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import requests
import json

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


# parameters:
# - the CV files will be uploaded to the API as a list of strings
# each string is a CV
# - the job description will be uploaded to the API as a string

# Command example:
# curl -X POST "http://127.0.0.1:8000/match" \
#   -H "Content-Type: application/json" \
#   -d '{
#         "job_description": String of the job description should be here,
#         "cvs": a list of CVs as strings should be here
#       }'
# Since in the Command expect a json object same as MatchRequest class

# --> and the response will be a list of CVs with their similarity scores as json Response
# and also the response should be a json object same as MatchResult class

ghaith_cv = load_cv_text("./cvs/Ghaith_BenHaj_CV.pdf")
nouha_cv = load_cv_text("./cvs/Nouha_Ben_Ouahada_CV.pdf")

ghaith_cv = {
    "name": "Ghaith BenHaj",
    "text": ghaith_cv
}
nouha_cv = {
    "name": "Nouha Ben Ouahada",
    "text": nouha_cv
}
job_description = read_text_file("./job.txt")

print("Ghaith CV:\n", ghaith_cv)
print("Nouha CV:\n", nouha_cv)
# print("Job Description:\n", job_description)

list_of_cvs = [ghaith_cv, nouha_cv]

curl_command = """
curl -X POST "http://127.0.0.1:8000/match" \
  -H "Content-Type: application/json" \
  -d '{
        "job_description": $job_description,
        "cvs": $list_of_cvs      
    }'
"""
# curl_command = curl_command.replace("$job_description", job_description).replace("$list_of_cvs", list_of_cvs)
# print("Curl command to test the API:\n", curl_command)

# Remarks:
# you will risk to have an error when you run the curl command
# because the job description and the CVs are not in the same format as the API expects
# so you need to make sure that the job description and the CVs are in the same format as the API expects
# maybe create a new file with the payload in json format then run the curl command with the json file

payload = {
    "job_description": job_description,
    "cvs": list_of_cvs
}
# print("Payload to send to the API:\n", payload)
with open("payload.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

# curl -X POST "http://127.0.0.1:8000/match" \
#   -H "Content-Type: application/json" \
#   -d @payload.json

model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI()

class CVInput(BaseModel):
    name: str
    text: str


class MatchRequest(BaseModel):
    job_description: str
    cvs: List[CVInput]


class MatchResult(BaseModel):
    best_cv_name: str
    best_similarity_score: float
    all_scores: List[dict]


@app.post("/match", response_model=MatchResult)
def match_cvs(request: MatchRequest):
    if not request.cvs:
        raise HTTPException(status_code=400, detail="CV list cannot be empty.")

    job_embedding = model.encode([request.job_description])
    cv_texts = [cv.text for cv in request.cvs]
    cv_names = [cv.name for cv in request.cvs]
    cv_embeddings = model.encode(cv_texts)

    similarities = cosine_similarity(job_embedding, cv_embeddings)[0]
    best_idx = int(similarities.argmax())

    return MatchResult(
        best_cv_name=cv_names[best_idx],
        best_similarity_score=round(float(similarities[best_idx]), 4),
        all_scores=[
            {"name": cv_names[i], "score": round(float(score), 4)}
            for i, score in enumerate(similarities)
        ]
    )

if __name__ == "__main__":
    uvicorn.run("chat2:app", host="0.0.0.0", port=8000, reload=True)


# #this part can be added when you want to run the curl command in the code

# url = "http://127.0.0.1:8000/match"
# payload = {
#     "job_description": job_description,
#     "cvs": list_of_cvs
# }
# print("Payload to send to the API:\n", payload)
# response = requests.post(url, json=payload)

# if response.status_code == 200:
#     print("Response:")
#     print(response.json())
# else:
#     print("Failed:", response.status_code, response.text)
