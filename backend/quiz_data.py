"""Quiz EN 975-1 — banque de questions sur la norme française classement chêne.
Les questions couvrent : types de produit (B/F/S/P), classes de qualité, dimensions,
défauts admissibles, et architecture du pipeline BEAVER.
"""
from typing import List, Dict, Tuple


QUIZ_QUESTIONS: List[Dict] = [
    {
        "id": "q1",
        "category": "Type de produit",
        "question": "Selon la norme EN 975-1, à quel type de produit correspond la lettre B ?",
        "options": {
            "a": "Plots (ou boules)",
            "b": "Frises et avivés",
            "c": "Plateaux sélectionnés",
            "d": "Pièces équarries",
        },
        "correct_answer": "a",
        "explanation": "Le type B désigne les plots (ou boules) : bille ouverte reconstituée. Largeur du plateau central ≥ 250 mm (≥ 350 mm pour Q-BA), longueur ≥ 2 m.",
    },
    {
        "id": "q2",
        "category": "Type de produit",
        "question": "Quelle est la largeur d'une frise selon la norme EN 975-1 (type F) ?",
        "options": {
            "a": "≥ 100 mm",
            "b": "40 à 99 mm",
            "c": "≤ 30 mm",
            "d": "≥ 250 mm",
        },
        "correct_answer": "b",
        "explanation": "Les frises ont une largeur de 40 à 99 mm. Au-delà (≥ 100 mm) on parle d'avivés. Longueurs : 250 à 2100 mm par pas de 50 mm.",
    },
    {
        "id": "q3",
        "category": "Type de produit",
        "question": "Pour le type S (plateaux sélectionnés), quelle est la zone de classement minimale ?",
        "options": {
            "a": "0,1 m × 1 m",
            "b": "0,2 m × 2 m",
            "c": "0,5 m × 3 m",
            "d": "1 m × 1 m",
        },
        "correct_answer": "b",
        "explanation": "Les plateaux sélectionnés (S) ont une zone de classement de 0,2 m × 2 m, avec les mêmes découverts minimums que les plots.",
    },
    {
        "id": "q4",
        "category": "Type de produit",
        "question": "Quelles dimensions courantes correspondent aux pièces équarries (type P) ?",
        "options": {
            "a": "40×40 à 80×80 mm",
            "b": "100×100 à 250×250 mm",
            "c": "300×300 mm uniquement",
            "d": "50×100 à 50×200 mm",
        },
        "correct_answer": "b",
        "explanation": "Les pièces équarries (P) sont des pièces massives. Dimensions courantes : 100×100, 120×120, 150×150, 180×180, 200×200, 250×250 mm.",
    },
    {
        "id": "q5",
        "category": "Classes de qualité",
        "question": "Quelle classe de qualité chêne (EN 975-1) admet le MOINS de défauts ?",
        "options": {
            "a": "Q-D",
            "b": "Q-C",
            "c": "Q-A1",
            "d": "Q-B2",
        },
        "correct_answer": "c",
        "explanation": "Q-A1 est la classe la plus stricte : surface quasi sans défauts. La hiérarchie décroissante est Q-A1 > Q-A2 > Q-B1 > Q-B2 > Q-C > Q-D.",
    },
    {
        "id": "q6",
        "category": "Classes de qualité",
        "question": "La moelle (cœur) est-elle admise en classe Q-A1 ?",
        "options": {
            "a": "Oui, sans restriction",
            "b": "Oui, si elle reste discrète",
            "c": "Non, jamais",
            "d": "Uniquement sur les rives",
        },
        "correct_answer": "c",
        "explanation": "En Q-A1, la moelle est exclue car elle compromet la stabilité dimensionnelle et l'aspect du bois. Elle n'est tolérée que dans les classes inférieures.",
    },
    {
        "id": "q7",
        "category": "Défauts",
        "question": "Le bleuissement du bois est causé par :",
        "options": {
            "a": "Une oxydation chimique de la sève",
            "b": "Des champignons saprophytes (lyctus, ophiostoma)",
            "c": "Un excès d'humidité dans la maille",
            "d": "Une contrainte de croissance",
        },
        "correct_answer": "b",
        "explanation": "Le bleuissement est dû à des champignons (notamment Ophiostoma) qui se développent dans l'aubier humide. Esthétique mais sans incidence mécanique majeure.",
    },
    {
        "id": "q8",
        "category": "Défauts",
        "question": "Dans le pipeline BEAVER, qu'est-ce qu'un nœud avec fissure ?",
        "options": {
            "a": "Un nœud sain entouré d'une auréole de résine",
            "b": "Un nœud présentant une fente débouchante ou interne",
            "c": "Un nœud manquant remplacé par du mastic",
            "d": "Un nœud noir oxydé",
        },
        "correct_answer": "b",
        "explanation": "Le nœud avec fissure est une classe spécifique : nœud présentant une fente. C'est un défaut critique car il fragilise mécaniquement la pièce.",
    },
    {
        "id": "q9",
        "category": "Pipeline BEAVER",
        "question": "Combien de frames consécutives BEAVER exige-t-il pour confirmer un défaut ?",
        "options": {
            "a": "5",
            "b": "10",
            "c": "40",
            "d": "100",
        },
        "correct_answer": "c",
        "explanation": "Le DefectTracker exige un minimum de 40 frames de suivi avant de confirmer un défaut. Cela élimine les faux positifs causés par poussière, reflets ou occlusions ponctuelles.",
    },
    {
        "id": "q10",
        "category": "Pipeline BEAVER",
        "question": "Quel rôle joue le modèle ROI (MobileNetV3) dans le pipeline ?",
        "options": {
            "a": "Détecter les défauts directement",
            "b": "Localiser la planche et calculer ses 4 coins pour la redresser",
            "c": "Compter les planches par minute",
            "d": "Mesurer l'humidité du bois",
        },
        "correct_answer": "b",
        "explanation": "ROI (MobileNetV3 CNN custom) détecte la planche dans chaque frame et estime ses 4 coins, ce qui permet une rectification perspective avant l'analyse fine par BOBER.",
    },
    {
        "id": "q11",
        "category": "Pipeline BEAVER",
        "question": "Combien de classes de défauts BOBER (YOLOv8) détecte-t-il ?",
        "options": {
            "a": "4",
            "b": "6",
            "c": "9",
            "d": "12",
        },
        "correct_answer": "c",
        "explanation": "BOBER détecte 9 classes : nœud vif, nœud mort, fissure, bleuissement, moelle, résine, quartzite, nœud manquant, nœud avec fissure.",
    },
    {
        "id": "q12",
        "category": "Classement",
        "question": "Selon le score BEAVER (0–100), à partir de quelle valeur une planche est-elle classée Premium ?",
        "options": {
            "a": "≥ 60",
            "b": "≥ 75",
            "c": "≥ 90",
            "d": "≥ 95",
        },
        "correct_answer": "c",
        "explanation": "Une planche obtient la classe Premium au-delà de 90/100. Standard : 70–89, Economy : 50–69, Reject : < 50. Ces seuils peuvent être ajustés par scierie.",
    },
    {
        "id": "q13",
        "category": "Norme EN 975-1",
        "question": "La norme EN 975-1 régit le classement de quel type de bois ?",
        "options": {
            "a": "Bois résineux structurels",
            "b": "Bois feuillus (chêne notamment)",
            "c": "Panneaux contreplaqués",
            "d": "Bois lamellé-collé",
        },
        "correct_answer": "b",
        "explanation": "EN 975-1 s'applique au classement d'aspect des sciages de feuillus, principalement le chêne. Pour les résineux, voir EN 1611-1.",
    },
    {
        "id": "q14",
        "category": "Type de produit",
        "question": "Pour un plot (B), quelle longueur minimale est requise ?",
        "options": {
            "a": "0,5 m",
            "b": "1 m",
            "c": "2 m",
            "d": "4 m",
        },
        "correct_answer": "c",
        "explanation": "Un plot doit avoir une longueur d'au moins 2 m. La largeur du plateau central doit être ≥ 250 mm (≥ 350 mm pour Q-B-A).",
    },
    {
        "id": "q15",
        "category": "Pipeline BEAVER",
        "question": "Pourquoi BEAVER utilise-t-il une machine à états par planche ?",
        "options": {
            "a": "Pour ajuster la vitesse du convoyeur",
            "b": "Pour ouvrir/fermer une session par planche selon sa présence dans le champ",
            "c": "Pour communiquer avec le frontend PyQt6",
            "d": "Pour entraîner les modèles en continu",
        },
        "correct_answer": "b",
        "explanation": "La machine à états ouvre une session quand la planche entre dans le champ et la ferme à sa sortie, garantissant un rapport JSON + photos par planche.",
    },
]


def build_public_questions() -> List[Dict]:
    """Return questions without the correct_answer / explanation (sent to frontend before submission)."""
    return [
        {
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "options": q["options"],
        }
        for q in QUIZ_QUESTIONS
    ]


def evaluate_answers(answers: List[Dict]) -> Tuple[int, int, List[Dict]]:
    """Score the answers and return (score, total, details)."""
    by_id = {q["id"]: q for q in QUIZ_QUESTIONS}
    given = {a["question_id"]: a["selected"] for a in answers}

    score = 0
    total = len(QUIZ_QUESTIONS)
    details: List[Dict] = []

    for q in QUIZ_QUESTIONS:
        sel = given.get(q["id"])
        is_correct = sel == q["correct_answer"]
        if is_correct:
            score += 1
        details.append({
            "question_id": q["id"],
            "question": q["question"],
            "selected": sel,
            "correct": q["correct_answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    return score, total, details
