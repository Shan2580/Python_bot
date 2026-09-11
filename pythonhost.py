import os
import subprocess
import shutil
import time
import sys
import json
import asyncio
import html
import threading
import random
import re
import zipfile
from datetime import datetime
from telegram import Update, ReactionTypeEmoji, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ═══════════════════════════════════════════════════════════════
#                      🤖 BOT TOKEN
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8717606762:AAHWAtgTjuti_3Mn-bYBDOMkGv09JRwODXg"

# ═══════════════════════════════════════════════════════════════
#                      👑 ADMIN & USER CONFIG
# ═══════════════════════════════════════════════════════════════

ADMIN_IDS = [6858000955]
PENDING_USERS = {}
ALLOWED_USERS = []
DEFAULT_LIMIT_MB = 5
DATA_FILE = "user_data.json"
PROJECTS_FILE = "projects_data.json"
running_processes = {}
script_outputs = {}
script_status = {}

# ═══════════════════════════════════════════════════════════════
#                      💾 LOAD / SAVE DATA
# ═══════════════════════════════════════════════════════════════

def load_user_data():
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                user_data = json.load(f)
        except:
            user_data = {}
    else:
        user_data = {}

def save_user_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=2)

load_user_data()

# ═══════════════════════════════════════════════════════════════
#                      🎨 PREMIUM EMOJI SYSTEM
# ═══════════════════════════════════════════════════════════════

P = {
    "check": "6233317763608226414",
    "cross": "6233533083203670586",
    "wave": "6233512991346660853",
    "kpay": "6233151621388308984",
    "money": "6087067873707035471",
    "money_fly": "6280552203316891805",
    "alarm": "6104858805068108294",
    "hourglass": "6163231452184975307",
    "lock_open": "5291873529464122510",
    "phone": "5237988788164107500",
    "game": "5319247469165433798",
    "dice": "5280816565657300091",
    "point_down": "5199412938099666948",
    "one": "5382322671679708881",
    "two": "5381990043642502553",
    "three": "5381879959335738545",
    "four": "5382054253403577563",
    "five": "5391197405553107640",
    "trophy": "6194737030165959506",
    "book": "5411369574157286161",
}

N = {
    "check": "✅",
    "cross": "❌",
    "wave": "👋",
    "kpay": "🇲🇲",
    "money": "💰",
    "money_fly": "💸",
    "alarm": "⏰",
    "hourglass": "⏳",
    "lock_open": "🔓",
    "phone": "📞",
    "game": "🎮",
    "dice": "🎲",
    "point_down": "👇",
    "one": "1️⃣",
    "two": "2️⃣",
    "three": "3️⃣",
    "four": "4️⃣",
    "five": "5️⃣",
    "trophy": "🏆",
    "book": "📖",
}

NORMAL = {
    "rocket": "🚀",
    "fire": "🔥",
    "wrench": "🔧",
    "gear": "⚙️",
    "star": "⭐",
    "warning": "⚠️",
}

BUTTON_EMOJIS = {
    "list": "📋",
    "status": "📊",
    "help": "❓",
    "check": "✅",
    "cross": "❌",
    "lock": "🔓",
}

def emoji_text(key):
    if key in P:
        return f'<tg-emoji emoji-id="{P[key]}">{N[key]}</tg-emoji>'
    elif key in NORMAL:
        return NORMAL[key]
    return "❓"

def emoji_button(key):
    return BUTTON_EMOJIS.get(key, "•")

def escape_html(text):
    if not text:
        return ""
    return html.escape(str(text))

# ═══════════════════════════════════════════════════════════════
#             📦 ADVANCED AUTO PACKAGE INSTALLER SYSTEM
# ═══════════════════════════════════════════════════════════════

BUILTIN_PYTHON_MODULES = set(sys.builtin_module_names).union({
    "os", "sys", "time", "datetime", "json", "asyncio", "threading", "subprocess",
    "shutil", "html", "random", "re", "math", "string", "types", "logging", "urllib",
    "base64", "hashlib", "socket", "struct", "select", "ctypes", "pathlib", "glob"
})

STD_JS_MODULES = {"fs", "path", "http", "https", "os", "child_process", "util", "events", "crypto", "stream", "buffer", "url"}

PIP_PACKAGE_MAP = {
    "telegram": "python-telegram-bot",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "fitz": "PyMuPDF",
    "sklearn": "scikit-learn",
    "attr": "attrs",
    "crypto": "pycryptodome"
}

def extract_python_imports(file_path):
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        matches = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
        for mod in matches:
            if mod not in BUILTIN_PYTHON_MODULES:
                pkg_name = PIP_PACKAGE_MAP.get(mod, mod)
                imports.add(pkg_name)
    except Exception as e:
        print(f"Error reading Python imports: {e}")
    return imports

