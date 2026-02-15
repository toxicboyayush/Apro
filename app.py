from flask import Flask, render_template_string, request, session, redirect, url_for
import threading
import time
import os
import database as db
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Default user ID (since no login)
DEFAULT_USER_ID = 1
DEFAULT_USERNAME = "User"

# Initialize default user
def init_default_user():
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (DEFAULT_USER_ID,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", 
                          (DEFAULT_USER_ID, DEFAULT_USERNAME, "default"))
            cursor.execute("INSERT INTO user_config (user_id) VALUES (?)", (DEFAULT_USER_ID,))
            cursor.execute("INSERT INTO automation_state (user_id) VALUES (?)", (DEFAULT_USER_ID,))
            conn.commit()
        conn.close()
    except:
        pass

init_default_user()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YKTI RAWAT - E2EE SYSTEM</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Orbitron', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://images.unsplash.com/photo-1557683316-973673baf926?w=1920');
            background-size: cover;
            background-position: center;
            opacity: 0.1;
            z-index: 0;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 20px;
            border: 2px solid rgba(255, 0, 255, 0.3);
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.2);
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(90deg, #ff00ff, #00ffff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
            letter-spacing: 8px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #00ffff;
            font-size: 0.9rem;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.6);
            border: 2px solid rgba(255, 0, 255, 0.3);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: #ff00ff;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.4);
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 900;
            color: #00ffff;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #ff00ff;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 10px;
        }
        
        .section {
            background: rgba(0, 0, 0, 0.6);
            border: 2px solid rgba(255, 0, 255, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 1.2rem;
            color: #ff00ff;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 0, 255, 0.3);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: #00ffff;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }
        
        .form-input, .form-textarea {
            width: 100%;
            padding: 15px;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid rgba(0, 255, 255, 0.3);
            border-radius: 8px;
            color: #fff;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .form-input:focus, .form-textarea:focus {
            outline: none;
            border-color: #00ffff;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }
        
        .form-input::placeholder, .form-textarea::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        
        .btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #ff00ff, #8000ff);
            border: none;
            border-radius: 10px;
            color: white;
            font-family: 'Orbitron', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 3px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(255, 0, 255, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(255, 0, 255, 0.5);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #00ff00, #00aa00);
            box-shadow: 0 5px 20px rgba(0, 255, 0, 0.3);
        }
        
        .btn-success:hover {
            box-shadow: 0 8px 30px rgba(0, 255, 0, 0.5);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff0000, #aa0000);
            box-shadow: 0 5px 20px rgba(255, 0, 0, 0.3);
        }
        
        .btn-danger:hover {
            box-shadow: 0 8px 30px rgba(255, 0, 0, 0.5);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .status-running {
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .status-stopped {
            color: #ff0000;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        }
        
        .console {
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid rgba(0, 255, 255, 0.3);
            border-radius: 10px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
        }
        
        .console-line {
            color: #00ff00;
            font-size: 0.85rem;
            margin-bottom: 5px;
            padding: 5px;
            border-left: 3px solid rgba(0, 255, 0, 0.3);
            padding-left: 10px;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 700;
        }
        
        .alert-success {
            background: rgba(0, 255, 0, 0.2);
            border: 2px solid #00ff00;
            color: #00ff00;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        @media (max-width: 600px) {
            .header h1 {
                font-size: 2rem;
                letter-spacing: 4px;
            }
            
            .grid-2 {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .collapsible {
            cursor: pointer;
            user-select: none;
        }
        
        .collapsible:hover {
            opacity: 0.8;
        }
        
        .content-hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        {{ content | safe }}
    </div>
    
    <script>
        function toggleSection(id) {
            const element = document.getElementById(id);
            if (element.style.display === 'none') {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

# Automation Classes
class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'automation_state' in session:
            session['automation_state']['logs'].append(formatted_msg)
            session.modified = True

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(5)
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[aria-label*="message" i]',
        'div[data-lexical-editor="true"]',
        'div.xzsf02u',
        'p[class*="x1ok221b"]'
    ]
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return elements[0]
        except:
            continue
    return None

def setup_browser(automation_state=None):
    log_message('Setting up browser...', automation_state)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    return webdriver.Chrome(options=chrome_options)

def send_messages(config, automation_state, user_id):
    driver = None
    try:
        driver = setup_browser(automation_state)
        chat_id = config.get('chat_id', '')
        cookies = config.get('cookies', '')
        messages = config.get('messages', 'Hello!').split('\n')
        delay = int(config.get('delay', 30))
        
        if not chat_id or not cookies:
            log_message('ERROR: Missing chat ID or cookies', automation_state)
            return
        
        log_message('Opening Instagram...', automation_state)
        driver.get('https://www.instagram.com/')
        time.sleep(3)
        
        log_message('Setting cookies...', automation_state)
        for cookie in cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                driver.add_cookie({'name': name, 'value': value, 'domain': '.instagram.com'})
        
        chat_url = f'https://www.instagram.com/direct/t/{chat_id}/' if '/e2ee/' not in chat_id else f'https://www.instagram.com/direct/e2ee/t/{chat_id}/'
        log_message(f'Opening chat: {chat_url}', automation_state)
        driver.get(chat_url)
        time.sleep(5)
        
        message_index = 0
        while session.get('automation_state', {}).get('running', False):
            message_input = find_message_input(driver, 'AUTO', automation_state)
            if message_input:
                msg = messages[message_index % len(messages)]
                log_message(f'Sending: {msg}', automation_state)
                driver.execute_script("arguments[0].textContent = arguments[1];", message_input, msg)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", message_input)
                time.sleep(1)
                
                # Click send
                send_buttons = driver.find_elements(By.CSS_SELECTOR, '[aria-label*="Send" i]')
                if send_buttons:
                    send_buttons[0].click()
                    automation_state.message_count += 1
                    log_message(f'Message sent! Total: {automation_state.message_count}', automation_state)
                
                message_index += 1
                time.sleep(delay)
            else:
                log_message('ERROR: Message input not found', automation_state)
                break
                
    except Exception as e:
        log_message(f'ERROR: {str(e)}', automation_state)
    finally:
        if driver:
            driver.quit()
            log_message('Browser closed', automation_state)

def start_automation(user_config, user_id):
    if 'automation_state' not in session:
        session['automation_state'] = {'running': False, 'message_count': 0, 'logs': []}
    
    session['automation_state']['running'] = True
    session['automation_state']['message_count'] = 0
    session['automation_state']['logs'] = []
    session.modified = True
    
    db.set_automation_running(user_id, True)
    
    automation_state_obj = AutomationState()
    automation_state_obj.running = True
    
    thread = threading.Thread(target=send_messages, args=(user_config, automation_state_obj, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    if 'automation_state' in session:
        session['automation_state']['running'] = False
        session.modified = True
    db.set_automation_running(user_id, False)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_id = DEFAULT_USER_ID
    
    if 'automation_state' not in session:
        session['automation_state'] = {'running': False, 'message_count': 0, 'logs': []}
    
    if request.method == 'POST':
        if 'save_config' in request.form:
            chat_id = request.form.get('chat_id', '')
            name_prefix = request.form.get('name_prefix', '')
            delay = int(request.form.get('delay', 30))
            cookies = request.form.get('cookies', '')
            messages = request.form.get('messages', '')
            db.update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages)
            return redirect(url_for('index'))
        
        elif 'start_automation' in request.form:
            user_config = db.get_user_config(user_id)
            start_automation(user_config, user_id)
            return redirect(url_for('index'))
        
        elif 'stop_automation' in request.form:
            stop_automation(user_id)
            return redirect(url_for('index'))
    
    user_config = db.get_user_config(user_id)
    automation_state = db.get_automation_state(user_id)
    session_automation = session.get('automation_state', {'running': False, 'message_count': 0, 'logs': []})
    
    console_logs = ''
    if session_automation.get('logs'):
        for log in session_automation['logs'][-20:]:
            console_logs += f'<div class="console-line">{log}</div>'
    else:
        console_logs = '<div class="console-line">No logs yet. Start automation to see activity...</div>'
    
    status_text = "RUNNING" if automation_state['is_running'] else "STOPPED"
    status_class = "status-running" if automation_state['is_running'] else "status-stopped"
    start_disabled = "disabled" if automation_state['is_running'] else ""
    stop_disabled = "disabled" if not automation_state['is_running'] else ""
    
    content = f'''
    <div class="header">
        <h1>YKTI RAWAT</h1>
        <p>Premium E2EE Offline Convo System</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{automation_state['messages_sent']}</div>
            <div class="stat-label">Sent</div>
        </div>
        <div class="stat-card">
            <div class="stat-value {status_class}">{status_text}</div>
            <div class="stat-label">Status</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{user_config.get('chat_id', 'Not Set')[:10]}...</div>
            <div class="stat-label">Chat ID</div>
        </div>
    </div>
    
    {"<div class='alert alert-success'>Automation started!</div>" if automation_state['is_running'] else ""}
    
    <div class="grid-2">
        <form method="POST">
            <button type="submit" name="start_automation" class="btn btn-success" {start_disabled}>START AUTOMATION</button>
        </form>
        <form method="POST">
            <button type="submit" name="stop_automation" class="btn btn-danger" {stop_disabled}>STOP AUTOMATION</button>
        </form>
    </div>
    
    <div class="section">
        <div class="section-title collapsible" onclick="toggleSection('target-settings')">▼ TARGET SETTINGS</div>
        <div id="target-settings">
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">CHAT / E2EE ID</label>
                    <input type="text" name="chat_id" class="form-input" value="{user_config.get('chat_id', '')}" placeholder="1300010200930401010">
                </div>
                
                <div class="form-group">
                    <label class="form-label">NAME PREFIX</label>
                    <input type="text" name="name_prefix" class="form-input" value="{user_config.get('name_prefix', '')}" placeholder="[YKTI - RAWAT]">
                </div>
                
                <div class="form-group">
                    <label class="form-label">DELAY (SEC)</label>
                    <input type="number" name="delay" class="form-input" value="{user_config.get('delay', 30)}" min="1">
                </div>
                
                <button type="submit" name="save_config" class="btn">SET</button>
            </form>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title collapsible" onclick="toggleSection('cookie-config')">▼ COOKIE CONFIG</div>
        <div id="cookie-config" class="content-hidden">
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">COOKIES</label>
                    <textarea name="cookies" class="form-textarea" rows="4" placeholder="Paste your cookies here">{user_config.get('cookies', '')}</textarea>
                </div>
                <button type="submit" name="save_config" class="btn">SET</button>
            </form>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title collapsible" onclick="toggleSection('message-config')">▼ MESSAGE CONFIG</div>
        <div id="message-config" class="content-hidden">
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">MESSAGES (one per line)</label>
                    <textarea name="messages" class="form-textarea" rows="6" placeholder="Message 1
Message 2
Message 3">{user_config.get('messages', '')}</textarea>
                </div>
                <button type="submit" name="save_config" class="btn">SET</button>
            </form>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">📡 LIVE CONSOLE</div>
        <div class="console">
            {console_logs}
        </div>
    </div>
    '''
    
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
