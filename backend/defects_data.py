"""Static reference data — BEAVER pipeline + EN 975-1 norm."""
from typing import List, Dict


DEFECT_CLASSES: List[Dict] = [
    {"key": "noeud_vif",          "name": "Nœud vif",          "impact": "Mineur",       "description": "Nœud sain, adhérent, issu d'une branche vivante au moment de l'abattage. Bonne intégration mécanique."},
    {"key": "noeud_mort",         "name": "Nœud mort",         "impact": "Modéré",      "description": "Nœud noir issu d'une branche déjà morte. Adhérence dégradée, risque de déchaussement."},
    {"key": "fissure",            "name": "Fissure",            "impact": "Critique",     "description": "Fente longitudinale ou transversale. Compromet la résistance mécanique de la pièce."},
    {"key": "bleuissement",       "name": "Bleuissement",       "impact": "Esthétique",   "description": "Coloration grise/bleutée due à des champignons (Ophiostoma) sur l'aubier humide."},
    {"key": "moelle",             "name": "Moelle",             "impact": "Modéré",      "description": "Cœur de l'arbre. Tissu spongieux instable, fragilise la stabilité dimensionnelle."},
    {"key": "resine",             "name": "Résine",             "impact": "Esthétique",   "description": "Poche ou suintement de résine. Affecte l'aspect et la finition de surface."},
    {"key": "quartzite",          "name": "Quartzite",          "impact": "Critique",     "description": "Inclusion minérale dans le bois. Casse instantanément les outils de coupe."},
    {"key": "noeud_manquant",     "name": "Nœud manquant",     "impact": "Modéré",      "description": "Cavité laissée par la chute d'un nœud. Trou traversant ou borgne."},
    {"key": "noeud_avec_fissure", "name": "Nœud avec fissure", "impact": "Critique",     "description": "Nœud présentant une fente. Cumul de deux défauts : déclassant en classes inférieures."},
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
        "description": "Localise 9 types de défauts sur la planche recadrée avec bounding boxes et indice de confiance, puis confirme chaque défaut sur 40 frames minimum.",
        "icon": "target",
    },
]


SCORING_CLASSES: List[Dict] = [
    {"name": "Premium",  "range": "≥ 90/100",   "description": "Quasi sans défaut. Ébénisterie, haute menuiserie."},
    {"name": "Standard", "range": "70 – 89/100", "description": "Défauts mineurs admis. Charpente noble, parquet."},
    {"name": "Economy",  "range": "50 – 69/100", "description": "Défauts modérés. Coffrage, palettes haut de gamme."},
    {"name": "Reject",   "range": "< 50/100",   "description": "Défauts critiques. Recyclage, valorisation énergétique."},
]


PRODUCT_TYPES: List[Dict] = [
    {"letter": "B", "name": "Plots reconstitués",     "desc": "Bille ouverte reconstituée. Largeur du plateau central ≥ 250 mm (≥ 350 mm pour Q-B A). Longueur 2 m et plus. Découvert minimum 80 à 120 mm selon la classe.", "specs": "L ≥ 250 MM · LONG. ≥ 2 M"},
    {"letter": "S", "name": "Plateaux sélectionnés",  "desc": "Plateaux individuels. Mêmes critères de découvert et de largeur que les plots. Zone de classement 0,2 m × 2 m.",                                                  "specs": "L ≥ 250 MM · LONG. ≥ 2 M"},
    {"letter": "F", "name": "Frises et avivés",        "desc": "Frises : 40–99 mm de largeur. Avivés : ≥ 100 mm. Longueurs 250 à 2100 mm par pas de 50 mm. Épaisseur typique 41 mm.",                                                       "specs": "40–99 MM (FRISES) · ≥ 100 MM (AVIVÉS)"},
    {"letter": "P", "name": "Pièces équarries",       "desc": "Pièces massives. Épaisseur + largeur ≥ 200 mm ET épaisseur ≥ 80 mm. Dimensions courantes : 100×100 à 250×250 mm.",                                                                  "specs": "ÉP. + LARG. ≥ 200 MM · ÉP. ≥ 80 MM"},
]


QUALITY_CLASSES: List[Dict] = [
    {"code": "Q-B A",  "name": "Plot · Qualité exceptionnelle", "desc": "Largeur ≥ 350 mm, découvert 120 mm. Nœud sain < 20 mm. Lunure, pourriture, roulure exclues."},
    {"code": "Q-B 1",  "name": "Plot · Qualité supérieure",     "desc": "Largeur ≥ 250 mm, découvert 100 mm. Nœuds sains < 5 mm (max 8). Lunure exclue."},
    {"code": "Q-B 2",  "name": "Plot · Qualité courante",       "desc": "Découvert 80 mm. Nœuds < 5 mm sans limite, < 40 mm équivalent à 100 mm. Cœur brun < 25 %."},
    {"code": "Q-B 3",  "name": "Plot · Qualité industrielle",   "desc": "Nœuds sains < 10 mm sans limite, < 70 mm équivalent à 160 mm. Lunure tolérée."},
    {"code": "Q-B 4",  "name": "Plot · Déclassée",              "desc": "Pas de limitation, sauf exclusions par accord contractuel."},
    {"code": "Q-F 1a", "name": "Frise · Droit fil",             "desc": "Pièces de droit fil (3 %). 1 nœud sain < 10 mm pour largeur < 120 mm."},
    {"code": "Q-F 2",  "name": "Frise · Standard",              "desc": "3 nœuds sains < 25 mm pour largeur < 120 mm. Équivalence 75 mm."},
    {"code": "Q-F 4",  "name": "Avivé · Industriel",            "desc": "Nœuds sains < 70 mm sans limitation. Flache jusqu'à 10 % largeur."},
]
