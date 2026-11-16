"""Données de référence — chaîne BEAVER + norme EN 975-1.

Alignées sur le logiciel (dépôt Beaver) et sur l'IA (ORGA-IA_BEAVER) : les noms
sont ceux que l'application affiche à l'opérateur, le statut de détection est
celui du modèle livré avec le logiciel (BOBER v1.7).

status :
  live      détecté, montré avec une photo sur la page d'accueil
  detected  détecté, listé sans photo
  soon      prévu dans le modèle, pas encore assez d'exemples pour être fiable
"""
from typing import List, Dict


DEFECT_CLASSES: List[Dict] = [
    {"key": "noeud_vif",       "name": "Nœud sain",      "impact": "Mineur",
     "description": "Nœud adhérent, issu d'une branche vivante au moment de l'abattage. Admis dans la plupart des choix selon son diamètre.",
     "status": "live"},
    {"key": "noeud_mort",      "name": "Nœud mort",      "impact": "Modéré",
     "description": "Nœud sombre issu d'une branche déjà morte. Adhérence dégradée, risque de déchaussement : limites plus strictes que le nœud sain.",
     "status": "live"},
    {"key": "fissure",         "name": "Fente",          "impact": "Critique",
     "description": "Séparation des fibres dans le sens du fil. Mesurée en longueur, elle déclasse vite la pièce.",
     "status": "live"},
    {"key": "noeud_saute",     "name": "Nœud sauté",     "impact": "Modéré",
     "description": "Trou laissé par un nœud tombé de la planche.",
     "status": "detected"},
    {"key": "noeud_fendu",     "name": "Nœud fendu",     "impact": "Modéré",
     "description": "Nœud traversé par une fente : compté comme un nœud et comme une fente.",
     "status": "detected"},
    {"key": "noeud_pourri",    "name": "Nœud pourri",    "impact": "Critique",
     "description": "Nœud attaqué par la pourriture. Distingué du nœud mort : ses limites sont différentes dans presque tous les choix.",
     "status": "detected"},
    {"key": "patte_de_chat",   "name": "Patte de chat",  "impact": "Mineur",
     "description": "Groupe de petits nœuds serrés, typique du chêne.",
     "status": "detected"},
    {"key": "piqure",          "name": "Piqûre",         "impact": "Critique",
     "description": "Trous de galeries d'insectes. Exclue des meilleurs choix.",
     "status": "detected"},
    {"key": "pourriture",      "name": "Pourriture",     "impact": "Critique",
     "description": "Bois dégradé par des champignons. Encore trop peu d'exemples pour une détection fiable.",
     "status": "soon"},
    {"key": "moelle",          "name": "Moelle",         "impact": "Modéré",
     "description": "Cœur de l'arbre. Tissu tendre et instable, il fragilise la stabilité de la pièce.",
     "status": "soon"},
    {"key": "aubier_altere",   "name": "Aubier altéré",  "impact": "Modéré",
     "description": "Aubier dégradé ou coloré. Il décide des suffixes X et XX du classement du chêne.",
     "status": "soon"},
    {"key": "poche_ecorce",    "name": "Poche d'écorce", "impact": "Modéré",
     "description": "Écorce incluse dans le bois. Exclusion franche dans de nombreux choix.",
     "status": "soon"},
]


# Chaîne : ROI, BOBER, puis le moteur de classement EN 975-1.
PIPELINE_STEPS: List[Dict] = [
    {
        "step": "01",
        "name": "ROI",
        "sub": "YOLO OBB · boîte orientée",
        "description": "Localise la planche dans chaque image et la redresse en perspective, même quand elle arrive de travers sur le tapis.",
        "icon": "scan",
    },
    {
        "step": "02",
        "name": "BOBER",
        "sub": "YOLO fine-tuné · v1.7",
        "description": "Repère les singularités sur la planche redressée. Un défaut n'est retenu que s'il est confirmé sur plusieurs images ; les détections fugaces sont écartées.",
        "icon": "target",
    },
    {
        "step": "03",
        "name": "EN 975-1",
        "sub": "Moteur de classement",
        "description": "Mesure chaque défaut retenu en millimètres sur la planche entière et attribue son choix selon le produit demandé : plots, plateaux, frises ou pièces équarries.",
        "icon": "ruler",
    },
]


# Ce que reçoit une planche : le statut de sa note EN 975-1, tel que le logiciel l'affiche.
SCORING_CLASSES: List[Dict] = [
    {"name": "Classée",      "range": "ex. Q-F 1a",
     "description": "Tous les critères ont été vérifiés : la planche reçoit son choix (A, 1, 2, 3 ou 4 selon le produit)."},
    {"name": "Sous réserve", "range": "ex. Q-S 2",
     "description": "Un choix est donné, mais certains critères n'ont pas pu être vérifiés, par exemple une seule face filmée. Les réserves sont listées."},
    {"name": "Hors choix",   "range": "Q-F hors choix",
     "description": "La planche n'atteint aucun choix du produit demandé. Le défaut qui la limite est indiqué."},
    {"name": "Non classée",  "range": "aucune note",
     "description": "Pas de note possible, par exemple sans échelle (distance caméra–planche non renseignée). Les défauts restent détectés."},
]
