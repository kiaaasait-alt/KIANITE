let currentUser = null;
let currentHit = null;
let scanRunning = false;
let scanResults = [];
let checkedCount = 0;
let foundCount = 0;
let scanInterval = null;
let mode = 'og';
let minYear = 2015;
let maxYear = 2017;

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initAuth();
    initScanner();
    initLookup();
    initHitlist();
    initMedia();
    initFx();
    checkLoggedIn();
});

window.switchTab = function(tab) {
    if ((tab === 'scanner' || tab === 'hitlist') && !currentUser) {
        openAuthModal('login');
        return;
    }
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => {
        if ((tab === 'scanner' && b.textContent.includes('Scanner')) ||
            (tab === 'hitlist' && b.textContent.includes('Hit')) ||
            (tab === 'lookup' && b.textContent.includes('Lookup')) ||
            (tab === 'credits' && b.textContent.includes('Credit'))) {
            b.classList.add('active');
        }
    });
    document.querySelectorAll('.tab-content').forEach(t => { t.classList.remove('active'); t.style.display = 'none'; });
    const el = document.getElementById(tab + 'Tab');
    if (el) {
        el.classList.add('active');
        el.style.display = 'block';
    }
    if (tab === 'hitlist' && typeof loadHitlist === 'function') {
        loadHitlist();
    }
}

function initTabs() {
    // tabs handled by onclick
}

function initAuth() {
    document.getElementById('loginBtn').addEventListener('click', () => openAuthModal('login'));
    document.getElementById('signupBtn').addEventListener('click', () => openAuthModal('signup'));
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    document.getElementById('authCloseBtn').addEventListener('click', closeAuthModal);
    document.getElementById('authSwitchBtn').addEventListener('click', switchAuthMode);
    document.getElementById('authSubmitBtn').addEventListener('click', submitAuth);
}

let authMode = 'login';
function openAuthModal(mode) {
    authMode = mode;
    document.getElementById('authModalTitle').textContent = mode === 'login' ? 'Login' : 'Sign Up';
    document.getElementById('authSubmitBtn').textContent = mode === 'login' ? 'Login' : 'Sign Up';
    document.getElementById('authSwitchText').textContent = mode === 'login' ? "Don't have an account?" : "Already have an account?";
    document.getElementById('authSwitchBtn').textContent = mode === 'login' ? 'Sign Up' : 'Login';
    document.getElementById('authModal').style.display = 'flex';
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
}

function switchAuthMode() {
    authMode = authMode === 'login' ? 'signup' : 'login';
    openAuthModal(authMode);
}

async function submitAuth() {
    const username = document.getElementById('authUsername').value.trim();
    const password = document.getElementById('authPassword').value.trim();
    
    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const res = await fetch('/api/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: authMode, username: username, password: password })
        });
        const data = await res.json();
        
        if (data.success) {
            currentUser = data.user;
            localStorage.setItem('kianite_user', JSON.stringify(currentUser));
            updateAuthUI();
            closeAuthModal();
            loadHitlist();
        } else {
            if (data.error && data.error.toLowerCase().includes('ban')) {
                showBanScreen(data.error);
                return;
            }
            alert(data.error || 'Error occurred');
        }
    } catch (e) {
        alert('Error occurred');
    }
}

function checkLoggedIn() {
    const saved = localStorage.getItem('kianite_user');
    if (saved) {
        currentUser = JSON.parse(saved);
        updateAuthUI();
    }
}

function showBanScreen(msg) {
    document.body.innerHTML = '<div style="background:#000;color:#ff3333;height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column;font-family:Consolas;"><div style="font-size:48px;letter-spacing:10px;">BANNED</div><div style="margin-top:20px;color:#666;">' + (msg||'Account banned') + '</div></div>';
}

