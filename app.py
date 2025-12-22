import streamlit as st
import random
import time
import json
import os

# ==========================================
# 1. DATABASE & AUTH SYSTEM (INTI MEMORY)
# ==========================================
DB_FILE = "users.json"

# --- Fungsi Database ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def register_user(username, password):
    users = load_db()
    if username in users:
        return False, "Username already exists!"
    
    # Data awal user baru
    users[username] = {
        "password": password,
        "points": 0,
        "tokens": 3,
        "level": 1,
        "aqi_cleaned": 0,
        "daily_quiz_done": False,
        "completed_challenges": []
    }
    save_db(users)
    return True, "Registration successful! Please login."

def login_user(username, password):
    users = load_db()
    if username not in users:
        return False, "User not found!"
    if users[username]["password"] != password:
        return False, "Wrong password!"
    return True, users[username]

def update_user_data(username, key, value):
    """Update satu data spesifik user dan simpan ke file"""
    users = load_db()
    if username in users:
        users[username][key] = value
        save_db(users)

def sync_session_to_db():
    """Simpan semua stats session state ke database"""
    if st.session_state.current_user:
        users = load_db()
        username = st.session_state.current_user
        users[username]["points"] = st.session_state.points
        users[username]["tokens"] = st.session_state.tokens
        users[username]["level"] = st.session_state.level
        users[username]["aqi_cleaned"] = st.session_state.total_pollution_cleaned
        users[username]["daily_quiz_done"] = st.session_state.daily_quiz_done
        users[username]["completed_challenges"] = st.session_state.completed_challenges
        save_db(users)

