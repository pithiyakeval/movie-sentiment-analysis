from flask import Flask, request, jsonify
import os
import sqlite3
from datetime import datetime
import json
import nltk
import psycopg2

# Set NLTK path for both Docker and local development
nltk_data_paths = [
    '/usr/local/nltk_data',  # Docker path
    './nltk_data',           # Local development
    os.path.expanduser('~/nltk_data'),  # User home directory
]

for path in nltk_data_paths:
    if os.path.exists(path):
        nltk.data.path.append(path)
        print(f"Added NLTK path: {path}")

print(f"Final NLTK paths: {nltk.data.path}")

# Import after setting NLTK path
from model import predict_sentiment

app = Flask(__name__)

# Database configuration
def get_db_config():
    """Determine database configuration based on environment"""
    if os.path.exists('/app') or os.getenv('DOCKER_ENV'):  # Docker environment
        return {
            'type': 'postgresql',
            'url': os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/moviesentiment"),
            'host': os.getenv("DB_HOST", "localhost"),
            'port': os.getenv("DB_PORT", "5432"),
            'name': os.getenv("DB_NAME", "moviesentiment"),
            'user': os.getenv("DB_USER", "postgres"),
            'password': os.getenv("DB_PASSWORD", "password")
        }
    else:  # Local development
        return {
            'type': 'sqlite',
            'path': os.path.join(os.path.dirname(__file__), 'reviews.db')
        }

DB_CONFIG = get_db_config()
DB_TYPE = DB_CONFIG['type']

