import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def init_db():
    """Initialize database with seed data if empty."""
    # Check if users exist
    response = supabase.table('users').select('id').limit(1).execute()
    if not response.data:
        seed_users()
        seed_stories()
    print("Supabase database initialized.")

def seed_stories():
    stories = [
        {
            "id": "1", "author_id": "1", 
            "content": "Today I spent a wonderful afternoon teaching Wei Jie how to make traditional kueh lapis! 🎂 He was so patient learning each layer. In return, he showed me how to use video calls on my phone. Now I can see my grandchildren in London anytime! This is what GeneraLink is all about - sharing knowledge across generations. ❤️",
            "likes": 47, "badges": "Storyteller,Verified"
        },
        {
            "id": "3", "author_id": "2", 
            "content": "Just had the most amazing conversation with Mdm Lim about her experience during Singapore's independence! 🇸🇬 Her stories brought my history textbook to life. She also taught me traditional Chinese calligraphy - my first attempt at writing '友谊' (friendship). Thank you for sharing your wisdom, Mdm Lim! 🙏",
            "likes": 134, "badges": "History Buff,First Connection"
        }
    ]
    
    for s in stories:
        supabase.table('stories').upsert(s).execute()

def seed_users():
    mock_users = [
        {
            "id": "1", "email": "margaret@example.com", 
            "password": generate_password_hash("password"), 
            "phone": "11111111", "nric": "111A",
            "profile_data": {
                "name": "Margaret Chen", "ageGroup": "senior", "age": 68,
                "interests": ["Cooking & Recipes", "History & Heritage", "Life Stories"],
                "bio": "Retired teacher who loves sharing traditional Peranakan recipes and Singapore's history.",
                "canShare": "Traditional cooking methods, stories from 1960s Singapore",
                "wantToLearn": "How to use video calls", "verified": True
            }
        },
        {
            "id": "2", "email": "weijie@example.com", 
            "password": generate_password_hash("password"), 
            "phone": "22222222", "nric": "222A",
            "profile_data": {
                "name": "Wei Jie", "ageGroup": "youth", "age": 19,
                "interests": ["Technology", "Music & Arts", "Languages"],
                "bio": "University student studying computer science.",
                "canShare": "Tech support, social media basics", 
                "wantToLearn": "Life wisdom, traditional Chinese calligraphy", "verified": True
            }
        },
        {
            "id": "3", "email": "tan@example.com", 
            "password": generate_password_hash("password"), 
            "phone": "33333333", "nric": "333A",
            "profile_data": {
                "name": "Uncle Tan", "ageGroup": "senior", "age": 72,
                "interests": ["Gardening", "Sports & Fitness", "Travel"],
                "bio": "Former national athlete and gardening enthusiast.",
                "canShare": "Gardening tips, fitness routines", 
                "wantToLearn": "Smartphone apps for tracking fitness", "verified": True
            }
        }
    ]

    for u in mock_users:
        supabase.table('users').upsert(u).execute()

# Key-Value Store Functions (using kv_store table)

def get_value(key):
    response = supabase.table('kv_store').select('value').eq('key', key).execute()
    if response.data:
        return json.loads(response.data[0]['value'])
    return None

def set_value(key, value):
    json_val = json.dumps(value)
    supabase.table('kv_store').upsert({'key': key, 'value': json_val}).execute()

def delete_value(key):
    supabase.table('kv_store').delete().eq('key', key).execute()

# Message Functions

def get_messages(conversation_id):
    key = f"messages:{conversation_id}"
    msgs = get_value(key)
    return msgs if isinstance(msgs, list) else []

def save_message(conversation_id, message_data):
    messages = get_messages(conversation_id)
    new_message = {
        'id': f"msg-{int(datetime.now().timestamp() * 1000)}",
        'senderId': message_data.get('senderId'),
        'text': message_data.get('text'),
        'timestamp': datetime.now().isoformat()
    }
    messages.append(new_message)
    set_value(f"messages:{conversation_id}", messages)
    return new_message

def save_report(conversation_id, report_data):
    key = f"reports:{conversation_id}"
    reports = get_value(key)
    if not isinstance(reports, list):
        reports = []
    
    new_report = {
        'id': f"report-{int(datetime.now().timestamp() * 1000)}",
        'reportedBy': report_data.get('userId'),
        'reason': report_data.get('reason'),
        'details': report_data.get('details', ""),
        'timestamp': datetime.now().isoformat(),
        'status': "pending"
    }
    reports.append(new_report)
    set_value(key, reports)
    
    # Store globally for admin
    all_reports_key = "admin:all-reports"
    all_reports = get_value(all_reports_key)
    if not isinstance(all_reports, list):
        all_reports = []
    
    report_summary = new_report.copy()
    report_summary['conversationId'] = conversation_id
    all_reports.append(report_summary)
    set_value(all_reports_key, all_reports)
    
    return new_report

# User/Auth Functions

def create_user(user_data):
    user_id = f"user-{int(datetime.now().timestamp())}"
    
    try:
        new_user = {
            'id': user_id,
            'email': user_data['email'],
            'password': generate_password_hash(user_data['password']),
            'phone': user_data['phone'],
            'nric': user_data['nric'],
            'profile_data': {
                'name': user_data.get('name', 'New User'),
                'badges': ['First Connection'],
                'verified': False
            }
        }
        supabase.table('users').insert(new_user).execute()
        return {'id': user_id, 'email': user_data['email']}
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user_by_email(email):
    response = supabase.table('users').select('*').eq('email', email).execute()
    if response.data:
        user = response.data[0]
        # Convert profile_data if it's a dict (Supabase returns jsonb as dict)
        if isinstance(user.get('profile_data'), dict):
            pass  # Already a dict, no conversion needed
        return user
    return None