def extract_node_imports(file_path):
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        matches = re.findall(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', content)
        matches_import = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
        
        for mod in matches + matches_import:
            if not mod.startswith('.') and not mod.startswith('/') and mod not in STD_JS_MODULES:
                pkg_name = mod.split('/')[0]
                imports.add(pkg_name)
    except Exception as e:
        print(f"Error reading JS imports: {e}")
    return imports

async def auto_install_dependencies(file_path, project_type):
    if project_type == "python":
        pkgs = extract_python_imports(file_path)
        if not pkgs:
            return True
            
        for pkg in pkgs:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'pip', 'install', pkg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
    elif project_type == "node":
        pkgs = extract_node_imports(file_path)
        if not pkgs:
            return True
            
        project_dir = os.path.dirname(file_path)
        package_json = os.path.join(project_dir, "package.json")
        if not os.path.exists(package_json):
            init_proc = await asyncio.create_subprocess_exec(
                'npm', 'init', '-y',
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await init_proc.communicate()
            
        for pkg in pkgs:
            proc = await asyncio.create_subprocess_exec(
                'npm', 'install', pkg,
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
    return True

# ═══════════════════════════════════════════════════════════════
#                      🎬 ANIMATIONS (5 types)
# ═══════════════════════════════════════════════════════════════

async def animate_dots(status_msg, text):
    dots = ["", ".", "..", "..."]
    for i in range(8):
        try:
            await status_msg.edit_text(f"{text}{dots[i % 4]}")
            await asyncio.sleep(0.2)
        except:
            break
    return status_msg

async def animate_spinner(status_msg, text):
    frames = ["◐", "◓", "◑", "◒"]
    for i in range(8):
        try:
            await status_msg.edit_text(f"{frames[i % 4]} {text}")
            await asyncio.sleep(0.2)
        except:
            break
    return status_msg

async def animate_progress(status_msg, text, current, total):
    percent = int((current / total) * 100)
    bar = "█" * int((current / total) * 20) + "░" * (20 - int((current / total) * 20))
    try:
        await status_msg.edit_text(
            f"{emoji_text('rocket')} {text}\n\n"
            f"┌{'─' * 24}┐\n"
            f"│ {bar} {percent:3}% │\n"
            f"└{'─' * 24}┘"
        )
    except:
        pass

async def animate_pulse(status_msg, text):
    pulses = ["🔴", "🟡", "🟢", "🟡", "🔴"]
    for i in range(5):
        try:
            await status_msg.edit_text(f"{pulses[i]} {text}")
            await asyncio.sleep(0.2)
        except:
            break
    return status_msg

async def animate_bounce(status_msg, text):
    dots = ["●", "◉", "○", "◉", "●"]
    for i in range(5):
        try:
            await status_msg.edit_text(f"{dots[i]} {text}")
            await asyncio.sleep(0.2)
        except:
            break
    return status_msg

async def add_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            reaction=[ReactionTypeEmoji("⚡")]
        )
    except:
        pass

# ═══════════════════════════════════════════════════════════════
#                      📁 PROJECT MANAGER
# ═══════════════════════════════════════════════════════════════

class ProjectManager:
    def __init__(self):
        self.projects = self.load_projects()
        self.project_processes = {}
        self.project_threads = {}
        self.project_running = {}
        self.loop = None

    def set_loop(self, loop):
        self.loop = loop

    def load_projects(self):
        if os.path.exists(PROJECTS_FILE):
            try:
                with open(PROJECTS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_projects(self):
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(self.projects, f, indent=2)

    def get_user_projects(self, user_id):
        user_projects = {}
        for name, data in self.projects.items():
            if data.get('user_id') == user_id:
                user_projects[name] = data
        return user_projects

    def add_project(self, name, file_path, user_id, project_type="python"):
        user_projects = self.get_user_projects(user_id)
        if len(user_projects) >= 3:
            return False, f"{emoji_text('cross')} သင့်အတွက် Project အများဆုံး 3 ခုသာ သိမ်းနိုင်ပါတယ်။"

        if name in self.projects:
            return False, f"{emoji_text('cross')} '{name}' ဆိုတဲ့ Project ရှိပြီးသားပါ။"

        self.projects[name] = {
            'file_path': file_path,
            'user_id': user_id,
            'type': project_type,
            'created_at': datetime.now().isoformat(),
            'status': 'stopped',
            'pid': None
        }
        self.save_projects()
        return True, f"{emoji_text('check')} Project '{name}' ကို သိမ်းဆည်းပြီးပါပြီ။"

    def delete_project(self, name, user_id):
        if name not in self.projects:
            return False, f"{emoji_text('cross')} '{name}' Project မတွေ့ပါ။"

        if self.projects[name].get('user_id') != user_id:
            return False, f"{emoji_text('cross')} သင့်ရဲ့ Project မဟုတ်ပါ။"

        if name in self.project_processes and self.project_processes[name].poll() is None:
            self.stop_project(name, user_id)

        file_path = self.projects[name]['file_path']
        project_dir = os.path.dirname(file_path)
        
        try:
            if os.path.exists(project_dir) and "bot_files" in project_dir:
                shutil.rmtree(project_dir)
            elif os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass

        del self.projects[name]
        self.save_projects()
        return True, f"{emoji_text('check')} Project '{name}' ကိုဖျက်ပြီးပါပြီ။"

    def stop_project(self, name, user_id):
        if name not in self.projects:
            return False, f"{emoji_text('cross')} '{name}' Project မတွေ့ပါ။"

        if self.projects[name].get('user_id') != user_id:
            return False, f"{emoji_text('cross')} သင့်ရဲ့ Project မဟုတ်ပါ။"

        if name not in self.project_processes:
            return False, f"{emoji_text('cross')} '{name}' Project က running မရှိပါ။"

        process = self.project_processes.get(name)
        if process and process.poll() is None:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()

            self.projects[name]['status'] = 'stopped'
            self.projects[name]['pid'] = None
            self.save_projects()

            if name in self.project_processes:
                del self.project_processes[name]
            if name in self.project_threads:
                del self.project_threads[name]
            if name in self.project_running:
                del self.project_running[name]

            return True, f"{emoji_text('alarm')} Project '{name}' ကိုရပ်လိုက်ပါပြီ။"
        return False, f"{emoji_text('cross')} Project '{name}' က ရပ်နေပြီးသားပါ။"

    def run_project(self, name, user_id, chat_id, context):
        if name not in self.projects:
            return False, f"{emoji_text('cross')} '{name}' Project မတွေ့ပါ။"

        if self.projects[name].get('user_id') != user_id:
            return False, f"{emoji_text('cross')} သင့်ရဲ့ Project မဟုတ်ပါ။"

        if name in self.project_running and self.project_running[name]:
            return False, f"{emoji_text('hourglass')} '{name}' Project က ပြေးနေပြီးသားပါ။"

        file_path = self.projects[name]['file_path']
        if not os.path.exists(file_path):
            return False, f"{emoji_text('cross')} '{name}' Project file မတွေ့ပါ။"

        project_type = self.projects[name].get('type', 'python')

        thread = threading.Thread(
            target=self._run_in_background,
            args=(name, file_path, chat_id, context, user_id, project_type),
            daemon=True
        )
        self.project_threads[name] = thread
        self.project_running[name] = True
        self.projects[name]['status'] = 'running'
        self.save_projects()
        thread.start()

        return True, f"{emoji_text('rocket')} Project '{name}' ({project_type.upper()}) ကို Run နေပါပြီ။"

    def _run_in_background(self, name, file_path, chat_id, context, user_id, project_type="python"):
        try:
            start_time = time.time()

            cmd = [sys.executable, file_path] if project_type == "python" else ['node', file_path]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(file_path)
            )
            self.project_processes[name] = process
            self.projects[name]['pid'] = process.pid
            self.save_projects()

            stdout, stderr = process.communicate()
            elapsed_time = time.time() - start_time

            output = stdout.strip() if stdout else ""
            error = stderr.strip() if stderr else ""

            if process.returncode == 0:
                if not output:
                    output = "(No Output)"

                response = f"{emoji_text('check')} Project: {name}\n"
                response += f"{emoji_text('hourglass')} ကြာမြင့်ချိန်: {elapsed_time:.2f}s\n\n"
                response += f"{output[:4000]}"

                if len(output) > 4000:
                    response += f"\n\n{emoji_text('warning')} Output ရှည်လွန်းလို့ ဖြတ်တောက်ပြထားပါတယ်။"
            else:
                if not error:
                    error = "Unknown Error"

                response = f"{emoji_text('cross')} Project: {name}\n"
                response += f"{emoji_text('hourglass')} ကြာမြင့်ချိန်: {elapsed_time:.2f}s\n\n"
                response += f"{error[:4000]}"

            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    context.bot.send_message(chat_id=chat_id, text=response, parse_mode='HTML'),
                    self.loop
                )

            self.project_running[name] = False
            self.projects[name]['status'] = 'stopped'
            self.projects[name]['pid'] = None
            self.save_projects()

            if name in self.project_processes:
                del self.project_processes[name]
            if name in self.project_threads:
                del self.project_threads[name]

        except Exception as e:
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    context.bot.send_message(chat_id=chat_id, text=f"{emoji_text('warning')} Error: {str(e)[:500]}", parse_mode='HTML'),
                    self.loop
                )
            self.project_running[name] = False

