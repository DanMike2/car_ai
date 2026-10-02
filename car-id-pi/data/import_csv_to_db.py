"""
Importe data/cars_template.csv (une fois rempli) dans data/cars.db.

Usage (depuis la racine du projet) :
    python3 data/import_csv_to_db.py

Remplace entièrement le contenu de la table `cars` à chaque exécution
(sûr de relancer autant de fois que nécessaire pendant que tu remplis
le CSV petit à petit).
"""

import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "cars_template.csv"
DB_PATH = BASE_DIR / "data" / "cars.db"
SCHEMA_PATH = BASE_DIR / "data" / "schema.sql"

# Colonnes numériques : converties en int/float, vides -> NULL
INT_COLUMNS = {"cylindree_cm3", "puissance_ch", "nb_cylindres", "couple_nm"}
FLOAT_COLUMNS = {"zero_a_cent_s", "conso_l100km"}


def parse_value(column: str, value: str):
    value = value.strip()
    if value == "":
        return None
    if column in INT_COLUMNS:
        try:
            return int(value)
        except ValueError:
            print(f"  ⚠️  valeur non numérique ignorée pour {column!r} : {value!r}")
            return None
    if column in FLOAT_COLUMNS:
        try:
            return float(value.replace(",", "."))  # tolère la virgule décimale française
        except ValueError:
            print(f"  ⚠️  valeur non numérique ignorée pour {column!r} : {value!r}")
            return None
    return value


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} introuvable -- lance d'abord generate_csv_template.py, "
            f"remplis le fichier, puis relance ce script."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(open(SCHEMA_PATH, encoding="utf-8").read())
    conn.execute("DELETE FROM cars")  # réimport propre à chaque exécution

    n_imported = 0
    n_skipped_empty = 0

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        for row in reader:
            # On considère une ligne "pas encore remplie" si tout, à part
            # label/marque/modele (déjà pré-remplis automatiquement), est vide.
            fields_to_check = [c for c in columns if c not in ("label", "marque", "modele")]
            if all(row[c].strip() == "" for c in fields_to_check):
                n_skipped_empty += 1
                continue

            values = {c: parse_value(c, row[c]) for c in columns}
            placeholders = ", ".join(["?"] * len(columns))
            conn.execute(
                f"INSERT INTO cars ({', '.join(columns)}) VALUES ({placeholders})",
                [values[c] for c in columns],
            )
            n_imported += 1

    conn.commit()
    conn.close()

    print(f"{n_imported} fiches importées dans cars.db")
    print(f"{n_skipped_empty} lignes pas encore remplies, ignorées (pas d'erreur)")


if __name__ == "__main__":
    main()
