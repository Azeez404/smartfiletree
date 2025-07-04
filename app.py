import os
import csv
from bst_core import FileBST            
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory

bst = FileBST()

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # Needed for sessions

def is_valid_user(username, password, role):
    return all([username.strip(), password.strip(), role.strip()])

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'  # 👈 Force role as 'user' always

        if is_valid_user(username, password, role):
            with open('users.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([username, password, role])
            message = 'Signup successful! You can now log in.'
        else:
            message = 'All fields are required. Please try again.'

    return render_template('signup.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        with open('users.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 3:
                    csv_username, csv_password, csv_role = row
                    if username == csv_username.strip() and password == csv_password.strip():
                        session['username'] = csv_username
                        session['role'] = csv_role
                        return redirect('/dashboard')

        message = "❌ Invalid username or password!"

    return render_template('login.html', message=message)


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    role = session['role']

    if role == 'admin':
        return render_template('admin_dashboard.html', username=username)
    else:
        return render_template('user_dashboard.html', username=username)

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    message = None
    if request.method == 'POST':
        file = request.files['file']
        filename = request.form['filename']

        if file.filename == '':
            message = 'No file selected!'
        else:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # ✅ VERSIONING LOGIC
            version = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(full_path):
                version += 1
                filename = f"{base}_v{version}{ext}"
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # ✅ Save to local folder
            file.save(full_path)

            # ✅ Add to BST
            bst.root = bst.insert(bst.root, filename)

            # ❌ No cloud sync for now
            message = f"'{filename}' uploaded successfully!"

    return render_template('upload.html', message=message)

@app.route('/view')
def view_page():
    files = os.listdir(app.config['UPLOAD_FOLDER']) 
    return render_template('view.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    results = []
    keyword = ''

    if request.method == 'POST':
        keyword = request.form['keyword'].lower()

        if keyword:
            all_files = bst.inorder(bst.root)  # 👈 assumes BST has files
            results = [f for f in all_files if keyword in f.lower()]

            if not results:
                flash('No matching files found.')

    return render_template('search.html', results=results, keyword=keyword)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        bst.root = bst.delete(bst.root, filename)
        message = f"'{filename}' deleted successfully!"
    else:
        message = f"'{filename}' not found!"
    return redirect(url_for('view_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/manage_users')
def manage_users():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    users = []
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            users.append(row)
    return render_template('manage_users.html', users=users)


@app.route('/delete_user/<username>')
def delete_user(username):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    updated_users = []
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and len(row) == 3 and row[0] != username:
                updated_users.append(row)

    with open('users.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_users)

    return redirect('/manage_users')


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    updated_users = []

    with open('users.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] != username:
                updated_users.append(row)

    with open('users.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_users)

    session.clear()
    flash("Your account has been deleted successfully.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
