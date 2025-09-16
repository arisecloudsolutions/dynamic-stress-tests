#!/usr/bin/env python3
"""
Mock API Server for Local Testing

This simple Flask server provides a realistic API for testing the framework
without relying on external services. Perfect for development and CI/CD.
"""

import json
import time
import random
from flask import Flask, jsonify, request, abort
from datetime import datetime

app = Flask(__name__)

# Mock data storage
users = {}
posts = {}
next_user_id = 1
next_post_id = 1

# Simulate some initial data
def init_mock_data():
    global next_user_id, next_post_id

    # Create some initial users
    for i in range(1, 6):
        users[i] = {
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        next_user_id = i + 1

    # Create some initial posts
    for i in range(1, 11):
        posts[i] = {
            "id": i,
            "title": f"Post {i}",
            "content": f"This is the content of post {i}",
            "author_id": random.randint(1, 5),
            "created_at": datetime.now().isoformat()
        }
        next_post_id = i + 1

# Helper functions
def simulate_delay():
    """Simulate realistic API response times."""
    delay = random.uniform(0.01, 0.1)  # 10-100ms
    time.sleep(delay)

def simulate_errors():
    """Occasionally simulate server errors for testing."""
    if random.random() < 0.05:  # 5% error rate
        abort(500, "Simulated server error")

def authenticate():
    """Simple authentication check."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return True  # Allow anonymous access for testing

    # Check for Bearer token
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token == 'demo-token-12345':
            return True

    # Check for API key
    api_key = request.headers.get('X-API-Key')
    if api_key == 'demo-api-key':
        return True

    return True  # Allow for demo purposes

# Routes
@app.route('/openapi.json')
def openapi_spec():
    """Serve OpenAPI specification."""
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Mock API for Load Testing",
            "version": "1.0.0",
            "description": "A mock API server for testing the Dynamic Stress Testing Framework"
        },
        "servers": [
            {"url": "http://localhost:5000", "description": "Local mock server"}
        ],
        "paths": {
            "/users": {
                "get": {
                    "tags": ["users"],
                    "summary": "List all users",
                    "responses": {
                        "200": {"description": "List of users"}
                    }
                },
                "post": {
                    "tags": ["users"],
                    "summary": "Create a new user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"}
                                    },
                                    "required": ["name", "email"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "User created"},
                        "400": {"description": "Invalid input"}
                    }
                }
            },
            "/users/{user_id}": {
                "get": {
                    "tags": ["users"],
                    "summary": "Get user by ID",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "User details"},
                        "404": {"description": "User not found"}
                    }
                },
                "put": {
                    "tags": ["users"],
                    "summary": "Update user",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "status": {"type": "string", "enum": ["active", "inactive"]}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "User updated"},
                        "404": {"description": "User not found"}
                    }
                },
                "delete": {
                    "tags": ["users", "admin"],
                    "summary": "Delete user",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "204": {"description": "User deleted"},
                        "404": {"description": "User not found"}
                    }
                }
            },
            "/posts": {
                "get": {
                    "tags": ["posts"],
                    "summary": "List all posts",
                    "parameters": [
                        {
                            "name": "author_id",
                            "in": "query",
                            "schema": {"type": "integer"},
                            "description": "Filter by author ID"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer", "minimum": 1, "maximum": 100},
                            "description": "Limit number of results"
                        }
                    ],
                    "responses": {
                        "200": {"description": "List of posts"}
                    }
                },
                "post": {
                    "tags": ["posts"],
                    "summary": "Create a new post",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "author_id": {"type": "integer"}
                                    },
                                    "required": ["title", "content", "author_id"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Post created"},
                        "400": {"description": "Invalid input"}
                    }
                }
            },
            "/posts/{post_id}": {
                "get": {
                    "tags": ["posts"],
                    "summary": "Get post by ID",
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Post details"},
                        "404": {"description": "Post not found"}
                    }
                },
                "delete": {
                    "tags": ["posts", "admin"],
                    "summary": "Delete post",
                    "parameters": [
                        {
                            "name": "post_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "204": {"description": "Post deleted"},
                        "404": {"description": "Post not found"}
                    }
                }
            },
            "/health": {
                "get": {
                    "tags": ["system"],
                    "summary": "Health check endpoint",
                    "responses": {
                        "200": {"description": "System is healthy"}
                    }
                }
            },
            "/slow": {
                "get": {
                    "tags": ["system"],
                    "summary": "Slow endpoint for testing",
                    "responses": {
                        "200": {"description": "Slow response"}
                    }
                }
            },
            "/error": {
                "get": {
                    "tags": ["system"],
                    "summary": "Error endpoint for testing",
                    "responses": {
                        "500": {"description": "Simulated error"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer"
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }
    return jsonify(spec)

# User endpoints
@app.route('/users', methods=['GET'])
def list_users():
    simulate_delay()
    simulate_errors()

    limit = request.args.get('limit', type=int, default=10)
    user_list = list(users.values())[:limit]

    return jsonify({
        "users": user_list,
        "total": len(users),
        "limit": limit
    })

@app.route('/users', methods=['POST'])
def create_user():
    global next_user_id
    simulate_delay()

    if not authenticate():
        abort(401, "Authentication required")

    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        abort(400, "Name and email are required")

    user = {
        "id": next_user_id,
        "name": data['name'],
        "email": data['email'],
        "status": "active",
        "created_at": datetime.now().isoformat()
    }

    users[next_user_id] = user
    next_user_id += 1

    return jsonify(user), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    simulate_delay()
    simulate_errors()

    if user_id not in users:
        abort(404, "User not found")

    return jsonify(users[user_id])

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    simulate_delay()

    if not authenticate():
        abort(401, "Authentication required")

    if user_id not in users:
        abort(404, "User not found")

    data = request.get_json()
    if not data:
        abort(400, "JSON body required")

    user = users[user_id].copy()
    user.update({k: v for k, v in data.items() if k in ['name', 'email', 'status']})
    user['updated_at'] = datetime.now().isoformat()

    users[user_id] = user
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    simulate_delay()

    if not authenticate():
        abort(401, "Authentication required")

    if user_id not in users:
        abort(404, "User not found")

    del users[user_id]
    return '', 204

# Post endpoints
@app.route('/posts', methods=['GET'])
def list_posts():
    simulate_delay()
    simulate_errors()

    author_id = request.args.get('author_id', type=int)
    limit = request.args.get('limit', type=int, default=10)

    post_list = list(posts.values())

    if author_id:
        post_list = [p for p in post_list if p['author_id'] == author_id]

    post_list = post_list[:limit]

    return jsonify({
        "posts": post_list,
        "total": len(post_list),
        "limit": limit
    })

@app.route('/posts', methods=['POST'])
def create_post():
    global next_post_id
    simulate_delay()

    if not authenticate():
        abort(401, "Authentication required")

    data = request.get_json()
    if not data or not all(k in data for k in ['title', 'content', 'author_id']):
        abort(400, "Title, content, and author_id are required")

    # Check if author exists
    if data['author_id'] not in users:
        abort(400, "Author not found")

    post = {
        "id": next_post_id,
        "title": data['title'],
        "content": data['content'],
        "author_id": data['author_id'],
        "created_at": datetime.now().isoformat()
    }

    posts[next_post_id] = post
    next_post_id += 1

    return jsonify(post), 201

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    simulate_delay()
    simulate_errors()

    if post_id not in posts:
        abort(404, "Post not found")

    return jsonify(posts[post_id])

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    simulate_delay()

    if not authenticate():
        abort(401, "Authentication required")

    if post_id not in posts:
        abort(404, "Post not found")

    del posts[post_id]
    return '', 204

# System endpoints
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users_count": len(users),
        "posts_count": len(posts)
    })

@app.route('/slow', methods=['GET'])
def slow_endpoint():
    # Simulate slow endpoint
    time.sleep(random.uniform(1, 3))
    return jsonify({"message": "This endpoint is intentionally slow"})

@app.route('/error', methods=['GET'])
def error_endpoint():
    # Always return error for testing
    abort(500, "This endpoint always returns an error")

# Root endpoint
@app.route('/')
def root():
    return jsonify({
        "message": "Mock API Server for Dynamic Stress Testing",
        "version": "1.0.0",
        "endpoints": {
            "openapi": "/openapi.json",
            "users": "/users",
            "posts": "/posts",
            "health": "/health"
        },
        "demo_auth": {
            "bearer_token": "demo-token-12345",
            "api_key": "demo-api-key (X-API-Key header)"
        }
    })

if __name__ == '__main__':
    print(" Starting Mock API Server...")
    print("📋 OpenAPI spec: http://localhost:5000/openapi.json")
    print("🔍 Health check: http://localhost:5000/health")
    print("📖 Demo auth tokens available at: http://localhost:5000/")
    print()

    init_mock_data()

    # Run with debug mode for development
    app.run(host='0.0.0.0', port=5000, debug=True)