def get_db_connection():
    """Get database connection with fallback handling"""
    try:
        if DB_TYPE == "sqlite":
            conn = sqlite3.connect(DB_CONFIG['path'])
            conn.row_factory = sqlite3.Row
            return conn
        else:
            # Try multiple connection methods for PostgreSQL
            connection_methods = [
                # Method 1: Direct connection with config
                lambda: psycopg2.connect(
                    host=DB_CONFIG['host'],
                    database=DB_CONFIG['name'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    port=DB_CONFIG['port'],
                    connect_timeout=5
                ),
                # Method 2: Connection URL
                lambda: psycopg2.connect(DB_CONFIG['url']),
                # Method 3: Localhost fallback
                lambda: psycopg2.connect(
                    host="localhost",
                    database="moviesentiment",
                    user="postgres",
                    password="password",
                    port="5432"
                )
            ]
            
            for method in connection_methods:
                try:
                    conn = method()
                    print(f"✅ Database connected using {method.__name__}")
                    return conn
                except Exception as e:
                    continue
            
            raise Exception("All database connection methods failed")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def init_db():
    """Initialize database with required tables"""
    try:
        conn = get_db_connection()
        if conn is None:
            print("⚠️  Database not available, running in no-db mode")
            return
            
        cur = conn.cursor()
        
        if DB_TYPE == "sqlite":
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    sentiment TEXT NOT NULL,
                    confidence_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

# Initialize database when app starts
init_db()

@app.route("/")
def home():
    return """
    <h1>Movie Sentiment Analysis API</h1>
    <p>Available endpoints:</p>
    <ul>
        <li><b>POST /predict</b> - Analyze sentiment of movie review</li>
        <li><b>GET /reviews</b> - Get all reviews</li>
        <li><b>GET /reviews/&lt;id&gt;</b> - Get specific review</li>
        <li><b>DELETE /reviews/&lt;id&gt;</b> - Delete a review</li>
        <li><b>GET /stats</b> - Get API statistics</li>
        <li><b>GET /health</b> - Health check</li>
        <li><b>POST /batch-predict</b> - Analyze multiple texts</li>
    </ul>
    <p>Use POSTMAN or curl to test the API endpoints.</p>
    """

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            if DB_TYPE == "sqlite":
                cur.execute("SELECT 1;")
            else:
                cur.execute("SELECT 1;")
            cur.close()
            conn.close()
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        # Check NLTK status
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
            nltk_status = "vader"
        except LookupError:
            nltk_status = "fallback"
        
        return jsonify({
            "status": "healthy",
            "database": db_status,
            "nltk": nltk_status,
            "environment": "local" if DB_TYPE == "sqlite" else "docker",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({
            "status": "healthy",  # API is still healthy even if DB has issues
            "database": "disconnected",
            "nltk": "fallback",
            "warning": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route("/predict", methods=['POST'])
def predict():
    """Analyze sentiment of movie review text and store in database"""
    data = request.get_json()
    text=data.get('review_text')
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided", "status": "error"}), 400

    text = data['text'].strip()
    
    if not text:
        return jsonify({"error": "Text cannot be empty", "status": "error"}), 400

    # Predict sentiment
    try:
        sentiment, confidence = predict_sentiment(text)
        
        # Try to store in database
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                
                if DB_TYPE == "sqlite":
                    cur.execute(
                        "INSERT INTO reviews (text, sentiment, confidence_score) VALUES (?, ?, ?);",
                        (text, sentiment, confidence)
                    )
                    review_id = cur.lastrowid
                    # Get the created_at timestamp
                    cur.execute("SELECT created_at FROM reviews WHERE id = ?;", (review_id,))
                    result = cur.fetchone()
                    created_at = result[0] if result else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    cur.execute(
                        "INSERT INTO reviews (text, sentiment, confidence_score) VALUES (%s, %s, %s) RETURNING id, created_at;",
                        (text, sentiment, confidence)
                    )
                    result = cur.fetchone()
                    review_id, created_at = result[0], result[1]
                    
                conn.commit()
                cur.close()
                conn.close()
                
                return jsonify({
                    "id": review_id,
                    "text": text,
                    "sentiment": sentiment,
                    "confidence_score": confidence,
                    "created_at": created_at,
                    "database": "stored",
                    "status": "success",
                    "description": f"This review is {sentiment} with {confidence:.2f} confidence"
                })
            except Exception as db_error:
                print(f"Database storage failed: {db_error}")
                # Continue without database storage
                conn.close()
        
        # If database is not available, return result without storage
        return jsonify({
            "text": text,
            "sentiment": sentiment,
            "confidence_score": confidence,
            "database": "not_available",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}", "status": "error"}), 500

@app.route("/batch-predict", methods=['POST'])
def batch_predict():
    """Analyze sentiment for multiple texts at once"""
    data = request.get_json()
    
    if not data or 'texts' not in data or not isinstance(data['texts'], list):
        return jsonify({"error": "No texts array provided", "status": "error"}), 400

    texts = [text.strip() for text in data['texts'] if text.strip()]
    
    if not texts:
        return jsonify({"error": "No valid texts provided", "status": "error"}), 400

    results = []
    for text in texts:
        try:
            sentiment, confidence = predict_sentiment(text)
            results.append({
                "text": text,
                "sentiment": sentiment,
                "confidence_score": confidence
            })
        except Exception as e:
            results.append({
                "text": text,
                "error": str(e),
                "status": "failed"
            })

    return jsonify({
        "results": results,
        "total_processed": len(results),
        "status": "success"
    })

@app.route("/reviews", methods=['GET'])
def get_reviews():
    """Get all reviews with pagination"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database not available", "status": "error"}), 503
            
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        cur = conn.cursor()
        
        # Get total count
        cur.execute("SELECT COUNT(*) FROM reviews;")
        total_count = cur.fetchone()[0]
        
        # Get paginated reviews
        if DB_TYPE == "sqlite":
            cur.execute("""
                SELECT id, text, sentiment, confidence_score, created_at 
                FROM reviews 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?;
            """, (limit, offset))
        else:
            cur.execute("""
                SELECT id, text, sentiment, confidence_score, created_at 
                FROM reviews 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s;
            """, (limit, offset))
        
        reviews = []
        for row in cur.fetchall():
            reviews.append({
                "id": row[0],
                "text": row[1],
                "sentiment": row[2],
                "confidence_score": float(row[3]) if row[3] else None,
                "created_at": row[4]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            "reviews": reviews,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            },
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}", "status": "error"}), 500

@app.route("/reviews/<int:review_id>", methods=['GET'])
def get_review(review_id):
    """Get a specific review by ID"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database not available", "status": "error"}), 503
            
        cur = conn.cursor()
        
        if DB_TYPE == "sqlite":
            cur.execute("""
                SELECT id, text, sentiment, confidence_score, created_at 
                FROM reviews 
                WHERE id = ?;
            """, (review_id,))
        else:
            cur.execute("""
                SELECT id, text, sentiment, confidence_score, created_at 
                FROM reviews 
                WHERE id = %s;
            """, (review_id,))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            return jsonify({"error": "Review not found", "status": "error"}), 404
        
        return jsonify({
            "id": row[0],
            "text": row[1],
            "sentiment": row[2],
            "confidence_score": float(row[3]) if row[3] else None,
            "created_at": row[4],
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}", "status": "error"}), 500

@app.route("/reviews/<int:review_id>", methods=['DELETE'])
def delete_review(review_id):
    """Delete a review by ID"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database not available", "status": "error"}), 503
            
        cur = conn.cursor()
        
        # Check if review exists
        if DB_TYPE == "sqlite":
            cur.execute("SELECT id FROM reviews WHERE id = ?;", (review_id,))
        else:
            cur.execute("SELECT id FROM reviews WHERE id = %s;", (review_id,))
            
        if not cur.fetchone():
            return jsonify({"error": "Review not found", "status": "error"}), 404
        
        if DB_TYPE == "sqlite":
            cur.execute("DELETE FROM reviews WHERE id = ?;", (review_id,))
        else:
            cur.execute("DELETE FROM reviews WHERE id = %s;", (review_id,))
            
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "message": f"Review {review_id} deleted successfully",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}", "status": "error"}), 500

@app.route("/stats", methods=['GET'])
def get_stats():
    """Get API and database statistics"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                "statistics": {
                    "total_reviews": 0,
                    "sentiment_distribution": {},
                    "latest_review_date": "No database connection",
                    "environment": "local" if DB_TYPE == "sqlite" else "docker",
                    "database_status": "disconnected"
                },
                "status": "success"
            })
            
        cur = conn.cursor()
        
        # Get total reviews count
        cur.execute("SELECT COUNT(*) FROM reviews;")
        total_reviews = cur.fetchone()[0]
        
        # Get sentiment distribution
        cur.execute("SELECT sentiment, COUNT(*) FROM reviews GROUP BY sentiment;")
        sentiment_stats = {row[0]: row[1] for row in cur.fetchall()}
        
        # Get latest review
        cur.execute("SELECT created_at FROM reviews ORDER BY created_at DESC LIMIT 1;")
        latest_review = cur.fetchone()
        latest_date = latest_review[0] if latest_review else "No reviews yet"
        
        cur.close()
        conn.close()
        
        return jsonify({
            "statistics": {
                "total_reviews": total_reviews,
                "sentiment_distribution": sentiment_stats,
                "latest_review_date": latest_date,
                "environment": "local" if DB_TYPE == "sqlite" else "docker",
                "database_status": "connected"
            },
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}", "status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  
