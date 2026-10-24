from datetime import datetime
import io
import base64
from pathlib import Path
import qrcode
from flask import Flask, render_template, request, jsonify, redirect, make_response
from flask_babel import Babel, gettext as _

app = Flask(__name__)
app.secret_key = "qr-secret-key"

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
app.jinja_env.globals["now"] = datetime.now()


@app.context_processor
def inject_globals():
    try:
        version = Path("VERSION").read_text().strip()
    except OSError:
        version = "dev"
    return {"now": datetime.now(), "version": version}


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
            lines = [
                "BEGIN:VCARD", "VERSION:3.0",
                f"FN:{data.get('naam', '')}",
                f"TEL:{data.get('tel', '')}",
                f"EMAIL:{data.get('email', '')}",
                f"URL:{data.get('url', '')}",
            ]
            if data.get("photo"):
                lines.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{data['photo']}")
            lines.append("END:VCARD")
            payload = "\n".join(lines)

        elif qr_type == "text":
            payload = data["text"]

        else:
            return jsonify({"error": "Onbekend type"}), 400

        return jsonify({"image": make_qr_b64(payload), "payload": payload})

    except KeyError as e:
        return jsonify({"error": _("missing_field", field=str(e))}), 400


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
