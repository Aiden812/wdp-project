from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import db
import os
import json
import uuid

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'generalink-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize DB (seeds data to Supabase if needed)
db.init_db()

# --- Page Routes ---

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/signup')
def signup():
    return render_template('auth/signup.html')

@app.route('/otp')
def otp():
    return render_template('auth/otp.html')

@app.route('/reset-password')
def reset_password():
    return render_template('auth/reset.html')

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

@app.route('/matching')
def matching():
    return render_template('matching.html')

@app.route('/matches')
def matches_view():
    return render_template('matches.html')

@app.route('/chat')
def chat_list():
    return render_template('chat.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/stories')
def stories():
    return render_template('stories.html')

@app.route('/guidelines')
def guidelines():
    return render_template('guidelines.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


# --- API Endpoints ---

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/api/messages/<conversation_id>', methods=['GET'])
def get_messages(conversation_id):
    try:
        messages = db.get_messages(conversation_id)
        return jsonify({"success": True, "messages": messages})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/messages', methods=['POST'])
def send_message():
    try:
        data = request.json
        conversation_id = data.get('conversationId')
        message = data.get('message')
        
        if not conversation_id or not message:
            return jsonify({"success": False, "error": "Missing conversationId or message"}), 400
            
        new_msg = db.save_message(conversation_id, message)
        
        # Emit real-time event to the conversation room
        socketio.emit('new_message', {
            'conversationId': conversation_id,
            'message': new_msg
        }, room=conversation_id)
        
        return jsonify({"success": True, "message": new_msg})
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/report', methods=['POST'])
def submit_report():
    try:
        data = request.json
        conversation_id = data.get('conversationId')
        report = data.get('report')
        
        if not conversation_id or not report:
            return jsonify({"success": False, "error": "Missing conversationId or report data"}), 400
            
        new_report = db.save_report(conversation_id, report)
        return jsonify({"success": True, "report": new_report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user = db.get_user_by_credentials(email, password)
        if user:
            return jsonify({"success": True, "user": {"id": user['id'], "email": user['email']}})
        
        # Admin Demo
        if email == "admin@generalink.sg":
             return jsonify({"success": True, "user": {"id": "admin", "email": email, "isAdmin": True}})
             
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.json
        # Validate required fields
        if not data.get('email') or not data.get('password'):
             return jsonify({"success": False, "error": "Missing fields"}), 400
             
        user = db.create_user(data)
        if user:
            return jsonify({"success": True, "user": user})
        else:
            return jsonify({"success": False, "error": "User already exists"}), 409
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/profile', methods=['GET', 'POST'])
def profile_api():
    try:
        if request.method == 'GET':
            user_id = request.args.get('userId')
            if not user_id:
                return jsonify({"success": False, "error": "Missing userId"}), 400
            user = db.get_user_by_id(user_id)
            if user:
                profile_data = user.get('profile_data', {})
                if isinstance(profile_data, str):
                    import json
                    profile_data = json.loads(profile_data)
                return jsonify({"success": True, "profile": profile_data})
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # POST - update profile
        data = request.json
        user_id = data.get('userId')
        updates = data.get('updates')
        
        if not user_id or not updates:
             return jsonify({"success": False, "error": "Missing userId or updates"}), 400
             
        updated_profile = db.update_user_profile(user_id, updates)
        if updated_profile:
            return jsonify({"success": True, "profile": updated_profile})
        else:
            return jsonify({"success": False, "error": "User not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/profile/photo', methods=['POST'])
def upload_profile_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({"success": False, "error": "No photo file provided"}), 400
        
        file = request.files['photo']
        user_id = request.form.get('userId')
        
        if not user_id:
            return jsonify({"success": False, "error": "Missing userId"}), 400
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
            filename = secure_filename(filename)
            
            # Ensure upload folder exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Save file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Update user profile with photo URL
            photo_url = f"/static/uploads/{filename}"
            db.update_user_profile(user_id, {"photo": photo_url})
            
            return jsonify({"success": True, "photoUrl": photo_url})
        else:
            return jsonify({"success": False, "error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/matches/potential', methods=['GET'])
def get_potential_matches():
    try:
        user_id = request.args.get('userId')
        if not user_id: return jsonify({"success": False, "error": "Missing userId"}), 400
        
        profiles = db.get_potential_matches(user_id)
        return jsonify({"success": True, "profiles": profiles})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/matches', methods=['GET', 'POST', 'DELETE'])
def match_ops():
    try:
        if request.method == 'GET':
            user_id = request.args.get('userId')
            if not user_id: return jsonify({"success": False, "error": "Missing userId"}), 400
            matches = db.get_user_matches(user_id)
            return jsonify({"success": True, "matches": matches})
            
        elif request.method == 'POST':
            data = request.json
            user_id = data.get('userId')
            match_id = data.get('matchId')
            if not user_id or not match_id: return jsonify({"success": False, "error": "Missing IDs"}), 400
            db.save_match(user_id, match_id)
            return jsonify({"success": True})
            
        elif request.method == 'DELETE':
            user_id = request.args.get('userId')
            match_id = request.args.get('matchId')
            if not user_id or not match_id: return jsonify({"success": False, "error": "Missing IDs"}), 400
            db.remove_match(user_id, match_id)
            return jsonify({"success": True})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stories', methods=['GET', 'POST'])
def stories_api():
    try:
        if request.method == 'GET':
            stories = db.get_all_stories()
            return jsonify({"success": True, "stories": stories})
        elif request.method == 'POST':
            data = request.json
            author_id = data.get('authorId')
            content = data.get('content')
            if not author_id or not content:
                return jsonify({"success": False, "error": "Missing fields"}), 400
            story = db.create_story(author_id, content)
            return jsonify({"success": True, "story": story})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stories/<story_id>/like', methods=['POST'])
def like_story(story_id):
    try:
        db.like_story(story_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        # Simple security: check for admin (removed for demo simplicity or add query param? let's assume public for now as requested)
        # Or better, just return all users for the admin panel client-side filtering
        users = db.get_all_users()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- SocketIO Events ---

@socketio.on('join')
def on_join(data):
    """Join a conversation room for real-time updates"""
    room = data.get('conversationId')
    if room:
        join_room(room)
        print(f"User joined room: {room}")

@socketio.on('leave')
def on_leave(data):
    """Leave a conversation room"""
    room = data.get('conversationId')
    if room:
        leave_room(room)
        print(f"User left room: {room}")

@socketio.on('typing')
def on_typing(data):
    """Broadcast typing indicator"""
    room = data.get('conversationId')
    user_id = data.get('userId')
    if room:
        emit('user_typing', {'userId': user_id}, room=room, include_self=False)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
