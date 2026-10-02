-- Schéma de la base de fiches techniques.
-- Une ligne par couple (marque, modèle) couvert par le classifieur.
-- Le champ `label` doit correspondre EXACTEMENT au texte présent dans labels.json,
-- car c'est la clé utilisée pour faire le lien reconnaissance -> fiche.

CREATE TABLE IF NOT EXISTS cars (
    label            TEXT PRIMARY KEY,   -- ex: "Peugeot 208"
    marque           TEXT NOT NULL,
    modele           TEXT NOT NULL,
    annees_prod      TEXT,               -- ex: "2019–présent" (texte libre, pas une année précise)
    carrosserie      TEXT,               -- ex: "Citadine", "SUV compact"
    motorisation      TEXT,               -- ex: "Essence / Diesel / Électrique / Hybride"
    cylindree_cm3    INTEGER,
    puissance_ch     INTEGER,
    nb_cylindres     INTEGER,
    couple_nm        INTEGER,
    transmission     TEXT,               -- ex: "Traction avant", "4 roues motrices"
    boite_vitesse    TEXT,               -- ex: "Manuelle 6 rapports", "Automatique"
    zero_a_cent_s    REAL,
    conso_l100km     REAL,
    notes            TEXT                -- texte libre, complément
);
