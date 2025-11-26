import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_data():
    # Reset users and posts data before each test
    from app import users, posts
    users.clear()
    users.extend([
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ])
    posts.clear()
    posts.extend([
        {"id": 1, "user_id": 1, "title": "First Post", "content": "Hello World"},
        {"id": 2, "user_id": 2, "title": "Second Post", "content": "Flask is great"}
    ])

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Welcome to Flask API"

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "healthy"

def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert len(data['users']) == 2
    assert data['users'][0]['name'] == "Alice"

def test_get_user_by_id(client):
    response = client.get('/users/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['name'] == "Alice"
    assert data['email'] == "alice@example.com"

def test_get_user_not_found(client):
    response = client.get('/users/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == "User not found"

def test_create_user(client):
    new_user = {
        "name": "Charlie",
        "email": "charlie@example.com"
    }
    response = client.post('/users', 
                          data=json.dumps(new_user),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == "Charlie"
    assert data['email'] == "charlie@example.com"
    assert 'id' in data

def test_create_user_missing_fields(client):
    incomplete_user = {"name": "Charlie"}
    response = client.post('/users',
                          data=json.dumps(incomplete_user),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_update_user(client):
    updated_data = {
        "name": "Alice Updated",
        "email": "alice.updated@example.com"
    }
    response = client.put('/users/1',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == "Alice Updated"
    assert data['email'] == "alice.updated@example.com"

def test_update_user_partial(client):
    updated_data = {"name": "Alice Modified"}
    response = client.put('/users/1',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == "Alice Modified"
    assert data['email'] == "alice@example.com"

def test_update_user_not_found(client):
    updated_data = {"name": "Nobody"}
    response = client.put('/users/999',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 404

def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify user is deleted
    response = client.get('/users/1')
    assert response.status_code == 404

def test_delete_user_not_found(client):
    response = client.delete('/users/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_search_users(client):
    response = client.get('/users/search?q=alice')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'results' in data
    assert data['count'] == 1
    assert data['results'][0]['name'] == "Alice"

def test_search_users_no_query(client):
    response = client.get('/users/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_count_users(client):
    response = client.get('/users/count')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 2

# Posts tests
def test_get_posts(client):
    response = client.get('/posts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'posts' in data
    assert len(data['posts']) == 2

def test_get_posts_by_user(client):
    response = client.get('/posts?user_id=1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['posts']) == 1
    assert data['posts'][0]['user_id'] == 1

def test_get_post_by_id(client):
    response = client.get('/posts/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['title'] == "First Post"

def test_get_post_not_found(client):
    response = client.get('/posts/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_create_post(client):
    new_post = {
        "user_id": 1,
        "title": "New Post",
        "content": "This is a new post"
    }
    response = client.post('/posts',
                          data=json.dumps(new_post),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == "New Post"
    assert data['user_id'] == 1
    assert 'id' in data

def test_create_post_invalid_user(client):
    new_post = {
        "user_id": 999,
        "title": "New Post",
        "content": "This is a new post"
    }
    response = client.post('/posts',
                          data=json.dumps(new_post),
                          content_type='application/json')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_create_post_missing_fields(client):
    incomplete_post = {"title": "New Post"}
    response = client.post('/posts',
                          data=json.dumps(incomplete_post),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_update_post(client):
    updated_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = client.put('/posts/1',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == "Updated Title"
    assert data['content'] == "Updated content"

def test_update_post_not_found(client):
    updated_data = {"title": "Updated"}
    response = client.put('/posts/999',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 404

def test_delete_post(client):
    response = client.delete('/posts/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify post is deleted
    response = client.get('/posts/1')
    assert response.status_code == 404

def test_delete_post_not_found(client):
    response = client.delete('/posts/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_get_user_posts(client):
    response = client.get('/users/1/posts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert 'posts' in data
    assert data['count'] == 1
    assert data['user']['name'] == "Alice"

def test_get_user_posts_not_found(client):
    response = client.get('/users/999/posts')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
