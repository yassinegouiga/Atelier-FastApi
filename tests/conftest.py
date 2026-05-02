# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.students_api import app
from app.database import get_db, Base

from sqlalchemy.pool import StaticPool

# Base de données en mémoire — isolée, détruite après chaque test
TEST_DATABASE_URL = 'sqlite:///:memory:'

@pytest.fixture(scope='function')  # recréée pour chaque fonction de test
def test_db():
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)  # crée les tables
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # nettoie tout

@pytest.fixture(scope='function')
def client(test_db):
    """TestClient FastAPI avec la DB de test injectée."""
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture
def sample_student():
    """Données d'un étudiant valide pour les tests."""
    return {
        'name': 'Test Étudiant',
        'email': 'test@um6p.ma',
        'major': 'Data Science',
        'gpa': 3.5
    }