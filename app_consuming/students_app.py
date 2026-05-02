# app_consuming/students_app.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import os

app = FastAPI(title='Students Web App')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

API_BASE = os.getenv('API_BASE_URL', 'http://localhost:8000')


@app.get('/', response_class=HTMLResponse)
def index(request: Request, search: str = '', major: str = ''):
    params = {}
    if search:
        params['search'] = search
    if major:
        params['major'] = major

    try:
        resp = requests.get(f'{API_BASE}/students/', params=params, timeout=5)
        students = resp.json() if resp.status_code == 200 else []
        error = None
    except requests.exceptions.ConnectionError:
        students = []
        error = "Impossible de joindre l'API. Vérifiez que le service est démarré."

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'students': students,
            'search': search,
            'major': major,
            'error': error,
        }
    )


@app.post('/add', response_class=RedirectResponse)
def add_student(
    name: str = Form(...),
    email: str = Form(...),
    major: str = Form(''),
    gpa: float = Form(0.0),
):
    requests.post(f'{API_BASE}/students/', json={
        'name': name,
        'email': email,
        'major': major,
        'gpa': gpa
    }, timeout=5)

    return RedirectResponse(url='/', status_code=303)


@app.post('/delete/{student_id}', response_class=RedirectResponse)
def delete_student(student_id: int):
    requests.delete(f'{API_BASE}/students/{student_id}', timeout=5)
    return RedirectResponse(url='/', status_code=303)