from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, CV, JobDescription

DATABASE_URL = "sqlite:///./mydb.sqlite3"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Créer les tables (automatiquement si elles n'existent pas)
Base.metadata.create_all(bind=engine)

# Dépendance pour les routes
from fastapi import Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
