from flask import Blueprint, jsonify, request
from src.models.note import Note, db
from src import llm

note_bp = Blueprint('note', __name__)

@note_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes, ordered by most recently updated"""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
        
        note = Note(title=data['title'], content=data['content'])
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    notes = Note.query.filter(
        (Note.title.contains(query)) | (Note.content.contains(query))
    ).order_by(Note.updated_at.desc()).all()
    
    return jsonify([note.to_dict() for note in notes])


@note_bp.route('/notes/translate', methods=['POST'])
def translate_note():
    """Translate note content. Accepts JSON with either `content` or `note_id`.

    Request JSON examples:
      { "content": "some english text" }
      { "note_id": 123 }
    """
    data = request.get_json(silent=True) or {}
    content = data.get('content')
    note_id = data.get('note_id')

    if not content and note_id:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'error': 'note not found'}), 404
        content = note.content

    if not content:
        return jsonify({'error': 'content or note_id required'}), 400

    try:
        translation = llm.translate_text(content, source_lang='English', target_lang='Chinese')
        return jsonify({'translation': translation}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'translation failed', 'detail': str(e)}), 500


@note_bp.route('/notes/complete', methods=['POST'])
def complete_note():
    """Auto-complete partial note content. Accepts JSON with either `content` or `note_id`.

    Returns { "completion": "..." }
    """
    data = request.get_json(silent=True) or {}
    content = data.get('content')
    note_id = data.get('note_id')

    if not content and note_id:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'error': 'note not found'}), 404
        content = note.content

    if not content:
        return jsonify({'error': 'content or note_id required'}), 400

    try:
        completion = llm.complete_text(content)
        return jsonify({'completion': completion}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'completion failed', 'detail': str(e)}), 500

