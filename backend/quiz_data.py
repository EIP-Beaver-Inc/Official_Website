"""Quiz EN 975-1 — banque de questions sur la norme officielle classement chêne.
Basé sur le PDF officiel de la norme NF B53-501 / EN 975-1 (Quercus = Q).
Nomenclature : Q + Type produit (B/S/F/P) + Classe qualité (A, 1, 2, 3, 4).
"""
from typing import List, Dict, Tuple


QUIZ_QUESTIONS: List[Dict] = [
    {
        "id": "q1",
        "category": "Nomenclature",
        "question": "Dans la norme EN 975-1, que représente la lettre 'Q' au début de l'appellation (ex. Q-B 1) ?",
        "options": {
            "a": "Qualité — indice global de la pièce",
            "b": "Quercus — nom latin du chêne",
            "c": "Quartzite — type d'inclusion minérale",
            "d": "Quad — quadrille de classement",
        },
        "correct_answer": "b",
        "explanation": "Le 'Q' initial désigne Quercus (le chêne). L'appellation suit le format Q-X N : Q (essence) + X (type produit B/S/F/P) + N (classe qualitative A, 1, 2, 3 ou 4).",
    },
    {
        "id": "q2",
        "category": "Type de produit",
        "question": "Quelles sont les 4 catégories de produits couvertes par la norme EN 975-1 ?",
        "options": {
            "a": "B (plots), S (plateaux sélectionnés), F (frises et avivés), P (pièces équarries)",
            "b": "A (avives), B (boules), C (chevrons), D (douelles)",
            "c": "L (lames), M (madriers), P (planches), R (rondins)",
            "d": "P (plots), Q (quartiers), R (rives), S (sciages)",
        },
        "correct_answer": "a",
        "explanation": "La norme distingue : B = plots reconstitués (boules), S = plateaux sélectionnés, F = frises et avivés, P = pièces équarries.",
    },
    {
        "id": "q3",
        "category": "Plots (B)",
        "question": "Pour un plot de classe Q-B A (qualité exceptionnelle), quelle largeur minimale du plateau central est exigée ?",
        "options": {
            "a": "≥ 200 mm",
            "b": "≥ 250 mm",
            "c": "≥ 350 mm",
            "d": "≥ 500 mm",
        },
        "correct_answer": "c",
        "explanation": "Q-B A exige une largeur du plateau central ≥ 350 mm (mesurée à mi-longueur, sous écorce, aubier compris). Pour les classes Q-B 1, 2, 3 et 4, le seuil descend à ≥ 250 mm.",
    },
    {
        "id": "q4",
        "category": "Plots (B)",
        "question": "Quel est le découvert minimum (hors aubier) exigé pour un plot Q-B 1 ?",
        "options": {
            "a": "60 mm",
            "b": "80 mm",
            "c": "100 mm",
            "d": "120 mm",
        },
        "correct_answer": "c",
        "explanation": "Q-B 1 : découvert minimum 100 mm à mi-longueur. Q-B A : 120 mm tout au long. Q-B 2, 3, 4 : 80 mm.",
    },
    {
        "id": "q5",
        "category": "Frises et avivés (F)",
        "question": "Une pièce de 65 mm de largeur est classée :",
        "options": {
            "a": "Frise (Q-F)",
            "b": "Avivé (Q-F)",
            "c": "Plateau sélectionné (Q-S)",
            "d": "Aucune des catégories ci-dessus",
        },
        "correct_answer": "a",
        "explanation": "Les frises ont une largeur de 40 à 99 mm. À partir de 100 mm on parle d'avivés. Les longueurs vont de 250 à 2100 mm par pas de 50 mm.",
    },
    {
        "id": "q6",
        "category": "Zone de classement",
        "question": "Quelle est la zone de classement (rectangle virtuel) appliquée aux plots et plateaux sélectionnés ?",
        "options": {
            "a": "0,1 m × 1 m",
            "b": "0,2 m × 2 m",
            "c": "0,5 m × 1 m",
            "d": "1 m × 1 m",
        },
        "correct_answer": "b",
        "explanation": "Le choix est déterminé à partir d'un rectangle virtuel de 0,2 m × 2 m contenant le maximum de singularités sur la face de classement. Cette règle ne s'applique pas à Q-B A et Q-S A.",
    },
    {
        "id": "q7",
        "category": "Zone de classement",
        "question": "Une singularité (nœud, fente…) est ignorée dans le classement si elle se situe à moins de :",
        "options": {
            "a": "1 cm des bords",
            "b": "5 cm des bords",
            "c": "10 cm des bords",
            "d": "25 cm des bords",
        },
        "correct_answer": "c",
        "explanation": "Les singularités situées à moins de 10 cm des bords ou des extrémités d'un plateau ne sont pas prises en compte, sauf si la surface restante ne permet plus d'inscrire le rectangle 0,2 m × 2 m.",
    },
    {
        "id": "q8",
        "category": "Aubier",
        "question": "Sur l'appellation d'un avivé (ex. Q-F 2 XX), que signifie le suffixe 'XX' ?",
        "options": {
            "a": "Pièce double (deux faces de classement)",
            "b": "Aubier sain inférieur aux 2/3 de l'épaisseur",
            "c": "Aubier traversant",
            "d": "Pourriture exclue par contrat",
        },
        "correct_answer": "c",
        "explanation": "X indique un aubier sain ≤ 2/3 de l'épaisseur. XX indique un aubier traversant (de part en part). C'est une mention complémentaire à la classe.",
    },
    {
        "id": "q9",
        "category": "Pièces équarries (P)",
        "question": "Pour qu'une pièce soit classée équarrie (P) selon EN 975-1, il faut :",
        "options": {
            "a": "Épaisseur + largeur ≥ 200 mm ET épaisseur ≥ 80 mm",
            "b": "Épaisseur ≥ 100 mm uniquement",
            "c": "Largeur ≥ 250 mm uniquement",
            "d": "Section carrée parfaite obligatoire",
        },
        "correct_answer": "a",
        "explanation": "Critère EN 975-1 pour Q-P : (épaisseur + largeur) ≥ 200 mm ET épaisseur ≥ 80 mm. Dimensions courantes : 100×100, 120×120, 150×150, 180×180, 200×200, 250×250 mm.",
    },
    {
        "id": "q10",
        "category": "Classes qualité",
        "question": "Quelle est la classe la plus exigeante (qualité exceptionnelle) pour un plot ?",
        "options": {
            "a": "Q-B 1",
            "b": "Q-B A",
            "c": "Q-B 4",
            "d": "Q-B X",
        },
        "correct_answer": "b",
        "explanation": "L'échelle décroissante est : Q-B A (exceptionnelle) > Q-B 1 > Q-B 2 > Q-B 3 > Q-B 4 (sans limitation sauf accord contractuel). Q-B A n'admet qu'un nœud sain < 20 mm et exige une couleur homogène.",
    },
    {
        "id": "q11",
        "category": "Défauts admissibles",
        "question": "Quels défauts sont EXCLUS d'une planche Q-B A (qualité exceptionnelle) ?",
        "options": {
            "a": "Nœuds sains < 20 mm uniquement",
            "b": "Lunure, queue de vache, pourriture, entre-écorce, roulure",
            "c": "Aubier sain isolé et piqûre d'aubier",
            "d": "Tous les défauts sont admis",
        },
        "correct_answer": "b",
        "explanation": "Q-B A exclut formellement : lunure, queue de vache, pourriture, entre-écorce, roulure. Sont admis avec réduction : un nœud isolé < 15% largeur, aubier altéré isolé, piqûre d'aubier.",
    },
    {
        "id": "q12",
        "category": "Frises et avivés (F)",
        "question": "Sur une frise Q-F 1a (largeur < 120 mm), combien de nœuds sains < 10 mm sont admis ?",
        "options": {
            "a": "Aucun",
            "b": "Un seul",
            "c": "Deux",
            "d": "Sans limitation",
        },
        "correct_answer": "b",
        "explanation": "Q-F 1a : pièces de droit fil pratiquement exemptes de singularités. Un seul nœud sain < 10 mm admis sur les pièces < 120 mm de largeur (deux pour les pièces plus larges). 20% des pièces peuvent porter un nœud sain supplémentaire en face.",
    },
    {
        "id": "q13",
        "category": "Pipeline BEAVER",
        "question": "Combien de frames consécutives BEAVER exige-t-il pour confirmer un défaut et éliminer les faux positifs ?",
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
        "id": "q14",
        "category": "Pipeline BEAVER",
        "question": "Quel modèle du pipeline BEAVER calcule les 4 coins de la planche pour la redresser en perspective ?",
        "options": {
            "a": "BOBER (YOLOv8)",
            "b": "DefectTracker",
            "c": "ROI (MobileNetV3)",
            "d": "La machine à états",
        },
        "correct_answer": "c",
        "explanation": "ROI (MobileNetV3 CNN custom) localise la planche et estime ses 4 coins, ce qui permet une rectification perspective avant que BOBER (YOLOv8 fine-tuné) ne classe les 9 défauts.",
    },
    {
        "id": "q15",
        "category": "Pipeline BEAVER",
        "question": "Combien de classes de défauts BEAVER détecte-t-il sur la planche recadrée ?",
        "options": {
            "a": "4",
            "b": "6",
            "c": "9",
            "d": "12",
        },
        "correct_answer": "c",
        "explanation": "BOBER détecte 9 classes : nœud vif, nœud mort, fissure, bleuissement, moelle, résine, quartzite, nœud manquant, nœud avec fissure.",
    },
]


def build_public_questions() -> List[Dict]:
    """Return questions without correct_answer / explanation (frontend before submission)."""
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
