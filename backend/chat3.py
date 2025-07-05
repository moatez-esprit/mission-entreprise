import json
import fitz 
from fastapi import FastAPI, HTTPException,UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import sqlite3
from io import BytesIO
from pdfminer.high_level import extract_text
import os
from typing import List
from fastapi import Body
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager
# Ajoutez ce middleware CORS en haut de votre fichier
from fastapi.middleware.cors import CORSMiddleware


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {str(e)}")
        return None

def read_pdf_file(file_path):
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {str(e)}")
        return None

def load_cv_text(file_path):
    if file_path.endswith('.txt'):
        return read_text_file(file_path)
    elif file_path.endswith('.pdf'):
        return read_pdf_file(file_path)
    return None

def load_all_cvs_from_folder(folder_path):
    cvs = []
    if not os.path.exists(folder_path):
        logger.error(f"CV folder not found: {folder_path}")
        return cvs

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and (filename.lower().endswith('.pdf') or filename.lower().endswith('.txt')):
            cv_text = load_cv_text(file_path)
            if cv_text:
                cv_name = os.path.splitext(filename)[0].replace('_', ' ')
                cvs.append({"name": cv_name, "text": cv_text})
    return cvs

def print_initial_info(cvs, job_desc):
    logger.info(f"\nLoaded {len(cvs)} CVs:")
    for cv in cvs:
        logger.info(f"- {cv['name']}")
    logger.info("\nJob Description Preview:")
    logger.info(job_desc[:300] + "...\n")

# Gestion du cycle de vie
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère les événements de démarrage et d'arrêt"""
    # Initialisation
    demo_cvs = load_all_cvs_from_folder("./cvs")
    demo_job = read_text_file("./job.txt")
    print_initial_info(demo_cvs, demo_job)
    
    payload = {
    "job_description": demo_job,
    "cvs": demo_cvs
    }
    # print("Payload to send to the API:\n", payload)
    with open("payload11.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    yield  # L'application est en cours d'exécution
    
    # Nettoyage (si nécessaire)


# Initialisation de l'application FastAPI
app = FastAPI(lifespan=lifespan)

# Configuration plus sécurisée
origins = [
    "http://localhost:4200",  # Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

# Vos routes ensuite...
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Modèles Pydantic
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
    cv_count: int

# Chargement du modèle (une seule fois)
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.post("/match",response_model=MatchResult,description="""
    Compare des CVs avec une description de poste.
    Retourne les scores de similarité sémantique.
    """,response_description="Résultats du matching")
#@app.post("/match", response_model=MatchResult)
async def match_cvs(request: MatchRequest):
    if not request.cvs:
        raise HTTPException(status_code=400, detail="CV list cannot be empty.")

    try:
        job_embedding = model.encode([request.job_description])
        cv_texts = [cv.text for cv in request.cvs]
        cv_names = [cv.name for cv in request.cvs]
        cv_embeddings = model.encode(cv_texts)

        similarities = cosine_similarity(job_embedding, cv_embeddings)[0]
        best_idx = similarities.argmax()

        # Enregistrer job et cvs + récupérer leurs IDs
        job_id = get_or_create_job(request.job_description)
        cv_ids = [get_or_create_cv(name, text) for name, text in zip(cv_names, cv_texts)]

        # Enregistrer scores
        for cv_id, score in zip(cv_ids, similarities):
            save_score(job_id, cv_id, float(score))

        sorted_scores = sorted(
            [{"name": cv_names[i], "score": round(float(score), 4)}
             for i, score in enumerate(similarities)],
            key=lambda x: x["score"],
            reverse=True
        )

        return MatchResult(
            best_cv_name=cv_names[best_idx],
            best_similarity_score=round(float(similarities[best_idx]), 4),
            all_scores=sorted_scores,
            cv_count=len(request.cvs)
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

DATABASE_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Crée la table jobs avec les colonnes nécessaires
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')

    # Crée les autres tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            cv_id INTEGER NOT NULL,
            similarity_score REAL NOT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id),
            FOREIGN KEY(cv_id) REFERENCES cvs(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('candidat', 'rh'))
        )
    ''')

    # Vérifiez si la table existe maintenant
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        raise Exception("La table users n'a pas pu être créée")

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        cv_id INTEGER NOT NULL,
        UNIQUE(job_id, cv_id),  -- empêche qu'un CV postule deux fois à une même offre
        FOREIGN KEY(job_id) REFERENCES jobs(id),
        FOREIGN KEY(cv_id) REFERENCES cvs(id)
    )
''')
    conn.commit()
    conn.close()

# Initialise la base de données au démarrage
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère les événements de démarrage et d'arrêt"""
    init_db()  # ✅ Initialisation de la base

    demo_cvs = load_all_cvs_from_folder("./cvs")
    demo_job = read_text_file("./job.txt")
    print_initial_info(demo_cvs, demo_job)
    
    payload = {
        "job_description": demo_job,
        "cvs": demo_cvs
    }
    with open("payload11.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    yield

def save_cv_to_db(name: str, text: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cvs (name, text) VALUES (?, ?)", (name, text))
    conn.commit()
    conn.close()

@app.post("/save_cv")
async def save_cv(cv: CVInput):
    save_cv_to_db(cv.name, cv.text)
    return {"message": f"CV '{cv.name}' saved to database."}


def get_all_cvs_from_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, text FROM cvs")
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row[0], "text": row[1]} for row in rows]

@app.get("/cvs", response_model=List[CVInput])
async def get_cvs():
    return get_all_cvs_from_db()

def save_job_to_db(title: str, company: str, location: str, description: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)",
        (title, company, location, description)
    )
    conn.commit()
    conn.close()

