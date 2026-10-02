"""
Agrégation des prédictions de plusieurs photos d'un même véhicule.

Chaque photo passée dans le modèle produit un vecteur de probabilités
(une valeur par classe marque+modèle). Ce module combine ces vecteurs
pour donner une décision finale plus robuste qu'une seule photo isolée.
"""

from dataclasses import dataclass


@dataclass
class Prediction:
    label: str
    confidence: float  # entre 0 et 1


def aggregate_by_average(all_probabilities: list[list[float]], labels: list[str]) -> Prediction:
    """
    Fait la moyenne des probabilités sur toutes les photos, classe par classe,
    puis retourne le label ayant la moyenne la plus haute.

    all_probabilities : une liste de vecteurs de probabilités (un vecteur par photo),
                         chaque vecteur ayant la même longueur que `labels`.
    labels             : liste des labels correspondant à chaque indice de probabilité.
    """
    if not all_probabilities:
        raise ValueError("Aucune probabilité fournie — au moins une photo est requise")

    n_classes = len(labels)
    for probs in all_probabilities:
        if len(probs) != n_classes:
            raise ValueError(
                f"Vecteur de probabilités de taille {len(probs)}, attendu {n_classes}"
            )

    n_photos = len(all_probabilities)
    sums = [0.0] * n_classes
    for probs in all_probabilities:
        for i, p in enumerate(probs):
            sums[i] += p

    averages = [s / n_photos for s in sums]
    best_index = max(range(n_classes), key=lambda i: averages[i])

    return Prediction(label=labels[best_index], confidence=averages[best_index])


def aggregate_top_k(all_probabilities: list[list[float]], labels: list[str], k: int = 3) -> list[Prediction]:
    """
    Comme aggregate_by_average, mais retourne les k meilleures prédictions
    (triées par confiance décroissante) au lieu d'une seule -- utile pour
    laisser plusieurs chances quand le modèle hésite entre des modèles proches.
    """
    if not all_probabilities:
        raise ValueError("Aucune probabilité fournie — au moins une photo est requise")

    n_classes = len(labels)
    for probs in all_probabilities:
        if len(probs) != n_classes:
            raise ValueError(
                f"Vecteur de probabilités de taille {len(probs)}, attendu {n_classes}"
            )

    n_photos = len(all_probabilities)
    sums = [0.0] * n_classes
    for probs in all_probabilities:
        for i, p in enumerate(probs):
            sums[i] += p
    averages = [s / n_photos for s in sums]

    ranked_indices = sorted(range(n_classes), key=lambda i: averages[i], reverse=True)
    top_indices = ranked_indices[:k]

    return [Prediction(label=labels[i], confidence=averages[i]) for i in top_indices]


def aggregate_by_majority_vote(all_probabilities: list[list[float]], labels: list[str]) -> Prediction:
    """
    Chaque photo « vote » pour son label le plus probable (argmax individuel).
    Le label avec le plus de votes gagne ; en cas d'égalité, on retombe sur
    la confiance moyenne pour départager.
    """
    if not all_probabilities:
        raise ValueError("Aucune probabilité fournie — au moins une photo est requise")

    votes: dict[str, int] = {}
    confidences_per_label: dict[str, list[float]] = {}

    for probs in all_probabilities:
        best_index = max(range(len(probs)), key=lambda i: probs[i])
        label = labels[best_index]
        votes[label] = votes.get(label, 0) + 1
        confidences_per_label.setdefault(label, []).append(probs[best_index])

    max_votes = max(votes.values())
    tied_labels = [l for l, v in votes.items() if v == max_votes]

    if len(tied_labels) == 1:
        winner = tied_labels[0]
    else:
        # Égalité : on choisit celui avec la meilleure confiance moyenne
        winner = max(tied_labels, key=lambda l: sum(confidences_per_label[l]) / len(confidences_per_label[l]))

    avg_confidence = sum(confidences_per_label[winner]) / len(confidences_per_label[winner])
    return Prediction(label=winner, confidence=avg_confidence)
