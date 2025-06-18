from flask import Flask, request, render_template_string, redirect, url_for, session, send_from_directory, flash
import os
import json
import rsa

app = Flask(__name__)
app.secret_key = 'your_secret_key_123456789'
UPLOAD_FOLDER = 'uploads'
USER_FILE = 'users.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

# Template cha
layout = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <style>
        body { font-family: Arial; margin: 40px;}
        .container { padding: 20px; border-radius: 10px; background: #fafafa; width: 470px; margin: auto;}
        input[type=file], input[type=submit], input[type=text], input[type=password], select { margin: 10px 0;}
        .info { color: green; }
        .err { color: red; }
    </style>
</head>
<body>
    <div class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="{{category}}">{{message}}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
'''

# Đăng ký
register_html = '''
    <h2>Đăng ký tài khoản</h2>
    <form method="post" enctype="multipart/form-data">
        <label>Tên đăng nhập:</label><br>
        <input type="text" name="username" required><br>
        <label>Mật khẩu:</label><br>
        <input type="password" name="password" required><br>
        <label>Upload Public Key (public.pem):</label><br>
        <input type="file" name="pubkey" required><br>
        <input type="submit" value="Đăng ký">
    </form>
    <a href="{{url_for('login')}}">Đã có tài khoản? Đăng nhập</a>
</div>
</body>
</html>
'''

# Đăng nhập
login_html = '''
    <h2>Đăng nhập</h2>
    <form method="post">
        <label>Tên đăng nhập:</label><br>
        <input type="text" name="username" required><br>
        <label>Mật khẩu:</label><br>
        <input type="password" name="password" required><br>
        <input type="submit" value="Đăng nhập">
    </form>
    <a href="{{url_for('register')}}">Chưa có tài khoản? Đăng ký</a>
</div>
</body>
</html>
'''

# Gửi file (chọn người nhận)
upload_html = '''
    <h2>Chào, {{username}}! Gửi file có ký số</h2>
    <form method="post" enctype="multipart/form-data">
        <label>Chọn người nhận:</label><br>
        <select name="receiver" required>
            {% for u in userlist %}
                {% if u != username %}
                <option value="{{u}}">{{u}}</option>
                {% endif %}
            {% endfor %}
        </select><br>
        <label>File dữ liệu:</label><br>
        <input type="file" name="file" required><br>
        <label>File chữ ký số:</label><br>
        <input type="file" name="signature" required><br>
        <input type="submit" value="Gửi file">
    </form>
    <a href="{{url_for('files')}}">Xem file đã gửi & nhận</a> | 
    <a href="{{url_for('logout')}}">Đăng xuất</a>
</div>
</body>
</html>
'''

# Danh sách file (phân biệt gửi/nhận)
files_html = '''
    <h2>File bạn gửi cho người khác</h2>
    <ul>
    {% for f in sent %}
        <li>
            Đến <b>{{f['receiver']}}</b>: {{f['name']}}
            [<a href="{{url_for('download', filename=f['file'])}}">Tải file</a>]
            [<a href="{{url_for('download', filename=f['sig'])}}">Tải chữ ký</a>]
        </li>
    {% endfor %}
    </ul>
    <h2>File bạn nhận từ người khác</h2>
    <ul>
    {% for f in received %}
        <li>
            Từ <b>{{f['sender']}}</b>: {{f['name']}}
            [<a href="{{url_for('download', filename=f['file'])}}">Tải file</a>]
            [<a href="{{url_for('download', filename=f['sig'])}}">Tải chữ ký</a>]
            [<a href="{{url_for('check', filename=f['file'])}}">Kiểm tra chữ ký</a>]
        </li>
    {% endfor %}
    </ul>
    <a href="{{url_for('upload')}}">Quay lại gửi file</a>
</div>
</body>
</html>
'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pubkey = request.files['pubkey']
        users = load_users()
        if username in users:
            flash("Tên đăng nhập đã tồn tại", "err")
        else:
            pubkey_path = os.path.join(UPLOAD_FOLDER, f'{username}_public.pem')
            pubkey.save(pubkey_path)
            users[username] = {'password': password, 'pubkey': pubkey_path}
            save_users(users)
            flash("Đăng ký thành công! Vui lòng đăng nhập.", "info")
            return redirect(url_for('login'))
    return render_template_string(layout + register_html, title="Đăng ký")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('upload'))
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "err")
    return render_template_string(layout + login_html, title="Đăng nhập")

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Đã đăng xuất", "info")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    users = load_users()
    userlist = list(users.keys())
    if request.method == 'POST':
        username = session['user']
        receiver = request.form['receiver']
        f1 = request.files['file']
        f2 = request.files['signature']
        # File lưu dạng: sender_receiver_filename
        filename = f"{username}_{receiver}_{f1.filename}"
        sigfile = f"{username}_{receiver}_sig_{f1.filename}.bin"
        f1.save(os.path.join(UPLOAD_FOLDER, filename))
        f2.save(os.path.join(UPLOAD_FOLDER, sigfile))
        flash(f"Đã gửi file cho {receiver}!", "info")
    return render_template_string(layout + upload_html, username=session['user'], userlist=userlist, title="Gửi file")

@app.route('/files')
def files():
    if 'user' not in session:
        return redirect(url_for('login'))
    files = os.listdir(UPLOAD_FOLDER)
    sent = []
    received = []
    username = session['user']
    for f in files:
        # Gửi: username_receiver_filename (và không phải signature file)
        if f.startswith(username+'_') and not '_sig_' in f and not f.endswith('_public.pem'):
            receiver = f.split('_')[1]
            sigf = f.replace(f"_{receiver}_", f"_{receiver}_sig_") + ".bin"
            sent.append({'receiver': receiver, 'name': f.split('_',2)[2], 'file': f, 'sig': sigf})
        # Nhận: sender_username_filename (và không phải signature file)
        elif f"_{username}_" in f and not '_sig_' in f and not f.startswith(username+'_') and not f.endswith('_public.pem'):
            sender = f.split('_')[0]
            sigf = f.replace(f"_{username}_", f"_{username}_sig_") + ".bin"
            received.append({'sender': sender, 'name': f.split('_',2)[2], 'file': f, 'sig': sigf})
    return render_template_string(layout + files_html, sent=sent, received=received, title="File đã gửi/nhận")

@app.route('/uploads/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/check/<filename>')
def check(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    # filename = sender_receiver_filename
    parts = filename.split('_', 2)
    sender = parts[0]
    receiver = parts[1]
    # Dùng public key của người gửi
    users = load_users()
    pubkey_path = users[sender]['pubkey']
    sigfile = f"{sender}_{receiver}_sig_{parts[2]}.bin"
    data_path = os.path.join(UPLOAD_FOLDER, filename)
    sig_path = os.path.join(UPLOAD_FOLDER, sigfile)
    try:
        with open(pubkey_path, 'rb') as f:
            pubkey = rsa.PublicKey.load_pkcs1(f.read())
        with open(data_path, 'rb') as f:
            data = f.read()
        with open(sig_path, 'rb') as f:
            signature = f.read()
        rsa.verify(data, signature, pubkey)
        flash("✅ Chữ ký số HỢP LỆ! File này đúng do người gửi ký.", "info")
    except Exception as e:
        flash(f"❌ Chữ ký số KHÔNG hợp lệ hoặc thiếu file! ({e})", "err")
    return redirect(url_for('files'))

if __name__ == '__main__':
    app.run(debug=True)
