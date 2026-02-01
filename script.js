// --- DATABASE SIMULATION (LocalStorage) ---
const DB_KEY = 'oxygenz_users';
const CURRENT_USER_KEY = 'oxygenz_current';

// Mock Data
const CHALLENGES = [
    {id: 1, title: "Open Windows", desc: "Ventilate for 10 mins", pts: 50, icon: "🪟"},
    {id: 2, title: "Add a Plant", desc: "Place a Snake Plant", pts: 100, icon: "🪴"},
    {id: 3, title: "Clean Dust", desc: "Wipe surfaces", pts: 75, icon: "🧹"},
];

const QUIZ_DATA = [
    {q: "What does PM2.5 damage?", options: ["Lungs", "Hair", "Nails"], ans: 0},
    {q: "Best plant for air?", options: ["Rose", "Snake Plant", "Grass"], ans: 1},
    {q: "Main indoor pollutant?", options: ["Oxygen", "Dust/VOCs", "Nitrogen"], ans: 1},
    {q: "When to ventilate?", options: ["Never", "Early Morning", "Noon"], ans: 1},
    {q: "Smog is mix of?", options: ["Smoke+Fog", "Dust+Rain", "Air+Fire"], ans: 0},
];

// --- APP STATE ---
let currentUser = null;
let userData = {};

// --- INIT ---
window.onload = () => {
    checkLogin();
};

function checkLogin() {
    const savedUser = localStorage.getItem(CURRENT_USER_KEY);
    if (savedUser) {
        currentUser = savedUser;
        loadUserData();
        showDashboard();
    } else {
        document.getElementById('auth-section').classList.remove('hidden');
        document.getElementById('dashboard-section').classList.add('hidden');
    }
}

function loadUserData() {
    const db = JSON.parse(localStorage.getItem(DB_KEY)) || {};
    userData = db[currentUser];
    updateUI();
}

function saveUserData() {
    const db = JSON.parse(localStorage.getItem(DB_KEY)) || {};
    db[currentUser] = userData;
    localStorage.setItem(DB_KEY, JSON.stringify(db));
    updateUI();
}

function updateUI() {
    document.getElementById('display-username').innerText = currentUser;
    document.getElementById('stat-points').innerText = userData.points;
    document.getElementById('stat-tokens').innerText = userData.tokens;
    document.getElementById('stat-cleaned').innerText = userData.cleaned;
    
    // Update AQI Logic
    let currentAqi = 150 - userData.cleaned;
    if(currentAqi < 50) currentAqi = 50;
    document.getElementById('aqi-val').innerText = currentAqi;
    
    // Render Challenges
    const container = document.getElementById('challenges-container');
    container.innerHTML = '';
    CHALLENGES.forEach(ch => {
        const isDone = userData.completedChallenges.includes(ch.id);
        const btn = isDone ? '<button disabled>✅ DONE</button>' : `<button class="primary-btn" onclick="completeChallenge(${ch.id}, ${ch.pts})">Complete</button>`;
        container.innerHTML += `
            <div class="rank-item">
                <div><h3>${ch.icon} ${ch.title}</h3><small>${ch.desc}</small></div>
                <div>${btn}</div>
            </div>`;
    });
}

// --- AUTH LOGIC ---
function switchTab(tab) {
    if(tab === 'login') {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('register-form').classList.add('hidden');
    } else {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('register-form').classList.remove('hidden');
    }
}

function handleRegister() {
    const user = document.getElementById('reg-user').value;
    const pass = document.getElementById('reg-pass').value;
    if(!user || !pass) return alert("Fill all fields!");
    
    const db = JSON.parse(localStorage.getItem(DB_KEY)) || {};
    if(db[user]) return alert("User exists!");
    
    db[user] = { pass: pass, points: 0, tokens: 3, cleaned: 0, completedChallenges: [] };
    localStorage.setItem(DB_KEY, JSON.stringify(db));
    alert("Registered! Please login.");
    switchTab('login');
}

function handleLogin() {
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    const db = JSON.parse(localStorage.getItem(DB_KEY)) || {};
    
    if(db[user] && db[user].pass === pass) {
        localStorage.setItem(CURRENT_USER_KEY, user);
        currentUser = user;
        loadUserData();
        showDashboard();
    } else {
        alert("Invalid credentials!");
    }
}

function logout() {
    localStorage.removeItem(CURRENT_USER_KEY);
    location.reload();
}

function showDashboard() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    showPage('overview');
}

// --- NAVIGATION ---
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(el => el.classList.add('hidden'));
    document.getElementById(`page-${pageId}`).classList.remove('hidden');
    
    if(pageId === 'game') {
        window.addEventListener('keydown', handleGameInput);
        if(gameBoard.every(row => row.every(val => val === 0))) initGame();
    } else {
        window.removeEventListener('keydown', handleGameInput);
    }

    if(pageId === 'leaderboard') renderLeaderboard();
}

// --- CHALLENGES ---
function completeChallenge(id, pts) {
    userData.completedChallenges.push(id);
    userData.points += pts;
    userData.tokens += 2;
    userData.cleaned += 20;
    saveUserData();
    showToast(`+${pts} Points!`);
}

// --- QUIZ LOGIC ---
function startQuiz() {
    document.getElementById('quiz-start-area').classList.add('hidden');
    document.getElementById('quiz-area').classList.remove('hidden');
    loadQuestion(0, 0);
}

