"""Quiz EN 975-1 — classification d'images.
L'utilisateur regarde une image de bois et doit choisir la bonne classe parmi
la liste exhaustive groupée par type de produit.
NB : les classifications mockées ici sont indicatives à des fins de démo —
le client pourra fournir un dataset annoté par expert pour la production.
"""
from typing import List, Dict, Tuple


# Liste exhaustive des réponses possibles (toujours affichées au quiz).
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
        "image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Plot reconstitué",
        "correct_answer": "QBA",
        "explanation": "Plot très large, fil droit, couleur homogène, aucun nœud apparent ni altération : critères Q-B A (qualité exceptionnelle, largeur ≥ 350 mm, découvert 120 mm).",
    },
    {
        "id": "img2",
        "image_url": "https://images.unsplash.com/photo-1597008641621-cefdcf7187d5?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Plot reconstitué",
        "correct_answer": "QB2",
        "explanation": "Plot présentant plusieurs nœuds sains de petit à moyen diamètre, cœur brun visible mais < 25 % de la largeur : caractéristiques Q-B 2 (qualité courante).",
    },
    {
        "id": "img3",
        "image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Plateau sélectionné",
        "correct_answer": "QS1",
        "explanation": "Plateau individuel propre, fil régulier, nœuds sains < 5 mm peu nombreux dans la zone de classement 0,2 m × 2 m : Q-S 1 (qualité supérieure).",
    },
    {
        "id": "img4",
        "image_url": "https://images.unsplash.com/photo-1597008641621-cefdcf7187d5?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Plateau sélectionné",
        "correct_answer": "QS3",
        "explanation": "Plateau marqué par plusieurs nœuds dont des nœuds non adhérents et cœur brun : se classe Q-S 3 (qualité industrielle, lunure tolérée).",
    },
    {
        "id": "img5",
        "image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Frise (largeur < 100 mm)",
        "correct_answer": "QF1B",
        "explanation": "Frise étroite, droit fil, quasi exempte de singularités ; quelques nœuds sains < 12 mm tolérés : Q-F 1b.",
    },
    {
        "id": "img6",
        "image_url": "https://images.unsplash.com/photo-1597008641621-cefdcf7187d5?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Avivé (largeur ≥ 100 mm)",
        "correct_answer": "QF2",
        "explanation": "Avivé standard avec 3 nœuds sains < 25 mm dans une largeur < 120 mm : caractéristique Q-F 2.",
    },
    {
        "id": "img7",
        "image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Avivé (largeur ≥ 100 mm)",
        "correct_answer": "QF4",
        "explanation": "Avivé industriel : nœuds sains marqués, quelques nœuds morts, flache acceptable. Q-F 4 (sans limitation sauf pourriture/piqûre).",
    },
    {
        "id": "img8",
        "image_url": "https://images.unsplash.com/photo-1597008641621-cefdcf7187d5?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Pièce équarrie",
        "correct_answer": "QP1",
        "explanation": "Pièce massive section ~150×150, fil droit, nœuds sains limités par mètre linéaire : critères Q-P 1.",
    },
    {
        "id": "img9",
        "image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Pièce équarrie",
        "correct_answer": "QPA",
        "explanation": "Pièce équarrie de section large (≥ 200×200), aspect quasi parfait sans nœud débouchant : Q-P A.",
    },
    {
        "id": "img10",
        "image_url": "https://images.unsplash.com/photo-1597008641621-cefdcf7187d5?auto=format&fit=crop&w=1400&q=80",
        "product_type": "Plot reconstitué",
        "correct_answer": "QB4",
        "explanation": "Plot présentant des défauts marqués : grosses fissures, multiples nœuds non adhérents, aubier traversant. Classé Q-B 4 (sans limitation).",
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
