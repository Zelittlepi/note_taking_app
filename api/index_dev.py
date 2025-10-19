import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp
from src.models.note import Note

# Load environment variables
load_dotenv()

def create_app():
    # Flask app setup
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    CORS(app)

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(note_bp, url_prefix='/api')

    # Database configuration - 支持本地开发和生产环境
    IS_LOCAL_DEV = os.getenv('LOCAL_DEV', 'false').lower() == 'true'
    
    if IS_LOCAL_DEV:
        # 本地开发使用SQLite
        db_path = os.path.join(os.path.dirname(__file__), '..', 'local_notes.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        print("Using local SQLite database for development")
    else:
        # 生产环境使用Supabase/PostgreSQL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            # 如果没有DATABASE_URL，尝试使用SQLite作为fallback
            print("WARNING: DATABASE_URL not set, falling back to SQLite")
            db_path = os.path.join(os.path.dirname(__file__), '..', 'fallback_notes.db')
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        else:
            # 标准化PostgreSQL URL
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            if 'sslmode=' not in db_url:
                db_url += ('&' if '?' in db_url else '?') + 'sslmode=require'
            
            app.config['SQLALCHEMY_DATABASE_URI'] = db_url
            print(f"Using PostgreSQL database")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        # 在生产环境可能需要抛出异常，本地开发可以继续
        if not IS_LOCAL_DEV:
            raise

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

    return app

# Create the Flask app instance
app = create_app()

# This is the entry point for Vercel
def handler(request):
    return app(request.environ, lambda *args: None)

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)