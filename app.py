from datetime import datetime
import io
import base64
import uuid
import bcrypt
from pathlib import Path
import qrcode
from flask import Flask, render_template, request, jsonify, redirect, make_response, session, Response, url_for
from flask_babel import Babel, gettext as _
from db import get_db, init_db

app = Flask(__name__)
app.secret_key = "qr-secret-key-change-in-production"

try:
    _version = Path("VERSION").read_text().strip()
except OSError:
    _version = "dev"

print(f" * QR Generator {_version}")

SUPPORTED_LANGS = ["nl", "en", "fr", "de"]


def get_locale():
    if request.cookies.get("lang") in SUPPORTED_LANGS:
        return request.cookies.get("lang")
    return request.accept_languages.best_match(SUPPORTED_LANGS, default="en")


babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals["get_locale"] = get_locale


@app.context_processor
def inject_globals():
    try:
        version = Path("VERSION").read_text().strip()
    except OSError:
        version = "dev"
    return {"now": datetime.now(), "version": version}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def is_logged_in():
    return session.get("admin_logged_in") is True


@app.route("/lang/<lang>")
def set_lang(lang):
    resp = make_response(redirect(request.referrer or "/"))
    if lang in SUPPORTED_LANGS:
        resp.set_cookie("lang", lang, max_age=60*60*24*365)
    return resp


def make_qr_b64(data: str) -> str:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    qr_type = data.get("type")

    try:
        if qr_type == "url":
            payload = data["url"]

        elif qr_type == "sepa":
            iban = data["iban"].replace(" ", "").upper()
            bedrag = float(data.get("bedrag") or 0)
            bedrag_str = f"EUR{bedrag:.2f}" if bedrag > 0 else ""
            payload = "\n".join([
                "BCD", "002", "1", "SCT",
                data.get("bic", "").upper(),
                data["naam"][:70],
                iban,
                bedrag_str,
                "",
                "",
                data.get("mededeling", "")[:140],
                ""
            ])

        elif qr_type == "wifi":
            ssid = data["ssid"]
            password = data.get("password", "")
            security = data.get("security", "WPA")
            hidden = "true" if data.get("hidden") else "false"
            payload = f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden};;"

        elif qr_type == "vcard":
            vcard_id = str(uuid.uuid4())
            naam = data.get("naam", "")
            photo_b64 = data.get("photo", "")
            lines = [
                "BEGIN:VCARD", "VERSION:3.0",
                f"FN:{naam}",
                f"TEL:{data.get('tel', '')}",
                f"EMAIL:{data.get('email', '')}",
                f"URL:{data.get('url', '')}",
            ]
            if photo_b64:
                lines.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{photo_b64}")
            lines.append("END:VCARD")
            vcf_data = "\n".join(lines)

            with get_db() as conn:
                conn.execute(
                    "INSERT INTO vcards (id, naam, vcf_data, foto_b64) VALUES (?, ?, ?, ?)",
                    (vcard_id, naam, vcf_data, photo_b64 or None)
                )

            vcard_url = url_for("serve_vcard", vcard_id=vcard_id, _external=True)
            return jsonify({"image": make_qr_b64(vcard_url), "payload": vcard_url})

        elif qr_type == "text":
            payload = data["text"]

        else:
            return jsonify({"error": "Onbekend type"}), 400

        return jsonify({"image": make_qr_b64(payload), "payload": payload})

    except KeyError as e:
        return jsonify({"error": _(f"missing_field", field=str(e))}), 400


@app.route("/vcard/<vcard_id>")
def serve_vcard(vcard_id):
    with get_db() as conn:
        vc = conn.execute("SELECT * FROM vcards WHERE id = ?", (vcard_id,)).fetchone()
    if not vc:
        return "Not found", 404
    return render_template("vcard.html", naam=vc["naam"], foto_b64=vc["foto_b64"], id=vcard_id)


@app.route("/vcard/<vcard_id>/download")
def download_vcard(vcard_id):
    with get_db() as conn:
        vc = conn.execute("SELECT * FROM vcards WHERE id = ?", (vcard_id,)).fetchone()
    if not vc:
        return "Not found", 404
    return Response(
        vc["vcf_data"],
        mimetype="text/vcard",
        headers={"Content-Disposition": f"attachment; filename={vc['naam']}.vcf"}
    )


@app.route("/admin/setup", methods=["GET", "POST"])
def admin_setup():
    with get_db() as conn:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return redirect("/admin")
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            return render_template("setup.html", error=_("Fill in all fields"))
        with get_db() as conn:
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                         (username, hash_password(password)))
        return redirect("/admin")
    return render_template("setup.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if is_logged_in():
        return redirect("/admin")
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()
        if user and check_password(password, user["password_hash"]):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            return redirect("/admin")
        return render_template("login.html", error=_("Invalid credentials"))
    return render_template("login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/")


@app.route("/admin")
def admin():
    with get_db() as conn:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            return redirect("/admin/setup")
    if not is_logged_in():
        return redirect("/admin/login")
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM vcards ORDER BY aangemaakt_op DESC").fetchall()
    vcards = []
    for vc in rows:
        vcard_url = url_for("serve_vcard", vcard_id=vc["id"], _external=True)
        vcards.append({**dict(vc), "qr": make_qr_b64(vcard_url)})
    return render_template("admin.html", vcards=vcards)


@app.route("/admin/delete/<vcard_id>", methods=["POST"])
def admin_delete(vcard_id):
    if not is_logged_in():
        return redirect("/admin/login")
    with get_db() as conn:
        conn.execute("DELETE FROM vcards WHERE id = ?", (vcard_id,))
    return redirect("/admin")


@app.route("/health")
def health():
    return "ok"


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