# ==========================================
# 2. CONFIG & THEME
# ==========================================
st.set_page_config(page_title="OxyGenZ: Mission Clean Air", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Fredoka:wght@500;700&display=swap');
    
    .stApp { 
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 50%, #ffd3b6 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Fredoka', cursive !important;
        color: #1b5e20 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main, p, span, label, .stMarkdown, li {
        color: #2d4a2b !important;
    }

    /* Auth Styling */
    .auth-container {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        max-width: 500px;
        margin: auto;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.6);
    }
    
    /* Navigation Buttons */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: white !important;
        color: #2e7d32 !important;
        border: 2px solid #66bb6a !important;
        font-weight: 600;
        margin-bottom: 5px;
        transition: all 0.2s;
    }
    
    div.stButton > button:hover {
        background: #66bb6a !important;
        color: white !important;
        transform: scale(1.02);
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
        padding: 25px;
        border-radius: 20px;
        border: 3px solid #66bb6a;
        text-align: center;
        box-shadow: 0 8px 20px rgba(46, 125, 50, 0.2);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 30px rgba(46, 125, 50, 0.3);
    }
    
    /* Profile Card */
    .profile-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        border: 4px solid #4CAF50;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }

    /* Room Display */
    .room-display {
        background: linear-gradient(145deg, #ffffff, #f0f9f4);
        padding: 50px;
        border-radius: 30px;
        border: 5px solid #4caf50;
        text-align: center;
        box-shadow: 0 15px 35px rgba(27, 94, 32, 0.3);
        margin-bottom: 30px;
    }
    
    /* Challenge Card */
    .challenge-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f8f4 100%);
        padding: 25px;
        border-radius: 20px;
        border: 3px solid #81c784;
        margin-bottom: 15px;
        box-shadow: 0 6px 15px rgba(46, 125, 50, 0.2);
    }

    /* Game Grid */
    .game-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        background: #8d7a66;
        padding: 12px;
        border-radius: 15px;
        width: 340px; 
        margin: 0 auto;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
    }
    .game-cell {
        width: 70px;
        height: 70px;
        background: rgba(238, 228, 218, 0.35);
        border-radius: 8px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 32px;
        font-weight: bold;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: transform 0.1s;
    }
    .game-msg-box {
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
        font-family: 'Fredoka', cursive;
        border: 3px solid rgba(0,0,0,0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Tags */
    .tag { padding: 5px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85em; display: inline-block; margin-bottom: 5px;}
    .tag-red { background-color: #FFEBEE; color: #D32F2F !important; border: 1px solid #D32F2F; }
    .tag-yellow { background-color: #FFFDE7; color: #FBC02D !important; border: 1px solid #FBC02D; }
    .tag-green { background-color: #E8F5E9; color: #2E7D32 !important; border: 1px solid #2E7D32; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. INITIALIZE STATE & AUTH CHECK
# ==========================================
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None

# States for App (akan di-load saat login)
if 'page' not in st.session_state: st.session_state.page = "Game Overview"
if 'aqi' not in st.session_state: st.session_state.aqi = 150
if 'points' not in st.session_state: st.session_state.points = 0
if 'tokens' not in st.session_state: st.session_state.tokens = 0
if 'level' not in st.session_state: st.session_state.level = 1
if 'total_pollution_cleaned' not in st.session_state: st.session_state.total_pollution_cleaned = 0
if 'daily_quiz_done' not in st.session_state: st.session_state.daily_quiz_done = False
if 'completed_challenges' not in st.session_state: st.session_state.completed_challenges = []

# Game Logic States (Transient)
if 'board' not in st.session_state: st.session_state.board = [[0]*4 for _ in range(4)]
if 'game_score' not in st.session_state: st.session_state.game_score = 0
if 'game_message' not in st.session_state: st.session_state.game_message = "Merge tiles to find the Plant (🌱)!"
if 'game_msg_color' not in st.session_state: st.session_state.game_msg_color = "#f9f6f2"
if 'game_won' not in st.session_state: st.session_state.game_won = False
if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'quiz_active' not in st.session_state: st.session_state.quiz_active = False
if 'current_question' not in st.session_state: st.session_state.current_question = 0
if 'quiz_score' not in st.session_state: st.session_state.quiz_score = 0

# ==========================================
# 4. AUTHENTICATION PAGES
# ==========================================
if not st.session_state.is_logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🌱 OxyGenZ</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Please Login or Register to save your progress.</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                login_user_input = st.text_input("Username", key="login_user")
                login_pass_input = st.text_input("Password", type="password", key="login_pass")
                submit_login = st.form_submit_button("Login")
                
                if submit_login:
                    success, data = login_user(login_user_input, login_pass_input)
                    if success:
                        st.session_state.is_logged_in = True
                        st.session_state.current_user = login_user_input
                        # LOAD DATA FROM DB TO SESSION
                        st.session_state.points = data["points"]
                        st.session_state.tokens = data["tokens"]
                        st.session_state.level = data["level"]
                        st.session_state.total_pollution_cleaned = data["aqi_cleaned"]
                        st.session_state.daily_quiz_done = data["daily_quiz_done"]
                        st.session_state.completed_challenges = data["completed_challenges"]
                        # Adjust AQI based on cleaned pollution (Simulation)
                        st.session_state.aqi = max(50, 150 - st.session_state.total_pollution_cleaned)
                        
                        st.success(f"Welcome back, {login_user_input}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(data)

        with tab2:
            with st.form("register_form"):
                reg_user_input = st.text_input("New Username", key="reg_user")
                reg_pass_input = st.text_input("New Password", type="password", key="reg_pass")
                submit_reg = st.form_submit_button("Register")
                
                if submit_reg:
                    if reg_user_input and reg_pass_input:
                        success, msg = register_user(reg_user_input, reg_pass_input)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill all fields.")
    
    st.stop() # STOP EXECUTION IF NOT LOGGED IN

# ==========================================
# 5. MAIN APP LOGIC (ONLY RUNS IF LOGGED IN)
# ==========================================

# --- QUIZ DATA ---
QUIZ_QUESTIONS = [
    {"question": "1. What does AQI stand for?", "options": ["Air Quality Index", "Air Quantity Indicator", "Air Quest Index"], "correct": 0},
    {"question": "2. Which gas do plants absorb?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide"], "correct": 2},
    {"question": "3. What is PM2.5?", "options": ["A plant species", "Particulate Matter", "A purifier model"], "correct": 1},
    {"question": "4. Which plant is a natural purifier?", "options": ["Cactus", "Snake Plant", "Rose"], "correct": 1},
    {"question": "5. What causes indoor pollution?", "options": ["Fresh air", "VOCs from spray", "Clean surfaces"], "correct": 1},
]

# --- CHALLENGES DATA ---
CHALLENGES = [
    {"id": 1, "title": "Open Windows", "description": "Open windows for 10 minutes", "points": 50, "tokens": 3, "icon": "🪟"},
    {"id": 2, "title": "Add a Plant", "description": "Place a new plant in your room", "points": 100, "tokens": 3, "icon": "🪴"},
    {"id": 3, "title": "Clean Dust", "description": "Dust surfaces to reduce PM", "points": 75, "tokens": 2, "icon": "🧹"},
    {"id": 4, "title": "Run Air Purifier", "description": "Turn on purifier for 1 hour", "points": 80, "tokens": 2, "icon": "💨"},
]

# --- GAME LOGIC (2048) ---
TIERS = {
    0: {"color": "#cdc1b4", "text": "#cdc1b4", "name": "Empty"}, 
    2: {"icon": "🌫️", "color": "#eee4da", "text": "#776e65", "name": "Dust Mite", "msg": "Dust detected! It's starting to get dirty."}, 
    4: {"icon": "🚗", "color": "#ede0c8", "text": "#776e65", "name": "Fumes", "msg": "Cough! Traffic fumes are building up."}, 
    8: {"icon": "🏭", "color": "#f2b179", "text": "#f9f6f2", "name": "Smoke", "msg": "Warning! Factory smoke is polluting the city!"}, 
    16: {"icon": "😶‍🌫️", "color": "#f59563", "text": "#f9f6f2", "name": "Haze", "msg": "Visibility is low! The haze is getting thick."}, 
    32: {"icon": "⚡", "color": "#f67c5f", "text": "#f9f6f2", "name": "Ozone", "msg": "Danger! Ground level Ozone is rising."}, 
    64: {"icon": "🫁", "color": "#f65e3b", "text": "#f9f6f2", "name": "Danger", "msg": "CRITICAL! Air quality is hazardous to lungs!"}, 
    128: {"icon": "🌱", "color": "#edcf72", "text": "#f9f6f2", "name": "Seed", "msg": "HOPE! You planted a seed. Nature is fighting back!"}, 
}

def init_game():
    st.session_state.board = [[0]*4 for _ in range(4)]
    st.session_state.game_score = 0
    st.session_state.game_message = "Merge tiles to find the Plant (🌱)!"
    st.session_state.game_msg_color = "#ffffff"
    st.session_state.game_won = False
    add_tile(); add_tile()

def add_tile():
    empty = [(r, c) for r in range(4) for c in range(4) if st.session_state.board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        st.session_state.board[r][c] = 2

def merge(row):
    non_zero = [x for x in row if x != 0]
    new_row = []
    i = 0
    while i < len(non_zero):
        if i + 1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
            val = non_zero[i] * 2
            new_row.append(val)
            # LOGIC
            st.session_state.game_score += val
            st.session_state.points += (val // 2)
            
            if val in TIERS:
                st.session_state.game_message = TIERS[val]['msg']
                st.session_state.game_msg_color = "#ffccbc" if val >= 64 else "#ffffff"

            if val == 128 and not st.session_state.game_won:
                st.session_state.game_won = True
                st.session_state.game_message = "🎉 VICTORY! You created a Plant!"
                st.session_state.game_msg_color = "#c8e6c9"
                st.session_state.aqi = max(50, st.session_state.aqi - 30)
                st.session_state.total_pollution_cleaned += 30
            i += 2
        else:
            new_row.append(non_zero[i])
            i += 1
    # After merge, sync to DB immediately for persistence
    sync_session_to_db()
    return new_row + [0] * (4 - len(new_row))

def move_logic(direction):
    if st.session_state.game_won: return 
    board = st.session_state.board
    rotations = {'LEFT': 0, 'UP': 3, 'RIGHT': 2, 'DOWN': 1}
    for _ in range(rotations[direction]): board = [list(r) for r in zip(*board[::-1])]
    new_board = [merge(row) for row in board]
    for _ in range((4 - rotations[direction]) % 4): new_board = [list(r) for r in zip(*new_board[::-1])]
    if new_board != st.session_state.board:
        st.session_state.board = new_board
        add_tile()

# ==========================================
# 6. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown(f"## Hi, {st.session_state.current_user}!")
    st.markdown("Navigation Menu")
    
    if st.button("🏠 Game Overview"):
        st.session_state.page = "Game Overview"; st.rerun()
    if st.button("🎯 Missions"):
        st.session_state.page = "Missions & Challenges"; st.rerun()
    if st.button("🎮 Pollution Game"):
        st.session_state.page = "Pollution to Solution"; st.rerun()
    if st.button("🏆 Leaderboard"):
        st.session_state.page = "Leaderboard"; st.rerun()
    
    # NEW: PROFILE PAGE
    if st.button("👤 My Profile"):
        st.session_state.page = "Profile"; st.rerun()

    st.markdown("---")
    # NEW: LOGOUT BUTTON
    if st.button("🚪 Logout"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = None
        st.rerun()

# HEADER
st.markdown("# 🌱 OxyGenZ: Mission Clean Air")
st.markdown(f"### Level {st.session_state.level} • Educational Clean Air Game")

# ============================================
# PAGE 1: GAME OVERVIEW
# ============================================
if st.session_state.page == "Game Overview":
    st.markdown("## 🎮 Welcome to OxyGenZ!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''<div class="metric-card"><b>POINTS</b><h2>🏆 {st.session_state.points}</h2></div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="metric-card"><b>TOKENS</b><h2>🎫 {st.session_state.tokens}</h2></div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="metric-card"><b>CLEANED</b><h2>♻️ {st.session_state.total_pollution_cleaned}</h2></div>''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Room Status
    if st.session_state.aqi > 100:
        emoji, message, color = "🌫️", "UNHEALTHY! High pollution!", "#f44336"
    elif st.session_state.aqi > 50:
        emoji, message, color = "☁️", "MODERATE - Keep going!", "#ffb74d"
    else:
        emoji, message, color = "✨", "EXCELLENT! Air quality is great!", "#4caf50"
    
    st.markdown(f'''
        <div class="room-display">
            <h1 style="font-size:100px; margin:0;">{emoji}</h1>
            <h2 style="color:{color};">{message}</h2>
            <p><b>Current AQI: {st.session_state.aqi}</b></p>
        </div>
    ''', unsafe_allow_html=True)

# ============================================
# PAGE 2: MISSIONS
# ============================================
elif st.session_state.page == "Missions & Challenges":
    st.markdown("## 🎮 Missions & Challenges")
    tab1, tab2 = st.tabs(["📚 Daily Quiz", "🎯 Weekly Challenges"])
    
    with tab1:
        st.markdown("### 📝 Daily Knowledge Quiz")
        if st.session_state.quiz_active:
            st.markdown('<div class="challenge-card" style="border-color:#FBC02D;"><h4>📝 Daily Quiz #5</h4>', unsafe_allow_html=True)
            with st.form("quiz_form"):
                user_answers = {}
                for i, q in enumerate(QUIZ_QUESTIONS):
                    st.markdown(f"**{q['question']}**")
                    user_answers[i] = st.radio("Select answer:", q['options'], key=f"q{i}")
                    st.markdown("---")
                
                if st.form_submit_button("Submit Answers"):
                    score = 0
                    st.write("### 📊 Quiz Results:")
                    for i, q in enumerate(QUIZ_QUESTIONS):
                        if user_answers[i] == q['options'][q['correct']]:
                            st.success(f"Q{i+1}: Correct! ✅")
                            score += 10
                        else:
                            st.error(f"Q{i+1}: Wrong ❌")
                    
                    st.session_state.points += score
                    st.session_state.tokens += 2
                    st.session_state.quiz_active = False
                    st.session_state.daily_quiz_done = True
                    sync_session_to_db() # SAVE
                    st.balloons()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            # Dashboard View
            st.markdown('<span class="tag tag-yellow">To do</span>', unsafe_allow_html=True)
            if not st.session_state.daily_quiz_done:
                col_q1, col_q2 = st.columns([3, 1])
                with col_q1:
                    st.markdown("""<div class="challenge-card" style="border-color:#FBC02D;"><b>Daily Quiz #5</b><br><small>+50 Pts</small></div>""", unsafe_allow_html=True)
                with col_q2:
                    st.write(""); 
                    if st.button("▶ START QUIZ"): st.session_state.quiz_active = True; st.rerun()
            else:
                 st.info("You have completed today's quiz!")

            if st.session_state.daily_quiz_done:
                 st.markdown('<span class="tag tag-green">Done</span>', unsafe_allow_html=True)
                 st.markdown("""<div class="challenge-card" style="border-color:#66BB6A; background:#E8F5E9;"><b>Daily Quiz #5</b><br><small>Completed ✅</small></div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🎯 Weekly Action Challenges")
        for challenge in CHALLENGES:
            completed = challenge['id'] in st.session_state.completed_challenges
            col_ch1, col_ch2 = st.columns([4, 1])
            with col_ch1:
                status_badge = "✅ DONE" if completed else "⏳ ACTIVE"
                st.markdown(f'''
                    <div class="challenge-card">
                        <h3>{challenge['icon']} {challenge['title']} - {status_badge}</h3>
                        <p>{challenge['description']}</p>
                        <p><b>Reward:</b> 🏆 {challenge['points']} Pts | 🎫 +{challenge['tokens']} Tokens</p>
                    </div>
                ''', unsafe_allow_html=True)
            with col_ch2:
                if not completed:
                    if st.button("Complete", key=f"ch_{challenge['id']}"):
                        st.session_state.completed_challenges.append(challenge['id'])
                        st.session_state.points += challenge['points']
                        st.session_state.tokens += challenge['tokens']
                        st.session_state.aqi = max(50, st.session_state.aqi - 20)
                        st.session_state.total_pollution_cleaned += 20
                        sync_session_to_db() # SAVE
                        st.balloons()
                        st.rerun()

# ============================================
# PAGE 3: GAME
# ============================================
elif st.session_state.page == "Pollution to Solution":
    st.markdown("## 🎮 Pollution to Solution (2048)")
    st.markdown(f'<div class="token-display">🎫 Tokens: {st.session_state.tokens}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state.game_active:
        st.info("Cost to play: 1 Token")
        if st.button("🎲 START GAME"):
            if st.session_state.tokens > 0:
                st.session_state.tokens -= 1
                st.session_state.game_active = True
                init_game()
                sync_session_to_db() # SAVE TOKEN SPEND
                st.rerun()
            else:
                st.error("❌ Not enough tokens!")
    else:
        col_game1, col_game2 = st.columns([1.5, 1])
        with col_game1:
            st.markdown(f"""<div class="game-msg-box" style="background-color: {st.session_state.game_msg_color};">{st.session_state.game_message}</div>""", unsafe_allow_html=True)
            html = '<div class="game-grid">'
            for row in st.session_state.board:
                for cell in row:
                    t = TIERS.get(cell, TIERS[0])
                    icon = t.get('icon', '')
                    bg = t.get('color', '#cdc1b4')
                    html += f'<div class="game-cell" style="background:{bg};">{icon}</div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            
        with col_game2:
            st.markdown(f"### Score: {st.session_state.game_score}")
            if st.session_state.game_won:
                st.success("🏆 YOU WON!")
                if st.button("Play Again (-1 Token)"):
                    if st.session_state.tokens > 0:
                        st.session_state.tokens -= 1
                        init_game()
                        sync_session_to_db()
                        st.rerun()
            else:
                c1,c2,c3 = st.columns([1,1,1])
                with c2: 
                    if st.button("⬆️"): move_logic('UP'); st.rerun()
                c4,c5,c6 = st.columns([1,1,1])
                with c4: 
                    if st.button("⬅️"): move_logic('LEFT'); st.rerun()
                with c5: 
                    if st.button("⬇️"): move_logic('DOWN'); st.rerun()
                with c6: 
                    if st.button("➡️"): move_logic('RIGHT'); st.rerun()
                st.write(""); 
                if st.button("Exit Game"): st.session_state.game_active = False; st.rerun()

# ============================================
# PAGE 4: LEADERBOARD (REAL DATA)
# ============================================
elif st.session_state.page == "Leaderboard":
    st.markdown("## 🏆 Global Leaderboard")
    
    # 1. LOAD REAL USERS FROM DB
    all_users = load_db()
    
    leaderboard_data = []
    
    # Masukkan user asli
    for user, data in all_users.items():
        leaderboard_data.append({"name": user, "points": data["points"], "is_bot": False})
    
    # Masukkan bot biar rame (kalau user sedikit)
    bots = [
        {"name": "EcoWarrior", "points": 1200, "is_bot": True},
        {"name": "GreenLeaf", "points": 1050, "is_bot": True},
        {"name": "SkyWalker", "points": 800, "is_bot": True},
    ]
    leaderboard_data.extend(bots)
    
    # Sort Ranking
    leaderboard_data = sorted(leaderboard_data, key=lambda x: x['points'], reverse=True)
    
    st.markdown("### 🥇 Top Champions")
    for idx, player in enumerate(leaderboard_data):
        rank = idx + 1
        border_color = "#FFD700" if rank == 1 else "#81c784"
        bg_color = "#fff"
        
        # Highlight current logged in user
        if not player["is_bot"] and player["name"] == st.session_state.current_user:
            border_color = "#2e7d32" 
            bg_color = "#C8E6C9" # Green highlight
            player_name = f"{player['name']} (You)"
        else:
            player_name = player['name']

        st.markdown(f'''
            <div class="challenge-card" style="border-color: {border_color}; background: {bg_color};">
                <h2>#{rank} - {player_name}</h2>
                <p><b>Points:</b> 🏆 {player['points']}</p>
            </div>
        ''', unsafe_allow_html=True)

# ============================================
# PAGE 5: NEW PROFILE PAGE
# ============================================
elif st.session_state.page == "Profile":
    st.markdown("## 👤 User Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="profile-card">
            <div style="background:#ddd; width:100px; height:100px; border-radius:50%; margin:0 auto;"></div>
            <h2 style="margin-top:15px;">{st.session_state.current_user}</h2>
            <p>Level {st.session_state.level} Recycler</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 📊 Account Statistics")
        st.markdown(f"""
        <div class="challenge-card">
            <p>🏆 <b>Total Points:</b> {st.session_state.points}</p>
            <p>🎫 <b>Tokens Available:</b> {st.session_state.tokens}</p>
            <p>♻️ <b>Pollution Cleaned:</b> {st.session_state.total_pollution_cleaned} AQI</p>
            <p>✅ <b>Missions Completed:</b> {len(st.session_state.completed_challenges)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 Keep playing to increase your level and rank up on the leaderboard!")