function updateAuthUI() {
    if (currentUser) {
        document.getElementById('authSection').style.display = 'none';
        document.getElementById('userSection').style.display = 'flex';
        document.getElementById('usernameDisplay').textContent = currentUser.username;
        document.getElementById('hitlistEmpty').textContent = 'Loading...';
        updateStatus('ready');
        loadHitlist();
    } else {
        document.getElementById('authSection').style.display = 'flex';
        document.getElementById('userSection').style.display = 'none';
        document.getElementById('hitlistEmpty').textContent = 'Login to view your hit list';
        document.getElementById('hitlistTable').style.display = 'none';
        document.getElementById('hitlistBody').innerHTML = '';
        stopScan();
        updateStatus('Login required to use scanner');
        document.getElementById('startScanBtn').disabled = true;
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('kianite_user');
    updateAuthUI();
}

function initScanner() {
    document.getElementById('modeSelect').addEventListener('change', (e) => {
        if (!currentUser) { openAuthModal('login'); e.target.value = mode; return; }
        mode = e.target.value;
        updateStatus(`Mode set to ${mode.toUpperCase()}`);
    });
    
    document.querySelectorAll('.year-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!currentUser) { openAuthModal('login'); return; }
            document.querySelectorAll('.year-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            minYear = parseInt(btn.dataset.min);
            maxYear = parseInt(btn.dataset.max);
            updateStatus(`Year range set to ${minYear}-${maxYear}`);
        });
    });
    
    document.getElementById('startScanBtn').addEventListener('click', () => { if (!currentUser) { openAuthModal('login'); return; } startScan(); });
    document.getElementById('stopScanBtn').addEventListener('click', stopScan);
    document.getElementById('clearScanBtn').addEventListener('click', clearScan);
    document.getElementById('copyAllBtn').addEventListener('click', copyAll);
    
    document.getElementById('addToHitlistBtn').addEventListener('click', addToHitlist);
    document.getElementById('openProfileBtn').addEventListener('click', openProfile);
    document.getElementById('copyUsernameBtn').addEventListener('click', copyCurrentUsername);
    
    updateStats();
    document.getElementById('profileEmpty').hidden = false;
    document.getElementById('profileContent').hidden = true;
    updateStatus(currentUser ? 'ready' : 'Login required to use scanner');
}

function updateStatus(text, isError = false) {
    document.getElementById('statusText').textContent = text;
    const statusBar = document.getElementById('status');
    statusBar.className = isError ? 'status error' : 'status';
}

function updateStats() {
    document.getElementById('statusStats').textContent = `found ${foundCount} / checked ${checkedCount}`;
}

async function startScan() {
    if (!currentUser) { openAuthModal('login'); return; }
    if (scanRunning) return;
    scanRunning = true;
    document.getElementById('startScanBtn').disabled = true;
    document.getElementById('stopScanBtn').disabled = false;
    updateStatus(`scanning for ${getModeLabel(mode)} usernames...`);
    
    scanResults = [];
    foundCount = 0;
    checkedCount = 0;
    document.getElementById('resultsBody').innerHTML = '';
    document.getElementById('resultsEmpty').style.display = 'block';
    
    scanInterval = setInterval(performScanBatch, 600);
}

function getModeLabel(m) {
    const labels = { og: 'OG MIX', lastnames: 'LAST NAMES', swag: 'SWAG', killer: 'KILLER', short: 'SHORT', aesthetic: 'AESTHETIC' };
    return labels[m] || m.toUpperCase();
}

async function performScanBatch() {
    if (!scanRunning) return;
    
    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: mode,
                minYear: minYear,
                maxYear: maxYear,
                batches: 6
            })
        });
        
        if (!res.ok) throw new Error('Scan failed');
        const data = await res.json();
        
        checkedCount += data.checked || 0;
        
        if (data.found && data.found.length > 0) {
            data.found.forEach(hit => {
                if (!scanResults.find(r => r.id == hit.id)) {
                    scanResults.push(hit);
                    addResultToTable(hit);
                    foundCount++;
                }
            });
        }
        
        updateStats();
        
        if (data.limited) {
            updateStatus('rate limited by roblox - slowing down...', true);
            clearInterval(scanInterval);
            scanInterval = setInterval(performScanBatch, 1800);
        } else {
            updateStatus(`scanning for ${getModeLabel(mode)} usernames...`);
        }
    } catch (e) {
        updateStatus('roblox is busy - retrying...', true);
        clearInterval(scanInterval);
        scanInterval = setInterval(performScanBatch, 1400);
    }
}

