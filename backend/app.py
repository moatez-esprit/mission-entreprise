from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import fitz

from matcher import compute_similarity

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all or specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

@app.post("/match")
async def match_cvs(job_description: str = Form(...), cvs: list[UploadFile] = File(...)):
    try:
        print(f"Received job_description: {job_description}")
        print(f"Received {len(cvs)} CVs")

        model = SentenceTransformer('all-MiniLM-L6-v2')
        job_embedding = model.encode([job_description])

        results = []
        for idx, cv in enumerate(cvs):
            content = await cv.read()
            print(f"Processing file: {cv.filename}, size: {len(content)} bytes")

            if cv.filename.endswith('.pdf'):
                # Save file temporarily
                temp_path = f"temp_{cv.filename}"
                with open(temp_path, "wb") as f:
                    f.write(content)

                text = read_pdf_file(temp_path)
                os.remove(temp_path)
            elif cv.filename.endswith('.txt'):
                text = content.decode('utf-8')
            else:
                return {"error": f"Unsupported file type: {cv.filename}"}

            cv_embedding = model.encode([text])
            similarity = cosine_similarity(job_embedding, cv_embedding)[0][0]
            results.append({"cv_name": cv.filename, "similarity": round(similarity, 4)})

        return {"results": results}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

