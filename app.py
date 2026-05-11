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

@app.route("/appconfig.json")
def appconfig():
    # Endpoint requis par FSM pour l'installation manuelle de l'extension
    # FSM appelle https://ton-app.render.com/appconfig.json pour lire les métadonnées
    return send_file("static/appconfig.json", mimetype="application/json")

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

    # Contexte FSM transmis par le frontend
    # Renseigné automatiquement selon la source de connexion :
    #   - iframe FSM   → via REQUIRE_CONTEXT (SDK)
    #   - lien direct  → via query params de l'URL
    fsm_account    = request.form.get("fsm_account",   "")
    fsm_account_id = request.form.get("fsm_accountId", "")
    fsm_company    = request.form.get("fsm_company",   "")
    fsm_company_id = request.form.get("fsm_companyId", "")
    fsm_user       = request.form.get("fsm_user",      "")
    fsm_cloud_host = request.form.get("fsm_cloudHost", "")

    context_summary = (
        f"Compte      : {fsm_account} ({fsm_account_id})\n"
        f"Société     : {fsm_company} ({fsm_company_id})\n"
        f"Utilisateur : {fsm_user}\n"
        f"Cloud Host  : {fsm_cloud_host}\n"
    )

    print(f"[FSM] Génération demandée — {context_summary.strip()}")

    wb = openpyxl.load_workbook(file)
    sheet = wb.active

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr(
            "resultat.txt",
            f"Fichier Excel chargé !\n"
            f"Nombre de lignes : {sheet.max_row}\n\n"
            f"=== Contexte FSM ===\n{context_summary}"
        )
        zf.writestr("info.txt", "Généré par l'extension FSM.")

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip",
                     as_attachment=True, download_name="resultat.zip")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