def get_user_by_credentials(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def update_user_profile(user_id, profile_updates):
    # Get current data
    response = supabase.table('users').select('profile_data').eq('id', user_id).execute()
    if not response.data:
        return None
        
    current_profile = response.data[0]['profile_data']
    if isinstance(current_profile, str):
        current_profile = json.loads(current_profile)
    
    # Update fields
    current_profile.update(profile_updates)
    
    supabase.table('users').update({'profile_data': current_profile}).eq('id', user_id).execute()
    return current_profile

def get_user_by_id(user_id):
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    return response.data[0] if response.data else None

def get_potential_matches(user_id):
    # Get current user
    user = get_user_by_id(user_id)
    if not user:
        return []
    
    profile_data = user.get('profile_data', {})
    if isinstance(profile_data, str):
        profile_data = json.loads(profile_data)
    user_age_group = profile_data.get('ageGroup', '')

    # Get already matched user IDs
    matches_response = supabase.table('matches').select('match_id').eq('user_id', user_id).execute()
    matched_ids = [m['match_id'] for m in matches_response.data] if matches_response.data else []
    matched_ids.append(user_id)  # Exclude self

    # Get all other users
    response = supabase.table('users').select('*').execute()
    
    candidates = []
    for row in response.data:
        if row['id'] in matched_ids:
            continue
        
        p = row.get('profile_data', {})
        if isinstance(p, str):
            p = json.loads(p)
        
        # Filter by opposite age group
        if p.get('ageGroup') != user_age_group:
            p['id'] = row['id']
            candidates.append(p)
            
    return candidates

def save_match(user_id, match_id):
    ts = datetime.now().isoformat()
    supabase.table('matches').upsert({
        'user_id': user_id, 
        'match_id': match_id, 
        'timestamp': ts
    }).execute()

def get_user_matches(user_id):
    # Get matches where user initiated the match
    initiated_response = supabase.table('matches').select('match_id').eq('user_id', user_id).execute()
    
    # Get matches where user was matched by someone else (bidirectional)
    received_response = supabase.table('matches').select('user_id').eq('match_id', user_id).execute()
    
    # Combine both directions
    match_ids = set()
    if initiated_response.data:
        for m in initiated_response.data:
            match_ids.add(m['match_id'])
    if received_response.data:
        for m in received_response.data:
            match_ids.add(m['user_id'])
    
    if not match_ids:
        return []
    
    # Get user profiles for all matches
    matches = []
    for match_id in match_ids:
        user = get_user_by_id(match_id)
        if user:
            p = user.get('profile_data', {})
            if isinstance(p, str):
                p = json.loads(p)
            p['id'] = user['id']
            matches.append(p)
    
    return matches

def remove_match(user_id, match_id):
    supabase.table('matches').delete().eq('user_id', user_id).eq('match_id', match_id).execute()

# Story Functions

def get_all_stories():
    response = supabase.table('stories').select('*, users!stories_author_id_fkey(profile_data)').order('timestamp', desc=True).execute()
    
    result = []
    for row in response.data:
        s = dict(row)
        
        # Handle joined user data
        user_data = s.pop('users', None)
        if user_data:
            profile = user_data.get('profile_data', {})
            if isinstance(profile, str):
                profile = json.loads(profile)
            s['author_name'] = profile.get('name')
            s['author_age_group'] = profile.get('ageGroup')
            s['author_age'] = profile.get('age')
        
        # Handle badges (stored as comma-separated string)
        badges = s.get('badges', '')
        if isinstance(badges, str) and badges:
            s['badges'] = badges.split(',')
        else:
            s['badges'] = []
            
        result.append(s)
    
    return result

def create_story(author_id, content):
    story_id = f"story-{int(datetime.now().timestamp())}"
    timestamp = datetime.now().isoformat()
    
    new_story = {
        'id': story_id,
        'author_id': author_id,
        'content': content,
        'timestamp': timestamp,
        'likes': 0,
        'badges': ''
    }
    
    supabase.table('stories').insert(new_story).execute()
    return get_story_by_id(story_id)

def get_story_by_id(story_id):
    response = supabase.table('stories').select('*, users!stories_author_id_fkey(profile_data)').eq('id', story_id).execute()
    
    if not response.data:
        return None
    
    s = dict(response.data[0])
    
    user_data = s.pop('users', None)
    if user_data:
        profile = user_data.get('profile_data', {})
        if isinstance(profile, str):
            profile = json.loads(profile)
        s['author_name'] = profile.get('name')
        s['author_age_group'] = profile.get('ageGroup')
        s['author_age'] = profile.get('age')
    
    badges = s.get('badges', '')
    if isinstance(badges, str) and badges:
        s['badges'] = badges.split(',')
    else:
        s['badges'] = []
        
    return s

def like_story(story_id):
    # Get current likes
    response = supabase.table('stories').select('likes').eq('id', story_id).execute()
    if response.data:
        current_likes = response.data[0].get('likes', 0)
        supabase.table('stories').update({'likes': current_likes + 1}).eq('id', story_id).execute()

def get_all_users():
    response = supabase.table('users').select('*').execute()
    
    users = []
    for row in response.data:
        u = dict(row)
        p = u.get('profile_data', {})
        if isinstance(p, str):
            p = json.loads(p)
        u.update(p)
        del u['profile_data']
        del u['password']  # Don't send password
        users.append(u)
    
    return users
