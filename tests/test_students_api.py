# tests/test_students_api.py
import pytest

class TestHealthRoutes:
    def test_root_returns_ok(self, client):
        r = client.get('/')
        assert r.status_code == 200
        assert r.json()['status'] == 'ok'

    def test_health_returns_count(self, client):
        r = client.get('/health')
        assert r.status_code == 200
        assert 'students_count' in r.json()


class TestCreateStudent:
    def test_create_valid_student(self, client, sample_student):
        r = client.post('/students/', json=sample_student)
        assert r.status_code == 201
        data = r.json()
        assert data['email'] == sample_student['email']
        assert data['name'] == 'Test Étudiant'  # .title() appliqué
        assert 'id' in data

    def test_create_duplicate_email_returns_409(self, client, sample_student):
        client.post('/students/', json=sample_student)  # 1er insert
        r = client.post('/students/', json=sample_student)  # doublon
        assert r.status_code == 409

    def test_create_invalid_gpa_returns_422(self, client, sample_student):
        sample_student['gpa'] = 5.0  # hors de [0, 4]
        r = client.post('/students/', json=sample_student)
        assert r.status_code == 422

    def test_create_invalid_email_returns_422(self, client, sample_student):
        sample_student['email'] = 'pas_un_email'
        r = client.post('/students/', json=sample_student)
        assert r.status_code == 422


class TestReadStudents:
    def test_list_empty(self, client):
        r = client.get('/students/')
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_created_student(self, client, sample_student):
        client.post('/students/', json=sample_student)
        r = client.get('/students/')
        assert len(r.json()) == 1

    def test_filter_by_major(self, client, sample_student):
        client.post('/students/', json=sample_student)
        r = client.get('/students/?major=Data Science')
        assert len(r.json()) == 1

        r2 = client.get('/students/?major=IA')
        assert len(r2.json()) == 0

    def test_get_existing_student(self, client, sample_student):
        created = client.post('/students/', json=sample_student).json()
        r = client.get(f'/students/{created["id"]}')
        assert r.status_code == 200

    def test_get_nonexistent_returns_404(self, client):
        r = client.get('/students/9999')
        assert r.status_code == 404


class TestUpdateStudent:
    def test_partial_update_gpa(self, client, sample_student):
        created = client.post('/students/', json=sample_student).json()
        r = client.put(f'/students/{created["id"]}', json={'gpa': 3.99})
        assert r.status_code == 200
        assert r.json()['gpa'] == 3.99
        assert r.json()['name'] == created['name']  # inchangé


class TestDeleteStudent:
    def test_delete_existing_student(self, client, sample_student):
        created = client.post('/students/', json=sample_student).json()
        r = client.delete(f'/students/{created["id"]}')
        assert r.status_code == 204

        # Vérifier qu'il n'existe plus
        r2 = client.get(f'/students/{created["id"]}')
        assert r2.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete('/students/9999')
        assert r.status_code == 404