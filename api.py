from flask import Flask, request, jsonify, render_template
from database import get_db, MongoDBConnection, get_user_from_session
from auth import require_auth
from mailer import Mailer
import requests
import re
import uuid
import secrets
from datetime import datetime
from auth import hash_password
from utility import update_user_field
from flask import send_from_directory
from os import path

# =============================================================================
# APIs
# =============================================================================
def register_api_handlers(app: Flask):

    @app.route("/api/fetchUrl", methods=["GET"])
    @require_auth
    def api_fetch_url():
        url = request.args.get("url")

        if not url or not url.strip():
            return jsonify({"success": 0, "error": "Missing URL"}), 400

        try:
            resp = requests.get(url)
            resp.raise_for_status()
            html = resp.text

            title_match = re.search(r"<title.*?>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""

            desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else "No description available."

            img_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
            image_url = img_match.group(1).strip() if img_match else "https://via.placeholder.com/300x150"

            return jsonify({
                "success": 1,
                "link": url,
                "meta": {
                    "title": title,
                    "description": description,
                    "image": {"url": image_url}
                }
            })
        except Exception as ex:
            return jsonify({
                "success": 0,
                "error": "Failed to fetch URL",
                "message": str(ex)
            })
        
    @app.route("/api/sendResetToken", methods=["POST"])
    def api_send_reset_token():
        username_or_email = request.form.get("username_or_email")
        user = get_db().execute_query(
                    "SELECT * FROM users WHERE username=%s OR email=%s",
                    (username_or_email, username_or_email), True
                )
        if not user:
            return jsonify({"success": 0, "message": "User not found!"}), 400
        
        temp = get_db().execute_query(
                    "DELETE FROM reset_password WHERE id=%s;",
                    (user['id'],), True
                )
        
        try:
            token = secrets.token_urlsafe(32)
            reset_link = f"http://127.0.0.1:5000/reset-password?token={token}"
            mailer = Mailer()
            subject = "Notes.io | Password Reset Requested"
            body = render_template("reset_password_mail.html", username=user["username"], reset_link=reset_link)
            from_address = mailer.username
            recipients = [user['email']]
            mailer.send_mail(subject, body, from_address, recipients,True)

            temp = get_db().execute_query(
                    "INSERT INTO reset_password (id, reset_token, created_at) VALUES (%s, %s, %s);",
                    ((user['id']), (token), datetime.now()), True
                )

            return jsonify({"success": 1, "message": "Reset link has been sent!" }), 200
                
        except Exception as ex:
            print(ex)
            return jsonify({"success": 0, "message": "Something Wrong Occured!"}), 400
        
    @app.route("/api/reset-password", methods=["POST"])
    def api_reset_password():
        token = request.form.get("token")
        password = request.form.get("password")

        id = get_db().execute_query(
                    "SELECT * FROM reset_password WHERE reset_token=%s",
                    (token,), True
                )['id']
        
        if not id: return jsonify({"success": 0, "message": "Something Wrong Occured!"}), 400

        try:
            get_db().execute_query(
                    "UPDATE users SET password= %s WHERE id= %s;",
                    ((hash_password(password)), (id)), True
                    )
            get_db().execute_query(
                    "DELETE FROM reset_password WHERE id=%s;",
                    (id,), True
                )

            return jsonify({"success": 1, "message": "Your Password has been Updated!" }), 200
        
        except Exception as ex:         
            print(ex)
            return jsonify({"success": 0, "message": "Something Wrong Occured!"}), 400
        
    
    @app.route("/api/handle-note", methods=["POST"])
    @require_auth
    def api_handle_note():

        session_cookie = request.cookies.get('session_cookie')
        user_id = get_user_from_session(session_cookie)['id']

        db = MongoDBConnection().collection
        
        data = request.get_json()
        action = data.get("action")
        note_data = data.get("note")

        if not action:
            return jsonify({"error": "Missing 'action' in request"}), 400

        # ---------- CREATE ----------
        if action == "create":
            note_id = str(uuid.uuid4())
            new_note = {
                "_id": note_id,  # Set _id as UUID string
                "title": 'New Note',
                "contentJson": '{}',
                "ownerId": user_id,
                "publicRead": note_data.get("publicRead", False),
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }

            db.insert_one(new_note)

            # Return clean note object
            response_note = {
                "id": note_id,
                "title": new_note["title"],
                "contentJson": new_note["contentJson"],
                "ownerId": new_note["ownerId"],
                "publicRead": new_note["publicRead"],
                "createdAt": new_note["createdAt"].isoformat(),
                "updatedAt": new_note["updatedAt"].isoformat()
            }

            return jsonify({"status": "created", "note": response_note}), 201

        # ---------- UPDATE ----------
        elif action == "update":
            note_id = note_data.get("id")
            if not note_id:
                return jsonify({"error": "Missing 'id' for update"}), 400

            # Ensure the note exists and belongs to the user
            existing_note = db.find_one({"_id": note_id, "ownerId": user_id})
            if not existing_note:
                return jsonify({"error": "Note not found"}), 404

            updated_note = db.find_one_and_update(
                {"_id": note_id},
                {
                    "$set": {
                        "title": note_data.get("title", ""),
                        "contentJson": note_data.get("contentJson", "{}"),
                        "publicRead": note_data.get("publicRead", False),
                        "updatedAt": datetime.utcnow()
                    }
                },
                return_document=True
            )

            if updated_note:
                response_note = {
                    "id": updated_note["_id"],
                    "title": updated_note["title"],
                    "contentJson": updated_note["contentJson"],
                    "ownerId": updated_note.get("ownerId", "guest"),
                    "publicRead": updated_note.get("publicRead", False),
                    "createdAt": updated_note["createdAt"].isoformat(),
                    "updatedAt": updated_note["updatedAt"].isoformat()
                }
                return jsonify({"status": "updated", "note": response_note}), 200
        # ---------- DELETE ----------
        elif action == "delete":
            if db.find({'_id': data.get("note").get("id"), 'ownerId': user_id }):
                note_id = note_data.get("id")
                if not note_id:
                    return jsonify({"error": "Missing 'id' for delete"}), 400

                result = db.delete_one({"_id": note_id})
                if result.deleted_count > 0:
                    return jsonify({"status": "deleted"}), 200
            else:
                return jsonify({"error": "Note not found"}), 404
            
        # ---------- LIST ----------
        elif action == "list":
            # owner_id = note_data.get("ownerId")
            # if not owner_id:
            #     return jsonify({"error": "Missing 'ownerId' for listing notes"}), 400

            notes = db.find(
                {"ownerId": user_id},
                {"_id": 1, "title": 1, "updatedAt": 1}  # include updatedAt for sorting
            )


            result = [{
                "id": note["_id"],
                "title": note.get("title", ""),
                "updatedAt": note.get("updatedAt", datetime.min).isoformat()
            } for note in notes]

            return jsonify({"status": "success", "notes": result}), 200
        
         # ---------- GET ----------
        elif action == "get":
            if db.find({'_id': data.get("note").get("id"), 'ownerId': user_id }): #Security
                note_id = note_data.get("id")
                if not note_id:
                    return jsonify({"error": "Missing 'id' for get"}), 400

                note = db.find_one({"_id": note_id})
                if not note:
                    return jsonify({"error": "Note not found"}), 404

                response_note = {
                    "id": note["_id"],
                    "title": note.get("title", ""),
                    "contentJson": note.get("contentJson", "{}"),
                    "ownerId": note.get("ownerId", "guest"),
                    "publicRead": note.get("publicRead", False),
                    "createdAt": note.get("createdAt", datetime.utcnow()).isoformat(),
                    "updatedAt": note.get("updatedAt", datetime.utcnow()).isoformat()
                }

                return jsonify({"status": "success", "note": response_note}), 200

        # ---------- Invalid Action ----------
        else:
            return jsonify({"error": f"Unsupported action '{action}'"}), 400
        
    @app.route("/api/update_mfa",methods=["POST"])
    @require_auth
    def update_mfa():
        user_data=get_user_from_session(request.cookies.get("session_cookie"))
        data = request.get_json()
        enabled = data.get("enabled")
        update_user_field(user_data["id"],'is_mfa_enabled', enabled)

        return jsonify({"success":True})
    

    @app.route("/api/update_user_settings",methods=["POST"])
    @require_auth
    def update_user_settings():
        user_data=get_user_from_session(request.cookies.get("session_cookie"))
        data = request.get_json()
        for key in data.keys():
            user = get_db().execute_query(
                    f"SELECT id FROM users WHERE {key}=%s", (data[key],), True
                )
            if not user:
                update_user_field(user_data["id"], key, data[key])
            else:
                return jsonify({"success":False})        

        return jsonify({"success":True})
    
    @app.route("/favicon.ico",methods=["GET"])
    def favicon():
        return send_from_directory(
        path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/x-icon')
        