function loadQuestion(idx, score) {
    if(idx >= QUIZ_DATA.length) {
        // Finish
        document.getElementById('quiz-area').classList.add('hidden');
        document.getElementById('quiz-result').classList.remove('hidden');
        document.getElementById('quiz-score').innerText = score;
        userData.points += score;
        userData.tokens += 2;
        saveUserData();
        return;
    }
    
    const q = QUIZ_DATA[idx];
    document.getElementById('quiz-question').innerText = q.q;
    const optsDiv = document.getElementById('quiz-options');
    optsDiv.innerHTML = '';
    
    q.options.forEach((opt, i) => {
        const btn = document.createElement('button');
        btn.innerText = opt;
        btn.onclick = () => {
            let pts = (i === q.ans) ? 10 : 0;
            if(pts > 0) showToast("Correct! +10");
            else showToast("Wrong!");
            loadQuestion(idx + 1, score + pts);
        };
        optsDiv.appendChild(btn);
    });
}

// --- GAME 2048 LOGIC (JS Version) ---
let gameBoard = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
let gameScore = 0;

function initGame() {
    gameBoard = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
    gameScore = 0;
    addNewTile(); addNewTile();
    renderBoard();
}

function renderBoard() {
    const boardDiv = document.getElementById('game-board');
    boardDiv.innerHTML = '';
    gameBoard.forEach(row => {
        row.forEach(val => {
            const tile = document.createElement('div');
            tile.className = `tile t-${val}`;
            tile.innerText = val > 0 ? getIcon(val) : '';
            boardDiv.appendChild(tile);
        });
    });
    document.getElementById('game-score').innerText = gameScore;
}

function getIcon(val) {
    const icons = {2:'🌫️', 4:'🚗', 8:'🏭', 16:'😶‍🌫️', 32:'⚡', 64:'🫁', 128:'🌱'};
    return icons[val] || val;
}

function addNewTile() {
    let empty = [];
    for(let r=0; r<4; r++) {
        for(let c=0; c<4; c++) {
            if(gameBoard[r][c] === 0) empty.push({r,c});
        }
    }
    if(empty.length > 0) {
        let spot = empty[Math.floor(Math.random() * empty.length)];
        gameBoard[spot.r][spot.c] = 2;
    }
}

function handleGameInput(e) {
    let moved = false;
    if(e.key === 'ArrowUp') moved = moveUp();
    if(e.key === 'ArrowDown') moved = moveDown();
    if(e.key === 'ArrowLeft') moved = moveLeft();
    if(e.key === 'ArrowRight') moved = moveRight();
    
    if(moved) {
        addNewTile();
        renderBoard();
        if(checkWin()) showToast("YOU CREATED A PLANT! 🌱");
    }
}

// Logic simplified for pitch: Swipe left logic applied to rotated arrays
function slide(row) {
    let arr = row.filter(val => val);
    for(let i=0; i<arr.length-1; i++){
        if(arr[i] === arr[i+1]) {
            arr[i] *= 2;
            gameScore += arr[i];
            arr[i+1] = 0;
        }
    }
    arr = arr.filter(val => val);
    while(arr.length < 4) arr.push(0);
    return arr;
}

function moveLeft() {
    let moved = false;
    for(let r=0; r<4; r++) {
        let oldRow = JSON.stringify(gameBoard[r]);
        gameBoard[r] = slide(gameBoard[r]);
        if(oldRow !== JSON.stringify(gameBoard[r])) moved = true;
    }
    return moved;
}
// Helper to rotate for Up/Down/Right reuse
function rotateGrid() {
    let newGrid = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
    for(let r=0; r<4; r++) {
        for(let c=0; c<4; c++) {
            newGrid[c][3-r] = gameBoard[r][c];
        }
    }
    gameBoard = newGrid;
}

function moveRight() { rotateGrid(); rotateGrid(); let m = moveLeft(); rotateGrid(); rotateGrid(); return m; }
function moveUp() { rotateGrid(); rotateGrid(); rotateGrid(); let m = moveLeft(); rotateGrid(); return m; }
function moveDown() { rotateGrid(); let m = moveLeft(); rotateGrid(); rotateGrid(); rotateGrid(); return m; }

function checkWin() {
    return gameBoard.some(row => row.some(val => val >= 128));
}

// --- LEADERBOARD ---
function renderLeaderboard() {
    const list = document.getElementById('leaderboard-list');
    list.innerHTML = '';
    const db = JSON.parse(localStorage.getItem(DB_KEY)) || {};
    let users = Object.keys(db).map(key => ({name: key, pts: db[key].points}));
    
    // Add Bots
    users.push({name: "EcoWarrior", pts: 1200});
    users.push({name: "GreenLeaf", pts: 1050});
    
    users.sort((a,b) => b.pts - a.pts);
    
    users.forEach((u, i) => {
        let cls = i < 3 ? `rank-${i+1}` : '';
        list.innerHTML += `
            <div class="rank-item ${cls}">
                <h3>#${i+1} ${u.name}</h3>
                <p>🏆 ${u.pts}</p>
            </div>`;
    });
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.classList.remove('hidden');
    setTimeout(() => t.classList.add('hidden'), 2000);
}