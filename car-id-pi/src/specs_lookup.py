"""
Recherche des caractéristiques techniques d'un véhicule à partir de son label
("Marque Modèle"), dans la base SQLite data/cars.db.
"""

import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cars.db"

# Colonnes de la table `cars`, dans l'ordre où on veut les présenter à l'utilisateur.
DISPLAY_FIELDS = [
    ("marque", "Marque"),
    ("modele", "Modèle"),
    ("annees_prod", "Années de production"),
    ("carrosserie", "Carrosserie"),
    ("motorisation", "Motorisation"),
    ("cylindree_cm3", "Cylindrée (cm³)"),
    ("puissance_ch", "Puissance (ch)"),
    ("nb_cylindres", "Nombre de cylindres"),
    ("couple_nm", "Couple (Nm)"),
    ("transmission", "Transmission"),
    ("boite_vitesse", "Boîte de vitesse"),
    ("zero_a_cent_s", "0 à 100 km/h (s)"),
    ("conso_l100km", "Consommation (L/100km)"),
    ("notes", "Notes"),
]


class SpecsNotFoundError(Exception):
    """Levée quand un label n'a pas (ou pas encore) de fiche dans la base."""


def get_specs(label: str) -> dict:
    """
    Retourne les caractéristiques du véhicule identifié par `label`
    (doit correspondre exactement à une entrée de labels.json et de la colonne `label` de cars.db).

    Lève SpecsNotFoundError si aucune fiche n'existe pour ce label
    (typiquement : la base n'a pas encore été complétée pour ce modèle).
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Base introuvable : {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM cars WHERE label = ?", (label,)).fetchone()
    finally:
        conn.close()

    if row is None:
        raise SpecsNotFoundError(f"Aucune fiche technique trouvée pour « {label} »")

    return dict(row)


def format_specs_for_display(specs: dict) -> list[tuple[str, str]]:
    """
    Transforme le dict brut de la base en liste de paires (libellé, valeur)
    prêtes à être affichées, en ignorant les champs vides/nuls.
    """
    result = []
    for key, human_label in DISPLAY_FIELDS:
        value = specs.get(key)
        if value is None or value == "":
            continue
        result.append((human_label, str(value)))
    return result


def get_known_labels() -> list[str]:
    """Retourne la liste des labels actuellement couverts par la base (utile pour les tests)."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT label FROM cars ORDER BY label").fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]
