"""
Chargement du modèle .tflite et prédiction sur une image.

Tant que le modèle réel n'est pas entraîné/déployé dans models/,
ce module bascule automatiquement en MODE SIMULÉ (probabilités aléatoires
mais reproductibles) afin de permettre de développer et tester le reste
du pipeline (web, agrégation, fiche technique) sans attendre l'entraînement.

Dès que models/car_classifier_int8.tflite et data/labels.json (rempli)
sont présents, ce module utilisera automatiquement le vrai modèle.
"""

import json
import random
from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "car_classifier_int8.tflite"
LABELS_PATH = BASE_DIR / "data" / "labels.json"

# Résolution d'entrée attendue par le modèle (à ajuster selon l'architecture
# retenue à l'étape d'entraînement — MobileNetV3/EfficientNet-Lite tournent
# typiquement en 224x224).
INPUT_SIZE = (224, 224)


class ModelNotReadyError(Exception):
    """Levée si on essaie de forcer le mode réel sans modèle/labels disponibles."""


def _load_labels() -> list[str]:
    if not LABELS_PATH.exists():
        return []
    with open(LABELS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    # labels.json est un mapping {"0": "Peugeot 208", "1": "Volkswagen Golf", ...}
    # on le trie par index pour retrouver l'ordre des classes du modèle
    return [data[str(i)] for i in range(len(data))]


class CarClassifier:
    """
    Interface unique de reconnaissance, que le modèle soit réel ou simulé.
    Le reste du code (aggregator, main) ne dépend que de cette classe,
    jamais du détail TFLite vs mock.
    """

    def __init__(self):
        self.labels = _load_labels()
        self.real_model_available = MODEL_PATH.exists() and len(self.labels) > 0
        self._interpreter = None

        if self.real_model_available:
            self._load_real_model()
        else:
            # Pas de modèle entraîné pour l'instant : mode simulé.
            # On garde une liste de labels de secours pour pouvoir développer
            # le reste du pipeline (web, fiche) même sans labels.json rempli.
            if not self.labels:
                self.labels = ["Peugeot 208", "Volkswagen Golf", "Renault Clio"]

    def _load_real_model(self):
        try:
            from ai_edge_litert.interpreter import Interpreter, OpResolverType
        except ImportError:
            from tflite_runtime.interpreter import Interpreter, OpResolverType

        self._interpreter = Interpreter(model_path=str(MODEL_PATH))
        try:
            self._interpreter.allocate_tensors()
        except RuntimeError as e:
            print(f"[inference] Délégué XNNPACK indisponible ({e!r}), bascule sur les noyaux de référence.")
            self._interpreter = Interpreter(
                model_path=str(MODEL_PATH),
                experimental_op_resolver_type=OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES,
            )
            self._interpreter.allocate_tensors()

        self._input_details = self._interpreter.get_input_details()
        self._output_details = self._interpreter.get_output_details()

    def is_using_real_model(self) -> bool:
        return self._interpreter is not None

    def predict_probabilities(self, image_path: str) -> list[float]:
        """
        Retourne un vecteur de probabilités (une valeur par classe, même ordre que self.labels)
        pour l'image donnée.
        """
        if self._interpreter is not None:
            return self._predict_real(image_path)
        return self._predict_mock(image_path)

    def _predict_real(self, image_path: str) -> list[float]:
        img = Image.open(image_path).convert("RGB").resize(INPUT_SIZE)
        import numpy as np
        # Le modèle attend des pixels bruts (0-255) en uint8, exactement comme
        # à l'entraînement (MobileNetV3 normalise en interne) — pas de /255 ici.
        input_data = np.expand_dims(np.array(img, dtype=np.uint8), axis=0)

        self._interpreter.set_tensor(self._input_details[0]["index"], input_data)
        self._interpreter.invoke()
        output = self._interpreter.get_tensor(self._output_details[0]["index"])
        return output[0].tolist()

    def _predict_mock(self, image_path: str) -> list[float]:
        """
        Mode simulé : on vérifie juste que l'image est lisible (pour détecter
        un vrai bug de fichier corrompu), puis on génère des probabilités
        aléatoires mais reproductibles (seed basée sur le nom de fichier),
        pour que les tests soient stables.
        """
        img = Image.open(image_path).convert("RGB").resize(INPUT_SIZE)
        del img  # on ne s'en sert pas en mode mock, juste valider la lecture

        rng = random.Random(image_path)
        raw = [rng.random() for _ in self.labels]
        total = sum(raw)
        return [x / total for x in raw]
