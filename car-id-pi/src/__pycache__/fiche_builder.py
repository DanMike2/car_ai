"""
Assemble le résultat de la reconnaissance (label + confiance) avec les
caractéristiques techniques (specs_lookup) en une fiche prête à afficher.
"""

from dataclasses import dataclass, field

from aggregator import Prediction
from specs_lookup import get_specs, format_specs_for_display, SpecsNotFoundError


@dataclass
class Fiche:
    label: str
    confidence: float
    specs_found: bool
    specs: list[tuple[str, str]] = field(default_factory=list)
    warning: str = ""


def build_fiche(prediction: Prediction) -> Fiche:
    """
    À partir d'une Prediction (label + confiance issus de l'agrégation),
    construit la fiche finale à afficher sur le mini site.

    Si aucune fiche technique n'existe encore pour ce label dans cars.db,
    la fiche est quand même renvoyée (avec l'identification), mais
    `specs_found` est False et un message d'avertissement est inclus —
    plutôt que de faire planter la requête.
    """
    try:
        specs = get_specs(prediction.label)
        return Fiche(
            label=prediction.label,
            confidence=prediction.confidence,
            specs_found=True,
            specs=format_specs_for_display(specs),
        )
    except SpecsNotFoundError:
        return Fiche(
            label=prediction.label,
            confidence=prediction.confidence,
            specs_found=False,
            warning=(
                f"Véhicule identifié comme « {prediction.label} », mais aucune fiche "
                f"technique n'est encore renseignée pour ce modèle dans la base."
            ),
        )


def build_fiches(predictions: list[Prediction]) -> list[Fiche]:
    """Construit une fiche par prédiction (ex. top-3) -- même logique que build_fiche, en lot."""
    return [build_fiche(p) for p in predictions]
