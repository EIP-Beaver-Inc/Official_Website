"""Static reference data for the BEAVER pipeline marketing site.
No external dependencies — used by /api/pipeline, /api/defects, /api/scoring,
and also drives the quiz Type de produit / classes qualité explanations.
"""
from typing import List, Dict


DEFECT_CLASSES: List[Dict] = [
    {
        "key": "noeud_vif",
        "name": "Nœud vif",
        "impact": "Mineur",
        "description": "Nœud sain, adhérent, issu d'une branche vivante au moment de l'abattage. Bonne intégration mécanique.",
    },
    {
        "key": "noeud_mort",
        "name": "Nœud mort",
        "impact": "Modéré",
        "description": "Nœud noir issu d'une branche déjà morte. Adhérence dégradée, risque de déchaussement.",
    },
    {
        "key": "fissure",
        "name": "Fissure",
        "impact": "Critique",
        "description": "Fente longitudinale ou transversale. Compromet la résistance mécanique de la pièce.",
    },
    {
        "key": "bleuissement",
        "name": "Bleuissement",
        "impact": "Esthétique",
        "description": "Coloration grise/bleutée due à des champignons (Ophiostoma) sur l'aubier humide.",
    },
    {
        "key": "moelle",
        "name": "Moelle",
        "impact": "Modéré",
        "description": "Cœur de l'arbre. Tissu spongieux instable, fragilise la stabilité dimensionnelle.",
    },
    {
        "key": "resine",
        "name": "Résine",
        "impact": "Esthétique",
        "description": "Poche ou suintement de résine. Affecte l'aspect et la finition de surface.",
    },
    {
        "key": "quartzite",
        "name": "Quartzite",
        "impact": "Critique",
        "description": "Inclusion minérale dans le bois. Casse instantanément les outils de coupe.",
    },
    {
        "key": "noeud_manquant",
        "name": "Nœud manquant",
        "impact": "Modéré",
        "description": "Cavité laissée par la chute d'un nœud. Trou traversant ou borgne.",
    },
    {
        "key": "noeud_avec_fissure",
        "name": "Nœud avec fissure",
        "impact": "Critique",
        "description": "Nœud présentant une fente. Cumul de deux défauts : déclassant en classes Q-B et inférieures.",
    },
]


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
        "description": "Localise 9 types de défauts sur la planche recadrée avec bounding boxes et indice de confiance.",
        "icon": "target",
    },
    {
        "step": "03",
        "name": "DefectTracker",
        "sub": "Multi-frame (min. 40)",
        "description": "Confirme les défauts en les suivant sur plusieurs frames pour éliminer les faux positifs.",
        "icon": "activity",
    },
]


SCORING_CLASSES: List[Dict] = [
    {"name": "Premium", "range": "≥ 90/100", "description": "Quasi sans défaut. Ébénisterie, haute menuiserie."},
    {"name": "Standard", "range": "70 – 89/100", "description": "Défauts mineurs admis. Charpente noble, parquet."},
    {"name": "Economy", "range": "50 – 69/100", "description": "Défauts modérés. Coffrage, palettes haut de gamme."},
    {"name": "Reject", "range": "< 50/100", "description": "Défauts critiques. Recyclage, valorisation énergétique."},
]


PRODUCT_TYPES: List[Dict] = [
    {
        "letter": "B",
        "name": "Plots (ou boules)",
        "desc": "Bille ouverte reconstituée. Largeur du plateau central ≥ 250 mm (≥ 350 mm pour Q-B-A). Longueur 2 m et plus.",
        "specs": "L ≥ 250 MM · LONG. ≥ 2 M",
    },
    {
        "letter": "F",
        "name": "Frises et avivés",
        "desc": "Frises : 40–99 mm de largeur. Avivés : ≥ 100 mm. Longueurs 250 à 2100 mm par pas de 50 mm.",
        "specs": "40–99 MM (FRISES) · ≥ 100 MM (AVIVÉS)",
    },
    {
        "letter": "S",
        "name": "Plateaux sélectionnés",
        "desc": "Plateaux individuels. Mêmes découverts minimums que les plots. Zone de classement 0,2 m × 2 m.",
        "specs": "L ≥ 250 MM · LONG. ≥ 2 M",
    },
    {
        "letter": "P",
        "name": "Pièces équarries",
        "desc": "Pièces massives. Dimensions courantes : 100×100, 120×120, 150×150, 180×180, 200×200, 250×250 mm.",
        "specs": "100×100 → 250×250",
    },
]


QUALITY_CLASSES: List[Dict] = [
    {"code": "Q-A1", "name": "Qualité supérieure stricte", "desc": "Quasi sans défaut. Ébénisterie de prestige."},
    {"code": "Q-A2", "name": "Qualité supérieure", "desc": "Défauts très limités. Menuiserie haut de gamme."},
    {"code": "Q-B1", "name": "Qualité courante stricte", "desc": "Défauts mineurs admis dans la zone de classement."},
    {"code": "Q-B2", "name": "Qualité courante", "desc": "Défauts modérés admis. Usage menuiserie courante."},
    {"code": "Q-C", "name": "Qualité industrielle", "desc": "Défauts marqués mais usage industriel viable."},
    {"code": "Q-D", "name": "Qualité déclassée", "desc": "Tous défauts admis. Usage palettes, coffrage."},
]
