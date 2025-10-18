import os
import sys
from dotenv import load_dotenv
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp
from src.models.note import Note

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Load .env if present (makes local testing easier)
load_dotenv()

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(note_bp, url_prefix='/api')

# Database configuration (MySQL only)
# Priority: DATABASE_URL or MYSQL_URL (full SQLAlchemy URL like mysql+pymysql://user:pass@host:port/db)
# Fallback: construct from DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME
db_url = os.getenv('DATABASE_URL') or os.getenv('MYSQL_URL')
if not db_url:
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    if db_user and db_pass and db_host and db_name:
        port_part = f":{db_port}" if db_port else ""
        # Use PyMySQL driver
        db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}{port_part}/{db_name}?charset=utf8mb4"
    else:
        # Fail fast: require MySQL configuration explicitly
        raise RuntimeError(
            "MySQL configuration not found. Set DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_NAME environment variables."
        )

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
print("Using SQLALCHEMY_DATABASE_URI:", db_url)
with app.app_context():
    db.create_all()

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
