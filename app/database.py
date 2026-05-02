# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Lit l'URL depuis la variable d'environnement, SQLite par défaut
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./students.db')

# check_same_thread=False requis uniquement pour SQLite en mode multi-thread
connect_args = {'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=True)

# echo=True affiche les requêtes SQL dans la console (utile en dev)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Dépendance FastAPI - injecte et ferme automatiquement la session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()