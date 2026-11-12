"""Quiz EN 975-1 : questions à choix multiples sur le classement d'aspect du bois."""
from typing import Dict, List, Tuple

QUIZ: Dict = {'title': 'Classement du bois : êtes-vous au niveau ?',
 'description': "20 questions pour comprendre la norme EN 975-1 et ce qu'un bon classement change pour une scierie.",
 'questions': [{'id': 'q1',
                'question': 'Quels types de bois la norme EN 975-1 permet-elle de classer ?',
                'options': [{'id': 'a', 'text': 'Tous les résineux'},
                            {'id': 'b', 'text': 'Le chêne et le hêtre'},
                            {'id': 'c', 'text': 'Le pin et le sapin'},
                            {'id': 'd', 'text': 'Tous les bois tropicaux'}],
                'answer': 'b',
                'explanation': 'Cette norme concerne les planches de chêne et de hêtre, deux bois de grande valeur.'},
               {'id': 'q2',
                'question': 'Sur quoi se base cette norme pour classer une planche ?',
                'options': [{'id': 'a', 'text': "Sur l'humidité du bois"},
                            {'id': 'b', 'text': 'Sur ce qui se voit à la surface : nœuds, fissures, couleur…'},
                            {'id': 'c', 'text': "Sur l'âge de l'arbre"},
                            {'id': 'd', 'text': 'Sur la solidité de la planche'}],
                'answer': 'b',
                'explanation': "C'est un classement « d'aspect » : on juge la planche à l'œil, d'après ce qu'on voit. "
                               "La solidité est traitée par d'autres normes."},
               {'id': 'q3',
                'question': "À quoi sert une norme de classement commune à toute l'Europe ?",
                'options': [{'id': 'a',
                             'text': "À ce que le vendeur et l'acheteur soient d'accord sur ce que veut dire « bonne "
                                     'qualité »'},
                            {'id': 'b', 'text': 'À fixer le prix du bois'},
                            {'id': 'c', 'text': 'À remplacer les labels écologiques'},
                            {'id': 'd', 'text': 'À limiter les exportations'}],
                'answer': 'a',
                'explanation': "Quand une scierie annonce une classe de qualité, son client sait exactement ce qu'il "
                               'va recevoir, quel que soit le pays.'},
               {'id': 'q4',
                'question': 'La norme range les planches en classes de qualité. Laquelle est la meilleure ?',
                'options': [{'id': 'a', 'text': 'La classe A'},
                            {'id': 'b', 'text': 'La classe 2'},
                            {'id': 'c', 'text': 'La classe 4'},
                            {'id': 'd', 'text': 'La classe 1'}],
                'answer': 'a',
                'explanation': 'A est la qualité exceptionnelle. Viennent ensuite les choix numérotés 1, 2, 3…, du meilleur au '
                               'moins bon. Leur nombre dépend du type de pièce : les pièces équarries, par exemple, '
                               's’arrêtent au choix 2.'},
               {'id': 'q5',
                'question': "Dans une classe de qualité comme « QB1 », que désigne la lettre B ?",
                'options': [{'id': 'a', 'text': 'Le niveau de qualité'},
                            {'id': 'b', 'text': 'Du bois brut, non raboté'},
                            {'id': 'c', 'text': 'Le type de pièce de bois (ici, des plots)'},
                            {'id': 'd', 'text': 'La région de production'}],
                'answer': 'c',
                'explanation': "La première lettre désigne l'essence, la deuxième le type de pièce (B : plots, S : "
                               'plateaux, F : avivés et frises, P : pièces équarries) et le dernier caractère le niveau '
                               'de qualité.'},
               {'id': 'q6',
                'question': "Pourquoi l'apparence d'une planche compte-t-elle autant ?",
                'options': [{'id': 'a', 'text': 'Parce que le bois est toujours peint'},
                            {'id': 'b', 'text': "Parce que la loi l'impose pour tous les bois"},
                            {'id': 'c', 'text': 'Parce que les planches servent surtout de bois de chauffage'},
                            {'id': 'd',
                             'text': 'Parce que le bois sert souvent à faire des parquets, des meubles ou des portes, '
                                     'où il reste visible'}],
                'answer': 'd',
                'explanation': 'Pour ces usages, le bois reste visible : son apparence fait donc directement son prix.'},
               {'id': 'q7',
                'question': "Sur une planche, qu'appelle-t-on la « flache » ?",
                'options': [{'id': 'a',
                             'text': 'Un bord arrondi où il manque du bois, car la planche a été coupée trop près de '
                                     "l'extérieur du tronc"},
                            {'id': 'b', 'text': 'Un trou laissé par un nœud tombé'},
                            {'id': 'c', 'text': 'Une fissure au bout de la planche'},
                            {'id': 'd', 'text': "Une tache d'humidité"}],
                'answer': 'a',
                'explanation': 'Le tronc est rond : si on coupe trop près du bord, la planche garde un angle arrondi '
                               "au lieu d'un angle droit. Plus il y en a, plus la planche perd de la valeur."},
               {'id': 'q8',
                'question': "Qu'est-ce que l'aubier ?",
                'options': [{'id': 'a', 'text': 'Un vernis de finition'},
                            {'id': 'b', 'text': "Le centre de l'arbre, la partie la plus dure"},
                            {'id': 'c', 'text': 'Un champignon qui abîme le bois'},
                            {'id': 'd', 'text': "La partie la plus jeune du bois, plus claire, juste sous l'écorce"}],
                'answer': 'd',
                'explanation': "L'aubier est plus clair et résiste moins bien dans le temps que le reste du bois. Il "
                               'est limité dans les meilleures classes.'},
               {'id': 'q9',
                'question': 'Un nœud « sain » est bien attaché au bois, un nœud « mort » peut se détacher. Lequel fait '
                            'le plus baisser la qualité ?',
                'options': [{'id': 'a', 'text': 'Le nœud mort'},
                            {'id': 'b', 'text': 'Aucun, les nœuds ne comptent pas'},
                            {'id': 'c', 'text': 'Le nœud sain'},
                            {'id': 'd', 'text': 'Les deux comptent exactement pareil'}],
                'answer': 'a',
                'explanation': 'Un nœud mort peut tomber et laisser un trou dans la planche. Il est donc beaucoup plus '
                               'pénalisant.'},
               {'id': 'q10',
                'question': "Qu'appelle-t-on une « fente » dans le bois ?",
                'options': [{'id': 'a', 'text': 'Une rainure faite exprès à la scie'},
                            {'id': 'b', 'text': "Une trace d'insecte"},
                            {'id': 'c', 'text': 'Un changement de couleur'},
                            {'id': 'd',
                             'text': 'Une fissure qui apparaît dans le bois, souvent au bout de la planche'}],
                'answer': 'd',
                'explanation': 'Les fentes apparaissent souvent quand le bois sèche. Elles réduisent la partie de la '
                               "planche qu'on peut utiliser."},
               {'id': 'q11',
                'question': 'Lequel de ces défauts est interdit dans les meilleures classes ?',
                'options': [{'id': 'a', 'text': 'Une planche un peu plus longue que prévu'},
                            {'id': 'b', 'text': 'Un petit nœud bien attaché'},
                            {'id': 'c', 'text': 'Une légère différence de couleur'},
                            {'id': 'd', 'text': 'Du bois pourri'}],
                'answer': 'd',
                'explanation': "La pourriture est exclue des meilleures classes : elle abîme l'apparence et la "
                               'solidité du bois.'},
               {'id': 'q12',
                'question': "Aujourd'hui, dans la plupart des scieries, comment les planches sont-elles classées ?",
                'options': [{'id': 'a', 'text': 'Elles ne sont pas classées, tout est vendu en vrac'},
                            {'id': 'b', 'text': 'Un opérateur regarde chaque planche et décide de sa classe'},
                            {'id': 'c', 'text': 'Elles sont envoyées dans un laboratoire'},
                            {'id': 'd', 'text': "C'est le client qui les classe à la livraison"}],
                'answer': 'b',
                'explanation': "Le classement se fait encore surtout à l'œil, grâce à l'expérience d'opérateurs "
                               'formés.'},
               {'id': 'q13',
                'question': "Quel est le principal point faible d'un classement fait uniquement à l'œil ?",
                'options': [{'id': 'a', 'text': 'On ne voit pas les nœuds'},
                            {'id': 'b', 'text': 'Ça ne marche pas sur les bois clairs'},
                            {'id': 'c', 'text': "C'est interdit par la norme"},
                            {'id': 'd',
                             'text': 'Le résultat change selon la personne, sa fatigue et la vitesse à laquelle '
                                     'défilent les planches'}],
                'answer': 'd',
                'explanation': 'Deux opérateurs peuvent classer différemment la même planche, surtout en fin de '
                               'journée ou quand il faut aller vite.'},
               {'id': 'q14',
                'question': "Une planche est classée meilleure qu'elle ne l'est vraiment, puis livrée au client. Que "
                            'risque la scierie ?',
                'options': [{'id': 'a', 'text': 'Une réclamation du client et une perte de confiance'},
                            {'id': 'b', 'text': "Rien, elle gagne plus d'argent"},
                            {'id': 'c', 'text': 'Rien, le client ne verra pas la différence'},
                            {'id': 'd', 'text': 'Une amende automatique'}],
                'answer': 'a',
                'explanation': "Le client a payé pour une qualité précise. S'il reçoit moins bien, il réclame, demande "
                               'un geste commercial, et la relation se dégrade.'},
               {'id': 'q15',
                'question': "À l'inverse, une planche est classée moins bonne qu'elle ne l'est vraiment. Quelle est la "
                            'conséquence ?',
                'options': [{'id': 'a', 'text': "Elle est vendue moins cher qu'elle ne vaut : c'est de l'argent perdu"},
                            {'id': 'b', 'text': 'Elle doit être recoupée'},
                            {'id': 'c', 'text': 'Le client la refuse'},
                            {'id': 'd', 'text': "Aucune, c'est plus prudent"}],
                'answer': 'a',
                'explanation': "Personne ne s'en plaint, mais ça coûte : chaque planche sous-classée est vendue en "
                               'dessous de sa vraie valeur.'},
               {'id': 'q16',
                'question': 'En plus de classer chaque planche, que fixe aussi la norme EN 975-1 ?',
                'options': [{'id': 'a', 'text': 'Comment regrouper les planches en lots cohérents pour la vente'},
                            {'id': 'b', 'text': 'Les prix de transport'},
                            {'id': 'c', 'text': 'Les délais de livraison'},
                            {'id': 'd', 'text': 'Les machines à utiliser pour scier'}],
                'answer': 'a',
                'explanation': 'La norme donne aussi les règles pour constituer les lots, afin que le client reçoive '
                               'un ensemble homogène et conforme à sa commande.'},
               {'id': 'q17',
                'question': "Qu'est-ce qu'une caméra reliée à une intelligence artificielle peut repérer sur une "
                            'planche ?',
                'options': [{'id': 'a', 'text': 'Les défauts visibles : nœuds, fentes, bords arrondis, aubier…'},
                            {'id': 'b', 'text': 'Le prix de vente conseillé'},
                            {'id': 'c', 'text': "La région d'où vient le bois"},
                            {'id': 'd', 'text': "L'humidité à l'intérieur de la planche"}],
                'answer': 'a',
                'explanation': 'La plupart des critères de la norme se voient à la surface de la planche : c’est ce qui '
                               'rend un classement automatique possible.'},
               {'id': 'q18',
                'question': 'Combien de types de défauts Beaver repère-t-il automatiquement ?',
                'options': [{'id': 'a', 'text': '3'},
                            {'id': 'b', 'text': '5'},
                            {'id': 'c', 'text': '9'},
                            {'id': 'd', 'text': '15'}],
                'answer': 'a',
                'explanation': 'Beaver repère 3 types de défauts et indique la classe de qualité correspondante selon '
                               'la norme EN 975-1.'},
               {'id': 'q19',
                'question': "Quel est le principal avantage d'un classement automatique pour une scierie ?",
                'options': [{'id': 'a', 'text': 'Couper les troncs plus vite'},
                            {'id': 'b', 'text': "Ne plus avoir besoin de personne dans l'atelier"},
                            {'id': 'c',
                             'text': "Un classement identique d'une planche à l'autre, même à grande vitesse"},
                            {'id': 'd', 'text': 'Changer les règles de la norme'}],
                'answer': 'c',
                'explanation': "La machine applique toujours les mêmes critères, sans fatigue. L'opérateur peut se "
                               'concentrer sur les planches difficiles à juger.'},
               {'id': 'q20',
                'question': "Un client n'est pas d'accord avec la qualité d'un lot livré. Qu'est-ce qui aide le plus "
                            'la scierie à lui répondre ?',
                'options': [{'id': 'a', 'text': 'Arrêter de travailler avec ce client'},
                            {'id': 'b', 'text': 'Baisser le prix sans discuter'},
                            {'id': 'c', 'text': 'Refaire tout le lot'},
                            {'id': 'd', 'text': 'Pouvoir montrer une photo et la liste des défauts de chaque planche'}],
                'answer': 'd',
                'explanation': 'Avec une trace de chaque planche, la scierie peut justifier son classement : la '
                               'discussion porte sur des faits, pas sur des impressions.'}]}

QUIZ_QUESTIONS: List[Dict] = QUIZ["questions"]


def build_public_questions() -> List[Dict]:
    return [{"id": q["id"], "question": q["question"], "options": q["options"]} for q in QUIZ_QUESTIONS]


def _option_text(question: Dict, option_id: str) -> str:
    return next((o["text"] for o in question["options"] if o["id"] == option_id), None)


def evaluate_answers(answers: List[Dict]) -> Tuple[int, int, List[Dict]]:
    given = {a["question_id"]: a["selected"] for a in answers}
    details: List[Dict] = []
    for q in QUIZ_QUESTIONS:
        selected = given.get(q["id"])
        details.append({
            "question_id": q["id"],
            "question": q["question"],
            "selected": selected,
            "selected_text": _option_text(q, selected) if selected else None,
            "correct": q["answer"],
            "correct_text": _option_text(q, q["answer"]),
            "is_correct": selected == q["answer"],
            "explanation": q["explanation"],
        })
    score = sum(d["is_correct"] for d in details)
    return score, len(QUIZ_QUESTIONS), details