function addResultToTable(hit) {
    document.getElementById('resultsEmpty').hidden = true;
    const tbody = document.getElementById('resultsBody');
    const row = document.createElement('tr');
    row.dataset.id = hit.id;
    
    const cells = [
        hit.username,
        hit.id,
        hit.created || '',
        hit.year || ''
    ];
    
    cells.forEach((value, index) => {
        const cell = document.createElement('td');
        cell.textContent = value;
        if (index === 0) cell.className = 'username-cell';
        row.appendChild(cell);
    });
    
    const addCell = document.createElement('td');
    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className = 'btn';
    addBtn.style.padding = '3px 6px';
    addBtn.style.fontSize = '10px';
    addBtn.textContent = 'ADD';
    addBtn.onclick = (e) => {
        e.stopPropagation();
        selectResult(hit.id);
        addToHitlist();
    };
    addCell.appendChild(addBtn);
    row.appendChild(addCell);
    
    row.addEventListener('click', () => {
        selectResult(hit.id);
    });
    
    tbody.appendChild(row);
}

function selectResult(id) {
    const hit = scanResults.find(r => r.id == id);
    if (!hit) return;
    currentHit = hit;
    
    document.querySelectorAll('#resultsBody tr').forEach(tr => tr.classList.remove('selected'));
    const rows = document.querySelectorAll('#resultsBody tr');
    rows.forEach(tr => {
        if (tr.dataset.id == id) tr.classList.add('selected');
    });
    
    document.getElementById('profileEmpty').hidden = true;
    document.getElementById('profileContent').hidden = false;
    
    document.getElementById('profileDisplayName').textContent = hit.displayName || hit.username;
    document.getElementById('profileUsername').textContent = '@' + hit.username;
    document.getElementById('profileId').textContent = hit.id;
    document.getElementById('profileCreated').textContent = hit.created || 'unknown';
    document.getElementById('profileAge').textContent = calculateAge(hit.created);
    document.getElementById('profileDesc').textContent = hit.description && hit.description.trim() ? hit.description : '(no description)';
    
    const flagsDiv = document.getElementById('profileFlags');
    flagsDiv.innerHTML = '';
    if (hit.hasVerifiedBadge) {
        const flag = document.createElement('span');
        flag.className = 'flag';
        flag.textContent = 'VERIFIED';
        flagsDiv.appendChild(flag);
    }
    if (hit.isBanned) {
        const flag = document.createElement('span');
        flag.className = 'flag banned';
        flag.textContent = 'BANNED';
        flagsDiv.appendChild(flag);
    }
    
    loadProfileAvatar(hit.id);
}

function calculateAge(created) {
    if (!created) return 'unknown';
    try {
        const date = new Date(created + 'T00:00:00Z');
        const now = new Date();
        let months = (now.getUTCFullYear() - date.getUTCFullYear()) * 12 + (now.getUTCMonth() - date.getUTCMonth());
        if (now.getUTCDate() < date.getUTCDate()) months -= 1;
        if (months < 0) return 'unknown';
        if (months >= 24) return Math.floor(months/12) + ' years';
        if (months >= 12) return '1 year';
        if (months === 0) return 'less than a month';
        if (months === 1) return '1 month';
        return months + ' months';
    } catch (e) {
        return 'unknown';
    }
}

async function loadProfileAvatar(id) {
    const img = document.getElementById('profileAvatar');
    const fallback = document.getElementById('profileAvatarFallback');
    img.hidden = true;
    fallback.hidden = false;
    fallback.textContent = '[ loading ]';
    
    try {
        const res = await fetch(`/api/avatar?id=${id}`);
        const data = await res.json();
        if (data.avatar) {
            img.src = data.avatar;
            img.hidden = false;
            fallback.hidden = true;
        } else {
            fallback.textContent = '[ no avatar ]';
        }
    } catch (e) {
        fallback.textContent = '[ no avatar ]';
    }
}

function stopScan() {
    scanRunning = false;
    if (scanInterval) {
        clearInterval(scanInterval);
        scanInterval = null;
    }
    document.getElementById('startScanBtn').disabled = false;
    document.getElementById('stopScanBtn').disabled = true;
    updateStatus('stopped');
}

