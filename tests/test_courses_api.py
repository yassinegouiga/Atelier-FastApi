class TestCreateCourse:
    def test_create_valid_course(self, client):
        course = {
            'title': 'Algorithms',
            'code': 'CS101',
            'credits': 4,
            'instructor': 'Ada Lovelace',
        }

        r = client.post('/courses/', json=course)

        assert r.status_code == 201
        data = r.json()
        assert data['title'] == course['title']
        assert data['code'] == course['code']
        assert data['credits'] == course['credits']
        assert data['instructor'] == course['instructor']
        assert 'id' in data

    def test_create_duplicate_code_returns_409(self, client):
        course = {
            'title': 'Databases',
            'code': 'DB202',
            'credits': 3,
        }

        client.post('/courses/', json=course)
        r = client.post('/courses/', json=course)

        assert r.status_code == 409

    def test_create_invalid_credits_returns_422(self, client):
        course = {
            'title': 'Invalid Credits',
            'code': 'BAD101',
            'credits': 7,
        }

        r = client.post('/courses/', json=course)

        assert r.status_code == 422


class TestReadCourses:
    def test_list_empty_courses(self, client):
        r = client.get('/courses/')

        assert r.status_code == 200
        assert r.json() == []

    def test_get_existing_course(self, client):
        created = client.post('/courses/', json={
            'title': 'Machine Learning',
            'code': 'ML301',
            'credits': 5,
            'instructor': 'Alan Turing',
        }).json()

        r = client.get(f'/courses/{created["id"]}')

        assert r.status_code == 200
        assert r.json()['code'] == 'ML301'

    def test_get_nonexistent_course_returns_404(self, client):
        r = client.get('/courses/9999')

        assert r.status_code == 404


class TestUpdateCourse:
    def test_partial_update_course_credits(self, client):
        created = client.post('/courses/', json={
            'title': 'Networks',
            'code': 'NET101',
            'credits': 2,
        }).json()

        r = client.put(f'/courses/{created["id"]}', json={'credits': 4})

        assert r.status_code == 200
        assert r.json()['credits'] == 4
        assert r.json()['title'] == created['title']


class TestDeleteCourse:
    def test_delete_existing_course(self, client):
        created = client.post('/courses/', json={
            'title': 'Operating Systems',
            'code': 'OS201',
            'credits': 4,
        }).json()

        r = client.delete(f'/courses/{created["id"]}')

        assert r.status_code == 204
        assert client.get(f'/courses/{created["id"]}').status_code == 404
