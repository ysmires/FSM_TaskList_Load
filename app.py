from flask import Flask, request, send_file, render_template, jsonify
import zipfile, io, openpyxl

app = Flask(__name__)

@app.after_request
def add_headers(response):
    # Nécessaire pour l'intégration dans l'iframe FSM Shell
    response.headers["X-Frame-Options"] = "ALLOWALL"
    response.headers["Content-Security-Policy"] = "frame-ancestors *"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/template")
def download_template():
    return send_file("static/template.xlsx",
                     as_attachment=True,
                     download_name="template.xlsx")

@app.route("/generate", methods=["POST"])
def generate():
    file = request.files.get("excel_file")
    if not file:
        return jsonify({"error": "Aucun fichier reçu"}), 400

    wb = openpyxl.load_workbook(file)
    sheet = wb.active

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("resultat.txt", f"Fichier Excel chargé !\nNombre de lignes : {sheet.max_row}")
        zf.writestr("info.txt", "Généré par l'extension FSM.")

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip",
                     as_attachment=True, download_name="resultat.zip")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
