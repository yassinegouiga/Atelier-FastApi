# models.py
from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, func
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.database import Base

# --- Modèle SQLAlchemy (ORM) --------------------------------------------
class StudentDB(Base):
    __tablename__ = 'students'

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, index=True, nullable=False)
    major      = Column(String(100), nullable=True)
    gpa        = Column(Float, default=0.0)
    phone      = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class CourseDB(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        CheckConstraint('credits >= 1 AND credits <= 6', name='check_course_credits_range'),
    )

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String(200), nullable=False)
    code       = Column(String(50), unique=True, index=True, nullable=False)
    credits    = Column(Integer, nullable=False)
    instructor = Column(String(100), nullable=True)

class EnrollmentDB(Base):
    __tablename__ = 'enrollments'

    student_id  = Column(Integer, ForeignKey('students.id'), primary_key=True)
    course_id   = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    enrolled_at = Column(DateTime, server_default=func.now(), nullable=False)

# --- Schémas Pydantic ---------------------------------------------------

# Schéma de base - champs communs
class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    major: Optional[str] = Field(None, max_length=100)
    gpa: float = Field(0.0, ge=0.0, le=4.0)
    phone: Optional[str] = Field(None, pattern=r'^\+212[0-9]{9}$')

    @field_validator('name')
    @classmethod
    def name_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError('Le nom ne peut pas être vide')
        return v.title()  # Capitalise chaque mot

# Schéma pour la création (POST) - hérite de StudentBase
class StudentCreate(StudentBase):
    pass

# Schéma pour la mise à jour (PUT) - tous les champs optionnels
class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    major: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    phone: Optional[str] = Field(None, pattern=r'^\+212[0-9]{9}$')

# Schéma pour la réponse (GET) - inclut id et created_at
class StudentResponse(StudentBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {'from_attributes': True}  # Pydantic v2

# --- Schemas Pydantic pour Course ---------------------------------------

class CourseBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=50)
    credits: int = Field(..., ge=1, le=6)
    instructor: Optional[str] = Field(None, max_length=100)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    credits: Optional[int] = Field(None, ge=1, le=6)
    instructor: Optional[str] = Field(None, max_length=100)

class CourseResponse(CourseBase):
    id: int

    model_config = {'from_attributes': True}

# --- Schemas Pydantic pour Enrollment -----------------------------------

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class EnrollmentResponse(EnrollmentCreate):
    enrolled_at: datetime

    model_config = {'from_attributes': True}
