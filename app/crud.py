# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import (
    CourseCreate,
    CourseDB,
    CourseUpdate,
    EnrollmentCreate,
    EnrollmentDB,
    StudentDB,
    StudentCreate,
    StudentUpdate,
)
from typing import Optional, List

def create_student(db: Session, student: StudentCreate) -> StudentDB:
    """Insère un nouvel étudiant. Lève une IntegrityError si l'email existe déjà."""
    db_student = StudentDB(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)  # recharge les valeurs générées par la DB (id, created_at)
    return db_student

def get_student(db: Session, student_id: int) -> Optional[StudentDB]:
    """Retourne un étudiant par son ID, ou None s'il n'existe pas."""
    return db.query(StudentDB).filter(StudentDB.id == student_id).first()

def get_student_by_email(db: Session, email: str) -> Optional[StudentDB]:
    return db.query(StudentDB).filter(StudentDB.email == email).first()

def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    major: Optional[str] = None,
    search: Optional[str] = None
) -> List[StudentDB]:
    """Liste les étudiants avec pagination, filtre par spécialité et recherche textuelle."""
    query = db.query(StudentDB)
    if major:
        query = query.filter(StudentDB.major == major)
    if search:
        query = query.filter(
            or_(
                StudentDB.name.ilike(f'%{search}%'),
                StudentDB.email.ilike(f'%{search}%')
            )
        )
    return query.offset(skip).limit(limit).all()

def update_student(
    db: Session, student_id: int, data: StudentUpdate
) -> Optional[StudentDB]:
    """Met à jour uniquement les champs fournis (mise à jour partielle)."""
    student = get_student(db, student_id)
    if not student:
        return None
    
    update_data = data.model_dump(exclude_unset=True)  # ignore les champs non fournis
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int) -> bool:
    """Supprime un étudiant. Retourne True si supprimé, False s'il n'existait pas."""
    student = get_student(db, student_id)
    if not student:
        return False
    
    db.delete(student)
    db.commit()
    return True

def count_students(db: Session) -> int:
    return db.query(StudentDB).count()

def create_course(db: Session, course: CourseCreate) -> CourseDB:
    """Insere un nouveau cours. Le code doit etre unique."""
    db_course = CourseDB(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course(db: Session, course_id: int) -> Optional[CourseDB]:
    """Retourne un cours par son ID, ou None s'il n'existe pas."""
    return db.query(CourseDB).filter(CourseDB.id == course_id).first()

def get_course_by_code(db: Session, code: str) -> Optional[CourseDB]:
    return db.query(CourseDB).filter(CourseDB.code == code).first()

def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
) -> List[CourseDB]:
    """Liste les cours avec pagination et recherche textuelle."""
    query = db.query(CourseDB)
    if search:
        query = query.filter(
            or_(
                CourseDB.title.ilike(f'%{search}%'),
                CourseDB.code.ilike(f'%{search}%'),
                CourseDB.instructor.ilike(f'%{search}%')
            )
        )
    return query.offset(skip).limit(limit).all()

def update_course(
    db: Session, course_id: int, data: CourseUpdate
) -> Optional[CourseDB]:
    """Met a jour uniquement les champs fournis pour un cours."""
    course = get_course(db, course_id)
    if not course:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course

def delete_course(db: Session, course_id: int) -> bool:
    """Supprime un cours. Retourne True si supprime, False s'il n'existait pas."""
    course = get_course(db, course_id)
    if not course:
        return False

    db.delete(course)
    db.commit()
    return True

def create_enrollment(db: Session, enrollment: EnrollmentCreate) -> EnrollmentDB:
    """Inscrit un etudiant a un cours."""
    db_enrollment = EnrollmentDB(**enrollment.model_dump())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def get_enrollment(
    db: Session, student_id: int, course_id: int
) -> Optional[EnrollmentDB]:
    """Retourne une inscription, ou None si elle n'existe pas."""
    return (
        db.query(EnrollmentDB)
        .filter(
            EnrollmentDB.student_id == student_id,
            EnrollmentDB.course_id == course_id,
        )
        .first()
    )

def get_courses_for_student(db: Session, student_id: int) -> List[CourseDB]:
    """Liste les cours auxquels un etudiant est inscrit."""
    return (
        db.query(CourseDB)
        .join(EnrollmentDB, EnrollmentDB.course_id == CourseDB.id)
        .filter(EnrollmentDB.student_id == student_id)
        .all()
    )

def get_students_for_course(db: Session, course_id: int) -> List[StudentDB]:
    """Liste les etudiants inscrits a un cours."""
    return (
        db.query(StudentDB)
        .join(EnrollmentDB, EnrollmentDB.student_id == StudentDB.id)
        .filter(EnrollmentDB.course_id == course_id)
        .all()
    )

def delete_enrollment(db: Session, student_id: int, course_id: int) -> bool:
    """Desinscrit un etudiant d'un cours."""
    enrollment = get_enrollment(db, student_id, course_id)
    if not enrollment:
        return False

    db.delete(enrollment)
    db.commit()
    return True