function clearScan() {
    scanResults = [];
    foundCount = 0;
    checkedCount = 0;
    document.getElementById('resultsBody').innerHTML = '';
    document.getElementById('resultsEmpty').hidden = false;
    document.getElementById('profileEmpty').hidden = false;
    document.getElementById('profileContent').hidden = true;
    updateStats();
    updateStatus(scanRunning ? 'results cleared - scan still running...' : 'ready');
    currentHit = null;
}

async function copyAll() {
    if (scanResults.length === 0) {
        updateStatus('nothing to copy yet', true);
        return;
    }
    const usernames = scanResults.map(r => r.username).sort().join('\n');
    try {
        await navigator.clipboard.writeText(usernames);
        updateStatus(`copied ${scanResults.length} usernames`);
    } catch (e) {
        updateStatus('copy failed - clipboard blocked', true);
    }
}

async function addToHitlist() {
    if (!currentUser) {
        alert('Please login to add to hit list');
        return;
    }
    if (!currentHit) {
        alert('No hit selected');
        return;
    }
    
    try {
        const res = await fetch('/api/hits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'add', userId: currentUser.id, hit: currentHit })
        });
        const data = await res.json();
        if (data.success) {
            updateStatus('Added to hit list');
            loadHitlist();
        }
    } catch (e) {
        updateStatus('Failed to add', true);
    }
}

function openProfile() {
    if (!currentHit) return;
    window.open(`https://www.roblox.com/users/${currentHit.id}/profile`, '_blank');
}

async function copyCurrentUsername() {
    if (!currentHit) return;
    try {
        await navigator.clipboard.writeText(currentHit.username);
        updateStatus('Username copied');
    } catch (e) {
        updateStatus('Copy failed', true);
    }
}

async function removeUserHit(hitId, idx) {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/hits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'remove', userId: currentUser.id, hitId: hitId, index: idx })
        });
        await res.json();
        loadHitlist();
    } catch (e) {}
}

function initHitlist() {
    const refreshBtn = document.getElementById('refreshHitlistBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadHitlist);
    }
}

async function loadHitlist() {
    if (!currentUser) {
        document.getElementById('hitlistEmpty').textContent = 'Login to view your hit list';
        document.getElementById('hitlistEmpty').style.display = 'block';
        document.getElementById('hitlistTable').style.display = 'none';
        document.getElementById('hitlistBody').innerHTML = '';
        return;
    }
    
    document.getElementById('hitlistEmpty').textContent = 'Loading...';
    document.getElementById('hitlistEmpty').style.display = 'block';
    document.getElementById('hitlistTable').style.display = 'none';
    
    try {
        const res = await fetch('/api/hits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'get', userId: currentUser.id })
        });
        const data = await res.json();
        
        const tbody = document.getElementById('hitlistBody');
        tbody.innerHTML = '';
        
        if (data.hits && data.hits.length > 0) {
            document.getElementById('hitlistEmpty').style.display = 'none';
            document.getElementById('hitlistTable').style.display = 'table';
            data.hits.forEach((hit, idx) => {
                const row = document.createElement('tr');
                const cells = [
                    hit.username,
                    hit.id,
                    hit.created || '',
                    hit.year || '',
                    hit.addedAt ? new Date(hit.addedAt).toLocaleString() : ''
                ];
                cells.forEach((value, index) => {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    if (index === 0) cell.className = 'username-cell';
                    row.appendChild(cell);
                });
                const actionCell = document.createElement('td');
                const btn = document.createElement('button');
                btn.className = 'btn';
                btn.style.padding = '2px 6px';
                btn.textContent = 'REMOVE';
                btn.onclick = () => removeUserHit(hit.id, idx);
                actionCell.appendChild(btn);
                row.appendChild(actionCell);
                tbody.appendChild(row);
            });
        } else {
            document.getElementById('hitlistEmpty').textContent = 'No hits yet';
            document.getElementById('hitlistEmpty').style.display = 'block';
            document.getElementById('hitlistTable').style.display = 'none';
        }
    } catch (e) {
        document.getElementById('hitlistEmpty').textContent = 'Error loading hit list';
        document.getElementById('hitlistEmpty').style.display = 'block';
        document.getElementById('hitlistTable').style.display = 'none';
    }
}

function initLookup() {
    document.getElementById('lookupBtn').addEventListener('click', performLookup);
    document.getElementById('lookupInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performLookup();
    });
}