pm = ProjectManager()

# ═══════════════════════════════════════════════════════════════
#                      🔐 PERMISSION SYSTEM
# ═══════════════════════════════════════════════════════════════

def request_permission_keyboard():
    keyboard = [[InlineKeyboardButton(f"{emoji_button('lock')} Request Access", callback_data="request_access")]]
    return InlineKeyboardMarkup(keyboard)

def admin_permission_keyboard(user_id):
    keyboard = [[
        InlineKeyboardButton(f"{emoji_button('check')} Approve", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton(f"{emoji_button('cross')} Reject", callback_data=f"reject_{user_id}")
    ]]
    return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════════════
#                      👑 START COMMAND
# ═══════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    username = update.effective_user.username or "N/A"

    if has_permission(user_id):
        keyboard = [
            [InlineKeyboardButton(f"{emoji_button('list')} Project စာရင်း", callback_data="list_projects")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_projects = pm.get_user_projects(user_id)
        projects_count = len(user_projects)
        used = get_user_used(user_id)

        await update.message.reply_text(
            f"{emoji_text('game')} TERMUX PYTHON & NODE.JS RUNNER - PROJECT MANAGER\n\n"
            f"{emoji_text('wave')} Powered by Telegram\n"
            f"{emoji_text('dice')} Execute Python (.py) & Node.js (.js) Files\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{emoji_text('book')} Features:\n"
            f"├ {emoji_text('check')} Project Manager (Max 3)\n"
            f"├ {emoji_text('rocket')} Auto Package Installer (Pip & Npm)\n"
            f"├ {emoji_text('trophy')} Advanced Monitor\n"
            f"├ {emoji_text('money')} File Limit: 5 MB Per User\n"
            f"└ {emoji_text('star')} Premium Emojis\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{emoji_text('phone')} Commands:\n"
            f"├ /start - {emoji_text('check')} Show menu\n"
            f"├ /projects - {emoji_text('book')} List projects\n"
            f"├ /run [name] - {emoji_text('rocket')} Run project\n"
            f"├ /stop [name] - {emoji_text('alarm')} Stop project\n"
            f"├ /delete [name] - {emoji_text('cross')} Delete project\n"
            f"├ /monitor - {emoji_text('phone')} System usage\n"
            f"├ /myinfo - {emoji_text('trophy')} Your info\n"
            f"└ /help - {emoji_text('wave')} Help menu\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{emoji_text('hourglass')} Runtime: Infinite\n"
            f"{emoji_text('money')} File Limit: 5 MB per user\n"
            f"{emoji_text('money')} Used: {used:.2f} MB / 5 MB\n"
            f"{emoji_text('book')} Your Projects: {projects_count}/3\n\n"
            f"{emoji_text('check')} Ready to run your code!",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    else:
        if str(user_id) in PENDING_USERS:
            await update.message.reply_text(
                f"{emoji_text('hourglass')} Access Request Pending\n\n"
                f"{emoji_text('hourglass')} Your request is waiting for admin approval.",
                parse_mode="HTML"
            )
            return

        await update.message.reply_text(
            f"{emoji_text('lock_open')} Access Restricted\n\n"
            f"{emoji_text('cross')} You don't have permission.\n\n"
            f"{emoji_text('phone')} Request access below.\n\n"
            f"👤 Your Info:\n"
            f"├ 🆔 {user_id}\n"
            f"├ 👤 {user_name}\n"
            f"└ @{username}\n\n"
            f"{emoji_text('alarm')} Admin will be notified.",
            parse_mode="HTML",
            reply_markup=request_permission_keyboard()
        )

# ═══════════════════════════════════════════════════════════════
#                      📋 PROJECTS LIST
# ═══════════════════════════════════════════════════════════════

async def projects_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    user_projects = pm.get_user_projects(user_id)

    if not user_projects:
        msg = f"{emoji_text('book')} Your Projects\n\n{emoji_text('warning')} Project မရှိသေးပါ။\n\nSend .py, .js or .zip file to create a project."
        if update.message:
            await update.message.reply_text(msg, parse_mode="HTML")
        elif update.callback_query:
            query = update.callback_query
            try:
                await query.edit_message_text(msg, parse_mode="HTML")
            except:
                await query.message.reply_text(msg, parse_mode="HTML")
        return

    response = f"{emoji_text('book')} Your Projects\n\n"
    response += f"━━━━━━━━━━━━━━━━━━━━━\n"

    for idx, (name, data) in enumerate(user_projects.items(), 1):
        status_emoji = "🟢" if data['status'] == 'running' else "🔴"
        p_type = data.get('type', 'python').upper()
        response += f"{idx}. {status_emoji} {name} [{p_type}]\n"
        response += f"   └─ 📅 {data['created_at'][:10]}\n"
        response += f"   └─ 📊 Status: {data['status']}\n"
        if data['pid']:
            response += f"   └─ 🆔 PID: {data['pid']}\n"
        response += "\n"

    response += f"━━━━━━━━━━━━━━━━━━━━━\n"
    response += f"\n📌 Project အရေအတွက်: {len(user_projects)}/3"

    if update.message:
        await update.message.reply_text(response, parse_mode="HTML")
    elif update.callback_query:
        query = update.callback_query
        try:
            await query.edit_message_text(response, parse_mode="HTML")
        except:
            await query.message.reply_text(response, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#                      🚀 RUN PROJECT
# ═══════════════════════════════════════════════════════════════

async def run_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    if not context.args:
        await update.message.reply_text(
            f"{emoji_text('point_down')} Usage: /run [project_name]\n\n"
            f"{emoji_text('book')} Example: /run my_project",
            parse_mode="HTML"
        )
        return

    name = context.args[0]

    status_msg = await update.message.reply_text(
        f"{emoji_text('hourglass')} Starting project...\n\n"
        f"┌{'─' * 24}┐\n"
        f"│ ░░░░░░░░░░░░░░░░░░░░░░  0% │\n"
        f"└{'─' * 24}┘",
        parse_mode="HTML"
    )

    for i in range(1, 11):
        await asyncio.sleep(0.1)
        try:
            bar = "█" * i + "░" * (10 - i)
            await status_msg.edit_text(
                f"{emoji_text('hourglass')} Starting project...\n\n"
                f"┌{'─' * 24}┐\n"
                f"│ {bar} {i*10:3}% │\n"
                f"└{'─' * 24}┘",
                parse_mode="HTML"
            )
        except:
            pass

    success, msg = pm.run_project(name, user_id, update.message.chat_id, context)
    await status_msg.edit_text(msg, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#                      🛑 STOP PROJECT
# ═══════════════════════════════════════════════════════════════

async def stop_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    if not context.args:
        await update.message.reply_text(
            f"{emoji_text('point_down')} Usage: /stop [project_name]\n\n"
            f"{emoji_text('book')} Example: /stop my_project",
            parse_mode="HTML"
        )
        return

    name = context.args[0]
    success, msg = pm.stop_project(name, user_id)
    await update.message.reply_text(msg, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#                      🗑️ DELETE PROJECT
# ═══════════════════════════════════════════════════════════════

async def delete_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    if not context.args:
        await update.message.reply_text(
            f"{emoji_text('point_down')} Usage: /delete [project_name]\n\n"
            f"{emoji_text('book')} Example: /delete my_project",
            parse_mode="HTML"
        )
        return

    name = context.args[0]
    success, msg = pm.delete_project(name, user_id)
    await update.message.reply_text(msg, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#                      📊 SYSTEM MONITOR
# ═══════════════════════════════════════════════════════════════

class SystemMonitor:
    @staticmethod
    def get_cpu_usage():
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                parts = line.split()
                if len(parts) >= 5:
                    user = int(parts[1])
                    nice = int(parts[2])
                    system = int(parts[3])
                    idle = int(parts[4])
                    total = user + nice + system + idle
                    time.sleep(0.5)
                    with open('/proc/stat', 'r') as f2:
                        line2 = f2.readline()
                        parts2 = line2.split()
                        if len(parts2) >= 5:
                            user2 = int(parts2[1])
                            nice2 = int(parts2[2])
                            system2 = int(parts2[3])
                            idle2 = int(parts2[4])
                            total2 = user2 + nice2 + system2 + idle2
                            diff_total = total2 - total
                            diff_idle = idle2 - idle
                            if diff_total > 0:
                                usage = 100 * (diff_total - diff_idle) / diff_total
                                return round(usage, 1)
            return 0
        except:
            return 0

    @staticmethod
    def get_ram_usage():
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            mem_total = 0
            mem_available = 0
            for line in lines:
                if 'MemTotal:' in line:
                    mem_total = int(line.split()[1]) / 1024 / 1024
                elif 'MemAvailable:' in line:
                    mem_available = int(line.split()[1]) / 1024 / 1024
            if mem_total > 0 and mem_available > 0:
                used = mem_total - mem_available
                percent = (used / mem_total) * 100
                return {'total': round(mem_total, 2), 'used': round(used, 2),
                        'free': round(mem_available, 2), 'percent': round(percent, 1)}
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}
        except:
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

    @staticmethod
    def get_disk_usage():
        try:
            result = subprocess.run("df -h / | tail -1", shell=True, capture_output=True, text=True)
            if result.stdout:
                parts = result.stdout.split()
                if len(parts) >= 5:
                    total = parts[1].replace('G', '').replace('T', '')
                    used = parts[2].replace('G', '').replace('T', '')
                    free = parts[3].replace('G', '').replace('T', '')
                    percent = parts[4].replace('%', '')
                    return {'total': float(total), 'used': float(used),
                            'free': float(free), 'percent': float(percent)}
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}
        except:
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

    @staticmethod
    def get_uptime():
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "N/A"

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    status_msg = await update.message.reply_text(f"{emoji_text('hourglass')} Loading system data...", parse_mode="HTML")
    
    await animate_dots(status_msg, "Fetching system info")
    await animate_spinner(status_msg, "Getting CPU stats")

    cpu = SystemMonitor.get_cpu_usage()
    ram = SystemMonitor.get_ram_usage()
    disk = SystemMonitor.get_disk_usage()
    uptime = SystemMonitor.get_uptime()

    await animate_pulse(status_msg, "Almost ready")

    cpu_bar = "█" * int(cpu / 5) + "░" * (20 - int(cpu / 5))
    ram_bar = "█" * int(ram['percent'] / 5) + "░" * (20 - int(ram['percent'] / 5))
    disk_bar = "█" * int(disk['percent'] / 5) + "░" * (20 - int(disk['percent'] / 5))

    await status_msg.edit_text(
        f"{emoji_text('trophy')} System Monitor\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji_text('hourglass')} Uptime: {uptime}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{emoji_text('gear')} CPU Usage\n"
        f"└ {cpu:.1f}% [{cpu_bar}]\n\n"
        f"{emoji_text('phone')} RAM Usage\n"
        f"└ {ram['percent']:.1f}% [{ram_bar}]\n"
        f"└ Used: {ram['used']:.2f}GB / {ram['total']:.2f}GB\n\n"
        f"{emoji_text('wrench')} Disk Usage\n"
        f"└ {disk['percent']:.1f}% [{disk_bar}]\n"
        f"└ Used: {disk['used']:.2f}GB / {disk['total']:.2f}GB\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{emoji_text('check')} Updated Real-Time",
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
#                      👤 MYINFO
# ═══════════════════════════════════════════════════════════════

async def myinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    user = update.effective_user
    limit = get_user_limit(user_id)
    used = get_user_used(user_id)
    files = get_user_files(user_id)
    remaining = limit - used
    user_projects = pm.get_user_projects(user_id)

    await update.message.reply_text(
        f"{emoji_text('trophy')} Your Information\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Name: {user.first_name}\n"
        f"📞 Username: @{user.username or 'N/A'}\n"
        f"{emoji_text('trophy')} Admin: {'Yes' if is_admin(user_id) else 'No'}\n"
        f"{emoji_text('check')} Access: {'Authorized' if is_allowed_user(user_id) else 'Unauthorized'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{emoji_text('money')} File Limit: 5 MB\n"
        f"{emoji_text('money')} Used: {used:.2f} MB\n"
        f"{emoji_text('check')} Remaining: {remaining:.2f} MB\n"
        f"{emoji_text('book')} Files: {files}\n"
        f"{emoji_text('book')} Your Projects: {len(user_projects)}/3\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
#                      ❓ HELP
# ═══════════════════════════════════════════════════════════════

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    await update.message.reply_text(
        f"{emoji_text('book')} Help Menu\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{emoji_text('rocket')} Project Management:\n"
        f"├ 📤 Send .py, .js or .zip file → Create project\n"
        f"├ /projects - {emoji_text('book')} List your projects\n"
        f"├ /run [name] - {emoji_text('rocket')} Run project\n"
        f"├ /stop [name] - {emoji_text('alarm')} Stop project\n"
        f"└ /delete [name] - {emoji_text('cross')} Delete project\n\n"
        f"{emoji_text('phone')} User Commands:\n"
        f"├ /start - {emoji_text('check')} Show menu\n"
        f"├ /monitor - {emoji_text('phone')} System usage\n"
        f"├ /myinfo - {emoji_text('trophy')} Your info\n"
        f"└ /help - {emoji_text('wave')} This menu\n\n"
        f"{emoji_text('trophy')} Admin Commands:\n"
        f"├ /addus - {emoji_text('check')} Add user\n"
        f"├ /removeus - {emoji_text('cross')} Remove user\n"
        f"├ /listus - {emoji_text('book')} List users\n"
        f"├ /setlimit - {emoji_text('money')} Set user limit\n"
        f"└ /stopbot - {emoji_text('alarm')} Stop bot\n\n"
        f"{emoji_text('game')} Runtime: Infinite\n"
        f"{emoji_text('book')} Projects: Max 3 per user\n"
        f"{emoji_text('money')} File Limit: 5 MB per user",
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
#                      📂 HANDLE FILE
# ═══════════════════════════════════════════════════════════════

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    document = update.message.document
    filename = document.file_name.lower()
    
    if not (filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.zip')):
        await update.message.reply_text(
            f"{emoji_text('cross')} Invalid File Type\n\nPlease send a .py, .js or .zip file only!",
            parse_mode="HTML"
        )
        return

    if filename.endswith('.py'):
        project_type = "python"
    elif filename.endswith('.js'):
        project_type = "node"
    else:
        project_type = "zip"

    file_size = document.file_size
    file_size_mb = file_size / (1024 * 1024)
    user_limit = 5
    user_used = get_user_used(user_id)
    remaining = user_limit - user_used

    if file_size_mb > user_limit:
        await update.message.reply_text(
            f"{emoji_text('cross')} File Exceeds Limit!\n\n"
            f"📄 File: {document.file_name}\n"
            f"💾 Size: {file_size_mb:.2f} MB\n"
            f"💾 Your Limit: 5 MB",
            parse_mode="HTML"
        )
        return

    if file_size_mb > remaining:
        await update.message.reply_text(
            f"{emoji_text('cross')} Not Enough Space!\n\n"
            f"📄 File: {document.file_name}\n"
            f"💾 Size: {file_size_mb:.2f} MB\n"
            f"💾 Remaining: {remaining:.2f} MB",
            parse_mode="HTML"
        )
        return

    track_user_file(user_id, file_size_mb, document.file_name)

    await update.message.reply_text(
        f"{emoji_text('book')} Project Name ထည့်ပါ ({project_type.upper()})\n\n"
        f"ဒီ Project အတွက် အမည်ပေးပါ။\n"
        f"ဥပမာ: my_project, test_bot\n\n"
        f"{emoji_text('point_down')} Name ကို ချက်ချင်းရိုက်ထည့်ပါ။\n"
        f"{emoji_text('warning')} သင့်အတွက် Project အများဆုံး 3 ခုသာ သိမ်းနိုင်ပါတယ်။\n"
        f"{emoji_text('money')} သင်၏ File Limit: 5 MB (သုံးပြီး: {user_used:.2f} MB)",
        parse_mode="HTML"
    )

    context.user_data['pending_file'] = {
        'file_id': document.file_id,
        'file_name': document.file_name,
        'file_size': file_size_mb,
        'project_type': project_type
    }

# ═══════════════════════════════════════════════════════════════
#                      💬 HANDLE TEXT
# ═══════════════════════════════════════════════════════════════

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not has_permission(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Access Denied", parse_mode="HTML")
        return

    await add_reaction(update, context)

    if 'pending_file' in context.user_data:
        project_name = update.message.text.strip()

        if not project_name:
            await update.message.reply_text(f"{emoji_text('cross')} Project Name မရှိပါ။ ထပ်ကြိုးစားပါ။", parse_mode="HTML")
            return

        if len(project_name) > 30:
            await update.message.reply_text(f"{emoji_text('cross')} Project Name က 30 လုံးထက်မပိုရပါ။", parse_mode="HTML")
            return

        file_info = context.user_data['pending_file']
        project_type = file_info.get('project_type', 'python')
        file_path = None
        user_folder = os.path.join(os.getcwd(), "bot_files", str(user_id), project_name)

        try:
            status_msg = await update.message.reply_text(
                f"{emoji_text('hourglass')} Creating project...\n\n"
                f"┌{'─' * 24}┐\n"
                f"│ ████████░░░░░░░░░░░░  40% │\n"
                f"└{'─' * 24}┘",
                parse_mode="HTML"
            )

            await animate_progress(status_msg, "Downloading file...", 1, 5)

            bot = context.bot
            file = await bot.get_file(file_info['file_id'])

            os.makedirs(user_folder, exist_ok=True)

            if project_type == "zip":
                zip_path = os.path.join(user_folder, f"temp_{int(time.time())}.zip")
                await file.download_to_drive(zip_path)
                
                # Pre-check zip content before extraction
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    namelist = zip_ref.namelist()
                    has_executable = any(f.endswith('.py') or f.endswith('.js') for f in namelist)

                    if not has_executable:
                        await status_msg.edit_text(
                            f"{emoji_text('cross')} Zip ထဲတွင် executable (.py သို့မဟုတ် .js) ဖိုင် မတွေ့ပါ။",
                            parse_mode="HTML"
                        )
                        os.unlink(zip_path)
                        shutil.rmtree(user_folder)
                        del context.user_data['pending_file']
                        return

                    await animate_progress(status_msg, "Extracting Zip...", 2, 5)
                    zip_ref.extractall(user_folder)

                os.unlink(zip_path)

                main_file = None
                detected_type = "python"

                # Priority Entrypoint check
                priority_files = {
                    "main.py": "python", "bot.py": "python", "app.py": "python", "index.py": "python",
                    "index.js": "node", "main.js": "node", "bot.js": "node", "app.js": "node"
                }

                for root, dirs, files in os.walk(user_folder):
                    for f in files:
                        if f.lower() in priority_files:
                            main_file = os.path.relpath(os.path.join(root, f), user_folder)
                            detected_type = priority_files[f.lower()]
                            break
                    if main_file:
                        break

                if not main_file:
                    for root, dirs, files in os.walk(user_folder):
                        for f in files:
                            if f.endswith(".py"):
                                main_file = os.path.relpath(os.path.join(root, f), user_folder)
                                detected_type = "python"
                                break
                            elif f.endswith(".js"):
                                main_file = os.path.relpath(os.path.join(root, f), user_folder)
                                detected_type = "node"
                                break
                        if main_file:
                            break

                file_path = os.path.join(user_folder, main_file)
                project_type = detected_type

            else:
                ext = ".py" if project_type == "python" else ".js"
                file_path = os.path.join(user_folder, f"{project_name}_{int(time.time())}{ext}")
                await file.download_to_drive(file_path)

            await animate_progress(status_msg, "Checking syntax...", 2, 5)

            if project_type == "python":
                syntax_check = await asyncio.create_subprocess_exec(
                    sys.executable, '-c',
                    f'import py_compile; py_compile.compile(r"{file_path}", doraise=True)',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                syntax_check = await asyncio.create_subprocess_exec(
                    'node', '--check', file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
            stdout, stderr = await syntax_check.communicate()

            if syntax_check.returncode != 0:
                error_msg = stderr.decode() if stderr else "Syntax Error"
                await status_msg.edit_text(
                    f"{emoji_text('cross')} Syntax Error ရှိပါတယ်!\n\n"
                    f"{error_msg[:4000]}",
                    parse_mode="HTML"
                )
                if os.path.exists(user_folder):
                    shutil.rmtree(user_folder)
                del context.user_data['pending_file']
                return

            await animate_progress(status_msg, "Auto-Installing packages...", 3, 5)
            await auto_install_dependencies(file_path, project_type)

            await animate_progress(status_msg, "Saving project...", 4, 5)

            success, msg = pm.add_project(project_name, file_path, user_id, project_type)

            await animate_progress(status_msg, "Complete!", 5, 5)
            await asyncio.sleep(0.3)

            if success:
                new_used = get_user_used(user_id)
                new_remaining = 5 - new_used

                await status_msg.edit_text(
                    f"{emoji_text('check')} Project Created!\n\n"
                    f"{msg}\n\n"
                    f"{emoji_text('book')} Project Info:\n"
                    f"├ 📄 Name: {project_name}\n"
                    f"├ ⚙️ Type: {project_type.upper()}\n"
                    f"├ 💾 Size: {file_info['file_size']:.2f} MB\n"
                    f"├ 📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"└ 📊 Status: stopped\n\n"
                    f"{emoji_text('money')} Your File Usage:\n"
                    f"├ 💾 Used: {new_used:.2f} MB / 5 MB\n"
                    f"└ 📊 Remaining: {new_remaining:.2f} MB\n\n"
                    f"{emoji_text('rocket')} Commands:\n"
                    f"├ /run {project_name} - Run\n"
                    f"├ /stop {project_name} - Stop\n"
                    f"└ /delete {project_name} - Delete",
                    parse_mode="HTML"
                )
            else:
                await status_msg.edit_text(msg, parse_mode="HTML")
                if os.path.exists(user_folder):
                    shutil.rmtree(user_folder)

            del context.user_data['pending_file']

        except Exception as e:
            await update.message.reply_text(f"{emoji_text('warning')} Error: {str(e)[:500]}", parse_mode="HTML")
            if os.path.exists(user_folder):
                try:
                    shutil.rmtree(user_folder)
                except:
                    pass
            del context.user_data['pending_file']

        return

    status_msg = await update.message.reply_text(f"{emoji_text('hourglass')} Processing...", parse_mode="HTML")
    await animate_bounce(status_msg, "Thinking")

    user_message = update.message.text[:200]

    await status_msg.edit_text(
        f"{emoji_text('check')} R E C\n\n"
        f"{emoji_text('wave')} I received your message!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 Your message:\n"
        f"{user_message}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{emoji_text('game')} Send a .py, .js or .zip file to create a project\n"
        f"{emoji_text('money')} File Limit: 5 MB per user",
        parse_mode="HTML"
    )

# ═══════════════════════════════════════════════════════════════
#                      🔘 CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await add_reaction(update, context)

    if query.data == "list_projects":
        await projects_list(update, context)
    elif query.data == "system_status":
        await monitor(update, context)
    elif query.data == "help":
        await help_cmd(update, context)

# ═══════════════════════════════════════════════════════════════
#                      👑 ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_allowed_user(user_id):
    return user_id in ALLOWED_USERS

def has_permission(user_id):
    return is_admin(user_id) or is_allowed_user(user_id)

def get_user_limit(user_id):
    return 5

def get_user_used(user_id):
    if str(user_id) in user_data:
        return user_data[str(user_id)].get('total_used', 0)
    return 0

def get_user_files(user_id):
    if str(user_id) in user_data:
        return user_data[str(user_id)].get('files', 0)
    return 0

def track_user_file(user_id, size_mb, filename):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {'limit_mb': 5, 'total_used': 0, 'files': 0, 'last_file': ''}
    user_data[uid]['total_used'] = user_data[uid].get('total_used', 0) + size_mb
    user_data[uid]['files'] = user_data[uid].get('files', 0) + 1
    user_data[uid]['last_file'] = filename
    save_user_data()

async def request_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_name = query.from_user.first_name
    username = query.from_user.username or "N/A"

    if has_permission(user_id):
        await query.edit_message_text(
            f"{emoji_text('check')} You already have access!",
            parse_mode="HTML"
        )
        return

    if str(user_id) in PENDING_USERS:
        await query.edit_message_text(
            f"{emoji_text('hourglass')} Request Already Sent",
            parse_mode="HTML"
        )
        return

    PENDING_USERS[str(user_id)] = {
        "name": user_name,
        "username": username,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    await query.edit_message_text(
        f"{emoji_text('check')} Access Request Sent!\n\n"
        f"{emoji_text('hourglass')} Admin will review your request.",
        parse_mode="HTML"
    )

    for admin_id in ADMIN_IDS:
        try:
            keyboard = admin_permission_keyboard(user_id)
            await context.bot.send_message(
                admin_id,
                f"{emoji_text('trophy')} New Access Request\n\n"
                f"🆔 User ID: {user_id}\n"
                f"👤 Name: {user_name}\n"
                f"🔰 Username: @{username}\n"
                f"📅 Requested: {PENDING_USERS[str(user_id)]['timestamp']}\n\n"
                f"{emoji_text('point_down')} Please approve or reject:",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except:
            pass

async def approve_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admin_id = query.from_user.id

    if not is_admin(admin_id):
        await query.answer("Not authorized!", show_alert=True)
        return

    data = query.data
    action, user_id_str = data.split("_")
    user_id = int(user_id_str)

    if action == "approve":
        if user_id not in ALLOWED_USERS:
            ALLOWED_USERS.append(user_id)
        if str(user_id) in PENDING_USERS:
            del PENDING_USERS[str(user_id)]

        await query.edit_message_text(
            f"{emoji_text('check')} Access Approved!",
            parse_mode="HTML"
        )

        try:
            await context.bot.send_message(
                user_id,
                f"{emoji_text('check')} Access Granted!\n\n"
                f"{emoji_text('game')} You can now use the bot.\n"
                f"📤 Send .py, .js or .zip files to create projects.\n"
                f"{emoji_text('money')} File Limit: 5 MB",
                parse_mode="HTML"
            )
        except:
            pass
    else:
        if str(user_id) in PENDING_USERS:
            del PENDING_USERS[str(user_id)]

        await query.edit_message_text(
            f"{emoji_text('cross')} Access Rejected!",
            parse_mode="HTML"
        )

        try:
            await context.bot.send_message(
                user_id,
                f"{emoji_text('cross')} Access Denied\n\n"
                f"{emoji_text('phone')} Contact admin for more info.",
                parse_mode="HTML"
            )
        except:
            pass

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Admin only!", parse_mode="HTML")
        return

    try:
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                f"{emoji_text('point_down')} Usage: /addus <user_id>\n\n"
                f"{emoji_text('money')} Example:\n"
                f"└ /addus 1234567890\n\n"
                f"{emoji_text('book')} Default limit is 5 MB per user",
                parse_mode="HTML"
            )
            return

        new_user_id = int(args[0])

        if new_user_id in ADMIN_IDS:
            await update.message.reply_text(f"{emoji_text('alarm')} This is an admin!", parse_mode="HTML")
            return

        if new_user_id in ALLOWED_USERS:
            await update.message.reply_text(
                f"{emoji_text('check')} User Already Exists\n\n"
                f"🆔 {new_user_id}\n"
                f"💾 Limit: 5 MB",
                parse_mode="HTML"
            )
            return

        ALLOWED_USERS.append(new_user_id)
        uid = str(new_user_id)
        if uid not in user_data:
            user_data[uid] = {'limit_mb': 5, 'total_used': 0, 'files': 0, 'last_file': ''}
            save_user_data()

        await update.message.reply_text(
            f"{emoji_text('check')} User Added\n\n"
            f"🆔 {new_user_id}\n"
            f"💾 File Limit: 5 MB",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"{emoji_text('cross')} Error: {str(e)}", parse_mode="HTML")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Admin only!", parse_mode="HTML")
        return

    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                f"{emoji_text('point_down')} Usage: /removeus <user_id>",
                parse_mode="HTML"
            )
            return

        remove_user_id = int(args[0])

        if remove_user_id in ADMIN_IDS:
            await update.message.reply_text(f"{emoji_text('cross')} Cannot remove admin!", parse_mode="HTML")
            return

        if remove_user_id not in ALLOWED_USERS:
            await update.message.reply_text(f"{emoji_text('alarm')} User not found!", parse_mode="HTML")
            return

        ALLOWED_USERS.remove(remove_user_id)
        if str(remove_user_id) in user_data:
            del user_data[str(remove_user_id)]
            save_user_data()

        await update.message.reply_text(
            f"{emoji_text('cross')} User Removed\n\n"
            f"🆔 {remove_user_id}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"{emoji_text('cross')} Error: {str(e)}", parse_mode="HTML")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Admin only!", parse_mode="HTML")
        return

    if not ALLOWED_USERS:
        await update.message.reply_text(
            f"{emoji_text('book')} User List\n\nNo users added yet!",
            parse_mode="HTML"
        )
        return

    user_list = ""
    for i, uid in enumerate(ALLOWED_USERS, 1):
        used = get_user_used(uid)
        files = get_user_files(uid)
        user_list += f"  {i}. {uid} - 💾 5MB | 📊 {used:.2f}MB | 📄 {files}\n"

    await update.message.reply_text(
        f"{emoji_text('book')} User List\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Total: {len(ALLOWED_USERS)}\n"
        f"💾 Limit: 5 MB per user\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{user_list}",
        parse_mode="HTML"
    )

async def set_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Admin only!", parse_mode="HTML")
        return

    await update.message.reply_text(
        f"{emoji_text('warning')} Note:\n\n"
        f"File limit is fixed at 5 MB per user.\n"
        f"Use /addus to add new users with 5 MB limit.",
        parse_mode="HTML"
    )

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(f"{emoji_text('cross')} Admin only!", parse_mode="HTML")
        return

    await add_reaction(update, context)
    await update.message.reply_text(
        f"{emoji_text('wave')} Stopping bot...\n\nGoodbye! 👋",
        parse_mode="HTML"
    )
    await asyncio.sleep(0.5)
    context.application.stop_running()
    os._exit(0)

# ═══════════════════════════════════════════════════════════════
#                      ❌ ERROR HANDLER
# ═══════════════════════════════════════════════════════════════

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# ═══════════════════════════════════════════════════════════════
#                      🚀 MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("🤖 TERMUX PYTHON & NODE.JS RUNNER - PROJECT MANAGER")
    print("=" * 60)
    print(f"👑 ADMIN IDs: {ADMIN_IDS}")
    print(f"👥 ALLOWED USERS: {len(ALLOWED_USERS)}")
    print(f"📁 DEFAULT LIMIT: 5 MB per user")
    print(f"📂 USER DATA: {len(user_data)} users")
    print(f"📁 PROJECTS: {len(pm.projects)}/3")
    print("=" * 60)
    print("📌 PREMIUM EMOJIS ENABLED")
    print("📌 5 ANIMATION TYPES")
    print("📌 REACTION: ⚡")
    print("📌 INFINITE RUNTIME")
    print("📌 AUTO PACKAGE INSTALLER (PIP / NPM)")
    print("📌 SUPPORT: PYTHON (.py), NODE.JS (.js) & ZIP (.zip)")
    print("📌 PROJECT MANAGER (MAX 3 PER USER)")
    print("📌 FILE LIMIT: 5 MB PER USER")
    print("=" * 60)

    app = Application.builder().token(BOT_TOKEN).build()

    loop = asyncio.get_event_loop()
    pm.set_loop(loop)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("projects", projects_list))
    app.add_handler(CommandHandler("run", run_project))
    app.add_handler(CommandHandler("stop", stop_project))
    app.add_handler(CommandHandler("delete", delete_project))
    app.add_handler(CommandHandler("monitor", monitor))
    app.add_handler(CommandHandler("myinfo", myinfo))
    app.add_handler(CommandHandler("help", help_cmd))

    app.add_handler(CommandHandler("addus", add_user))
    app.add_handler(CommandHandler("removeus", remove_user))
    app.add_handler(CommandHandler("listus", list_users))
    app.add_handler(CommandHandler("setlimit", set_limit))
    app.add_handler(CommandHandler("stopbot", stop_bot))

    app.add_handler(CallbackQueryHandler(request_access_callback, pattern="request_access"))
    app.add_handler(CallbackQueryHandler(approve_reject_callback, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(approve_reject_callback, pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="list_projects"))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="system_status"))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="help"))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.add_error_handler(error_handler)

    print("✅ BOT IS RUNNING!")
    print("📤 Send .py, .js or .zip files to create projects (Max 3 per user)")
    print("💾 File Limit: 5 MB per user")
    print("🔒 New users must request access via /start")
    print("💬 Send any text message to get reply + ⚡ reaction")
    print("⏱️ Scripts run FOREVER until stopped")
    print("=" * 60)

    app.run_polling()

if __name__ == "__main__":
    main()
