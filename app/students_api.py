# students_api.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models import (
    Base,
    CourseCreate,
    CourseResponse,
    CourseUpdate,
    EnrollmentCreate,
    EnrollmentResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from app.database import get_db, engine
from app import crud

# Crée les tables au démarrage si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Students CRUD API',
    description='API de gestion des étudiants — Master IA 2025/2026',
    version='1.0.0',
    contact={'name': 'Pr. Fahd KALLOUBI', 'email': 'fahd.kalloubi@um6p.ma'},
)

# ── Route de santé (health check) ────────────────────────────────────

@app.get('/', tags=['Health'])
def root():
    return {'status': 'ok', 'message': 'Students API opérationnelle. Accédez à /docs.'}

@app.get('/health', tags=['Health'])
def health(db: Session = Depends(get_db)):
    """Vérifie que l'API et la base de données sont accessibles."""
    count = crud.count_students(db)
    return {'status': 'ok', 'students_count': count}

# ── CREATE ───────────────────────────────────────────────────────────

@app.post('/students/', response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=['Students'])
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel étudiant.
    - Valide automatiquement email, gpa (0-4), nom non vide
    - Retourne 409 si l'email est déjà utilisé
    """
    if crud.get_student_by_email(db, student.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Un étudiant avec l\'email {student.email} existe déjà'
        )
    return crud.create_student(db, student)

# ── READ ALL ─────────────────────────────────────────────────────────

@app.get('/students/', response_model=List[StudentResponse], tags=['Students'])
def list_students(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(10, ge=1, le=100, description="Nb max d'éléments"),
    major: Optional[str] = Query(None, description='Filtrer par spécialité'),
    search: Optional[str] = Query(None, description='Recherche dans nom ou email'),
    db: Session = Depends(get_db)
):
    """Liste les étudiants avec pagination, filtre et recherche textuelle."""
    return crud.get_students(db, skip=skip, limit=limit, major=major, search=search)

@app.get('/students/{student_id}/courses', response_model=List[CourseResponse], tags=['Enrollments'])
def list_student_courses(student_id: int, db: Session = Depends(get_db)):
    """Liste les cours auxquels un etudiant est inscrit."""
    if not crud.get_student(db, student_id):
        raise HTTPException(status_code=404, detail='Etudiant introuvable')
    return crud.get_courses_for_student(db, student_id)

# ── READ ONE ─────────────────────────────────────────────────────────

@app.get('/students/{student_id}', response_model=StudentResponse, tags=['Students'])
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail='Étudiant introuvable')
    return student

# ── UPDATE ───────────────────────────────────────────────────────────

@app.put('/students/{student_id}', response_model=StudentResponse, tags=['Students'])
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db)
):
    """Mise à jour partielle : seuls les champs envoyés sont modifiés."""
    student = crud.update_student(db, student_id, data)
    if not student:
        raise HTTPException(status_code=404, detail='Étudiant introuvable')
    return student

# ── DELETE ───────────────────────────────────────────────────────────

@app.delete('/students/{student_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Students'])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Supprime un étudiant. Retourne 204 No Content si succès."""
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail='Étudiant introuvable')

# ── STATISTIQUES ─────────────────────────────────────────────────────

@app.get('/students/stats/summary', tags=['Stats'])
def stats(db: Session = Depends(get_db)):
    """Retourne des statistiques agrégées sur les étudiants."""
    students = crud.get_students(db, limit=10000)
    if not students:
        return {'count': 0, 'gpa_moyen': None, 'specialites': []}
    
    gpas = [s.gpa for s in students if s.gpa is not None]
    majors = list(set(s.major for s in students if s.major))
    
    return {
        'count': len(students),
        'gpa_moyen': round(sum(gpas) / len(gpas), 2) if gpas else None,
        'gpa_max': max(gpas) if gpas else None,
        'gpa_min': min(gpas) if gpas else None,
        'specialites': sorted(majors),
    }

# --- COURSES -------------------------------------------------------------

@app.post('/courses/', response_model=CourseResponse, status_code=status.HTTP_201_CREATED, tags=['Courses'])
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """
    Cree un nouveau cours.
    - Valide automatiquement credits (1-6)
    - Retourne 409 si le code est deja utilise
    """
    if crud.get_course_by_code(db, course.code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Un cours avec le code {course.code} existe deja'
        )
    return crud.create_course(db, course)

@app.get('/courses/', response_model=List[CourseResponse], tags=['Courses'])
def list_courses(
    skip: int = Query(0, ge=0, description="Nombre d'elements a sauter"),
    limit: int = Query(10, ge=1, le=100, description="Nb max d'elements"),
    search: Optional[str] = Query(None, description='Recherche dans titre, code ou enseignant'),
    db: Session = Depends(get_db)
):
    """Liste les cours avec pagination et recherche textuelle."""
    return crud.get_courses(db, skip=skip, limit=limit, search=search)

@app.get('/courses/{course_id}/students', response_model=List[StudentResponse], tags=['Enrollments'])
def list_course_students(course_id: int, db: Session = Depends(get_db)):
    """Liste les etudiants inscrits a un cours."""
    if not crud.get_course(db, course_id):
        raise HTTPException(status_code=404, detail='Cours introuvable')
    return crud.get_students_for_course(db, course_id)

@app.get('/courses/{course_id}', response_model=CourseResponse, tags=['Courses'])
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail='Cours introuvable')
    return course

@app.put('/courses/{course_id}', response_model=CourseResponse, tags=['Courses'])
def update_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db)
):
    """Mise a jour partielle : seuls les champs envoyes sont modifies."""
    if data.code:
        existing_course = crud.get_course_by_code(db, data.code)
        if existing_course and existing_course.id != course_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Un cours avec le code {data.code} existe deja'
            )

    course = crud.update_course(db, course_id, data)
    if not course:
        raise HTTPException(status_code=404, detail='Cours introuvable')
    return course

@app.delete('/courses/{course_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Courses'])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Supprime un cours. Retourne 204 No Content si succes."""
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail='Cours introuvable')

# --- ENROLLMENTS ---------------------------------------------------------

@app.post('/enrollments/', response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED, tags=['Enrollments'])
def create_enrollment(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    """Inscrit un etudiant a un cours."""
    if not crud.get_student(db, enrollment.student_id):
        raise HTTPException(status_code=404, detail='Etudiant introuvable')
    if not crud.get_course(db, enrollment.course_id):
        raise HTTPException(status_code=404, detail='Cours introuvable')
    if crud.get_enrollment(db, enrollment.student_id, enrollment.course_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Etudiant deja inscrit a ce cours'
        )
    return crud.create_enrollment(db, enrollment)

@app.delete('/enrollments/{student_id}/{course_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Enrollments'])
def delete_enrollment(student_id: int, course_id: int, db: Session = Depends(get_db)):
    """Desinscrit un etudiant d'un cours."""
    if not crud.get_student(db, student_id):
        raise HTTPException(status_code=404, detail='Etudiant introuvable')
    if not crud.get_course(db, course_id):
        raise HTTPException(status_code=404, detail='Cours introuvable')

    success = crud.delete_enrollment(db, student_id, course_id)
    if not success:
        raise HTTPException(status_code=404, detail='Inscription introuvable')
