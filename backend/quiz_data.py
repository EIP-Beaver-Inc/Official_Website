"""Quiz EN 975-1 — classification d'images.
L'utilisateur regarde une image de bois et doit choisir la bonne classe parmi
la liste exhaustive groupée par type de produit.
NB : les classifications mockées ici sont indicatives à des fins de démo —
le client pourra fournir un dataset annoté par expert pour la production.
"""
from typing import List, Dict, Tuple


ANSWER_GROUPS: List[Dict] = [
    {
        "label": "Plots reconstitués (B)",
        "options": [
            {"key": "QBA",  "code": "Q-B A",  "hint": "Qualité exceptionnelle"},
            {"key": "QB1",  "code": "Q-B 1",  "hint": "Qualité supérieure"},
            {"key": "QB2",  "code": "Q-B 2",  "hint": "Qualité courante"},
            {"key": "QB3",  "code": "Q-B 3",  "hint": "Qualité industrielle"},
            {"key": "QB4",  "code": "Q-B 4",  "hint": "Déclassée"},
        ],
    },
    {
        "label": "Plateaux sélectionnés (S)",
        "options": [
            {"key": "QSA",  "code": "Q-S A",  "hint": "Qualité exceptionnelle"},
            {"key": "QS1",  "code": "Q-S 1",  "hint": "Qualité supérieure"},
            {"key": "QS2",  "code": "Q-S 2",  "hint": "Qualité courante"},
            {"key": "QS3",  "code": "Q-S 3",  "hint": "Qualité industrielle"},
            {"key": "QS4",  "code": "Q-S 4",  "hint": "Déclassée"},
        ],
    },
    {
        "label": "Frises et avivés (F)",
        "options": [
            {"key": "QF1A", "code": "Q-F 1a", "hint": "Droit fil (3%)"},
            {"key": "QF1B", "code": "Q-F 1b", "hint": "Supérieure"},
            {"key": "QF2",  "code": "Q-F 2",  "hint": "Standard"},
            {"key": "QF3",  "code": "Q-F 3",  "hint": "Courante"},
            {"key": "QF4",  "code": "Q-F 4",  "hint": "Industrielle"},
        ],
    },
    {
        "label": "Pièces équarries (P)",
        "options": [
            {"key": "QPA",  "code": "Q-P A",  "hint": "Qualité exceptionnelle"},
            {"key": "QP1",  "code": "Q-P 1",  "hint": "Qualité supérieure"},
            {"key": "QP2",  "code": "Q-P 2",  "hint": "Qualité courante"},
        ],
    },
]


# Set des clés valides (pour la validation backend).
VALID_KEYS = {opt["key"] for grp in ANSWER_GROUPS for opt in grp["options"]}


# Quiz items : chaque item = une image à classer.
QUIZ_QUESTIONS: List[Dict] = [
    {
        "id": "img1",
        "image_url": "/assets/wood_1_Q-B_4.jpg",
        "product_type": "Plot reconstitué",
        "correct_answer": "QB4",
        "explanation": "Plot présentant des défauts marqués : nœuds non adhérents, fissures et aubier traversant. Ces critères correspondent à Q-B 4 (qualité déclassée, sans limitation de singularités).",
    },
    {
        "id": "img2",
        "image_url": "/assets/wood_2_Q-F_1a.jpg",
        "product_type": "Frise ou avivé",
        "correct_answer": "QF1A",
        "explanation": "Pièce à fil parfaitement droit, quasi exempte de singularités. La flèche de fil ≤ 3 % de la largeur et l'absence de nœuds débouchants caractérisent Q-F 1a (droit fil exceptionnel).",
    },
    {
        "id": "img3",
        "image_url": "/assets/wood_3_Q-S_2.jpg",
        "product_type": "Plateau sélectionné",
        "correct_answer": "QS2",
        "explanation": "Plateau présentant des nœuds sains de diamètre modéré et un fil légèrement dévié. Ces caractéristiques correspondent à Q-S 2 (qualité courante, nœuds adhérents acceptés).",
    },
    {
        "id": "img4",
        "image_url": "/assets/wood_4_Q-B_2.jpg",
        "product_type": "Plot reconstitué",
        "correct_answer": "QB2",
        "explanation": "Plot présentant plusieurs nœuds sains de petit à moyen diamètre, cœur brun visible mais < 25 % de la largeur. Caractéristiques de Q-B 2 (qualité courante).",
    },
    {
        "id": "img5",
        "image_url": "/assets/wood_5_Q-S_3.jpg",
        "product_type": "Plateau sélectionné",
        "correct_answer": "QS3",
        "explanation": "Plateau marqué par plusieurs nœuds dont certains non adhérents et présence de cœur brun. Se classe Q-S 3 (qualité industrielle, lunure tolérée).",
    },
    {
        "id": "img6",
        "image_url": "/assets/wood_6_Q-F_3.png",
        "product_type": "Frise ou avivé",
        "correct_answer": "QF3",
        "explanation": "Pièce avec nœuds sains marqués et légères irrégularités de fil. Ces critères correspondent à Q-F 3 (qualité courante, nœuds < 40 mm autorisés).",
    },
    {
        "id": "img7",
        "image_url": "/assets/wood_7_Q-B_1.jpg",
        "product_type": "Plot reconstitué",
        "correct_answer": "QB1",
        "explanation": "Plot de belle facture : fil régulier, nœuds sains de petit diamètre peu fréquents, pas d'aubier ni de cœur brun apparent. Critères Q-B 1 (qualité supérieure).",
    },
    {
        "id": "img8",
        "image_url": "/assets/wood_8_Q-B_3.jpg",
        "product_type": "Plot reconstitué",
        "correct_answer": "QB3",
        "explanation": "Plot avec nœuds sains plus nombreux, flache et légères fissures admises. Le profil de singularités correspond à Q-B 3 (qualité industrielle).",
    },
    {
        "id": "img9",
        "image_url": "/assets/wood_9_Q-S_1.jpg",
        "product_type": "Plateau sélectionné",
        "correct_answer": "QS1",
        "explanation": "Plateau individuel propre, fil régulier, nœuds sains < 5 mm peu nombreux dans la zone de classement 0,2 m × 2 m. Critères Q-S 1 (qualité supérieure).",
    },
    {
        "id": "img10",
        "image_url": "/assets/wood_10-Q-F_2.jpg",
        "product_type": "Frise ou avivé",
        "correct_answer": "QF2",
        "explanation": "Avivé standard présentant quelques nœuds sains < 25 mm, fil légèrement dévié. Caractéristique de Q-F 2 (qualité standard, 3 nœuds max par mètre linéaire).",
    },
]


def build_public_questions() -> List[Dict]:
    """Return questions without correct_answer / explanation."""
    return [
        {
            "id": q["id"],
            "image_url": q["image_url"],
            "product_type": q["product_type"],
        }
        for q in QUIZ_QUESTIONS
    ]


def get_answer_groups() -> List[Dict]:
    return ANSWER_GROUPS


def _code_for_key(key: str) -> str:
    for grp in ANSWER_GROUPS:
        for opt in grp["options"]:
            if opt["key"] == key:
                return opt["code"]
    return key


def evaluate_answers(answers: List[Dict]) -> Tuple[int, int, List[Dict]]:
    """Score the answers and return (score, total, details)."""
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
            "image_url": q["image_url"],
            "product_type": q["product_type"],
            "selected": sel,
            "selected_code": _code_for_key(sel) if sel else None,
            "correct": q["correct_answer"],
            "correct_code": _code_for_key(q["correct_answer"]),
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    return score, total, details