async function performLookup() {
    const query = document.getElementById('lookupInput').value.trim();
    if (!query) {
        alert('Please enter a username or user ID');
        return;
    }
    
    document.getElementById('lookupBtn').disabled = true;
    document.getElementById('lookupBtn').textContent = 'LOOKING...';
    
    try {
        const res = await fetch(`/api/lookup?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('lookupResult').style.display = 'block';
            document.getElementById('lookupAvatar').src = data.avatar || '';
            document.getElementById('lookupDisplayName').textContent = data.user.displayName || data.user.username;
            document.getElementById('lookupUsername').textContent = '@' + data.user.username;
            document.getElementById('lookupId').textContent = data.user.id;
            document.getElementById('lookupVerified').textContent = data.verified ? 'Yes' : 'No';
            document.getElementById('lookupInventory').textContent = data.inventoryPublic;
            document.getElementById('lookupLastSeen').textContent = data.lastSeen;
            document.getElementById('lookupCreated').textContent = data.user.created ? data.user.created.split('T')[0] : 'Unknown';
            document.getElementById('lookupBanned').textContent = data.user.isBanned ? 'Yes' : 'No';
            document.getElementById('lookupDesc').textContent = data.user.description && data.user.description.trim() ? data.user.description : '(no description)';
        } else {
            alert(data.error || 'User not found');
        }
    } catch (e) {
        alert('Error performing lookup');
    } finally {
        document.getElementById('lookupBtn').disabled = false;
        document.getElementById('lookupBtn').textContent = 'LOOKUP';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initMedia() {
    const bgLayer = document.getElementById('bg-layer');
    if (bgLayer) {
        fetch('/api/media').then(r => r.json()).then(data => {
            if (data.background && data.background.url) {
                bgLayer.style.backgroundImage = "url('" + data.background.url + "')";
                bgLayer.classList.add('ready');
            }
        }).catch(() => {});
    }
    
    const audio = document.getElementById('bg-audio');
    const audioToggle = document.getElementById('audio-toggle');
    const volumeSlider = document.getElementById('audio-volume');
    const volumeValue = document.getElementById('volume-value');
    const trackPicker = document.getElementById('track-picker');
    const trackName = document.getElementById('track-name');
    
    if (audio && audioToggle) {
        fetch('/api/media').then(r => r.json()).then(data => {
            const tracks = data.tracks || [];
            if (tracks.length > 0) {
                trackPicker.innerHTML = '';
                tracks.forEach((track, idx) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'track-btn' + (idx === 0 ? ' active' : '');
                    const label = track.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').toUpperCase();
                    btn.textContent = label;
                    btn.onclick = () => {
                        audio.src = track.url;
                        trackName.textContent = label;
                        document.querySelectorAll('.track-btn').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        audio.play().catch(() => {});
                        audioToggle.textContent = 'PAUSE';
                        document.body.classList.add('playing');
                    };
                    trackPicker.appendChild(btn);
                });
                audio.src = tracks[0].url;
                trackName.textContent = tracks[0].name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ').toUpperCase();
                audioToggle.disabled = false;
            }
        }).catch(() => {});
        
        audioToggle.onclick = () => {
            if (audio.paused) {
                audio.play().catch(() => {});
                audioToggle.textContent = 'PAUSE';
                document.body.classList.add('playing');
            } else {
                audio.pause();
                audioToggle.textContent = 'PLAY';
                document.body.classList.remove('playing');
            }
        };
        
        audio.onplay = () => {
            document.body.classList.add('playing');
            audioToggle.textContent = 'PAUSE';
        };
        audio.onpause = () => {
            document.body.classList.remove('playing');
            audioToggle.textContent = 'PLAY';
        };
    }
    
    if (volumeSlider && audio) {
        volumeSlider.oninput = () => {
            audio.volume = volumeSlider.value / 100;
            if (volumeValue) volumeValue.textContent = volumeSlider.value + '%';
        };
        audio.volume = 0.35;
        if (volumeValue) volumeValue.textContent = '35%';
    }
}

function initFx() {
    const canvas = document.getElementById('fx-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resize();
    window.addEventListener('resize', resize);
    
    for (let i = 0; i < 60; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.2,
            r: Math.random() * 1.5 + 0.3
        });
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(0, 255, 65, 0.3)';
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
}
