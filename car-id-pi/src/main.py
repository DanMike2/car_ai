"""
Point d'entrée : petite interface web locale.

L'utilisateur upload une ou plusieurs photos d'un même véhicule depuis
son téléphone ou son PC (sur le réseau local), et obtient une fiche
descriptive affichée directement sur la page.

Lancement (depuis la racine du projet) :
    python3 src/main.py

Puis ouvrir http://<ip-du-pi>:5000 depuis un appareil du même réseau.
"""

import sys
import tempfile
from pathlib import Path

from flask import Flask, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent))  # pour les imports relatifs simples
from inference import CarClassifier
from aggregator import aggregate_top_k
from fiche_builder import build_fiches

app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parent.parent / "templates"),
)

# Le classifieur est chargé une seule fois au démarrage (pas à chaque requête,
# pour ne pas recharger le modèle à chaque photo envoyée).
classifier = CarClassifier()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", mock_mode=not classifier.is_using_real_model(), fiches=None, error=None)


@app.route("/identifier", methods=["POST"])
def identifier():
    files = request.files.getlist("photos")
    files = [f for f in files if f and f.filename]

    if not files:
        return render_template(
            "index.html",
            mock_mode=not classifier.is_using_real_model(),
            fiches=None,
            error="Aucune photo reçue — merci d'en sélectionner au moins une.",
        )

    all_probabilities = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        for f in files:
            tmp_path = Path(tmp_dir) / f.filename
            f.save(tmp_path)
            try:
                probs = classifier.predict_probabilities(str(tmp_path))
            except Exception as e:
                return render_template(
                    "index.html",
                    mock_mode=not classifier.is_using_real_model(),
                    fiches=None,
                    error=f"Erreur lors du traitement de « {f.filename} » : {e}",
                )
            all_probabilities.append(probs)

    top_predictions = aggregate_top_k(all_probabilities, classifier.labels, k=3)
    fiches = build_fiches(top_predictions)

    return render_template(
        "index.html",
        mock_mode=not classifier.is_using_real_model(),
        fiches=fiches,
        error=None,
    )


if __name__ == "__main__":
    # host="0.0.0.0" pour être accessible depuis d'autres appareils du réseau local
    app.run(host="0.0.0.0", port=5000, debug=True)