class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str

@app.post("/save_job")
async def save_job(job: Job):
    save_job_to_db(job.title, job.company, job.location, job.description)
    return {"message": "Job saved successfully"}


def get_or_create_job(description: str) -> int:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM jobs WHERE description = ?", (description,))
    row = cursor.fetchone()
    if row:
        job_id = row[0]
    else:
        cursor.execute("INSERT INTO jobs (description) VALUES (?)", (description,))
        job_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return job_id

def get_or_create_cv(name: str, text: str) -> int:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cvs WHERE name = ? AND text = ?", (name, text))
    row = cursor.fetchone()
    if row:
        cv_id = row[0]
    else:
        cursor.execute("INSERT INTO cvs (name, text) VALUES (?, ?)", (name, text))
        cv_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return cv_id

def save_score(job_id: int, cv_id: int, similarity_score: float):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO score (job_id, cv_id, similarity_score) VALUES (?, ?, ?)",
        (job_id, cv_id, similarity_score)
    )
    conn.commit()
    conn.close()

def get_all_jobs_from_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, company, location, description FROM jobs")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": row[0], "title": row[1], "company": row[2], "location": row[3], "description": row[4]}
        for row in rows
    ]
class JobOutput(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str

@app.get("/jobs", response_model=List[JobOutput])
async def get_jobs():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, company, location, description FROM jobs")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "company": r[2], "location": r[3], "description": r[4]} for r in rows]

class CVModel(BaseModel):
    name: str
    text: str


@app.post("/api/cvs")
def upload_cv(cv: CVModel):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cvs (name, text) VALUES (?, ?)", (cv.name, cv.text))
    conn.commit()
    conn.close()
    return {"message": "CV enregistré"}


@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...), job_id: int = Form(...)):
    contents = await file.read()

    # Extraire le texte du CV
    try:
        text = extract_text(BytesIO(contents))
    except Exception:
        text = "Erreur d'extraction de texte"

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Vérifier si le CV existe déjà
    cursor.execute("SELECT id FROM cvs WHERE name = ? AND text = ?", (file.filename, text))
    cv_row = cursor.fetchone()

    if cv_row:
        cv_id = cv_row[0]
    else:
        cursor.execute("INSERT INTO cvs (name, text) VALUES (?, ?)", (file.filename, text))
        cv_id = cursor.lastrowid
        conn.commit()

    # Vérifier si l'application existe déjà
    cursor.execute("SELECT id FROM applications WHERE job_id = ? AND cv_id = ?", (job_id, cv_id))
    existing_application = cursor.fetchone()

    if existing_application:
        conn.close()
        return {"message": "already_exists"}

    # Ajouter l'application
    cursor.execute("INSERT INTO applications (job_id, cv_id) VALUES (?, ?)", (job_id, cv_id))
    conn.commit()
    conn.close()

    return {"message": "added"}

        #conn.commit()
        #conn.close()

    #return {"message": "CV enregistré avec extraction de texte"}

@app.get("/users")
def get_users():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return [{"id": u[0], "username": u[1], "role": u[2]} for u in users]


@app.get("/applications/{job_id}", response_model=List[CVInput])
def get_cvs_for_job(job_id: int):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cvs.name, cvs.text
        FROM applications
        JOIN cvs ON applications.cv_id = cvs.id
        WHERE applications.job_id = ?
    ''', (job_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "text": r[1]} for r in rows]

@app.get("/applications_by_cv")
def get_applications_by_cv():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cvs.name, jobs.title, jobs.company, jobs.location
        FROM applications
        JOIN cvs ON applications.cv_id = cvs.id
        JOIN jobs ON applications.job_id = jobs.id
    """)
    rows = cursor.fetchall()
    conn.close()

    applications_by_cv = {}
    for name, title, company, location in rows:
        if name not in applications_by_cv:
            applications_by_cv[name] = []
        applications_by_cv[name].append({
            "title": title,
            "company": company,
            "location": location
        })

    return applications_by_cv

class LoginRequestSimple(BaseModel):
    username: str
    role: str  # 'rh' ou 'candidat'

@app.post("/login")
def login(request: LoginRequestSimple):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, role FROM users WHERE username=? AND role=?",
        (request.username, request.role)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"username": user[0], "role": user[1]}
    else:
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou rôle incorrect")


@app.post("/send_match_result")
def send_match_result(request: dict):
    job_id = request.get("job_id")
    best_cv_name = request.get("best_cv_name")
    score = request.get("score")

    # Tu peux enregistrer cela dans une table `notifications` ou l'écrire dans un fichier temporaire
    with open(f"notifications/job_{job_id}.json", "w", encoding="utf-8") as f:
        json.dump({
            "best_cv_name": best_cv_name,
            "score": score
        }, f)

    return {"message": "Notification enregistrée"}

@app.get("/get_match_result/{job_id}")
def get_match_result(job_id: int):
    notif_path = f"notifications/job_{job_id}.json"
    if os.path.exists(notif_path):
        with open(notif_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@app.post("/save_test_date")
def save_test_date(request: dict):
    job_id = request.get("job_id")
    date = request.get("date")

    if not os.path.exists("test_dates"):
        os.makedirs("test_dates")

    with open(f"test_dates/job_{job_id}.json", "w", encoding="utf-8") as f:
        json.dump({"test_date": date}, f)

    return {"message": "Date enregistrée avec succès"}

@app.get("/get_test_date/{job_id}")
def get_test_date(job_id: int):
    file_path = f"test_dates/job_{job_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"test_date": None}


if __name__ == "__main__":
    uvicorn.run("chat3:app", host="0.0.0.0", port=8000, reload=True)