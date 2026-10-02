# car-id-pi

IA locale de reconnaissance automobile sur Raspberry Pi 5.
Identifie la marque et le modèle d'une voiture à partir de photos,
puis génère une fiche descriptive (caractéristiques moteur, etc.).

## Structure
- `src/` : code d'inférence et de génération de fiche
- `models/` : modèle .tflite entraîné (déposé après entraînement)
- `data/` : base de fiches techniques (cars.db) et labels du classifieur
- `scripts/` : prétraitement des images
- `training/` : notebook d'entraînement (à exécuter sur Google Colab, pas sur le Pi)

## Installation
