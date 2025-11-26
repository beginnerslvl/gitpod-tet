from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

posts = [
    {"id": 1, "user_id": 1, "title": "First Post", "content": "Hello World"},
    {"id": 2, "user_id": 2, "title": "Second Post", "content": "Flask is great"}
]

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Flask API"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({"users": users}), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    new_id = max([u["id"] for u in users]) + 1 if users else 1
    new_user = {
        "id": new_id,
        "name": data["name"],
        "email": data["email"]
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    
    return jsonify(user), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": "User deleted"}), 200

@app.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    results = [u for u in users if query in u["name"].lower() or query in u["email"].lower()]
    return jsonify({"results": results, "count": len(results)}), 200

@app.route('/users/count', methods=['GET'])
def count_users():
    return jsonify({"count": len(users)}), 200

# Posts endpoints
@app.route('/posts', methods=['GET'])
def get_posts():
    user_id = request.args.get('user_id', type=int)
    if user_id:
        filtered_posts = [p for p in posts if p["user_id"] == user_id]
        return jsonify({"posts": filtered_posts}), 200
    return jsonify({"posts": posts}), 200

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if post:
        return jsonify(post), 200
    return jsonify({"error": "Post not found"}), 404

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "user_id, title, and content are required"}), 400
    
    user = next((u for u in users if u["id"] == data["user_id"]), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    new_id = max([p["id"] for p in posts]) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "user_id": data["user_id"],
        "title": data["title"],
        "content": data["content"]
    }
    posts.append(new_post)
    return jsonify(new_post), 201

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    data = request.get_json()
    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']
    
    return jsonify(post), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global posts
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    posts = [p for p in posts if p["id"] != post_id]
    return jsonify({"message": "Post deleted"}), 200

@app.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_posts = [p for p in posts if p["user_id"] == user_id]
    return jsonify({"user": user, "posts": user_posts, "count": len(user_posts)}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
