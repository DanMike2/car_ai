"""
Génère data/cars_template.csv, déjà rempli à partir des estimations de
specs_data.py (une génération représentative par modèle, cf. notes du
fichier). Tu peux ensuite corriger/affiner directement dans le tableur.

Usage (depuis la racine du projet) :
    python3 data/generate_filled_csv.py
"""

import csv
import json
from pathlib import Path

from specs_data import SPECS

BASE_DIR = Path(__file__).resolve().parent.parent
LABELS_PATH = BASE_DIR / "data" / "labels.json"
OUTPUT_PATH = BASE_DIR / "data" / "cars_template.csv"

COLUMNS = [
    "label", "marque", "modele", "annees_prod", "carrosserie", "motorisation",
    "cylindree_cm3", "puissance_ch", "nb_cylindres", "couple_nm",
    "transmission", "boite_vitesse", "zero_a_cent_s", "conso_l100km", "notes",
]

SPEC_FIELDS = [
    "annees_prod", "carrosserie", "motorisation", "cylindree_cm3",
    "puissance_ch", "nb_cylindres", "couple_nm", "transmission",
    "boite_vitesse", "zero_a_cent_s", "conso_l100km", "notes",
]


def guess_marque_modele(label: str) -> tuple[str, str]:
    parts = label.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return label, ""


def main():
    labels = json.load(open(LABELS_PATH, encoding="utf-8"))
    ordered_labels = [labels[str(i)] for i in range(len(labels))]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for label in ordered_labels:
            marque, modele = guess_marque_modele(label)
            spec_values = SPECS.get(label)
            if spec_values is None:
                row = [label, marque, modele] + [""] * len(SPEC_FIELDS)
            else:
                row = [label, marque, modele] + list(spec_values)
            writer.writerow(row)

    print(f"{len(ordered_labels)} lignes écrites dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
