from flask import (
    Flask, flash, render_template, request, redirect, url_for, make_response, jsonify
)

from auth import check_password_hash, create_session, hash_password
from config import Config
from database import get_db, MongoDBConnection, get_user_from_session
from logger import logger
import json
from auth import require_auth, generate_numeric_code, logout_user
import uuid
from note import Note
from mailer import Mailer
import pprint

# =============================================================================
# AUTHENTICATION & USER MANAGEMENT - ROUTES
# =============================================================================
def register_auth_handlers(app: Flask):
    @app.route("/login", methods=["GET", "POST"])
    @app.route("/register", methods=["GET", "POST"])
    def login_or_register():
        if request.method == "POST":
            if request.base_url.split("/")[-1] == "login":
                username_or_email = request.form.get("username_or_email")
                password = request.form.get("password")

                # Proper parameter duplication for both username and email
                user = get_db().execute_query(
                    "SELECT * FROM users WHERE username=%s OR email=%s",
                    (username_or_email, username_or_email), True
                )

                if not user or not check_password_hash(user['password'], password):
                    flash("Credentials not valid or user does not exist.", "error")
                    return redirect("/login")
                
                if user["is_mfa_enabled"]:
                    otp_secret = generate_numeric_code()
                    get_db().execute_query("INSERT INTO mfa_tokens(user_id, mfa_secret) VALUES(%s, %s)", (user["id"],otp_secret))
                    Mailer().send_mail("Your 2FA Code",render_template("2fa_mail.html",otp_secret=otp_secret, username=user["username"]),Mailer().username,user["email"],html=True)

                session_cookie = create_session(user["id"], not user["is_mfa_enabled"])
                resp = make_response(redirect(url_for("index")))
                resp.set_cookie("session_cookie", session_cookie, max_age=Config.MAX_COOKIE_LIFETIME, path="/")
                return resp

            elif request.base_url.split("/")[-1] == "register":
                id = str(uuid.uuid4())
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")

                user = get_db().execute_query(
                    "SELECT id FROM users WHERE username=%s OR email=%s", (username,email), True
                )

                if user:
                    flash("User already exists.", "error")
                    return redirect("/register")
                    

                hashed_pw = hash_password(password)

                get_db().execute_query(
                    "INSERT INTO users (id, username, email, password) VALUES (%s, %s, %s, %s)",
                    (id, username, email, hashed_pw), True
                )   

                session_cookie = create_session(id, True)
                resp = make_response(redirect(url_for("index")))
                resp.set_cookie("session_cookie", session_cookie, max_age=Config.MAX_COOKIE_LIFETIME, path="/")
                return resp

        return render_template("login.html")

    @app.route("/mfa",methods=["GET","POST"])
    def mfa():
        if request.method=="POST":
            session_cookie = request.cookies.get("session_cookie")
            session_data = get_db().execute_query("SELECT * FROM sessions WHERE session_token = %s", (session_cookie,), True)
            if session_data and session_data["valid"]:
                return redirect(url_for("index"))

            mfa_code = request.form.get("mfa-code")
            user = get_db().execute_query("""SELECT user_id FROM mfa_tokens WHERE is_valid = 1 AND mfa_secret = %s """, (mfa_code,), True)
            if user:
                get_db().execute_query("UPDATE mfa_tokens SET is_valid = 0 WHERE user_id=%s", (user["user_id"],))
                get_db().execute_query("UPDATE sessions SET valid = 1 WHERE user_id=%s", (user["user_id"],))
                return redirect(url_for("index"))

        return render_template("MFA.html")

    @app.route("/verify-email",methods=["GET"])
    def verify_email():    
        pass

    @app.route("/reset-password" ,methods=["GET"])
    def reset_password():
        token = request.args.get('token')
        if not token or not get_db().execute_query(
                    "SELECT * FROM reset_password WHERE reset_token=%s",
                    (token,), True
                ): return redirect("/login")
        return render_template("reset-password.html", token=token)
    
    @app.route("/logout", methods=["GET"])
    def logout():
        return logout_user()
    

# =============================================================================
# MAIN ROUTES
# =============================================================================
def register_user_handlers(app: Flask):
    @app.route("/", methods=["GET", "POST"])
    @app.route("/<string:id>", methods=["GET", "POST"])
    @require_auth
    def index(id=""):
        session_cookie = request.cookies.get('session_cookie')
        user_id = get_user_from_session(session_cookie)['id']
        
        saved_data = ''
        title = ''
        note_id = ''
        PublicRead = False

        print(f"Site ID: {id}")

        if id == "getting-started":
            saved_data= Config.GETTING_STARTED
            title = 'Welcome to Notes.io'
            note_id = 'getting-started'

        

        if id:
            db = MongoDBConnection().collection
            note = db.find_one({"_id": id, "ownerId": user_id})

            if note:
                try:
                    saved_data = json.loads(note.get("contentJson", "{}"))
                    title = note.get("title")
                    note_id =note.get("_id")
                    PublicRead=note.get("publicRead")
                    print(f"Note found: {note_id}, PublicRead: {PublicRead}")
                except Exception as e:
                    print(f"Failed to parse contentJson: {e}")
                    saved_data = ''

        return render_template("index.html", saved_json=json.dumps(saved_data) , title= title , note_id= note_id, PublicRead=PublicRead)

    @app.route("/settings", methods=["GET"])
    @require_auth
    def settings():
        session_cookie = request.cookies.get("session_cookie")
        user_data = get_user_from_session(session_cookie)
        return render_template("settings.html", user_data=user_data)
    
    @app.route("/shared/<string:id>", methods=["GET"])
    def shared_note(id: str):
        """View a shared note by ID."""
        db = MongoDBConnection().collection
        note = db.find_one({"_id": id})

        if not note or not note.get("publicRead"):
            return redirect('/')

        try:
            saved_data = json.loads(note.get("contentJson", "{}"))
            title = note.get("title")
        except Exception as e:
            logger.error(f"Failed to parse contentJson for note {id}: {e}")
            saved_data = {}

        return render_template("GuestNote.html", saved_json=json.dumps(saved_data), title=title, note_id=id)

    
# =============================================================================
# ERROR HANDLERS
# =============================================================================

def register_error_handlers(app: Flask):
    """Register application error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('error.html', error="Internal server error"), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error.html', error="Access forbidden"), 403

    @app.route("/quaranitine")
    def quaranitine():
        pass
