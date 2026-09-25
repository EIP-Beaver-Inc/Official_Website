"""Static reference data — BEAVER pipeline + EN 975-1 norm."""
from typing import List, Dict


DEFECT_CLASSES: List[Dict] = [
    {"key": "noeud_vif",          "name": "Nœud vif",          "impact": "Mineur",       "description": "Nœud sain, adhérent, issu d'une branche vivante au moment de l'abattage. Bonne intégration mécanique.", "status": "live"},
    {"key": "noeud_mort",         "name": "Nœud mort",         "impact": "Modéré",      "description": "Nœud noir issu d'une branche déjà morte. Adhérence dégradée, risque de déchaussement.", "status": "live"},
    {"key": "fissure",            "name": "Fissure",            "impact": "Critique",     "description": "Fente longitudinale ou transversale. Compromet la résistance mécanique de la pièce.", "status": "live"},
    {"key": "bleuissement",       "name": "Bleuissement",       "impact": "Esthétique",   "description": "Coloration grise/bleutée due à des champignons (Ophiostoma) sur l'aubier humide.", "status": "soon"},
    {"key": "moelle",             "name": "Moelle",             "impact": "Modéré",      "description": "Cœur de l'arbre. Tissu spongieux instable, fragilise la stabilité dimensionnelle.", "status": "soon"},
    {"key": "resine",             "name": "Résine",             "impact": "Esthétique",   "description": "Poche ou suintement de résine. Affecte l'aspect et la finition de surface.", "status": "soon"},
    {"key": "quartzite",          "name": "Quartzite",          "impact": "Critique",     "description": "Inclusion minérale dans le bois. Casse instantanément les outils de coupe.", "status": "soon"},
]


# Pipeline montré sur la home : ROI + BOBER (DefectTracker intégré en interne).
PIPELINE_STEPS: List[Dict] = [
    {
        "step": "01",
        "name": "ROI",
        "sub": "MobileNetV3 · CNN custom",
        "description": "Détecte la planche dans chaque frame et calcule ses 4 coins pour la redresser en perspective avant analyse.",
        "icon": "scan",
    },
    {
        "step": "02",
        "name": "BOBER",
        "sub": "YOLOv8 fine-tuné",
        "description": "Localise les nœuds et les fissures sur la planche recadrée avec bounding boxes et indice de confiance, puis confirme chaque défaut sur 40 frames minimum.",
        "icon": "target",
    },
]


SCORING_CLASSES: List[Dict] = [
    {"name": "Premium",  "range": "≥ 90/100",   "description": "Quasi sans défaut. Ébénisterie, haute menuiserie."},
    {"name": "Standard", "range": "70 – 89/100", "description": "Défauts mineurs admis. Charpente noble, parquet."},
    {"name": "Economy",  "range": "50 – 69/100", "description": "Défauts modérés. Coffrage, palettes haut de gamme."},
    {"name": "Reject",   "range": "< 50/100",   "description": "Défauts critiques. Recyclage, valorisation énergétique."},
]
