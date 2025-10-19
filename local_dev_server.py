"""
本地开发临时解决方案

由于网络环境限制，无法连接到Supabase和PyPI，这里提供一个纯SQLite的本地版本。
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from flask import Flask, send_from_directory, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Error: Flask not installed. Please install flask and flask-cors:")
    print("pip install flask flask-cors")
    sys.exit(1)

# 创建Flask应用
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'local-dev-secret-key'
CORS(app)

# SQLite数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'local_notes.db')

def init_db():
    """初始化SQLite数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(120) NOT NULL
        )
    ''')
    
    # 创建笔记表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS note (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使结果像字典一样可访问
    return conn

# API路由
@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM note ORDER BY updated_at DESC')
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get('title', 'Untitled')
    content = data.get('content', '')
    user_id = data.get('user_id', 1)  # 默认用户ID
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO note (title, content, user_id) VALUES (?, ?, ?)',
        (title, content, user_id)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': note_id, 'title': title, 'content': content, 'user_id': user_id})

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE note SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, content, note_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'id': note_id, 'title': title, 'content': content})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM note WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Note deleted successfully'})

@app.route('/api/notes/search', methods=['GET'])
def search_notes():
    query = request.args.get('q', '')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM note WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC',
        (f'%{query}%', f'%{query}%')
    )
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(notes)

# 简化版翻译功能（无需OpenAI）
@app.route('/api/notes/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    
    # 简单的模拟翻译（实际应用中需要真正的翻译服务）
    translated = f"[Translated] {text}"
    
    return jsonify({
        'original': text,
        'translated': translated,
        'message': 'Translation service unavailable in local mode'
    })

# 简化版补全功能
@app.route('/api/notes/complete', methods=['POST'])
def complete_text():
    data = request.get_json()
    text = data.get('text', '')
    
    # 简单的模拟补全
    completion = f"{text} [auto-completed content...]"
    
    return jsonify({
        'original': text,
        'completed': completion,
        'message': 'Completion service unavailable in local mode'
    })

# 静态文件服务
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
    print("Starting local development server...")
    print("Using SQLite database for local development")
    
    # 初始化数据库
    init_db()
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5001, debug=True)