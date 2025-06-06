import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY", "securekey123")

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)

users = {"admin": generate_password_hash("adminpass")}

class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route("/", methods=["GET"])
def home():
    if current_user.is_authenticated:
        return redirect("/dashboard")
    return "<h1>NextGen AI Day Trader</h1><p><a href='/login'>Login</a></p>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user in users and check_password_hash(users[user], pwd):
            login_user(User(user))
            return redirect("/dashboard")
        return "Invalid login"
    return render_template_string("""
    <form method='POST'>
        <input name='username' placeholder='Username'>
        <input type='password' name='password' placeholder='Password'>
        <button type='submit'>Login</button>
    </form>
    """)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    symbols = session.get("symbols", ["AAPL", "MSFT"])
    charts = "".join([
        f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={s}&interval=D&theme=light&style=1&timezone=Etc%2FUTC&withdateranges=1' width='600' height='400' frameborder='0'></iframe><br>"
        for s in symbols])
    return render_template_string(f"""<html><body>
        <h2>📈 {current_user.username}'s Trading Dashboard</h2>
        {charts}
        <form method='POST' action='/update_symbols'>
            <input name='symbols' placeholder='Comma-separated symbols (e.g., AAPL,NVDA)'>
            <button type='submit'>Update Symbols</button>
        </form>
        <p><a href='/logout'>Logout</a></p>
    </body></html>""")

@app.route("/update_symbols", methods=["POST"])
@login_required
def update_symbols():
    raw = request.form.get("symbols", "")
    cleaned = [s.strip().upper() for s in raw.split(",") if s.strip()]
    session["symbols"] = cleaned
    return redirect("/dashboard")

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
